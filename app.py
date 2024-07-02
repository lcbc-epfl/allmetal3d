#!/usr/bin/env python3

import glob
import argparse
import time
import json

import gradio as gr

from gradio_molecule3d import Molecule3D

import torch
import torch.nn as nn
from utils.helpersNew import *

# from utils.voxelization import processStructures
from utils.voxelizationNew import processStructures as processStructures
from utils.voxelizationNew import voxelize_identity_location
from utils.model import LocationModel, IdentityModel
from moleculekit.tools.voxeldescriptors import getVoxelDescriptors, viewVoxelFeatures

from moleculekit.util import boundingBox

from scipy.spatial import distance

import warnings

import pandas as pd
import ast

from tabulate import tabulate

from tqdm import tqdm

from Bio.PDB import *

from frontend_novacancy import html_molecule

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

private_link = ""

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
    return unique_sites, cube


def visualize(pdb="", probe="", results="", cube="", private_link = ""):
    # <code id="res">"""+json.dumps(results)+"""</code> <br> <br> <code id="probe">"""+json.dumps(probe)+"""</code>
    
    with open(pdb, 'r+') as fp:
        pdb_content = fp.read()
    x = html_molecule(pdb_content, probe, results, cube, private_link)
    return f"""<iframe style="width:100%; height: 1300px" name="result" allow="midi; geolocation; microphone; camera; 
    display-capture; encrypted-media;" sandbox="allow-modals allow-forms 
    allow-scripts allow-same-origin allow-popups 
    allow-top-navigation-by-user-activation allow-downloads" allowfullscreen="" 
    allowpaymentrequest="" frameborder="0" srcdoc='{x}'></iframe>"""


def predict_identity(model, device, pdb, sites):

    voxels = voxelize_identity_location(pdb, sites)
    probabilities = [site[1] for site in sites]
    probabilities = torch.FloatTensor(probabilities)
    probabilities.to(device)

    voxels.to(device)
    model.eval()
    o = model(voxels, probabilities)

    l_metal = ['Alkali', 'MG','CA','ZN', 'NonZNTM', 'NoMetal']
    l_geometry = ['tetrahedron', 'octahedron', 'pentagonal bipyramid',   'square','Irregular', 'other','NoMetal']
    # l_metal = ["MG", "NonZNTM", "Alkali", "ZN", "NoMetal", "CA"]
    # l_vacancy = ["full", "NoMetal", "irregular", "vacancy"]
    # l_geometry = ['trigonal bipyramid', 'trigonal prism', "other",  'pentagonal bipyramid',"trigonal plane", "octahedron",    'square','NoMetal', "tetrahedron", "irregular"]



    df = pd.DataFrame(columns=["Site", "Identity", "Geometry", "Probability"])

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
        # "probabilities_vacancy":[round(x,2) for x in o[1][i].tolist()],
        # "probabilities_geometry":[round(x,2) for x in o[2][i].tolist()],
        "probabilities_geometry":[round(x,2) for x in o[1][i].tolist()],
        "close_residues":close_residues}
        results.append(res)
    return probe_content, results


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


    

def predict(pdb, pthreshold=0.1, threshold=7, batch_size=20, mode="fast", central_residue=None, radius=8):
    start_time = time.time()

    probefile = os.path.basename(pdb.name).split(".")[0] + "_probes.pdb"
    
    cubefile = os.path.basename(pdb.name).split(".")[0] + "_out.cube"

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
    predicted_metal_locations,cube = predict_location(
            model,
            device,
            pdb.name,
            batch_size=batch_size,
            threshold=threshold,
            pthreshold=pthreshold,
            probefile=probefile,
            cubefile=cubefile, 
            mode=mode, 
            central_residue=central_residue,
            radius=radius
    )

    # step 2 
    # predict features
    if predicted_metal_locations==None:
        raise gr.Error(f"No density found above choses probability cutoff p={pthreshold:.2f}")
    
    probe_content, results  = predict_identity(
        identity_model,
        device,
        pdb.name,
        predicted_metal_locations
    )
    # sort final based on probability


    print("--- %s seconds ---" % (time.time() - start_time))

    
    return visualize(pdb=pdb.name,probe=probe_content,results=results,cube=cube, private_link=private_link)

def update_mode(mode):
    if mode in ['fast', 'all']:
        return gr.Textbox(visible=False), gr.Slider(visible=False)
    else:
        return gr.Textbox(visible=True), gr.Slider(visible=True)


with gr.Blocks() as blocks: 
    gr.Markdown("## Metalloprotein Prediction")
    pdb = Molecule3D(label="Input PDB", showviewer=False) #gr.File("2cba.pdb",label="Upload PDB file")

    gr.Markdown("Metals might bind anywhere in the protein, choose how to sample the residues in the protein")
    gr.Markdown("Fast uses blocked sampling of residues to reduce required computational time, full uses all residues, site allows you to look around a specific site in the protein")
    
    with gr.Row("Mode"):
        mode = gr.Dropdown(["fast", "all", "site"], value="fast")
        central_residue = gr.Textbox(label="Central residue")
        radius = gr.Slider(value=8, minimum=4, maximum=50, label="Distance threshold")
    mode.change(update_mode, mode, [central_residue, radius])

    with gr.Accordion("Settings"):
        threshold = gr.Slider(value=7,minimum=0, maximum=10,  label="Threshold")
        pthreshold = gr.Slider(value=0.25,minimum=0.1, maximum=1,  label="Probability Threshold")
        batch_size = gr.Slider(value=50, minimum=0, maximum=100, label="Batch Size")

    btn = gr.Button("Predict")

    out = gr.HTML("")
    btn.click(predict, inputs=[pdb, pthreshold, threshold, batch_size, mode, central_residue, radius], outputs=out)

_,_,pl = blocks.launch(share=True, prevent_thread_lock=True, allowed_paths=["frontend"])

private_link = pl

input("press to enter")


    

    

