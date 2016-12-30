import os
import unittest

import numpy

from molml.molecule import BagOfBonds, Connectivity
from molml.molecule import CoulombMatrix, EncodedBond
from molml.utils import read_file_data


DATA_PATH = os.path.join(os.path.dirname(__file__), "data")

METHANE_PATH = os.path.join(DATA_PATH, "methane.out")
METHANE_ELEMENTS, METHANE_NUMBERS, METHANE_COORDS = read_file_data(
    METHANE_PATH)
METHANE = (METHANE_ELEMENTS, METHANE_COORDS)
METHANE2 = (METHANE[0], 2 * METHANE[1])

BIG_PATH = os.path.join(DATA_PATH, "big.out")
BIG_ELEMENTS, BIG_NUMBERS, BIG_COORDS = read_file_data(BIG_PATH)
BIG = (BIG_ELEMENTS, BIG_COORDS)

MID_PATH = os.path.join(DATA_PATH, "mid.out")
MID_ELEMENTS, MID_NUMBERS, MID_COORDS = read_file_data(MID_PATH)
MID = (MID_ELEMENTS, MID_COORDS)

ALL_DATA = [METHANE, MID, BIG]


class ConnectivityTest(unittest.TestCase):

    def test_fit_atom(self):
        a = Connectivity(depth=1)
        a.fit(ALL_DATA)
        self.assertEqual(a._base_chains,
                         set([('N',), ('C',), ('O',), ('H',)]))

    def test_fit_atom_separated(self):
        a = Connectivity(depth=1)
        a.fit([METHANE2])
        self.assertEqual(a._base_chains,
                         set([('C',), ('H',)]))
        self.assertTrue(
            (a.transform([METHANE2]) == numpy.array([[1, 4]])).all())

    def test_fit_bond(self):
        a = Connectivity(depth=2)
        a.fit(ALL_DATA)
        self.assertEqual(a._base_chains,
                         set([('H', 'O'), ('C', 'H'), ('H', 'N'), ('C', 'C'),
                              ('H', 'H'), ('O', 'O'), ('C', 'N'), ('C', 'O')]))

    def test_fit_angle(self):
        a = Connectivity(depth=3)
        a.fit(ALL_DATA)
        self.assertEqual(a._base_chains,
                         set([('H', 'N', 'H'), ('C', 'N', 'H'),
                              ('C', 'C', 'O'), ('N', 'C', 'N'),
                              ('C', 'O', 'C'), ('C', 'N', 'C'),
                              ('H', 'C', 'H'), ('C', 'O', 'H'),
                              ('C', 'C', 'C'), ('C', 'C', 'H'),
                              ('H', 'C', 'O'), ('N', 'C', 'O'),
                              ('H', 'C', 'N'), ('C', 'C', 'N')]))

    def test_fit_dihedral(self):
        # This is to test the double order flipping (CCCH vs HCCC)
        a = Connectivity(depth=4)
        a.fit(ALL_DATA)
        self.assertEqual(a._base_chains,
                         set([('N', 'C', 'N', 'C'), ('C', 'C', 'C', 'O'),
                              ('H', 'C', 'O', 'C'), ('H', 'C', 'C', 'N'),
                              ('H', 'C', 'N', 'C'), ('N', 'C', 'C', 'O'),
                              ('C', 'C', 'C', 'N'), ('H', 'C', 'C', 'H'),
                              ('C', 'C', 'N', 'C'), ('O', 'C', 'N', 'C'),
                              ('C', 'C', 'O', 'C'), ('C', 'C', 'C', 'H'),
                              ('C', 'C', 'C', 'C'), ('H', 'C', 'C', 'O'),
                              ('C', 'C', 'N', 'H'), ('N', 'C', 'O', 'H'),
                              ('C', 'C', 'O', 'H'), ('N', 'C', 'N', 'H')]))

    def test_fit_atom_bond(self):
        # This should be the exact same thing as doing it with
        # use_bond_order=False
        a = Connectivity(depth=1, use_bond_order=True)
        a.fit(ALL_DATA)
        self.assertEqual(a._base_chains,
                         set([('N',), ('C',), ('O',), ('H',)]))

    def test_fit_bond_bond(self):
        a = Connectivity(depth=2, use_bond_order=True)
        a.fit(ALL_DATA)
        self.assertEqual(a._base_chains,
                         set([(('H', 'N', '1'),), (('C', 'N', '3'),),
                              (('H', 'O', '1'),), (('H', 'H', '1'),),
                              (('C', 'H', '1'),), (('O', 'O', '1'),),
                              (('C', 'N', '2'),), (('C', 'O', '1'),),
                              (('C', 'C', '3'),), (('C', 'N', 'Ar'),),
                              (('C', 'C', '1'),), (('C', 'O', 'Ar'),),
                              (('C', 'C', '2'),), (('C', 'C', 'Ar'),)]))

    def test_fit_atom_coordination(self):
        a = Connectivity(depth=1, use_coordination=True)
        a.fit(ALL_DATA)
        self.assertEqual(a._base_chains,
                         set([('C1',), ('N3',), ('N2',), ('O2',), ('N1',),
                              ('O1',), ('C4',), ('H0',), ('H1',), ('O0',),
                              ('C3',), ('C2',)]))

    def test_transform(self):
        a = Connectivity()
        a.fit(ALL_DATA)
        expected_results = numpy.array([[0,  1,  0,  4],
                                        [0,  2,  4,  3],
                                        [5, 25,  4, 15]])
        self.assertTrue((a.transform(ALL_DATA) == expected_results).all())

    def test_small_to_large_transform(self):
        a = Connectivity()
        a.fit([METHANE])
        expected_results = numpy.array([[1,  4],
                                        [2,  3],
                                        [25, 15]])
        self.assertTrue((a.transform(ALL_DATA) == expected_results).all())

    def test_large_to_small_transform(self):
        a = Connectivity()
        a.fit([BIG])
        expected_results = numpy.array([[0,  1,  0,  4],
                                        [0,  2,  4,  3],
                                        [5, 25,  4, 15]])
        self.assertTrue((a.transform(ALL_DATA) == expected_results).all())

    def test_transform_before_fit(self):
        a = Connectivity()
        with self.assertRaises(ValueError):
            a.transform(ALL_DATA)

    def test_fit_transform(self):
        a = Connectivity()
        expected_results = numpy.array([[0,  1,  0,  4],
                                        [0,  2,  4,  3],
                                        [5, 25,  4, 15]])
        self.assertTrue((a.fit_transform(ALL_DATA) == expected_results).all())

    def test_unknown(self):
        a = Connectivity(add_unknown=True)
        expected_results = numpy.array([[1,  4, 0],
                                        [2,  3, 4],
                                        [25, 15, 9]])
        a.fit([METHANE])
        self.assertTrue((a.transform(ALL_DATA) == expected_results).all())


class EncodedBondTest(unittest.TestCase):

    def test_fit(self):
        a = EncodedBond()
        a.fit(ALL_DATA)
        self.assertEqual(a._element_pairs,
                         set([('H', 'O'), ('O', 'O'), ('N', 'O'), ('C', 'O'),
                              ('C', 'H'), ('H', 'N'), ('H', 'H'), ('C', 'C'),
                              ('C', 'N'), ('N', 'N')]))

    def test_transform(self):
        a = EncodedBond()
        a.fit([METHANE])
        expected_results = numpy.array([
            [3.71282290e-218,   2.44307522e-202,   4.07306219e-187,
             1.72050858e-172,   1.84138348e-158,   4.99324926e-145,
             3.43062977e-132,   5.97194862e-120,   2.63396427e-108,
             2.94344078e-097,   8.33397769e-087,   5.97862032e-077,
             1.08667888e-067,   5.00441234e-059,   5.83924316e-051,
             1.72628162e-043,   1.29305902e-036,   2.45401190e-030,
             1.18001246e-024,   1.43763335e-019,   4.43773437e-015,
             3.47077198e-011,   6.87768813e-008,   3.45311063e-005,
             4.39268564e-003,   1.41579826e-001,   1.15617678e+000,
             2.39220684e+000,   1.25407882e+000,   1.66572213e-001,
             5.60572640e-003,   4.77983446e-005,   1.03263165e-007,
             5.65235757e-011,   7.83908619e-015,   2.75456401e-019,
             2.45240342e-024,   5.53200513e-030,   3.16173051e-036,
             4.57845280e-043,   1.67982580e-050,   1.56156967e-058,
             3.67798619e-067,   2.19487825e-076,   3.31865715e-086,
             1.27135240e-096,   1.23401693e-107,   3.03478476e-119,
             1.89097714e-131,   2.98535694e-144,   1.19414718e-157,
             1.21023873e-171,   3.10767677e-186,   2.02186537e-201,
             3.33288419e-217,   1.39200184e-233,   1.47302795e-250,
             3.94942399e-268,   2.68292247e-286,   4.61778888e-305] +
            [0.00000000e+000] * 40 +
            [1.16211813e-069,   7.02993879e-061,
             1.07752720e-052,   4.18485776e-045,   4.11821720e-038,
             1.02686702e-031,   6.48777691e-026,   1.03861520e-020,
             4.21299397e-016,   4.33016773e-012,   1.12770796e-008,
             7.44161069e-006,   1.24427375e-003,   5.27161824e-002,
             5.65915129e-001,   1.53935334e+000,   1.06097540e+000,
             1.85290268e-001,   8.19937065e-003,   9.19367947e-005,
             2.61203770e-007,   1.88040360e-010,   3.43008252e-014,
             1.58540502e-018,   1.85677105e-023,   5.51009711e-029,
             4.14326979e-035,   7.89424375e-042,   3.81119789e-049,
             4.66225905e-057,   1.44515863e-065,   1.13506083e-074,
             2.25895472e-084,   1.13915011e-094,   1.45559213e-105,
             4.71285425e-117,   3.86646558e-129,   8.03767362e-142,
             4.23382510e-155,   5.65095734e-169,   1.91116397e-183,
             1.63780015e-198,   3.55640431e-214,   1.95681076e-230,
             2.72818756e-247,   9.63801330e-265,   8.62757854e-283,
             1.95694499e-301,   1.12498748e-320] +
            [0.00000000e+000] * 51
        ])
        try:
            numpy.testing.assert_array_almost_equal(
                a.transform([METHANE]),
                expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_large_to_small_transform(self):
        a = EncodedBond()
        a.fit([MID])

        expected_results = numpy.array([
            [0.00000000e+000] * 100 +
            [1.16211813e-069,   7.02993879e-061,
             1.07752720e-052,   4.18485776e-045,   4.11821720e-038,
             1.02686702e-031,   6.48777691e-026,   1.03861520e-020,
             4.21299397e-016,   4.33016773e-012,   1.12770796e-008,
             7.44161069e-006,   1.24427375e-003,   5.27161824e-002,
             5.65915129e-001,   1.53935334e+000,   1.06097540e+000,
             1.85290268e-001,   8.19937065e-003,   9.19367947e-005,
             2.61203770e-007,   1.88040360e-010,   3.43008252e-014,
             1.58540502e-018,   1.85677105e-023,   5.51009711e-029,
             4.14326979e-035,   7.89424375e-042,   3.81119789e-049,
             4.66225905e-057,   1.44515863e-065,   1.13506083e-074,
             2.25895472e-084,   1.13915011e-094,   1.45559213e-105,
             4.71285425e-117,   3.86646558e-129,   8.03767362e-142,
             4.23382510e-155,   5.65095734e-169,   1.91116397e-183,
             1.63780015e-198,   3.55640431e-214,   1.95681076e-230,
             2.72818756e-247,   9.63801330e-265,   8.62757854e-283,
             1.95694499e-301,   1.12498748e-320] +
            [0.00000000e+000] * 151 +
            [3.71282290e-218,   2.44307522e-202,   4.07306219e-187,
             1.72050858e-172,   1.84138348e-158,   4.99324926e-145,
             3.43062977e-132,   5.97194862e-120,   2.63396427e-108,
             2.94344078e-097,   8.33397769e-087,   5.97862032e-077,
             1.08667888e-067,   5.00441234e-059,   5.83924316e-051,
             1.72628162e-043,   1.29305902e-036,   2.45401190e-030,
             1.18001246e-024,   1.43763335e-019,   4.43773437e-015,
             3.47077198e-011,   6.87768813e-008,   3.45311063e-005,
             4.39268564e-003,   1.41579826e-001,   1.15617678e+000,
             2.39220684e+000,   1.25407882e+000,   1.66572213e-001,
             5.60572640e-003,   4.77983446e-005,   1.03263165e-007,
             5.65235757e-011,   7.83908619e-015,   2.75456401e-019,
             2.45240342e-024,   5.53200513e-030,   3.16173051e-036,
             4.57845280e-043,   1.67982580e-050,   1.56156967e-058,
             3.67798619e-067,   2.19487825e-076,   3.31865715e-086,
             1.27135240e-096,   1.23401693e-107,   3.03478476e-119,
             1.89097714e-131,   2.98535694e-144,   1.19414718e-157,
             1.21023873e-171,   3.10767677e-186,   2.02186537e-201,
             3.33288419e-217,   1.39200184e-233,   1.47302795e-250,
             3.94942399e-268,   2.68292247e-286,   4.61778888e-305] +
            [0.00000000e+000] * 240
        ])
        try:
            numpy.testing.assert_array_almost_equal(
                a.transform([METHANE]),
                expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_fit_transform(self):
        a = EncodedBond()
        expected_results = numpy.array([
            [3.71282290e-218,   2.44307522e-202,   4.07306219e-187,
             1.72050858e-172,   1.84138348e-158,   4.99324926e-145,
             3.43062977e-132,   5.97194862e-120,   2.63396427e-108,
             2.94344078e-097,   8.33397769e-087,   5.97862032e-077,
             1.08667888e-067,   5.00441234e-059,   5.83924316e-051,
             1.72628162e-043,   1.29305902e-036,   2.45401190e-030,
             1.18001246e-024,   1.43763335e-019,   4.43773437e-015,
             3.47077198e-011,   6.87768813e-008,   3.45311063e-005,
             4.39268564e-003,   1.41579826e-001,   1.15617678e+000,
             2.39220684e+000,   1.25407882e+000,   1.66572213e-001,
             5.60572640e-003,   4.77983446e-005,   1.03263165e-007,
             5.65235757e-011,   7.83908619e-015,   2.75456401e-019,
             2.45240342e-024,   5.53200513e-030,   3.16173051e-036,
             4.57845280e-043,   1.67982580e-050,   1.56156967e-058,
             3.67798619e-067,   2.19487825e-076,   3.31865715e-086,
             1.27135240e-096,   1.23401693e-107,   3.03478476e-119,
             1.89097714e-131,   2.98535694e-144,   1.19414718e-157,
             1.21023873e-171,   3.10767677e-186,   2.02186537e-201,
             3.33288419e-217,   1.39200184e-233,   1.47302795e-250,
             3.94942399e-268,   2.68292247e-286,   4.61778888e-305] +
            [0.00000000e+000] * 40 +
            [1.16211813e-069,   7.02993879e-061,
             1.07752720e-052,   4.18485776e-045,   4.11821720e-038,
             1.02686702e-031,   6.48777691e-026,   1.03861520e-020,
             4.21299397e-016,   4.33016773e-012,   1.12770796e-008,
             7.44161069e-006,   1.24427375e-003,   5.27161824e-002,
             5.65915129e-001,   1.53935334e+000,   1.06097540e+000,
             1.85290268e-001,   8.19937065e-003,   9.19367947e-005,
             2.61203770e-007,   1.88040360e-010,   3.43008252e-014,
             1.58540502e-018,   1.85677105e-023,   5.51009711e-029,
             4.14326979e-035,   7.89424375e-042,   3.81119789e-049,
             4.66225905e-057,   1.44515863e-065,   1.13506083e-074,
             2.25895472e-084,   1.13915011e-094,   1.45559213e-105,
             4.71285425e-117,   3.86646558e-129,   8.03767362e-142,
             4.23382510e-155,   5.65095734e-169,   1.91116397e-183,
             1.63780015e-198,   3.55640431e-214,   1.95681076e-230,
             2.72818756e-247,   9.63801330e-265,   8.62757854e-283,
             1.95694499e-301,   1.12498748e-320] +
            [0.00000000e+000] * 51
        ])
        try:
            numpy.testing.assert_array_almost_equal(
                a.fit_transform([METHANE]),
                expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_transform_before_fit(self):
        a = EncodedBond()
        with self.assertRaises(ValueError):
            a.transform(ALL_DATA)

    def test_smoothing_function(self):
        a = EncodedBond(smoothing="norm_cdf")

        expected_results = numpy.array([
            [1.17115012e-219,   8.00172390e-204,   1.38721414e-188,
             6.10300931e-174,   6.81464578e-160,   1.93155503e-146,
             1.38998566e-133,   2.54002905e-121,   1.17893774e-109,
             1.39021289e-098,   4.16623455e-088,   3.17420971e-078,
             6.15098063e-069,   3.03315842e-060,   3.80856686e-052,
             1.21865612e-044,   9.94662898e-038,   2.07340038e-031,
             1.10560799e-025,   1.51132936e-020,   5.31164824e-016,
             4.81963746e-012,   1.13599721e-008,   7.02198318e-006,
             1.15645754e-003,   5.22045543e-002,   6.82991151e-001,
             2.91699190e+000,   5.23342049e+000,   5.93712625e+000,
             5.99849831e+000,   5.99999015e+000,   5.99999998e+000] +
            [6.00000000e+000] * 67 +
            [6.49272432e-071,   4.20175133e-062,
             6.92331704e-054,   2.90671285e-046,   3.11241497e-039,
             8.50965518e-033,   5.94986888e-027,   1.06600695e-021,
             4.90752185e-017,   5.82761547e-013,   1.79515002e-009,
             1.44699564e-006,   3.09573634e-004,   1.80252413e-002,
             2.99797572e-001,   1.57708565e+000,   3.26745998e+000,
             3.92405799e+000,   3.99766622e+000,   3.99998013e+000,
             3.99999995e+000] +
            [4.00000000e+000] * 79
        ])
        try:
            numpy.testing.assert_array_almost_equal(
                a.fit_transform([METHANE]),
                expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_smoothing_function_error(self):
        a = EncodedBond(smoothing="not valid")

        with self.assertRaises(KeyError):
            a.fit_transform([METHANE])

    def test_max_depth_neg(self):
        a = EncodedBond(max_depth=-1)
        # This is a cheap test to prevent needing all the values here
        expected_results = numpy.array([
            0.503237244954,  # mean
            0.857850829564,  # std
            0.,  # min
            7.15861023,  # max
        ])
        try:
            m = a.fit_transform([BIG])
            value = numpy.array([
                                m.mean(),
                                m.std(),
                                m.min(),
                                m.max(),
                                ])
            numpy.testing.assert_array_almost_equal(
                value,
                expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_max_depth_1(self):
        a = EncodedBond(max_depth=1)

        # This is a cheap test to prevent needing all the values here
        expected_results = numpy.array([
            0.0443793,  # mean
            0.33766942,  # std
            0.,  # min
            5.76559336,  # max
        ])
        try:
            m = a.fit_transform([BIG])
            value = numpy.array([
                                m.mean(),
                                m.std(),
                                m.min(),
                                m.max(),
                                ])
            numpy.testing.assert_array_almost_equal(
                value,
                expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_max_depth_3(self):
        a = EncodedBond(max_depth=3)

        # This is a cheap test to prevent needing all the values here
        expected_results = numpy.array([
            0.18434482,  # mean
            0.62589799,  # std
            0.,  # min
            7.15861023,  # max
        ])
        try:
            m = a.fit_transform([BIG])
            value = numpy.array([
                                m.mean(),
                                m.std(),
                                m.min(),
                                m.max(),
                                ])
            numpy.testing.assert_array_almost_equal(
                value,
                expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_spacing_inverse(self):
        a = EncodedBond(spacing="inverse")

        # This is a cheap test to prevent needing all the values here
        expected_results = numpy.array([
            0.051207,  # mean
            0.269248,  # std
            0.,  # min
            2.387995,  # max
        ])
        try:
            m = a.fit_transform([METHANE])
            value = numpy.array([
                                m.mean(),
                                m.std(),
                                m.min(),
                                m.max(),
                                ])
            numpy.testing.assert_array_almost_equal(
                value,
                expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_spacing_log(self):
        a = EncodedBond(spacing="log")

        # This is a cheap test to prevent needing all the values here
        expected_results = numpy.array([
            0.072768,  # mean
            0.318508,  # std
            0.,  # min
            2.339376,  # max
        ])
        try:
            m = a.fit_transform([METHANE])
            value = numpy.array([
                                m.mean(),
                                m.std(),
                                m.min(),
                                m.max(),
                                ])
            numpy.testing.assert_array_almost_equal(
                value,
                expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_spacing_invalid(self):
        a = EncodedBond(spacing="not valid")

        with self.assertRaises(KeyError):
            a.fit_transform([METHANE])


class CoulombMatrixTest(unittest.TestCase):

    def test_fit(self):
        a = CoulombMatrix()
        a.fit(ALL_DATA)
        self.assertEqual(a._max_size, 49)

    def test_transform(self):
        a = CoulombMatrix()
        a.fit([METHANE])
        expected_results = numpy.array([
            [36.8581052,   5.49459021,   5.49462885,   5.4945,
                5.49031286,   5.49459021,   0.5,   0.56071947,
                0.56071656,   0.56064037,   5.49462885,   0.56071947,
                0.5,   0.56071752,   0.56064089,   5.4945,
                0.56071656,   0.56071752,   0.5,   0.56063783,
                5.49031286,   0.56064037,   0.56064089,   0.56063783,
                0.5]])
        try:
            numpy.testing.assert_array_almost_equal(
                a.transform([METHANE]),
                expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_small_to_large_transform(self):
        a = CoulombMatrix()
        a.fit([METHANE])
        with self.assertRaises(ValueError):
            a.transform(ALL_DATA)

    def test_large_to_small_transform(self):
        a = CoulombMatrix()
        a.fit([MID])

        expected_results = numpy.array([
            [36.8581052,   5.49459021,   5.49462885,   5.4945,
             5.49031286,   0.,   0.,   0.,
             0.,   5.49459021,   0.5,   0.56071947,
             0.56071656,   0.56064037,   0.,   0.,
             0.,   0.,   5.49462885,   0.56071947,
             0.5,   0.56071752,   0.56064089,   0.,
             0.,   0.,   0.,   5.4945,
             0.56071656,   0.56071752,   0.5,   0.56063783,
             0.,   0.,   0.,   0.,
             5.49031286,   0.56064037,   0.56064089,   0.56063783,
             0.5] + [0.0] * 40
        ])
        try:
            numpy.testing.assert_array_almost_equal(
                a.transform([METHANE]),
                expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_transform_before_fit(self):
        a = CoulombMatrix()
        with self.assertRaises(ValueError):
            a.transform(ALL_DATA)

    def test_fit_transform(self):
        a = CoulombMatrix()
        expected_results = numpy.array([
            [36.8581052,   5.49459021,   5.49462885,   5.4945,
                5.49031286,   5.49459021,   0.5,   0.56071947,
                0.56071656,   0.56064037,   5.49462885,   0.56071947,
                0.5,   0.56071752,   0.56064089,   5.4945,
                0.56071656,   0.56071752,   0.5,   0.56063783,
                5.49031286,   0.56064037,   0.56064089,   0.56063783,
                0.5]])
        try:
            numpy.testing.assert_array_almost_equal(
                a.fit_transform([METHANE]),
                expected_results)
        except AssertionError as e:
            self.fail(e)


class BagOfBondsTest(unittest.TestCase):

    def test_fit(self):
        a = BagOfBonds()
        a.fit([METHANE])
        expected_results = {
            ('C', 'H'): 4,
            ('H', 'H'): 6,
        }
        self.assertEqual(a._bag_sizes, expected_results)

    def test_fit_multi_mol(self):
        a = BagOfBonds()
        a.fit(ALL_DATA)
        expected_results = {
            ('H', 'O'): 60,
            ('C', 'H'): 375,
            ('H', 'N'): 75,
            ('C', 'C'): 300,
            ('H', 'H'): 105,
            ('O', 'O'): 6,
            ('C', 'N'): 125,
            ('N', 'O'): 20,
            ('C', 'O'): 100,
            ('N', 'N'): 10,
        }
        self.assertEqual(a._bag_sizes, expected_results)

    def test_transform(self):
        a = BagOfBonds()
        a.fit([METHANE])
        expected_results = numpy.array([
            [0.56071947,  0.56071752,  0.56071656,  0.56064089,  0.56064037,
             0.56063783,  5.49462885,  5.49459021,  5.4945,  5.49031286]
        ])
        try:
            numpy.testing.assert_array_almost_equal(
                a.transform([METHANE]),
                expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_small_to_large_transform(self):
        a = BagOfBonds()
        a.fit([METHANE])
        with self.assertRaises(ValueError):
            a.transform(ALL_DATA)

    def test_large_to_small_transform(self):
        a = BagOfBonds()
        a.fit([BIG])

        expected_results = numpy.array([
            [0.0] * 60 +
            [5.494628848219048, 5.494590213211275, 5.494499999706413,
             5.49031286145183] +
            [0.0] * 746 +
            [0.5607194714171738, 0.5607175240809282, 0.5607165613824526,
             0.5606408892793993, 0.5606403708987712, 0.560637829974531] +
            [0.0] * 360
        ])
        try:
            numpy.testing.assert_array_almost_equal(
                a.transform([METHANE]),
                expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_transform_before_fit(self):
        a = BagOfBonds()
        with self.assertRaises(ValueError):
            a.transform(ALL_DATA)


if __name__ == '__main__':
    unittest.main()