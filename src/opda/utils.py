"""Utilities"""

import numpy as np
from scipy import stats

from opda import exceptions


def sort_by_first(*args):
    """Return the arrays sorted by the first array.

    Parameters
    ----------
    *args : arrays, required
        The arrays to sort.

    Returns
    -------
    arrays
        The arrays sorted by the first array. Thus, the first array will
        be sorted and the other arrays will have their elements permuted
        the same way as the elements from the first array.
    """
    # Validate the arguments.
    args = tuple(map(np.array, args))
    if any(arg.shape != args[0].shape for arg in args):
        raise ValueError(
            'All argument arrays must have the same shape.'
        )

    # Return sorted copies of the arrays.
    if len(args) == 0:
        return ()

    sorting = np.argsort(args[0])
    return tuple(arg[sorting] for arg in args)


def dkw_epsilon(n, confidence):
    """Return epsilon from the Dvoretzky-Kiefer-Wolfowitz inequaltiy.

    The Dvoretzky-Kiefer-Wolfowitz inequality states that a confidence
    interval for the CDF is given by the empirical CDF plus or minus:

    .. math::

       \\epsilon = \\sqrt{\\frac{\\log \\frac{2}{\\alpha}}{2n}}

    Where :math:`1 - \\alpha` is the coverage.

    Parameters
    ----------
    n : positive int, required
        The number of samples.
    confidence : float between 0 and 1, required
        The desired confidence or coverage.

    Returns
    -------
    float
        The epsilon for the Dvoretzky-Kiefer-Wolfowitz inequality.
    """
    # Validate the arguments.
    n = np.array(n)
    if n <= 0:
        raise ValueError('n must be positive.')

    confidence = np.array(confidence)
    if np.any((confidence < 0.) | (confidence > 1.)):
        raise ValueError('confidence must be between 0 and 1.')

    # Compute the DKW epsilon.
    return np.sqrt(
        np.log(2. / (1. - confidence))
        / (2. * n)
    )


def beta_equal_tailed_interval(a, b, coverage):
    """Return an interval containing ``coverage`` of the probability.

    For the beta distribution with parameters ``a`` and ``b``, return
    the equal-tailed interval that contains ``coverage`` of the
    probability mass.

    Parameters
    ----------
    a : positive float or array of floats, required
        The alpha parameter for the beta distribution.
    b : positive float or array of floats, required
        The beta parameter for the beta distribution.
    coverage : float or array of floats between 0 and 1, required
        The desired coverage for the returned intervals.

    Returns
    -------
    float or array of floats, float or array of floats
        A pair of floats or arrays of floats with the shape determined
        by broadcasting ``a``, ``b``, and ``coverage`` together. The
        first returned value gives the lower bound and the second the
        upper bound for the equal-tailed intervals.
    """
    # Validate the arguments.
    a = np.array(a)
    if np.any(a <= 0):
        raise ValueError('a must be positive.')

    b = np.array(b)
    if np.any(b <= 0):
        raise ValueError('b must be positive.')

    coverage = np.array(coverage)
    if np.any((coverage < 0.) | (coverage > 1.)):
        raise ValueError('coverage must be between 0 and 1.')

    # Compute the equal-tailed interval.
    beta = stats.beta(a, b)

    x = beta.ppf((1. - coverage) / 2.)
    y = beta.ppf((1. + coverage) / 2.)

    return x, y


def beta_highest_density_interval(a, b, coverage, atol=1e-10):
    """Return an interval containing ``coverage`` of the probability.

    For the beta distribution with parameters ``a`` and ``b``, return
    the shortest interval that contains ``coverage`` of the
    probability mass. Note that the highest density interval only
    exists if at least one of ``a`` or ``b`` is greater than 1.

    Parameters
    ----------
    a : positive float or array of floats, required
        The alpha parameter for the beta distribution.
    b : positive float or array of floats, required
        The beta parameter for the beta distribution.
    coverage : float or array of floats between 0 and 1, required
        The desired coverage for the returned intervals.

    Returns
    -------
    float or array of floats, float or array of floats
        A pair of floats or arrays of floats with the shape determined
        by broadcasting ``a``, ``b``, and ``coverage`` together. The
        first returned value gives the lower bound and the second the
        upper bound for the intervals.
    """
    # NOTE: Given the lower endpoint of the interval, ``x``, we can immediately
    # compute the upper one as: ``beta.ppf(beta.cdf(x) + coverage)``. Below the
    # interval, the density of the lower endpoint is less than the upper
    # one. Above the interval, it's the reverse. Thus, we can find the lower
    # endpoint via binary search.
    #
    # The beta distribution only has a mode when ``a`` or ``b`` is greater than
    # 1. If both are greater than 1, the mode is in the interior of [0, 1]. If
    # ``a`` or ``b`` is less than or equal to 1, then the mode is on the
    # boundary. If ``a`` and ``b`` are less than or equal to 1, then the mode
    # is not unique and the highest density region is not necessarily an
    # interval.

    # Validate the arguments.
    a = np.array(a)
    if np.any(a <= 0):
        raise ValueError('a must be positive.')

    b = np.array(b)
    if np.any(b <= 0):
        raise ValueError('b must be positive.')

    coverage = np.array(coverage)
    if np.any((coverage < 0.) | (coverage > 1.)):
        raise ValueError('coverage must be between 0 and 1.')

    if np.any((a <= 1.) & (b <= 1.)):
        raise ValueError(
            f'Either a ({a}) or b ({b}) must be greater than one to have'
            f' a highest density interval.'
        )

    # Compute the highest density interval.
    beta = stats.beta(a, b)

    mode = np.clip((a - 1) / (a + b - 2), 0., 1.)

    # Initialize bounds.
    x_lo = beta.ppf(np.maximum(beta.cdf(mode) - coverage, 0.))
    x_hi = np.minimum(mode, beta.ppf(1. - coverage))

    # Binary search for the lower endpoint.
    # NOTE: Each iteration cuts the bracket's length in half, so run
    # enough iterations so that max(x_hi - x_lo) / 2**n_iter < atol.
    n_iter = int(np.ceil(
        # Even when the maximum bracket length is below atol, run at
        # least 1 iteration in order to compute the midpoint and y.
        np.log2(max(2, np.max(x_hi - x_lo) / atol))
    ))
    for _ in range(n_iter):
        x = (x_lo + x_hi) / 2.
        y = beta.ppf(np.clip(beta.cdf(x) + coverage, 0., 1.))
        # NOTE: For small values of coverage, y (the upper confidence
        # limit) can fall below x (the lower confidence limit) when
        # computed as above due to discretization/rounding errors, so
        # fix that below.
        y = np.clip(y, x, 1.)

        # NOTE: Inline the unnormalized beta density rather than using
        # scipy.stats.beta.pdf because:
        #   * scipy.stats.beta.pdf is not monotonic from the
        #     boundaries to the mode. This bug causes the binary
        #     search to fail for small coverages.
        #   * The unnormalized version is significantly faster to
        #     compute.
        # In addition, raise the density to the 1/(b-1) power. This
        # transformation is monotonic, so it doesn't affect the points at
        # which the density is equal; however, it means we can avoid using
        # an expensive power operation on the large arrays.
        with np.errstate(divide='ignore'):
            x_pdf = x**((a-1)/(b-1)) * (1-x)
            y_pdf = y**((a-1)/(b-1)) * (1-y)

        x_lo = np.where(x_pdf <= y_pdf, x, x_lo)
        x_hi = np.where(x_pdf >= y_pdf, x, x_hi)

    return x, y


def beta_equal_tailed_coverage(a, b, x):
    """Return the coverage of the smallest interval containing ``x``.

    For the beta distribution with parameters ``a`` and ``b``, return
    the coverage of the smallest equal-tailed interval containing
    ``x``. See the related function: ``beta_equal_tailed_interval``.

    Parameters
    ----------
    a : positive float or array of floats, required
        The alpha parameter for the beta distribution.
    b : positive float or array of floats, required
        The beta parameter for the beta distribution.
    x : float or array of floats between 0 and 1, required
        The points defining the minimal equal-tailed intervals whose
        coverage to return.

    Returns
    -------
    float or array of floats
        A float or array of floats with shape determined by broadcasting
        ``a``, ``b``, and ``x`` together. The values represent the
        coverage of the minimal equal-tailed interval containing the
        corresponding value from ``x``.
    """
    a = np.array(a)
    b = np.array(b)
    x = np.array(x)

    beta = stats.beta(a, b)

    return 2 * np.abs(0.5 - beta.cdf(x))


def beta_highest_density_coverage(a, b, x, atol=1e-10):
    """Return the coverage of the smallest interval containing ``x``.

    For the beta distribution with parameters ``a`` and ``b``, return
    the coverage of the smallest highest density interval containing
    ``x``. See the related function: ``beta_highest_density_interval``.

    Parameters
    ----------
    a : float or array of floats, required
        The alpha parameter for the beta distribution.
    b : float or array of floats, required
        The beta parameter for the beta distribution.
    x : float or array of floats, required
        The points defining the minimal intervals whose coverage to
        return.

    Returns
    -------
    float or array of floats
        A float or array of floats with shape determined by broadcasting
        ``a``, ``b``, and ``x`` together. The values represent the
        coverage of the minimal highest density interval containing the
        corresponding value from ``x``.
    """
    # Use binary search to find the coverage of the highest density interval
    # containing x.
    a = np.array(a)
    b = np.array(b)
    x = np.array(x)

    if np.any((a <= 1.) & (b <= 1.)):
        raise ValueError(
            f'Either a ({a}) or b ({b}) must be greater than one to have'
            f' a highest density interval.'
        )

    beta = stats.beta(a, b)

    mode = np.clip((a - 1) / (a + b - 2), 0., 1.)
    x_is_lower_end = x < mode
    # NOTE: Inline the unnormalized beta density rather than using
    # scipy.stats.beta.pdf because:
    #   * scipy.stats.beta.pdf is not monotonic from the
    #     boundaries to the mode. This bug causes the binary
    #     search to fail for small coverages.
    #   * The unnormalized version is significantly faster to
    #     compute.
    # In addition, raise the density to the 1/(b-1) power. This
    # transformation is monotonic, so it doesn't affect the points at
    # which the density is equal; however, it means we can avoid using
    # a power operation on the large array of y's, which makes the
    # function significantly faster.
    with np.errstate(divide='ignore'):
        x_pdf = x**((a-1)/(b-1)) * (1-x)

    # Initialize bounds.
    y_lo = np.where(x_is_lower_end, mode, 0.)
    y_hi = np.where(x_is_lower_end, 1., mode)

    # Binary search for the other end.
    # NOTE: Each iteration cuts the bracket's length in half, so run
    # enough iterations so that max(y_hi - y_lo) / 2**n_iter < atol.
    n_iter = int(np.ceil(
        # Even when the maximum bracket length is below atol, run at
        # least 1 iteration in order to compute the midpoint and figure
        # out if x or y is the lower end.
        np.log2(max(2, np.max(y_hi - y_lo) / atol))
    ))
    for _ in range(n_iter):
        y = (y_lo + y_hi) / 2.

        with np.errstate(divide='ignore'):
            y_is_lo = x_is_lower_end == (x_pdf < y**((a-1)/(b-1)) * (1-y))

        y_lo = np.where(y_is_lo, y, y_lo)
        y_hi = np.where(~y_is_lo, y, y_hi)

    x, y = np.where(x_is_lower_end, x, y), np.where(x_is_lower_end, y, x)

    return beta.cdf(y) - beta.cdf(x)


def binomial_confidence_interval(n_successes, n_total, confidence):
    """Return a confidence interval for the binomial distribution.

    Given ``n_successes`` out of ``n_total``, return an equal-tailed
    Clopper-Pearson confidence interval with coverage ``confidence``.

    Parameters
    ----------
    n_successes : int or array of ints, required
        An int or array of ints with each entry denoting the number of
        successes in a sample. Must be broadcastable with ``n_total``.
    n_total : int or array of ints, required
        An int or array of ints with each entry denoting the total
        number of observations in a sample. Must be broadcastable with
       ``n_successes``.
    confidence : float or array of floats, required
        A float or array of floats between zero and one denoting the
        desired confidence for each confidence interval. Must be
        broadcastable with ``n_successes`` broadcasted with ``n_total``.

    Returns
    -------
    array of floats, array of floats
        A possibly scalar array of floats representing the lower
        confidence bounds and a possibly scalar array of floats
        representing the upper confidence bounds.

    Notes
    -----
    The Clopper-Pearson interval [1]_ does not account for the
    binomial distribution's discreteness. This lack of correction
    causes Clopper-Pearson intervals to be conservative. In addition,
    this function implements an equal-tailed version of the
    Clopper-Pearson interval which can be very conservative when the
    number of successes is zero or the total number of observations.

    References
    ----------
    .. [1] Clopper, C. and Pearson, E. S., "The Use of Confidence or
       Fiducial Limits Illustrated in the Case of the Binomial"
       (1934). Biometrika. 26 (4): 404–413. doi:10.1093/biomet/26.4.404.
    """
    n_successes = np.array(n_successes)
    n_total = np.array(n_total)
    confidence = np.array(confidence)

    if np.any(n_successes < 0):
        raise ValueError(
            f'n_successes ({n_successes}) must be greater than or equal'
            f' to 0.'
        )
    if np.any(n_total < 1):
        raise ValueError(
            f'n_total ({n_total}) must be greater than or equal to 1.'
        )
    if np.any((confidence < 0.) | (confidence > 1.)):
        raise ValueError(
            f'confidence ({confidence}) must be between 0 and 1.'
        )
    if np.any(n_successes > n_total):
        raise ValueError(
            f'n_successes ({n_successes}) must be less than or equal to'
            f' n_total ({n_total}).'
        )

    lo = np.where(
        n_successes == 0,
        0.,
        stats.beta(
            n_successes,
            n_total - n_successes + 1,
        ).ppf((1 - confidence)/2),
    )
    hi = np.where(
        n_successes == n_total,
        1.,
        stats.beta(
            n_successes + 1,
            n_total - n_successes,
        ).ppf(1 - (1 - confidence)/2),
    )

    return lo, hi
