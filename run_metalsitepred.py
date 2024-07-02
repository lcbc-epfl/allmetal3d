#!/usr/bin/env python3

import glob
import argparse
import time

import torch
import torch.nn as nn
from utils.helpersNew import *

# from utils.voxelization import processStructures
from utils.voxelizationNew import processStructures as processStructures
from utils.voxelizationNew import voxelize_identity_location
from utils.model import LocationModel, IdentityModel


import warnings

import pandas as pd


from tabulate import tabulate


from Bio.PDB import *

metalions = [
    "ZN",
    "K",
    "NA",
    "CA",
    "MG",
    "FE2",
    "FE",
    "CO",
    "CU",
    "CU1",
    "MN",
    "NI",
]


def predict_location(
    model,
    device,
    pdb,
    batch_size=50,
    threshold=7,
    pthreshold=0.10,
    cubefile="prediction.cube",
    probefile="prediction.pdb",
    mode="fast",
    central_residue="",
    radius=8
):

    # since we detect also alkali and earth alkali ions -> need to voxelize whole protein

    if mode == "fast":
        coords = get_all_protein_resids_blocked(pdb)
    elif mode == "all":
        coords = get_all_protein_resids(pdb)
    else:
        coords = get_coords_central_res(pdb, central_residue, radius)
           

    if len(coords) == 0:
        print("no coords specified")
    voxels, prot_centers, prot_N, prots = processStructures(pdb, coords)
    voxels.to(device)
    model.eval()
    outputs = torch.zeros([voxels.size()[0], 1, 32, 32, 32])

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")

        for i in range(0, voxels.size()[0], batch_size):
            o = model(voxels[i : i + batch_size])
            outputs[i : i + batch_size] = o.cpu().detach()

    prot_v = np.vstack(prot_centers)

    output_v = outputs.flatten().numpy()

    bb = get_bb(prot_v)

    grid, box_N = create_grid_fromBB(bb)

    probability_values = get_probability_mean(grid, prot_v, output_v)

    if cubefile != None:
        cube = write_cubefile(
            bb,
            probability_values,
            box_N,
            outname=cubefile,
            gridres=1,
        )

    if probefile != None:
        unique_sites = find_unique_sites(
            probability_values,
            grid,
            writeprobes=True,
            probefile=probefile,
            threshold=threshold,
            p=pthreshold,
        )
    else:
         unique_sites = find_unique_sites(
            probability_values,
            grid,
            writeprobes=False,
            probefile="",
            threshold=threshold,
            p=pthreshold,
        )
    return unique_sites


def determine_close_residues(pdb, probe, threshold=3.5):

    pdbparser = PDBParser()
    structure = pdbparser.get_structure("protein", pdb)
    
    # do neighbor search with probe coord
    atoms  = Selection.unfold_entities(structure, 'A')
    ns = NeighborSearch(atoms)

    close_atoms = ns.search(probe, threshold)
    # get residues 
    close_residues = []
    for atom in close_atoms: 
        close_residues.append(atom.get_parent())
    
    # make unique
    close_residues = list(set(close_residues))
    # convert to {"resid":resid, "chain":chain, model":model}
    vals = []
    for res in close_residues:
        # if hetero continue
        if res.id[0] != " ":
            continue
        val = {"resi":res.id[1], "chain":res.get_parent().id, "model":0, "resn":res.get_resname()}
        vals.append(val)
    return vals



def predict_identity(model, device, pdb, sites):


    voxels = voxelize_identity_location(pdb, sites)
    probabilities = [site[1] for site in sites]
    probabilities = torch.FloatTensor(probabilities)
    probabilities.to(device)

    voxels.to(device)
    model.eval()
    o = model(voxels, probabilities)

    voxels = voxelize_identity_location(pdb, sites)
    probabilities = [site[1] for site in sites]
    probabilities = torch.FloatTensor(probabilities)
    probabilities.to(device)

    voxels.to(device)
    model.eval()
    o = model(voxels, probabilities)

    l_metal = ['Alkali', 'MG','CA','ZN', 'NonZNTM', 'NoMetal']
    l_geometry = ['tetrahedron', 'octahedron', 'pentagonal bipyramid',   'square','Irregular', 'other','NoMetal']


    df = pd.DataFrame(columns=["Site", "Identity", "Vacancy", "Geometry", "Probability"])
    df = pd.DataFrame(columns=["Site", "Identity", "Vacancy", "Geometry", "Probability"])

    # Populate the DataFrame
    identities = []
    for i, site in enumerate(sites):
        identity = f"{l_metal[o[0][i].argmax()]} {o[0][i][o[0][i].argmax()]*100:.2f}%"
        # vacancy = f"{l_vacancy[o[1][i].argmax()]} {o[1][i][o[1][i].argmax()]*100:.2f}%"
        # geometry = f"{l_geometry[o[2][i].argmax()]} {o[2][i][o[2][i].argmax()]*100:.2f}%"
        geometry = f"{l_geometry[o[1][i].argmax()]} {o[1][i][o[1][i].argmax()]*100:.2f}%"
        identities.append(l_metal[o[0][i].argmax()])
        # df = df.append({"Site": i, "Identity": identity, "Vacancy": vacancy, "Geometry": geometry, "Probability": f"{site[1]*100:.2f} %"}, ignore_index=True)
        df = df.append({"Site": i, "Identity": identity, "Geometry": geometry, "Probability": f"{site[1]*100:.2f} %"}, ignore_index=True)

    
    probe_content = write_probefile(sites, identities, "probefile.pdb")
    # Print the formatted table
    print(tabulate(df, headers='keys', tablefmt='psql'))
    results = []
    for i, row in df.iterrows(): 

        close_residues = determine_close_residues(pdb, sites[i][0])
        res =  {"index":i+1,
        "location_confidence": round(float(row["Probability"].replace("%","")),2),
        "probabilities_identity":[round(x,2) for x in o[0][i].tolist()],
        "probabilities_geometry":[round(x,2) for x in o[1][i].tolist()],
        "close_residues":close_residues}
        results.append(res)
    return probe_content, results



if __name__ == "__main__":
    start_time = time.time()

    parser = argparse.ArgumentParser(
        description="predict metal location and features"
    )


    parser.add_argument("--threshold", help="cluster threshold", type=float, default=7)
    parser.add_argument("--pthreshold", help="p threshold", type=float, default=0.25)
    parser.add_argument("--batch_size", help="default(50)", type=int, default=50)
    parser.add_argument(
        "--pdb", help="path to pdb file", type=str, default="", required=True
    )
    parser.add_argument(
        "--cubefile", help="path to cubefile", type=str, default="",
    )
    parser.add_argument(
        "--probefile", help="path to probefile", type=str, default=""
    )
    parser.add_argument(
        "--residuesamplingmode", help="how to sample residues, fast(blocked), all or around a site ", type=str, default="fast"
    )
    parser.add_argument(
        "--central_residue", help="if sampling around a residue, id of residue", type=int, default=1
    )
    parser.add_argument(
        "--radius", help="Radius to include residues in around the central residue", type=int, default=5
    )

    args = parser.parse_args()


    probefile = None
    if args.probefile != "":
        probefile = args.probefile
    
    cubefile = None
    if args.cubefile != "":
        cubefile = args.cubefile

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = LocationModel()
    model.to(device)

    model.load_state_dict(
        torch.load(
            f"weights/metal_0.5A_allmetal_one3dchannel_16Abox_filter6_epoch6.pth"
        )
    )

    identity_model = IdentityModel()

    identity_model = nn.DataParallel(identity_model)

    identity_model.to(device)

    identity_model.load_state_dict(
        torch.load(
            "weights/identity_vacancy_geometry_model_2024-03-01_train_lessclasses_skipconnect_hyperparametertuned_geometry_identity_all_g09_300epoch_p01_epoch300.pth"
        )
    )

    # step 1 
    # location prediction
    predicted_metal_locations = predict_location(
            model,
            device,
            args.pdb,
            batch_size=args.batch_size,
            threshold=args.threshold,
            pthreshold=args.pthreshold,
            probefile=probefile,
            cubefile=cubefile
    )
    predicted_metal_locations = predict_location(
            model,
            device,
            args.pdb,
            batch_size=args.batch_size,
            threshold=args.threshold,
            pthreshold=args.pthreshold,
            probefile=probefile,
            cubefile=cubefile, 
            mode=args.residuesamplingmode, 
            central_residue=args.central_residue,
            radius=args.radius
    )
    

    # step 2 
    # predict features
    final = predict_identity(
        identity_model,
        device,
        args.pdb,
        predicted_metal_locations
    )
    print(final)
