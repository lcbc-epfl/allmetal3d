import time
import pickle
import os
import glob
import argparse


import torch
import torch.nn as nn
import torch.nn.functional as F

import numpy as np

import multiprocessing
from multiprocessing import Pool

from moleculekit.molecule import Molecule
from moleculekit.tools.voxeldescriptors import getVoxelDescriptors, viewVoxelFeatures
from moleculekit.tools.atomtyper import prepareProteinForAtomtyping
from moleculekit.tools.preparation import proteinPrepare, systemPrepare
from moleculekit.tools.graphalignment import maximalSubstructureAlignment
from moleculekit.home import home
import ray

metal_atypes = (
    "MG",
    "ZN",
    "MN",
    "CA",
    "FE",
    "HG",
    "CD",
    "NI",
    "CO",
    "CU",
    "K",
    "LI",
    "Mg",
    "Zn",
    "Mn",
    "Ca",
    "Fe",
    "Hg",
    "Cd",
    "Ni",
    "Co",
    "Cu",
    "Li",
)


@ray.remote
def voxelize_single_notcentered(env):
    prot, c = env

    # c = prot.get("coords", sel=f"index {id} and name CA")
    all_coords = prot.get("coords")
    try:
        index = np.where(np.all(all_coords == c, axis=1))[0][0]
    except:
        print(f"{id}, index not found")
        return None
    prot.remove(f"same residue as not within 30 of index {index}")
    # print(prot.get("resname", sel=f"index {id}"), prot.get("name", sel=f"index {id}"))
    size = [16, 16, 16]  # size of box
    voxels = torch.zeros(8, 32, 32, 32)
    try:
        hydrophobic = prot.atomselect("element C")
        hydrophobic = hydrophobic.reshape(hydrophobic.shape[0], 1)

        aromatic = prot.atomselect(
            "resname HIS TRP TYR PHE and sidechain and not name CB and not hydrogen"
        )
        aromatic = aromatic.reshape(aromatic.shape[0], 1)

        metalcoordination = prot.atomselect(
            "(name ND1 NE2 SG OE1 OE2 OD2) or (protein and name O N)"
        )
        metalcoordination = metalcoordination.reshape(metalcoordination.shape[0], 1)

        hbondacceptor = prot.atomselect(
            "(resname ASP GLU HIS SER THR MSE CYS MET and name ND2 NE2 OE1 OE2 OD1 OD2 OG OG1 SE SG) or name O"
        )
        hbondacceptor = hbondacceptor.reshape(metalcoordination.shape[0], 1)

        hbonddonor = prot.atomselect(
            "(resname ASN GLN TRP MSE SER THR MET CYS and name ND2 NE2 NE1 SG SE OG OG1) or name N"
        )
        hbonddonor = hbonddonor.reshape(metalcoordination.shape[0], 1)

        positive = prot.atomselect("resname LYS ARG HIS and name NZ NH1 NH2 ND1 NE2 NE")
        positive = positive.reshape(positive.shape[0], 1)

        negative = prot.atomselect("(resname ASP GLU and name OD1 OD2 OE1 OE2)")
        negative = negative.reshape(negative.shape[0], 1)

        occupancy = prot.atomselect("protein and not hydrogen")
        occupancy = occupancy.reshape(occupancy.shape[0], 1)
        userchannels = np.hstack(
            [
                hydrophobic,
                aromatic,
                metalcoordination,
                hbondacceptor,
                hbonddonor,
                positive,
                negative,
                occupancy,
            ]
        )
        prot_vox, prot_centers, prot_N = getVoxelDescriptors(
            prot,
            center=c,
            userchannels=userchannels,
            boxsize=size,
            voxelsize=0.5,
            validitychecks=False,
        )
    except:
        print(f"{id}, voxelization input failed")
        return None
    nchannels = prot_vox.shape[1]
    prot_vox_t = (
        prot_vox.transpose()
        .reshape([1, nchannels, prot_N[0], prot_N[1], prot_N[2]])
        .copy()
    )

    voxels = torch.from_numpy(prot_vox_t)
    return (voxels, prot_centers, prot_N, prot.copy())


def processStructures(pdb_file, coords, clean=True):
    """process 1 structure, executed on a single CPU"""

    start_time_processing = time.time()

    # load molecule using MoleculeKit

    try:
        prot = Molecule(pdb_file, type="pdb", validateElements=False)
    except:
        exit("could not read file")

    if clean:
        prot.filter("protein and not hydrogen")

    environments = []
    for coord in coords:
        try:
            environments.append((prot.copy(), coord))
        except:
            print("ignore " + coord)

    prot_centers_list = []
    prot_n_list = []
    envs = []
    print("starting voxelization")
    # cpuCount = multiprocessing.cpu_count()
    # p = Pool(cpuCount)
    ray.init()
    results = ray.get(
        [voxelize_single_notcentered.remote(env) for env in environments]
    )  # prot_centers, prot_N
    
    # remove None results
    results = [x for x in results if x is not None]

    voxels = torch.empty(len(results), 8, 32, 32, 32, device="cuda")
    print("results:", len(results))
    ray.shutdown()
    if len(results) == 0:
        print(
            "something went wrong with the voxelization, check that there are no discontinuities in the protein"
        )
        return np.array([]), None, None, None

    vox_env, prot_centers_list, prot_n_list, envs = zip(*results)

    for i, vox_env in enumerate(vox_env):
        voxels[i] = vox_env

    print("-----  Voxelization  -----")
    print(f"-----  {time.time() - start_time_processing:.3f} seconds -----")
    print("--------------------------")
    return voxels, prot_centers_list, prot_n_list, envs




def voxelize_identity_location(pdb, sites):
    counter = 0

    voxels = torch.empty(len(sites), 8, 32, 32, 32)

    for site in sites:
        probe_coord, probability = site
        c = probe_coord
        boxsize = [16, 16, 16]  # size of box
        voxelsize = 0.5
        try:
            prot = Molecule(pdb, type="pdb", validateElements=False)
        except:
            exit("could not read file")

        prot.filter("protein and not hydrogen")

        # voxelize
        try:
            hydrophobic = prot.atomselect("element C")
            hydrophobic = hydrophobic.reshape(hydrophobic.shape[0], 1)

            aromatic = prot.atomselect(
                "resname HIS TRP TYR PHE and sidechain and not name CB and not hydrogen"
            )
            aromatic = aromatic.reshape(aromatic.shape[0], 1)

            metalcoordination = prot.atomselect(
                "(name ND1 NE2 SG OE1 OE2 OD2) or (protein and name O N)"
            )
            metalcoordination = metalcoordination.reshape(
                metalcoordination.shape[0], 1
            )

            hbondacceptor = prot.atomselect(
                "(resname ASP GLU HIS SER THR MSE CYS MET and name ND2 NE2 OE1 OE2 OD1 OD2 OG OG1 SE SG) or name O"
            )
            hbondacceptor = hbondacceptor.reshape(metalcoordination.shape[0], 1)

            hbonddonor = prot.atomselect(
                "(resname ASN GLN TRP MSE SER THR MET CYS and name ND2 NE2 NE1 SG SE OG OG1) or name N"
            )
            hbonddonor = hbonddonor.reshape(metalcoordination.shape[0], 1)

            positive = prot.atomselect(
                "resname LYS ARG HIS and name NZ NH1 NH2 ND1 NE2 NE"
            )
            positive = positive.reshape(positive.shape[0], 1)

            negative = prot.atomselect(
                "(resname ASP GLU and name OD1 OD2 OE1 OE2)"
            )
            negative = negative.reshape(negative.shape[0], 1)

            occupancy = prot.atomselect("protein and not hydrogen")
            occupancy = occupancy.reshape(occupancy.shape[0], 1)
            userchannels = np.hstack(
                [
                    hydrophobic,
                    aromatic,
                    metalcoordination,
                    hbondacceptor,
                    hbonddonor,
                    positive,
                    negative,
                    occupancy,
                ]
            )
            prot_vox, prot_centers, prot_N = getVoxelDescriptors(
                prot,
                center=c,
                userchannels=userchannels,
                boxsize=boxsize,
                voxelsize=voxelsize,
                validitychecks=False,
            )
        except:
            print(
                f"{pdb}, {site['label']}, voxelization input failed"
            )
            return None
            
        prot_vox_t = prot_vox.transpose().reshape([8, prot_N[0], prot_N[1], prot_N[2]])
        prot_vox_t = torch.tensor(prot_vox_t.astype(np.float32))
        voxels[counter] = prot_vox_t
        counter += 1
    return voxels


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Voxelization test")
    parser.add_argument(
        "--no-clean", help="do not clean the pdb file", action="store_false"
    )
    parser.add_argument(
        "--sidechain", help="do not remove sidechain", action="store_false"
    )
    parser.add_argument("--pdb", help="pdb, pdb.gz, cif or cif.gz file", required=True)
    args = parser.parse_args()

    voxels = processStructures(args.pdb, [1], False, args.sidechain)
    print(voxels.shape)
