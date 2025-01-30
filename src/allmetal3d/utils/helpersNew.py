import torch
import pandas as pd
from moleculekit.molecule import Molecule
from scipy.spatial import distance, KDTree

import multiprocessing
from multiprocessing import Pool

from joblib import Parallel, delayed

import gradio as gr

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

import numpy as np


def create_grid_fromBB(boundingBox, voxelSize=1):
    """creates grid from x, y and z bounding box"""
    # increase grid by 0.5 to sample everything
    xrange = np.arange(boundingBox[0][0], boundingBox[1][0] + 0.5, step=voxelSize)
    yrange = np.arange(boundingBox[0][1], boundingBox[1][1] + 0.5, step=voxelSize)
    zrange = np.arange(boundingBox[0][2], boundingBox[1][2] + 0.5, step=voxelSize)

    gridpoints = np.zeros((xrange.shape[0] * yrange.shape[0] * zrange.shape[0], 3))
    i = 0
    for x in xrange:
        for y in yrange:
            for z in zrange:
                gridpoints[i][0] = x
                gridpoints[i][1] = y
                gridpoints[i][2] = z
                i += 1
    return gridpoints, (xrange.shape[0], yrange.shape[0], zrange.shape[0])


def get_bb(points):
    """Return bounding box from a set of points (N,3)"""
    minx = np.min(points[:, 0])
    maxx = np.max(points[:, 0])

    miny = np.min(points[:, 1])
    maxy = np.max(points[:, 1])

    minz = np.min(points[:, 2])
    maxz = np.max(points[:, 2])
    bb = [[minx, miny, minz], [maxx, maxy, maxz]]
    return bb


# def get_probability_mean(all_to_all_dist, output_v):
#     probability_values =[]
#     for i in range(all_to_all_dist.shape[0]):
#         indexes = np.where(all_to_all_dist[i]<1)[0]
#         if len(indexes)>0:
#             probability_values.append(np.mean(output_v[indexes]))
#         else:
#             probability_values.append(0.)

#     return np.array(probability_values)


def get_all_protein_resids(pdb_file):
    try:
        prot = Molecule(pdb_file, _logger=False)
    except:
        exit("could not read file")
    prot.filter("protein and not hydrogen",  _logger=False)
    return prot.get("coords", f"name CA")



def find_non_neighbor_coordinates(coordinates, cutoff):
    """
    Find coordinates that don't have any other coordinates within a certain cutoff distance.
    
    Args:
    - coordinates (list of tuples): List of XYZ coordinates.
    - cutoff (float): Cutoff distance for considering neighbors.
    
    Returns:
    - List of tuples: Coordinates that don't have any other coordinates within the cutoff distance.
    - List of integers: Indices of the non-neighbor coordinates in the original list.
    """
    non_neighbor_coordinates = []
    non_neighbor_indices = []
    orig_coordinates = coordinates

    while len(coordinates)>0:
        non_neighbor_coordinates.append(coordinates[0])
        non_neighbor_indices.append(np.where((orig_coordinates == coordinates[0]).all(axis=1))[0][0])
        coordinates = np.delete(coordinates,0, axis=0)
        items_to_delete = []
        for i, coord in enumerate(non_neighbor_coordinates):
          for j, other_coord in enumerate(coordinates):
            if np.linalg.norm(np.array(coord) - np.array(other_coord)) < cutoff and i != j:    
              items_to_delete.append(j)
        coordinates = np.delete(coordinates,items_to_delete, axis=0)
    return non_neighbor_coordinates, non_neighbor_indices

def get_all_protein_resids_blocked(pdb_file, cutoff=8):
    try:
        prot = Molecule(pdb_file, _logger=False)
    except:
        exit("could not read file")
    prot.filter("protein and not hydrogen", _logger=False)

    coords = prot.get("coords", f"name CA")
    
    selected_coords, index = find_non_neighbor_coordinates(coords, cutoff)

    return selected_coords


def get_coords_central_res(pdb_file, central_residue, radius):
    try:
        prot = Molecule(pdb_file, _logger=False)
    except:
        exit("could not read file")
    prot.filter("protein and not hydrogen", _logger=False)

    try:
        coords = prot.get("coords", f"name CA and within {radius} of resid {central_residue}")
    except:
        raise gr.Error("Couldn't parse residue selection")
    return coords

def read_summary(path):
    with open(path, "r") as fp:
        data = fp.readlines()
    metal = []
    for l in data:
        id, classifier = l.split(":")
        classifier = classifier.strip()
        m, id, index, chain = id.split("_")
        metal.append([m,id, index, chain, classifier])
    return pd.DataFrame(metal, columns=['metal', 'id', 'index', 'chain', 'class'])



def show_probes(probefile):
    try:
        probes = Molecule(probefile,  _logger=False)
    except Exception as e:
        exit("could not read probefile", e)
    probes.view(style="VDW", color="Occupancy")


def compute_average_p(point, cutoff=0.5):
    "this computes average probability of all points given a certain cutoff using cdist"
    p = 0
    dists = distance.cdist([point], prot_v)
    indexes = np.where(dists < cutoff)[1]
    if len(indexes) > 0:
        p = np.mean(output_v[indexes])
    return p


def compute_average_p_fast(point,cutoff=1):
    """This is a faster approach that uses a KDTree to find the closes gridpoints
    For each point the computation is run on one cpu."""
    p = 0
    nearest_neighbors, indices = tree.query(
        point, k=20, distance_upper_bound=0.25, workers=1
    )
    if np.min(nearest_neighbors) != np.inf:
        p = np.mean(output_v[indices[nearest_neighbors != np.inf]])
    return p


from scipy import ndimage


def get_probability_mean(grid, prot_centers, pvalues, implementation="multiprocessing"):
    global output_v
    output_v = pvalues
    global prot_v
    prot_v = prot_centers
    cpuCount = multiprocessing.cpu_count()
    if implementation == "cdist":
        # old
        # p = Pool(cpuCount)
        # results = p.map(compute_average_p, grid)
        results = process_map(compute_average_p, grid, chunksize=cpuCount)
    elif implementation == "multiprocessing":
        global tree
        tree = KDTree(prot_v)
        p = Pool(cpuCount)
        results = p.map(compute_average_p_fast, grid)
    elif implementation == "joblib":
        results = Parallel(n_jobs=cpuCount)(delayed(compute_average_p_fast)(g) for g in grid)
    else:
        raise RuntimeError("No backend specified")

    return np.array(results)


def write_cubefile(bb, pvalues, box_N, outname="Metal3D_pmap.cube", gridres=1):
    with open(outname, "w") as cube:
        cube.write(" Metal3D Cube File\n")
        cube.write(" Outer Loop: X, Middle Loop y, inner Loop z\n")

        angstromToBohr = 1.89
        cube.write(
            f"    1   {bb[0][0]*angstromToBohr: .6f}  {bb[0][1]*angstromToBohr: .6f}   {bb[0][2]*angstromToBohr: .6f}\n"
        )
        cube.write(
            f"{str(box_N[0]).rjust(5)}    {1.890000*gridres:.9f}    0.000000    0.000000\n"
        )
        cube.write(
            f"{str(box_N[1]).rjust(5)}    0.000000    {1.890000*gridres:.9f}    0.000000\n"
        )
        cube.write(
            f"{str(box_N[2]).rjust(5)}    0.000000    0.000000    {1.890000*gridres:.9f}\n"
        )
        cube.write("    1    1.000000    0.000000    0.000000    0.000000\n")

        o = pvalues.reshape(box_N)
        for x in range(box_N[0]):
            for y in range(box_N[1]):
                for z in range(box_N[2]):
                    cube.write(f" {o[x][y][z]: .5E}")
                    if z % 6 == 5:
                        cube.write("\n")
                cube.write("\n")
    cube_content = ""
    with open(outname, "r") as cube:
        cube_content = cube.read()
    return cube_content


from sklearn.cluster import AgglomerativeClustering

# def find_unique_sites(pvalues, grid, writeprobes=False, probefile='probes.xyz', threshold=2.8, p=0.75):
#     """The probability voxels are points and the voxel clouds may contain multiple metals
#     This function finds the unique sites and returns the coordinates of the unique sites.
#     It uses the AgglomerativeClustering algorithm to find the unique sites.
#     The threshold is the maximum distance between two points in the same cluster it can be changed to get more metal points."""

#     points=grid[pvalues>p]
#     clustering = AgglomerativeClustering(n_clusters=None,linkage="complete", distance_threshold=threshold).fit(points)
#     print(f'p={p}, n(metals):', clustering.n_clusters_)
#     pname = probefile.split('.')
#     pname = pname[0]+'_p='+str(p)+'.'+pname[1]
#     if writeprobes:
#         print(f'writing probes to {pname}')
#         with open(pname, 'w') as f:
#             f.write(str(clustering.n_clusters_)+'\n\n')
#             for c in range(clustering.n_clusters_):
#                 c_points = points[clustering.labels_==c]
#                 probe = c_points.mean(axis=0)
#                 f.write(f'ZN    {probe[0]:10.6f} {probe[1]:10.6f} {probe[2]: 10.6f}\n')


def find_unique_sites(
    pvalues, grid, writeprobes=False, probefile="probes.pdb", threshold=5, p=0.75, mode="metal"
):
    """The probability voxels are points and the voxel clouds may contain multiple metals
    This function finds the unique sites and returns the coordinates of the unique sites.
    It uses the AgglomerativeClustering algorithm to find the unique sites.
    The threshold is the maximum distance between two points in the same cluster it can be changed to get more metal points.
    """

    points = grid[pvalues > p]
    point_p = pvalues[pvalues > p]
    if len(points) == 0:
        print("no points available for clustering")
        return None
    if len(points) == 1:
        sites = [(points[0], point_p[0])]
        print("only one point available for clustering")
    else:
        clustering = AgglomerativeClustering(
            n_clusters=None, linkage="complete", distance_threshold=threshold
        ).fit(points)
        # print(f"p={p}, n({mode}):", clustering.n_clusters_)
        sites = []
        for i in range(clustering.n_clusters_):
            c_points = points[clustering.labels_ == i]
            c_points_p = point_p[clustering.labels_ == i]

            # compute center of probabilities as COM
            CM = np.average(c_points, axis=0, weights=c_points_p)
            position = CM

            sites.append((position, np.max(c_points_p)))
    if writeprobes:
        if mode == "metal":
            with open(probefile, "w") as f:
                for i, site in enumerate(sites):
                    f.write(
                        f"HETATM  {i+1:3} ZN    ZN A  1    {site[0][0]: 8.3f}{site[0][1]: 8.3f}{site[0][2]: 8.3f}  {site[1]:.2f}  0.0            ZN \n"
                    )
        else:
            with open(probefile, "w") as f:
                for i, site in enumerate(sites):
                    f.write(
                        f"HETATM  {i+1:3}  O   HOH X{i+1:4}    {site[0][0]: 8.3f}{site[0][1]: 8.3f}{site[0][2]: 8.3f}  {site[1]:.2f}  0.0            O  \n"
                    )
        
    return sites


import os


def write_probefile(sites, identities, probefile,  remove_nometal=False, forbidden_chains=[], metal=True):
    file_content = ""


    with open(probefile, "w") as f:
        for i, (site,p) in enumerate(sites):
            if metal:
                if identities[i] == "NoMetal":
                    id = "  X"
                    if remove_nometal:
                        continue
                elif identities[i] ==  "NonZNTM":
                    id = " CU"
                elif identities[i]== "Alkali":
                    id = " NA"
                else:
                    id = identities[i].rjust(3)
                probe_line = f"HETATM  {i+1:3}{id}   {id} X{i+1:3}    {site[0]: 8.3f}{site[1]: 8.3f}{site[2]: 8.3f}  {p:.2f}  0.0            {id}  \n"
            else:
                probe_line = f"HETATM  {i+1:3}  O   HOH X{i+1:3}    {site[0]: 8.3f}{site[1]: 8.3f}{site[2]: 8.3f}  {p:.2f}  0.0            O  \n"
            f.write(
                probe_line
            )
            file_content+=probe_line
    return file_content


def maxprobability(pvalues, grid, pdb, label):
    """Returns the point in the grid with the highest probability"""

    print(
        f"Max p={np.max(pvalues)} xyz: {grid[np.argmax(pvalues)][0]: .4f} {grid[np.argmax(pvalues)][1]: .4f} {grid[np.argmax(pvalues)][2]: .4f}"
    )
    if os.path.isfile("maxp_" + os.path.basename(label) + ".csv"):
        with open("maxp_" + os.path.basename(label) + ".csv", "a") as fp:
            fp.write(
                f"{pdb},{np.max(pvalues):.4f}, {grid[np.argmax(pvalues)][0]: .4f}, {grid[np.argmax(pvalues)][1]: .4f}, {grid[np.argmax(pvalues)][2]: .4f}\n"
            )
    else:
        with open("maxp_" + os.path.basename(label) + ".csv", "w") as fp:
            fp.write("pdb,p,x,y,z\n")
            fp.write(
                f"{pdb},{np.max(pvalues):.4f}, {grid[np.argmax(pvalues)][0]: .4f}, {grid[np.argmax(pvalues)][1]: .4f}, {grid[np.argmax(pvalues)][2]: .4f}\n"
            )


# def prettyPrintResults(results):
#     revCanonical = {v: k for k, v in canonical.items()}
#     print('probabilites')
#     print("-------------------")
#     print('|  aa  |    prob  |')
#     print("-------------------")
#     for i, value in enumerate(results.cpu().detach().numpy().squeeze()):
#         print('| ',revCanonical[i],'|',f"{value:.6f} |")

# def prettyPrintResultsDF(results, resnames, name="predictions"):
#     revCanonical = {v: k for k, v in canonical.items()}
#     columnNames =[]
#     for i in range(20):
#         columnNames.append(revCanonical[i])
#     df = pd.DataFrame(results.cpu().detach().numpy().squeeze(), columns = columnNames, index=resnames)
#     df.to_csv(name)
#     print(f'written predictions to file: {name}')
