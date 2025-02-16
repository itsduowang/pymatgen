# Copyright (c) Pymatgen Development Team.
# Distributed under the terms of the MIT License.

"""
Development script to test the algorithms of a given model coordination environments
"""

from __future__ import annotations

import itertools
import time
from math import factorial
from random import shuffle

import numpy as np

from pymatgen.analysis.chemenv.coordination_environments.coordination_geometries import (
    AllCoordinationGeometries,
)
from pymatgen.analysis.chemenv.coordination_environments.coordination_geometry_finder import (
    AbstractGeometry,
    LocalGeometryFinder,
)

__author__ = "David Waroquiers"
__copyright__ = "Copyright 2012, The Materials Project"
__version__ = "2.0"
__maintainer__ = "David Waroquiers"
__email__ = "david.waroquiers@gmail.com"
__date__ = "Feb 20, 2016"

if __name__ == "__main__":

    allcg = AllCoordinationGeometries()

    while True:
        cg_symbol = input("Enter symbol of the geometry for which you want to get the explicit permutations : ")
        try:
            cg = allcg[cg_symbol]
            break
        except LookupError:
            print("Wrong geometry, try again ...")
            continue

    lgf = LocalGeometryFinder()
    lgf.setup_parameters(structure_refinement=lgf.STRUCTURE_REFINEMENT_NONE)

    myindices = range(cg.coordination_number)

    test = input(
        'Enter if you want to test all possible permutations ("all" or "a") or a given number of '
        'random permutations (i.e. "25")'
    )

    if test == "all" or test == "a":
        perms_iterator = itertools.permutations(myindices)
        nperms = factorial(cg.coordination_number)
    else:
        try:
            nperms = int(test)
        except Exception:
            raise ValueError(f"Could not turn {test} into integer ...")
        perms_iterator = []
        for _ in range(nperms):
            shuffle(myindices)
            perms_iterator.append(list(myindices))

    iperm = 1
    t1 = time.clock()
    for indices_perm in perms_iterator:

        lgf.setup_test_perfect_environment(cg_symbol, indices=indices_perm)

        lgf.perfect_geometry = AbstractGeometry.from_cg(cg=cg)
        points_perfect = lgf.perfect_geometry.points_wocs_ctwocc()

        print(f"Perm # {iperm:d}/{nperms:d} : ", indices_perm)

        algos_results = []
        for algo in cg.algorithms:
            print(algo)
            if algo.algorithm_type == "EXPLICIT_PERMUTATIONS":
                raise ValueError("Do something for the explicit ones ... (these should anyway be by far ok!)")

            results = lgf.coordination_geometry_symmetry_measures_separation_plane(
                coordination_geometry=cg,
                separation_plane_algo=algo,
                tested_permutations=False,
                points_perfect=points_perfect,
            )
            print("Number of permutations tested : ", len(results[0]))
            algos_results.append(min(results[0]))

            if not np.isclose(min(results[0]), 0.0):
                print("Following is not 0.0 ...")
                input(results)
        print("   => ", algos_results)
        iperm += 1
    t2 = time.clock()
    print(f"Time to test {nperms} permutations for geometry {cg.name!r} (symbol {cg_symbol!r}) : {t2 - t1:.2f} seconds")
