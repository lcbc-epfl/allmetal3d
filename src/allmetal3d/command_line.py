

import gradio as gr

from .utils.helpersNew import *
from .utils.main import predict, predict_cli, update_mode

from gradio_molecule3d import Molecule3D



def server_cli():
    with gr.Blocks() as blocks: 
        gr.Markdown("## AllMetal3D and Water3D")
        pdb = Molecule3D(label="Input PDB", showviewer=False) #gr.File("2cba.pdb",label="Upload PDB file")

    
        gr.Markdown("Metals might bind anywhere in the protein, choose how to sample the residues in the protein. <br>Fast uses blocked sampling of residues to reduce required computational time, full uses all residues, site allows you to look around a specific site in the protein")
        with gr.Row("Prediction mode"):
            mode = gr.Dropdown(["fast", "all", "site"], value="fast", label="Mode")
            central_residue = gr.Textbox(label="Central residue", info="add multiple residues with space e.g 101 203", visible=False)
            radius = gr.Slider(value=8, minimum=4, maximum=50, label="Distance threshold", visible=False)
        mode.change(update_mode, mode, [central_residue, radius])

        models = gr.Radio(["AllMetal3D + Water3D", "Only AllMetal3D", "Only Water3D"], value="AllMetal3D + Water3D", label="Which models to run?")

        with gr.Accordion("Settings"):
            threshold = gr.Slider(value=7,minimum=0, maximum=10,  label="Threshold")
            pthreshold = gr.Slider(value=0.25,minimum=0.1, maximum=1,  label="Probability Threshold")
            batch_size = gr.Slider(value=50, minimum=0, maximum=100, label="Batch Size")

        btn = gr.Button("Predict")

        with gr.Row():
            metal_pdb = gr.File(label="predicted metals (PDB)", visible=False)
            metal_cube = gr.File(label="predicted metal density (CUBE)",visible=False)
            water_pdb = gr.File(label="predicted waters (PDB)", visible=False)
            water_cube = gr.File(label="predicted water density (CUBE)", visible=False)
            
        out = gr.HTML("")
        results_json = gr.JSON(visible=False)
        waters_json = gr.JSON(visible=False)


        btn.click(predict, inputs=[pdb, models, pthreshold, threshold, batch_size, mode, central_residue, radius], outputs=[out, metal_pdb, metal_cube, water_pdb, water_cube, results_json, waters_json])


    # in order to get private link for the app for the viewer we need to disable thread lock and grab the link
    _,_,pl = blocks.launch(share=True, prevent_thread_lock=True, allowed_paths=["frontend"])

    private_link = pl

    input("press any key to terminate server")


import argparse

def cli():
    parser = argparse.ArgumentParser(description="AllMetal3D Command Line Interface")
    parser.add_argument("-i", "--input", help="Input PDB file", required=True)
    parser.add_argument("-a", "--models", help="Models", choices=["all", "water3d", "allmetal3d"], default="all")
    parser.add_argument("-m", "--mode", help="Prediction mode", choices=["fast", "all", "site"], default="fast")
    parser.add_argument("-c", "--central_residue", help="Central residue", default="")
    parser.add_argument("-r", "--radius", help="Distance threshold", type=int, default=8)
    parser.add_argument("-t", "--threshold", help="Threshold", type=float, default=7)
    parser.add_argument("-p", "--pthreshold", help="Probability Threshold", type=float, default=0.25)
    parser.add_argument("-b", "--batch_size", help="Batch Size", type=int, default=50)
    parser.add_argument("-o", "--output_dir", help="Output directory", default="")
    args = parser.parse_args()

    predict_cli(args.input, args.models, pthreshold=args.pthreshold, threshold=args.threshold, batch_size=args.batch_size, mode=args.mode, central_residue=args.central_residue, radius=args.radius, output_dir=args.output_dir)

