"""Tests for ersa.utils"""

import unittest

import numpy as np
import pytest
from scipy import stats

from ersa import utils


class SortByFirstTestCase(unittest.TestCase):
    """Test ersa.utils.sort_by_first."""

    def test_sort_by_first(self):
        tolist = lambda a: a.tolist()

        # Test on no arguments.
        self.assertEqual(utils.sort_by_first(), ())
        # Test on empty lists.
        self.assertEqual(
            tuple(map(tolist, utils.sort_by_first([]))),
            ([],)
        )
        self.assertEqual(
            tuple(map(tolist, utils.sort_by_first([], []))),
            ([], []),
        )
        self.assertEqual(
            tuple(map(tolist, utils.sort_by_first([], [], []))),
            ([], [], []),
        )
        # Test list of length 1.
        self.assertEqual(
            tuple(map(tolist, utils.sort_by_first([1.]))),
            ([1.],),
        )
        self.assertEqual(
            tuple(map(tolist, utils.sort_by_first([1.], [2.]))),
            ([1.], [2.]),
        )
        self.assertEqual(
            tuple(map(tolist, utils.sort_by_first([1.], [2.], ['a']))),
            ([1.], [2.], ['a']),
        )
        # Test lists of length greater than 1.
        #   when first is sorted
        self.assertEqual(
            tuple(map(tolist, utils.sort_by_first([1., 2., 3.]))),
            ([1., 2., 3.],),
        )
        self.assertEqual(
            tuple(map(tolist, utils.sort_by_first(
                [1., 2., 3.],
                [3., 2., 1.],
            ))),
            (
                [1., 2., 3.],
                [3., 2., 1.],
            ),
        )
        self.assertEqual(
            tuple(map(tolist, utils.sort_by_first(
                [1., 2., 3.],
                [3., 2., 1.],
                ['a', 'c', 'b'],
            ))),
            (
                [1., 2., 3.],
                [3., 2., 1.],
                ['a', 'c', 'b'],
            ),
        )
        #   when first is unsorted
        self.assertEqual(
            tuple(map(tolist, utils.sort_by_first([2., 1., 3.]))),
            ([1., 2., 3.],),
        )
        self.assertEqual(
            tuple(map(tolist, utils.sort_by_first(
                [2., 1., 3.],
                [3., 2., 1.],
            ))),
            (
                [1., 2., 3.],
                [2., 3., 1.],
            ),
        )
        self.assertEqual(
            tuple(map(tolist, utils.sort_by_first(
                [2., 1., 3.],
                [3., 2., 1.],
                ['a', 'c', 'b'],
            ))),
            (
                [1., 2., 3.],
                [2., 3., 1.],
                ['c', 'a', 'b'],
            ),
        )


class DkwEpsilonTestCase(unittest.TestCase):
    """Test ersa.utils.dkw_epsilon."""

    def test_dkw_epsilon(self):
        self.assertEqual(utils.dkw_epsilon(2, 1. - 2./np.e), 0.5)
        self.assertEqual(utils.dkw_epsilon(8, 1. - 2./np.e), 0.25)
        self.assertEqual(utils.dkw_epsilon(1, 1. - 2./np.e**2), 1.)
        self.assertEqual(utils.dkw_epsilon(4, 1. - 2./np.e**2), 0.5)


class BetaEqualTailedIntervalTestCase(unittest.TestCase):
    """Test ersa.utils.beta_equal_tailed_interval."""

    def test_beta_equal_tailed_interval(self):
        # Test when a and b are scalars.
        for a in [1., 5., 10.]:
            for b in [1., 5., 10.]:
                beta = stats.beta(a, b)
                # when coverage is a scalar.
                for coverage in [0.25, 0.50, 0.75]:
                    lo, hi = utils.beta_equal_tailed_interval(a, b, coverage)
                    self.assertEqual(lo.shape, ())
                    self.assertEqual(hi.shape, ())
                    self.assertAlmostEqual(
                        beta.cdf(hi) - beta.cdf(lo),
                        coverage,
                    )
                    self.assertAlmostEqual(beta.cdf(lo), (1. - coverage) / 2.)
                    self.assertAlmostEqual(beta.cdf(hi), (1. + coverage) / 2.)
                # when coverage is an array.
                k = 5
                coverage = np.random.rand(k)
                lo, hi = utils.beta_equal_tailed_interval(a, b, coverage)
                self.assertEqual(lo.shape, (k,))
                self.assertEqual(hi.shape, (k,))
                self.assertTrue(np.allclose(
                    beta.cdf(hi) - beta.cdf(lo),
                    coverage,
                ))
                self.assertTrue(np.all(
                    np.abs(beta.cdf(lo) - (1. - coverage) / 2.)
                    < 1e-10
                ))
                self.assertTrue(np.all(
                    np.abs(beta.cdf(hi) - (1. + coverage) / 2.)
                    < 1e-10
                ))
        # Test when a and b are 1D arrays.
        n = 10
        a = np.arange(1, n + 1)
        b = np.arange(n + 1, 1, -1)
        beta = stats.beta(a, b)
        #   when coverage is a scalar.
        for coverage in [0.25, 0.50, 0.75]:
            lo, hi = utils.beta_equal_tailed_interval(a, b, coverage)
            self.assertEqual(lo.shape, (n,))
            self.assertEqual(hi.shape, (n,))
            self.assertTrue(np.all(
                np.abs((beta.cdf(hi) - beta.cdf(lo)) - coverage)
                < 1e-10
            ))
            self.assertTrue(np.all(
                np.abs(beta.cdf(lo) - (1. - coverage) / 2.)
                < 1e-10
            ))
            self.assertTrue(np.all(
                np.abs(beta.cdf(hi) - (1. + coverage) / 2.)
                < 1e-10
            ))
        #   when coverage is an array.
        coverage = np.random.rand(n)
        lo, hi = utils.beta_equal_tailed_interval(a, b, coverage)
        self.assertEqual(lo.shape, (n,))
        self.assertEqual(hi.shape, (n,))
        self.assertTrue(np.allclose(
            beta.cdf(hi) - beta.cdf(lo),
            coverage,
        ))
        self.assertTrue(np.all(
            np.abs(beta.cdf(lo) - (1. - coverage) / 2.)
            < 1e-10
        ))
        self.assertTrue(np.all(
            np.abs(beta.cdf(hi) - (1. + coverage) / 2.)
            < 1e-10
        ))
        # Test when a and b are 2D arrays.
        n, m = 5, 2
        a = np.arange(1, n * m + 1).reshape(n, m)
        b = np.arange(n * m + 1, 1, -1).reshape(n, m)
        beta = stats.beta(a, b)
        #   when coverage is a scalar.
        for coverage in [0.25, 0.50, 0.75]:
            lo, hi = utils.beta_equal_tailed_interval(a, b, coverage)
            self.assertEqual(lo.shape, (n, m))
            self.assertEqual(hi.shape, (n, m))
            self.assertTrue(np.all(
                np.abs((beta.cdf(hi) - beta.cdf(lo)) - coverage)
                < 1e-10
            ))
            self.assertTrue(np.all(
                np.abs(beta.cdf(lo) - (1. - coverage) / 2.)
                < 1e-10
            ))
            self.assertTrue(np.all(
                np.abs(beta.cdf(hi) - (1. + coverage) / 2.)
                < 1e-10
            ))
        #   when coverage is an array.
        coverage = np.random.rand(n, m)
        lo, hi = utils.beta_equal_tailed_interval(a, b, coverage)
        self.assertEqual(lo.shape, (n, m))
        self.assertEqual(hi.shape, (n, m))
        self.assertTrue(np.allclose(
            beta.cdf(hi) - beta.cdf(lo),
            coverage,
        ))
        self.assertTrue(np.all(
            np.abs(beta.cdf(lo) - (1. - coverage) / 2.)
            < 1e-10
        ))
        self.assertTrue(np.all(
            np.abs(beta.cdf(hi) - (1. + coverage) / 2.)
            < 1e-10
        ))
        # Test when a and b broadcast over each other.
        n, m = 5, 2
        a = np.arange(1, n + 1).reshape(n, 1)
        b = np.arange(m + 1, 1, -1).reshape(1, m)
        beta = stats.beta(a, b)
        #   when coverage is a scalar.
        for coverage in [0.25, 0.50, 0.75]:
            lo, hi = utils.beta_equal_tailed_interval(a, b, coverage)
            self.assertEqual(lo.shape, (n, m))
            self.assertEqual(hi.shape, (n, m))
            self.assertTrue(np.all(
                np.abs((beta.cdf(hi) - beta.cdf(lo)) - coverage)
                < 1e-10
            ))
            self.assertTrue(np.all(
                np.abs(beta.cdf(lo) - (1. - coverage) / 2.)
                < 1e-10
            ))
            self.assertTrue(np.all(
                np.abs(beta.cdf(hi) - (1. + coverage) / 2.)
                < 1e-10
            ))
        #   when coverage is an array.
        coverage = np.random.rand(n, m)
        lo, hi = utils.beta_equal_tailed_interval(a, b, coverage)
        self.assertEqual(lo.shape, (n, m))
        self.assertEqual(hi.shape, (n, m))
        self.assertTrue(np.allclose(
            beta.cdf(hi) - beta.cdf(lo),
            coverage,
        ))
        self.assertTrue(np.all(
            np.abs(beta.cdf(lo) - (1. - coverage) / 2.)
            < 1e-10
        ))
        self.assertTrue(np.all(
            np.abs(beta.cdf(hi) - (1. + coverage) / 2.)
            < 1e-10
        ))
        # Test when coverage broadcasts over a and b.
        #   when a and b have the same shape.
        n = 10
        a = np.arange(1, n + 1)[:, None]
        b = np.arange(n + 1, 1, -1)[:, None]
        beta = stats.beta(a, b)
        k = 5
        coverage = np.random.rand(k)[None, :]
        lo, hi = utils.beta_equal_tailed_interval(a, b, coverage)
        self.assertEqual(lo.shape, (n, k))
        self.assertEqual(hi.shape, (n, k))
        self.assertTrue(np.allclose(
            beta.cdf(hi) - beta.cdf(lo),
            np.tile(coverage, (n, 1))
        ))
        self.assertTrue(np.all(
            np.abs(beta.cdf(lo) - (1. - coverage) / 2.)
            < 1e-10
        ))
        self.assertTrue(np.all(
            np.abs(beta.cdf(hi) - (1. + coverage) / 2.)
            < 1e-10
        ))
        #   when a and b broadcast over each other.
        n, m = 3, 2
        a = np.arange(1, n + 1).reshape(n, 1)[..., None]
        b = np.arange(m + 1, 1, -1).reshape(1, m)[..., None]
        beta = stats.beta(a, b)
        k = 5
        coverage = np.random.rand(k)[None, None, :]
        lo, hi = utils.beta_equal_tailed_interval(a, b, coverage)
        self.assertEqual(lo.shape, (n, m, k))
        self.assertEqual(hi.shape, (n, m, k))
        self.assertTrue(np.allclose(
            beta.cdf(hi) - beta.cdf(lo),
            np.tile(coverage, (n, m, 1))
        ))
        self.assertTrue(np.all(
            np.abs(beta.cdf(lo) - (1. - coverage) / 2.)
            < 1e-10
        ))
        self.assertTrue(np.all(
            np.abs(beta.cdf(hi) - (1. + coverage) / 2.)
            < 1e-10
        ))


class BetaHighestDensityIntervalTestCase(unittest.TestCase):
    """Test ersa.utils.beta_highest_density_interval."""

    @pytest.mark.level(1)
    def test_beta_highest_density_interval(self):
        # Test when a and b are scalars.
        for a in [1., 5., 10.]:
            for b in [1., 5., 10.]:
                if a == 1. and b == 1.:
                    # No highest density interval exists when a <= 1 and b <= 1.
                    continue
                beta = stats.beta(a, b)
                # when coverage is a scalar.
                for coverage in [0.25, 0.50, 0.75]:
                    lo, hi = utils.beta_highest_density_interval(a, b, coverage)
                    self.assertEqual(lo.shape, ())
                    self.assertEqual(hi.shape, ())
                    self.assertAlmostEqual(
                        beta.cdf(hi) - beta.cdf(lo),
                        coverage,
                    )
                    equal_tailed_lo, equal_tailed_hi =\
                        utils.beta_equal_tailed_interval(a, b, coverage)
                    self.assertLess(
                        (hi - lo) - (equal_tailed_hi - equal_tailed_lo),
                        1e-12,
                    )
                # when coverage is an array.
                k = 5
                coverage = np.random.rand(k)
                lo, hi = utils.beta_highest_density_interval(a, b, coverage)
                self.assertEqual(lo.shape, (k,))
                self.assertEqual(hi.shape, (k,))
                self.assertTrue(np.allclose(
                    beta.cdf(hi) - beta.cdf(lo),
                    coverage,
                ))
                equal_tailed_lo, equal_tailed_hi =\
                    utils.beta_equal_tailed_interval(a, b, coverage)
                self.assertTrue(np.all(
                    (hi - lo) - (equal_tailed_hi - equal_tailed_lo) < 1e-12
                ))
        # Test when a and b are 1D arrays.
        n = 10
        a = np.arange(1, n + 1)
        b = np.arange(n + 1, 1, -1)
        beta = stats.beta(a, b)
        #   when coverage is a scalar.
        for coverage in [0.25, 0.50, 0.75]:
            lo, hi = utils.beta_highest_density_interval(a, b, coverage)
            self.assertEqual(lo.shape, (n,))
            self.assertEqual(hi.shape, (n,))
            self.assertTrue(np.all(
                np.abs((beta.cdf(hi) - beta.cdf(lo)) - coverage)
                < 1e-10
            ))
            equal_tailed_lo, equal_tailed_hi =\
                utils.beta_equal_tailed_interval(a, b, coverage)
            self.assertTrue(np.all(
                (hi - lo) - (equal_tailed_hi - equal_tailed_lo) < 1e-12
            ))
            self.assertTrue(np.any(
                (equal_tailed_hi - equal_tailed_lo) - (hi - lo) > 1e-5
            ))
        #   when coverage is an array.
        coverage = np.random.rand(n)
        lo, hi = utils.beta_highest_density_interval(a, b, coverage)
        self.assertEqual(lo.shape, (n,))
        self.assertEqual(hi.shape, (n,))
        self.assertTrue(np.allclose(
            beta.cdf(hi) - beta.cdf(lo),
            coverage,
        ))
        equal_tailed_lo, equal_tailed_hi =\
            utils.beta_equal_tailed_interval(a, b, coverage)
        self.assertTrue(np.all(
            (hi - lo) - (equal_tailed_hi - equal_tailed_lo) < 1e-12
        ))
        self.assertTrue(np.any(
            (equal_tailed_hi - equal_tailed_lo) - (hi - lo) > 1e-5
        ))
        # Test when a and b are 2D arrays.
        n, m = 5, 2
        a = np.arange(1, n * m + 1).reshape(n, m)
        b = np.arange(n * m + 1, 1, -1).reshape(n, m)
        beta = stats.beta(a, b)
        #   when coverage is a scalar.
        for coverage in [0.25, 0.50, 0.75]:
            lo, hi = utils.beta_highest_density_interval(a, b, coverage)
            self.assertEqual(lo.shape, (n, m))
            self.assertEqual(hi.shape, (n, m))
            self.assertTrue(np.all(
                np.abs((beta.cdf(hi) - beta.cdf(lo)) - coverage)
                < 1e-10
            ))
            equal_tailed_lo, equal_tailed_hi =\
                utils.beta_equal_tailed_interval(a, b, coverage)
            self.assertTrue(np.all(
                (hi - lo) - (equal_tailed_hi - equal_tailed_lo) < 1e-12
            ))
            self.assertTrue(np.any(
                (equal_tailed_hi - equal_tailed_lo) - (hi - lo) > 1e-5
            ))
        #   when coverage is an array.
        coverage = np.random.rand(n, m)
        lo, hi = utils.beta_highest_density_interval(a, b, coverage)
        self.assertEqual(lo.shape, (n, m))
        self.assertEqual(hi.shape, (n, m))
        self.assertTrue(np.allclose(
            beta.cdf(hi) - beta.cdf(lo),
            coverage,
        ))
        equal_tailed_lo, equal_tailed_hi =\
            utils.beta_equal_tailed_interval(a, b, coverage)
        self.assertTrue(np.all(
            (hi - lo) - (equal_tailed_hi - equal_tailed_lo) < 1e-12
        ))
        self.assertTrue(np.any(
            (equal_tailed_hi - equal_tailed_lo) - (hi - lo) > 1e-5
        ))
        # Test when a and b broadcast over each other.
        n, m = 5, 2
        a = np.arange(1, n + 1).reshape(n, 1)
        b = np.arange(m + 1, 1, -1).reshape(1, m)
        beta = stats.beta(a, b)
        #   when coverage is a scalar.
        for coverage in [0.25, 0.50, 0.75]:
            lo, hi = utils.beta_highest_density_interval(a, b, coverage)
            self.assertEqual(lo.shape, (n, m))
            self.assertEqual(hi.shape, (n, m))
            self.assertTrue(np.all(
                np.abs((beta.cdf(hi) - beta.cdf(lo)) - coverage)
                < 1e-10
            ))
            equal_tailed_lo, equal_tailed_hi =\
                utils.beta_equal_tailed_interval(a, b, coverage)
            self.assertTrue(np.all(
                (hi - lo) - (equal_tailed_hi - equal_tailed_lo) < 1e-12
            ))
            self.assertTrue(np.any(
                (equal_tailed_hi - equal_tailed_lo) - (hi - lo) > 1e-5
            ))
        #   when coverage is an array.
        coverage = np.random.rand(n, m)
        lo, hi = utils.beta_highest_density_interval(a, b, coverage)
        self.assertEqual(lo.shape, (n, m))
        self.assertEqual(hi.shape, (n, m))
        self.assertTrue(np.allclose(
            beta.cdf(hi) - beta.cdf(lo),
            coverage,
        ))
        equal_tailed_lo, equal_tailed_hi =\
            utils.beta_equal_tailed_interval(a, b, coverage)
        self.assertTrue(np.all(
            (hi - lo) - (equal_tailed_hi - equal_tailed_lo) < 1e-12
        ))
        self.assertTrue(np.any(
            (equal_tailed_hi - equal_tailed_lo) - (hi - lo) > 1e-5
        ))
        # Test when coverage broadcasts over a and b.
        #   when a and b have the same shape.
        n = 10
        a = np.arange(1, n + 1)[:, None]
        b = np.arange(n + 1, 1, -1)[:, None]
        beta = stats.beta(a, b)
        k = 5
        coverage = np.random.rand(k)[None, :]
        lo, hi = utils.beta_highest_density_interval(a, b, coverage)
        self.assertEqual(lo.shape, (n, k))
        self.assertEqual(hi.shape, (n, k))
        self.assertTrue(np.allclose(
            beta.cdf(hi) - beta.cdf(lo),
            np.tile(coverage, (n, 1)),
        ))
        equal_tailed_lo, equal_tailed_hi =\
            utils.beta_equal_tailed_interval(a, b, coverage)
        self.assertTrue(np.all(
            (hi - lo) - (equal_tailed_hi - equal_tailed_lo) < 1e-12
        ))
        self.assertTrue(np.any(
            (equal_tailed_hi - equal_tailed_lo) - (hi - lo) > 1e-5
        ))
        #   when a and b broadcast over each other.
        n, m = 3, 2
        a = np.arange(1, n + 1).reshape(n, 1)[..., None]
        b = np.arange(m + 1, 1, -1).reshape(1, m)[..., None]
        beta = stats.beta(a, b)
        k = 5
        coverage = np.random.rand(k)[None, None, :]
        lo, hi = utils.beta_highest_density_interval(a, b, coverage)
        self.assertEqual(lo.shape, (n, m, k))
        self.assertEqual(hi.shape, (n, m, k))
        self.assertTrue(np.allclose(
            beta.cdf(hi) - beta.cdf(lo),
            np.tile(coverage, (n, m, 1)),
        ))
        equal_tailed_lo, equal_tailed_hi =\
            utils.beta_equal_tailed_interval(a, b, coverage)
        self.assertTrue(np.all(
            (hi - lo) - (equal_tailed_hi - equal_tailed_lo) < 1e-12
        ))
        self.assertTrue(np.any(
            (equal_tailed_hi - equal_tailed_lo) - (hi - lo) > 1e-5
        ))

    def test_converges_for_short_intervals(self):
        coverage = 1e-8
        for a in [2., 5., 10.]:
            for b in [2., 5., 10.]:
                beta = stats.beta(a, b)
                lo, hi = utils.beta_highest_density_interval(a, b, coverage)
                self.assertEqual(lo.shape, ())
                self.assertEqual(hi.shape, ())
                self.assertLess(lo, hi)
                self.assertAlmostEqual(beta.cdf(hi) - beta.cdf(lo), coverage)


class BetaEqualTailedCoverageTestCase(unittest.TestCase):
    """Test ersa.utils.beta_equal_tailed_coverage."""

    def test_beta_equal_tailed_coverage(self):
        # Test when a and b are scalars.
        for a in [1., 2., 3.]:
            for b in [1., 2., 3.]:
                # when x is a scalar.
                for x in [0.25, 0.50, 0.75]:
                    coverage = utils.beta_equal_tailed_coverage(a, b, x)
                    lo, hi = utils.beta_equal_tailed_interval(a, b, coverage)
                    self.assertEqual(coverage.shape, ())
                    self.assertTrue(np.all(
                        np.isclose(lo, x) | np.isclose(hi, x)
                    ))
                # when x is an array.
                k = 5
                x = np.random.rand(k)
                coverage = utils.beta_equal_tailed_coverage(a, b, x)
                lo, hi = utils.beta_equal_tailed_interval(a, b, coverage)
                self.assertEqual(coverage.shape, (k,))
                self.assertTrue(np.all(
                    np.isclose(lo, x) | np.isclose(hi, x)
                ))
        # Test when a and b are 1D arrays.
        n = 3
        a = np.arange(1, n + 1)
        b = np.arange(n + 1, 1, -1)
        #   when x is a scalar.
        for x in [0.25, 0.50, 0.75]:
            coverage = utils.beta_equal_tailed_coverage(a, b, x)
            lo, hi = utils.beta_equal_tailed_interval(a, b, coverage)
            self.assertEqual(coverage.shape, (n,))
            self.assertTrue(np.all(
                np.isclose(lo, x) | np.isclose(hi, x)
            ))
        #   when x is an array.
        x = np.random.rand(n)
        coverage = utils.beta_equal_tailed_coverage(a, b, x)
        lo, hi = utils.beta_equal_tailed_interval(a, b, coverage)
        self.assertEqual(coverage.shape, (n,))
        self.assertTrue(np.all(
            np.isclose(lo, x) | np.isclose(hi, x)
        ))
        # Test when a and b are 2D arrays.
        n, m = 3, 2
        a = np.arange(1, n * m + 1).reshape(n, m)
        b = np.arange(n * m + 1, 1, -1).reshape(n, m)
        #   when x is a scalar.
        for x in [0.25, 0.50, 0.75]:
            coverage = utils.beta_equal_tailed_coverage(a, b, x)
            lo, hi = utils.beta_equal_tailed_interval(a, b, coverage)
            self.assertEqual(coverage.shape, (n, m))
            self.assertTrue(np.all(
                np.isclose(lo, x) | np.isclose(hi, x)
            ))
        #   when x is an array.
        x = np.random.rand(n, m)
        coverage = utils.beta_equal_tailed_coverage(a, b, x)
        lo, hi = utils.beta_equal_tailed_interval(a, b, coverage)
        self.assertEqual(coverage.shape, (n, m))
        self.assertTrue(np.all(
            np.isclose(lo, x) | np.isclose(hi, x)
        ))
        # Test when a and b broadcast over each other.
        n, m = 3, 2
        a = np.arange(1, n + 1).reshape(n, 1)
        b = np.arange(m + 1, 1, -1).reshape(1, m)
        #   when x is a scalar.
        for x in [0.25, 0.50, 0.75]:
            coverage = utils.beta_equal_tailed_coverage(a, b, x)
            lo, hi = utils.beta_equal_tailed_interval(a, b, coverage)
            self.assertEqual(coverage.shape, (n, m))
            self.assertTrue(np.all(
                np.isclose(lo, x) | np.isclose(hi, x)
            ))
        #   when x is an array.
        x = np.random.rand(n, m)
        coverage = utils.beta_equal_tailed_coverage(a, b, x)
        lo, hi = utils.beta_equal_tailed_interval(a, b, coverage)
        self.assertEqual(coverage.shape, (n, m))
        self.assertTrue(np.all(
            np.isclose(lo, x) | np.isclose(hi, x)
        ))
        # Test when x broadcasts over a and b.
        #   when a and b have the same shape.
        n = 3
        a = np.arange(1, n + 1)[:, None]
        b = np.arange(n + 1, 1, -1)[:, None]
        k = 5
        x = np.random.rand(k)[None, :]
        coverage = utils.beta_equal_tailed_coverage(a, b, x)
        lo, hi = utils.beta_equal_tailed_interval(a, b, coverage)
        self.assertEqual(coverage.shape, (n, k))
        self.assertTrue(np.all(
            np.isclose(lo, x) | np.isclose(hi, x)
        ))
        #   when a and b broadcast over each other.
        n, m = 3, 2
        a = np.arange(1, n + 1).reshape(n, 1)[..., None]
        b = np.arange(m + 1, 1, -1).reshape(1, m)[..., None]
        k = 5
        x = np.random.rand(k)[None, None, :]
        coverage = utils.beta_equal_tailed_coverage(a, b, x)
        lo, hi = utils.beta_equal_tailed_interval(a, b, coverage)
        self.assertEqual(coverage.shape, (n, m, k))
        self.assertTrue(np.all(
            np.isclose(lo, x) | np.isclose(hi, x)
        ))


class BetaHighestDensityCoverageTestCase(unittest.TestCase):
    """Test ersa.utils.beta_highest_density_coverage."""

    @pytest.mark.level(1)
    def test_beta_highest_density_coverage(self):
        # Test when a and b are scalars.
        for a in [1., 2., 3.]:
            for b in [1., 2., 3.]:
                if a == 1. and b == 1.:
                    # No highest density interval exists when a <= 1 and b <= 1.
                    continue
                # when x is a scalar.
                for x in [0.25, 0.50, 0.75]:
                    coverage = utils.beta_highest_density_coverage(a, b, x)
                    lo, hi = utils.beta_highest_density_interval(a, b, coverage)
                    self.assertEqual(coverage.shape, ())
                    self.assertTrue(np.all(
                        np.isclose(lo, x) | np.isclose(hi, x)
                    ))
                # when x is an array.
                k = 5
                x = np.random.rand(k)
                coverage = utils.beta_highest_density_coverage(a, b, x)
                lo, hi = utils.beta_highest_density_interval(a, b, coverage)
                self.assertEqual(coverage.shape, (k,))
                self.assertTrue(np.all(
                    np.isclose(lo, x) | np.isclose(hi, x)
                ))
        # Test when a and b are 1D arrays.
        n = 3
        a = np.arange(1, n + 1)
        b = np.arange(n + 1, 1, -1)
        #   when x is a scalar.
        for x in [0.25, 0.50, 0.75]:
            coverage = utils.beta_highest_density_coverage(a, b, x)
            lo, hi = utils.beta_highest_density_interval(a, b, coverage)
            self.assertEqual(coverage.shape, (n,))
            self.assertTrue(np.all(
                np.isclose(lo, x) | np.isclose(hi, x)
            ))
        #   when x is an array.
        x = np.random.rand(n)
        coverage = utils.beta_highest_density_coverage(a, b, x)
        lo, hi = utils.beta_highest_density_interval(a, b, coverage)
        self.assertEqual(coverage.shape, (n,))
        self.assertTrue(np.all(
            np.isclose(lo, x) | np.isclose(hi, x)
        ))
        # Test when a and b are 2D arrays.
        n, m = 3, 2
        a = np.arange(1, n * m + 1).reshape(n, m)
        b = np.arange(n * m + 1, 1, -1).reshape(n, m)
        #   when x is a scalar.
        for x in [0.25, 0.50, 0.75]:
            coverage = utils.beta_highest_density_coverage(a, b, x)
            lo, hi = utils.beta_highest_density_interval(a, b, coverage)
            self.assertEqual(coverage.shape, (n, m))
            self.assertTrue(np.all(
                np.isclose(lo, x) | np.isclose(hi, x)
            ))
        #   when x is an array.
        x = np.random.rand(n, m)
        coverage = utils.beta_highest_density_coverage(a, b, x)
        lo, hi = utils.beta_highest_density_interval(a, b, coverage)
        self.assertEqual(coverage.shape, (n, m))
        self.assertTrue(np.all(
            np.isclose(lo, x) | np.isclose(hi, x)
        ))
        # Test when a and b broadcast over each other.
        n, m = 3, 2
        a = np.arange(1, n + 1).reshape(n, 1)
        b = np.arange(m + 1, 1, -1).reshape(1, m)
        #   when x is a scalar.
        for x in [0.25, 0.50, 0.75]:
            coverage = utils.beta_highest_density_coverage(a, b, x)
            lo, hi = utils.beta_highest_density_interval(a, b, coverage)
            self.assertEqual(coverage.shape, (n, m))
            self.assertTrue(np.all(
                np.isclose(lo, x) | np.isclose(hi, x)
            ))
        #   when x is an array.
        x = np.random.rand(n, m)
        coverage = utils.beta_highest_density_coverage(a, b, x)
        lo, hi = utils.beta_highest_density_interval(a, b, coverage)
        self.assertEqual(coverage.shape, (n, m))
        self.assertTrue(np.all(
            np.isclose(lo, x) | np.isclose(hi, x)
        ))
        # Test when x broadcasts over a and b.
        #   when a and b have the same shape.
        n = 3
        a = np.arange(1, n + 1)[:, None]
        b = np.arange(n + 1, 1, -1)[:, None]
        k = 5
        x = np.random.rand(k)[None, :]
        coverage = utils.beta_highest_density_coverage(a, b, x)
        lo, hi = utils.beta_highest_density_interval(a, b, coverage)
        self.assertEqual(coverage.shape, (n, k))
        self.assertTrue(np.all(
            np.isclose(lo, x) | np.isclose(hi, x)
        ))
        #   when a and b broadcast over each other.
        n, m = 3, 2
        a = np.arange(1, n + 1).reshape(n, 1)[..., None]
        b = np.arange(m + 1, 1, -1).reshape(1, m)[..., None]
        k = 5
        x = np.random.rand(k)[None, None, :]
        coverage = utils.beta_highest_density_coverage(a, b, x)
        lo, hi = utils.beta_highest_density_interval(a, b, coverage)
        self.assertEqual(coverage.shape, (n, m, k))
        self.assertTrue(np.all(
            np.isclose(lo, x) | np.isclose(hi, x)
        ))


class BinomialConfidenceIntervalTestCase(unittest.TestCase):
    """Test ersa.utils.binomial_confidence_interval."""

    def test_binomial_confidence_interval(self):
        for n_successes, n_total, confidence, (lo_expected, hi_expected) in [
                # n_total == 1
                ( 0,  1, 0.0, (0.0000, 0.5000)),
                ( 0,  1, 0.5, (0.0000, 0.7500)),
                ( 0,  1, 1.0, (0.0000, 1.0000)),
                ( 1,  1, 0.0, (0.5000, 1.0000)),
                ( 1,  1, 0.5, (0.2500, 1.0000)),
                ( 1,  1, 1.0, (0.0000, 1.0000)),
                # n_successes == 0
                ( 0, 10, 0.0, (0.0000, 0.0670)),
                ( 0, 10, 0.5, (0.0000, 0.1295)),
                ( 0, 10, 1.0, (0.0000, 1.0000)),
                # 0 < n_successes < n_total
                ( 5, 10, 0.0, (0.4517, 0.5483)),
                ( 5, 10, 0.5, (0.3507, 0.6493)),
                ( 5, 10, 1.0, (0.0000, 1.0000)),
                # n_successes == n_total
                (10, 10, 0.0, (0.9330, 1.0000)),
                (10, 10, 0.5, (0.8705, 1.0000)),
                (10, 10, 1.0, (0.0000, 1.0000)),
        ]:
            lo_actual, hi_actual = utils.binomial_confidence_interval(
                n_successes, n_total, confidence,
            )
            self.assertAlmostEqual(lo_actual, lo_expected, places=3)
            self.assertAlmostEqual(hi_actual, hi_expected, places=3)

    def test_binomial_confidence_interval_broadcasts(self):
        # 1D array x scalar x scalar
        lo, hi = utils.binomial_confidence_interval(
            n_successes=[0, 5, 10],
            n_total=10,
            confidence=0.5,
        )
        self.assertTrue(np.allclose(
            lo,
            [0.0000, 0.3507, 0.8705],
            atol=5e-4,
        ))
        self.assertTrue(np.allclose(
            hi,
            [0.1295, 0.6493, 1.0000],
            atol=5e-4,
        ))
        # scalar x 1D array x scalar
        lo, hi = utils.binomial_confidence_interval(
            n_successes=0,
            n_total=[1, 10],
            confidence=0.5,
        )
        self.assertTrue(np.allclose(
            lo,
            [0.0000, 0.0000],
            atol=5e-4,
        ))
        self.assertTrue(np.allclose(
            hi,
            [0.7500, 0.1295],
            atol=5e-4,
        ))
        # scalar x scalar x 1D array
        lo, hi = utils.binomial_confidence_interval(
            n_successes=5,
            n_total=10,
            confidence=[0.0, 0.5, 1.0],
        )
        self.assertTrue(np.allclose(
            lo,
            [0.4517, 0.3507, 0.0000],
            atol=5e-4,
        ))
        self.assertTrue(np.allclose(
            hi,
            [0.5483, 0.6493, 1.0000],
            atol=5e-4,
        ))

    def test_binomial_confidence_interval_is_symmetric(self):
        for n_successes, n_total in [
                (  0,   1),
                (  0, 100),
                ( 25, 100),
                ( 50, 100),
        ]:
            for confidence in [0.00, 0.25, 0.50, 0.75, 1.00]:
                lo1, hi1 = utils.binomial_confidence_interval(
                    n_successes, n_total, confidence,
                )
                lo2, hi2 = utils.binomial_confidence_interval(
                    n_total - n_successes, n_total, confidence,
                )
                self.assertAlmostEqual(lo1, 1 - hi2)
                self.assertAlmostEqual(hi1, 1 - lo2)
