#!/usr/bin/env python3

import warnings
import time


import gradio as gr

import torch
import torch.nn as nn

from .helpersNew import *

from .voxelizationNew import processStructures as processStructures
from .voxelizationNew import voxelize_identity_location
from .model import LocationModel, IdentityModel, WaterModel

from gradio_molecule3d import Molecule3D

from pathlib import Path

import pandas as pd

from tabulate import tabulate

from Bio.PDB import *

from ..frontend.frontend_novacancy import html_molecule

from . import constants


from halo import Halo

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



def voxelize(
    device,
    pdb,
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
    return voxels, prot_centers

def predict_location(
    model,
    device,
    pdb,
    voxels,
    prot_centers,
    batch_size=50,
    threshold=7,
    pthreshold=0.10,
    cubefile="prediction.cube",
    probefile="prediction.pdb",
    backend="multiprocessing"
):

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

    probability_values = get_probability_mean(grid, prot_v, output_v, implementation=backend)

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



def predict_water(
    model,
    device,
    pdb,
    voxels, 
    prot_centers,
    batch_size=50,
    threshold=4,
    pthreshold=0.10,
    cubefile="water.cube",
    probefile="water.pdb",
    mode="fast",
    central_residue="",
    radius=8,
    backend="multiprocessing"
):

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

    probability_values = get_probability_mean(grid, prot_v, output_v,implementation=backend)

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
            mode="water"
        )
    else:
         unique_sites = find_unique_sites(
            probability_values,
            grid,
            writeprobes=False,
            probefile="",
            threshold=threshold,
            p=pthreshold,
            mode="water"
        )
    return_json = [p for coords,p   in unique_sites]
    return return_json, cube


def visualize(pdb="", probe="", results="", cube="",water_cube="", private_link = ""):

    with open(pdb, 'r+') as fp:
        pdb_content = fp.read()
    x = html_molecule(pdb_content, probe, results, cube, water_cube, private_link)

    # in order to get around browser security restrictions, we need to use an iframe
    return f"""<iframe style="width:100%; height: 1300px" name="result" allow="midi; geolocation; microphone; camera; 
    display-capture; encrypted-media;" sandbox="allow-modals allow-forms 
    allow-scripts allow-same-origin allow-popups 
    allow-top-navigation-by-user-activation allow-downloads" allowfullscreen="" 
    allowpaymentrequest="" frameborder="0" srcdoc='{x}'></iframe>"""


def predict_identity(model, device, pdb, sites, probefile, spinner=None):

    voxels = voxelize_identity_location(pdb, sites)
    probabilities = [site[1] for site in sites]
    probabilities = torch.FloatTensor(probabilities)
    probabilities.to(device)

    voxels.to(device)
    model.eval()
    o = model(voxels, probabilities)

    l_metal = ['Alkali', 'MG','CA','ZN', 'NonZNTM', 'NoMetal']
    l_geometry = ['tetrahedron', 'octahedron', 'pentagonal bipyramid',   'square','Irregular', 'other','NoMetal']

    df = pd.DataFrame(columns=["Site", "Identity", "Geometry", "Probability"])

    # Populate the DataFrame
    identities = []
    for i, site in enumerate(sites):
        identity = f"{l_metal[o[0][i].argmax()]} {o[0][i][o[0][i].argmax()]*100:.2f}%"
        geometry = f"{l_geometry[o[1][i].argmax()]} {o[1][i][o[1][i].argmax()]*100:.2f}%"
        identities.append(l_metal[o[0][i].argmax()])
        df = pd.concat([df, pd.DataFrame({"Site": [i], "Identity": [identity], "Geometry": [geometry], "Probability": [f"{site[1]*100:.2f} %"]})])

    
    probe_content = write_probefile(sites, identities, probefile)
    # Print output
    if spinner!=None:
        spinner.info("AllMetal3D found the following metals:\n")
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


def determine_close_residues(pdb, probe, threshold=3.5):

    pdbparser = PDBParser()
    mmcifparser = MMCIFParser()

    if pdb.split(".")[-1] == "pdb":
        structure = pdbparser.get_structure("protein", pdb)
    else:
        structure = mmcifparser.get_structure("protein", pdb)
    
    # do neighbor search with probe coord
    atoms  = Selection.unfold_entities(structure, 'A')
    ns = NeighborSearch(atoms)

    close_atoms = ns.search(probe, threshold)
    close_residues = []
    for atom in close_atoms: 
        close_residues.append(atom.get_parent())
    
    # make unique
    close_residues = list(set(close_residues))

    vals = []
    for res in close_residues:
        # if hetero continue
        if res.id[0] != " ":
            continue
        val = {"resi":res.id[1], "chain":res.get_parent().id, "model":0, "resn":res.get_resname()}
        vals.append(val)
    return vals

  

def predict(pdb, models, pthreshold=0.1, threshold=7, batch_size=20, mode="fast", central_residue=None, radius=8, backend="multiprocessing"):
    start_time = time.time()

    probefile = os.path.basename(pdb).split(".")[0] + "_metals.pdb"
    
    cubefile = os.path.basename(pdb).split(".")[0] + "_out.cube"

    probefile_water = os.path.basename(pdb).split(".")[0] + "_water.pdb"
    
    cubefile_water = os.path.basename(pdb).split(".")[0] + "_water.cube"



    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = LocationModel()
    model.to(device)
    
    home = Path.home()

    if int(torch.__version__[0])>1:
        model.load_state_dict(
            torch.load(
                str(home)+constants.model_weights['metal'], weights_only=True
            )
        )
    else:
        model.load_state_dict(
            torch.load(
                str(home)+constants.model_weights['metal']
            )
        )


    water_model = WaterModel()
    water_model.to(device)

    if int(torch.__version__[0])>1:
        water_model.load_state_dict(
            torch.load(
                str(home)+constants.model_weights['water'], weights_only=True
            )
        )
    else:
        water_model.load_state_dict(
            torch.load(
                str(home)+constants.model_weights['water']
            )
        )

    identity_model = IdentityModel()

    identity_model = nn.DataParallel(identity_model)

    identity_model.to(device)


    if int(torch.__version__[0])>1:
        identity_model.load_state_dict(
            torch.load(
                str(home)+constants.model_weights['identity'], weights_only=True
            )
        )
    else:
        identity_model.load_state_dict(
            torch.load(
                str(home)+constants.model_weights['identity']
            )
        )


    # step0 voxelize
    voxels,prot_centers =  voxelize(
            device,
            pdb,
            mode=mode,
            central_residue=central_residue,
            radius=radius
            
    )

    # step 1 
    # location prediction
    if "AllMetal3D" in models:
        predicted_metal_locations,cube = predict_location(
                model,
                device,
                pdb,
                voxels, prot_centers,
                batch_size=batch_size,
                threshold=threshold,
                pthreshold=pthreshold,
                probefile=probefile,
                cubefile=cubefile,
                backend=backend 
        )
        # step 3 
        # predict metal identity
        if predicted_metal_locations==None:
            # raise gr.Error(f"No density found above choses probability cutoff p={pthreshold:.2f}")
            probe_content = ""
            results = []
            gradio_probefile = gr.File(visible=False)
            gradio_cubefile = gr.File(cubefile, visible=True)
        else:
            probe_content, results  = predict_identity(
                identity_model,
                device,
                pdb,
                predicted_metal_locations,
                probefile
            )
            gradio_probefile = gr.File(probefile,visible=True)
            gradio_cubefile = gr.File(cubefile, visible=True)
    else:
        probe_content = ""
        results = []
        cube = ""
        gradio_probefile = gr.File(visible=False)
        gradio_cubefile = gr.File(visible=False)

    # step 2
    # water prediction
    if "Water3D" in models:
        predicted_water_locations,water_cube  = predict_water(
                water_model,
                device,
                pdb,
                voxels, prot_centers,
                batch_size=batch_size,
                threshold=threshold,
                pthreshold=pthreshold,
                probefile=probefile_water,
                cubefile=cubefile_water, 
                mode=mode, 
                central_residue=central_residue,
                radius=radius,
                backend=backend
        )
        gradio_probefile_water = gr.File(probefile_water, visible=True)
        gradio_cubefile_water = gr.File(cubefile_water,visible=True)
    else:
        predicted_water_locations, water_cube = [], ""
        gradio_probefile_water = gr.File(visible=False)
        gradio_cubefile_water = gr.File(visible=False)


    print("--- %s seconds ---" % (time.time() - start_time))

    return visualize(pdb=pdb,probe=probe_content,results=results,cube=cube,water_cube=water_cube, private_link=private_link), gradio_probefile, gradio_cubefile, gradio_probefile_water,gradio_cubefile_water, results, predicted_water_locations




def predict_cli(pdb, models, pthreshold=0.1, threshold=7, batch_size=20, mode="fast", central_residue=None, radius=8, output_dir = ".", backend="multiprocessing"):
    start_time = time.time()
    total_time = start_time
    with Halo(text='initializing', spinner='dots') as spinner:
        probefile = os.path.join(output_dir, os.path.basename(pdb).split(".")[0] + "_metals.pdb")
        
        cubefile = os.path.join(output_dir,os.path.basename(pdb).split(".")[0] + "_out.cube")

        probefile_water = os.path.join(output_dir,os.path.basename(pdb).split(".")[0] + "_water.pdb")
        
        cubefile_water = os.path.join(output_dir,os.path.basename(pdb).split(".")[0] + "_water.cube")

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        model = LocationModel()
        model.to(device)
        
        home = Path.home()

        if int(torch.__version__[0])>1:
            model.load_state_dict(
                torch.load(
                    str(home)+constants.model_weights['metal'], weights_only=True
                )
            )
        else:
            model.load_state_dict(
                torch.load(
                    str(home)+constants.model_weights['metal']
                )
            )
        model = nn.DataParallel(model)


        water_model = WaterModel()
        water_model.to(device)
        if int(torch.__version__[0])>1:
            water_model.load_state_dict(
                torch.load(
                    str(home)+constants.model_weights['water'], weights_only=True
                )
            )
        else:
            water_model.load_state_dict(
                torch.load(
                    str(home)+constants.model_weights['water']
                )
            )

        water_model = nn.DataParallel(water_model)

        identity_model = IdentityModel()

        identity_model = nn.DataParallel(identity_model)

        identity_model.to(device)


        if int(torch.__version__[0])>1:
            identity_model.load_state_dict(
                torch.load(
                    str(home)+constants.model_weights['identity'], weights_only=True
                )
            )
        else:
            identity_model.load_state_dict(
                torch.load(
                    str(home)+constants.model_weights['identity']
                )
            )
        
        spinner.succeed(f"models loaded in {time.time() - start_time:.3f} seconds")
        start_time = time.time()
        spinner.start("voxelizing environments")

        # step0 voxelize
        voxels,prot_centers =  voxelize(
                device,
                pdb,
                mode=mode,
                central_residue=central_residue,
                radius=radius
                
        )
        spinner.succeed(f"voxelization completed in {time.time() - start_time:.3f} seconds")
        start_time = time.time()
        # step 1 
        # location prediction
        if models == "all" or models=="allmetal3d":
            spinner.start("running AllMetal3D")
            predicted_metal_locations,cube = predict_location(
                    model,
                    device,
                    pdb,
                    voxels, prot_centers,
                    batch_size=batch_size,
                    threshold=threshold,
                    pthreshold=pthreshold,
                    probefile=probefile,
                    cubefile=cubefile,
                    backend=backend
            )
            # step 3 
            # predict metal identity
            if predicted_metal_locations==None:
                probe_content = ""
                results = []
            else:
                probe_content, results  = predict_identity(
                    identity_model,
                    device,
                    pdb,
                    predicted_metal_locations,
                    probefile,
                    spinner=spinner 
                )
            spinner.succeed(f"AllMetal3D completed in {time.time() - start_time:.3f} seconds")
            start_time = time.time()
        else:
            probe_content = ""
            results = []
            cube = ""
            spinner.info("skipping AllMetal3D")

        
        
        
        # step 2
        # water prediction
        if models == "all" or models=="water3d":
            spinner.start("running Water3D")
            predicted_water_locations,water_cube  = predict_water(
                    water_model,
                    device,
                    pdb,
                    voxels, prot_centers,
                    batch_size=batch_size,
                    threshold=threshold,
                    pthreshold=pthreshold,
                    probefile=probefile_water,
                    cubefile=cubefile_water, 
                    mode=mode, 
                    central_residue=central_residue,
                    radius=radius,
                    backend=backend
            )
            spinner.succeed(f"Water3D completed in {time.time() - start_time:.3f} seconds")
        else:
            predicted_water_locations, water_cube = [], ""

        spinner.succeed(f"completed in {time.time() - total_time:.3f} seconds")

    return probefile, cubefile, probefile_water,cubefile_water, results



def update_mode(mode):
    if mode in ['fast', 'all']:
        return gr.Textbox(visible=False), gr.Slider(visible=False)
    else:
        return gr.Textbox(visible=True), gr.Slider(visible=True)