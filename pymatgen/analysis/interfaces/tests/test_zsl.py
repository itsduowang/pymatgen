# Copyright (c) Pymatgen Development Team.
# Distributed under the terms of the MIT License.

from __future__ import annotations

import unittest

import pytest

from pymatgen.analysis.interfaces.zsl import (
    ZSLGenerator,
    fast_norm,
    get_factors,
    reduce_vectors,
    vec_area,
)
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen.util.testing import PymatgenTest

__author__ = "Shyam Dwaraknath"
__copyright__ = "Copyright 2016, The Materials Project"
__version__ = "0.1"
__maintainer__ = "Shyam Dwaraknath"
__email__ = "shyamd@lbl.gov"
__date__ = "2/5/16"


class ZSLGenTest(PymatgenTest):
    def setUp(self):
        # Film VO2
        self.film = SpacegroupAnalyzer(self.get_structure("VO2"), symprec=0.1).get_conventional_standard_structure()

        # Substrate TiO2
        self.substrate = SpacegroupAnalyzer(
            self.get_structure("TiO2"), symprec=0.1
        ).get_conventional_standard_structure()

    def test_zsl(self):

        z = ZSLGenerator()

        assert fast_norm([3, 2, 1]) == pytest.approx(3.74165738)
        self.assertArrayEqual(reduce_vectors([1, 0, 0], [2, 2, 0]), [[1, 0, 0], [0, 2, 0]])
        assert vec_area([1, 0, 0], [0, 2, 0]) == 2
        self.assertArrayEqual(list(get_factors(18)), [1, 2, 3, 6, 9, 18])
        assert z.is_same_vectors([[1.01, 0, 0], [0, 2, 0]], [[1, 0, 0], [0, 2.01, 0]])
        assert not z.is_same_vectors([[1.01, 2, 0], [0, 2, 0]], [[1, 0, 0], [0, 2.01, 0]])

        matches = list(z(self.film.lattice.matrix[:2], self.substrate.lattice.matrix[:2]))
        assert len(matches) == 8

    def test_bidirectional(self):

        z = ZSLGenerator(max_area_ratio_tol=0.05, max_angle_tol=0.05, max_length_tol=0.05)

        matches = list(z(self.film.lattice.matrix[:2], self.substrate.lattice.matrix[:2]))
        assert len(matches) == 48

        matches = list(z(self.substrate.lattice.matrix[:2], self.film.lattice.matrix[:2]))
        assert len(matches) == 40

        z.bidirectional = True
        matches = list(z(self.substrate.lattice.matrix[:2], self.film.lattice.matrix[:2]))
        assert len(matches) == 48

        for match in matches:
            assert match is not None
            assert isinstance(match.match_area, float)


if __name__ == "__main__":
    unittest.main()
