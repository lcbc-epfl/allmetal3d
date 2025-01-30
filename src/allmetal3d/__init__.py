# read version from installed package
from importlib.metadata import version
__version__ = version("allmetal3d")

import os
import requests

from pathlib import Path

from .utils import constants

from .utils.main import predict_cli

try:
    import torch
except ImportError:
    raise ImportError("No PyTorch found, please install it")

if torch.cuda.is_available()==False:
    raise ImportError("No CUDA detected by PyTorch, please install a CUDA compatible PyTorch build")



# check if weights are downloaded


def download_file(url, filepath):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filepath, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded to {filepath}")
    else:
        print(f"Error: HTTP status: {response.status_code}")

home = Path.home()

if not os.path.exists(str(home)+constants.weight_path):
    os.system(f"mkdir -p {str(home)+constants.weight_path}")

for id, weight in constants.model_weights.items():
    if not os.path.exists(str(home)+weight):
        print(id, "weight doesn't exist, downloading from HF")
        # download weights from GIT LFS
        download_file(constants.download_weights[id], str(home)+weight)


def predict(input_pdb=None, models="all", mode="fast", central_residue="", radius=8, threshold=7, pthreshold=0.25, batch_size=50, output_dir="./") -> tuple[str, str, str, str, dict]:
    """Main entry point for running AllMetal3D and Water3D

    Args:
        input_pdb (_type_, required): path to input pdb.
        models (str, optional): You can run either AllMetal3D and Water3D (all) Otherwise use `water3d` or `allmetal3d` to run only one of the models. Defaults to "all".
        mode (str, optional): fast uses blocked sampling to sample non-connected residues, all uses every residue, site allows you to run only in a radius of X Angstroms around a specific residue. Defaults to "fast".
        central_residue (str, optional): residue id of the central residue for site mode. Defaults to "".
        radius (int, optional): Radius in angstrom for site mode. Residues with their CA atom within this radius will be included. Defaults to 8.
        threshold (int, optional): Distance threshold for agglomerative clustering to place metal ions/waters in the density for AllMetal3D. Defaults to 7.
        pthreshold (float, optional): Probability threshold to include for clustering and placing of metal ions and water. Defaults to 0.25.
        batch_size (int, optional): Batch size. Defaults to 50.
        output_dir (str, optional): Where to output cube and pdb files containing the predicted density and the locations of metal ions/water. Defaults to "./".

    Returns:
        tuple of path to (probefile, cubefile, probefile_water, cubefile_water) and dictionary of results with detailed output for metal predictions with location_confidence, probability for all identity and geometry classes
    """
    if input_pdb == None:
        raise ValueError("need to provide input pdb")
    if not isinstance(input_pdb, (str, Path)) or not Path(input_pdb).is_file():
        raise ValueError("input pdb must be a valid file path")

    if mode not in ['fast', 'all', 'site']:
        raise ValueError(f"{mode} unknown, please choose fast, all or site")
    
    if mode == "site":
        # check if central residue is set
        if not central_residue:
            raise ValueError("central residue must be set when mode is 'site'")

    if threshold<=0:
        raise ValueError("threshold must be larger than 0, default 7 A")
    if pthreshold<=0 or pthreshold>1:
        raise ValueError("Probability threshold must be between 0 and 1.")

    if not isinstance(output_dir, (str, Path)) or not Path(output_dir).is_dir():
        raise ValueError("output_dir must be a valid directory path")

    probefile, cubefile, probefile_water,cubefile_water, results = predict_cli(input_pdb, models, pthreshold=pthreshold, threshold=threshold, batch_size=batch_size, mode=mode, central_residue=central_residue, radius=radius, output_dir=output_dir)

    identity_labels = ['Alkali', 'MG','CA','ZN', 'NonZNTM', 'NoMetal']
    geometry_labels = ['tetrahedron', 'octahedron', 'pentagonal bipyramid',   'square','Irregular', 'other','NoMetal']
 
    # Process each item in the results list
    for item in results:
        # Remove the close_residues key
        if 'close_residues' in item:
            del item['close_residues']
        
        # Refactor probabilities_identity and probabilities_geometry
        item['identity'] = {
            'labels': identity_labels,
            'p': item.pop('probabilities_identity')
        }
        item['geometry'] = {
            'labels': geometry_labels,
            'p': item.pop('probabilities_geometry')
        }
    return probefile, cubefile, probefile_water,cubefile_water, results


from .command_line import server_cli

def launch_server():
    """Launch server
    """
    server_cli()

