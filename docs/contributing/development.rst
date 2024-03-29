===========
Development
===========
We use the following tools and guidelines when developing opda.

.. admonition:: Before contributing to opda
   :class: caution

   Before contributing to opda, it's a good idea to discuss in an issue
   what you'd like to do. A pull request might not get accepted. You can
   save effort by discussing things beforehand and reducing the chance
   of this outcome.

Make sure you've installed all :ref:`optional dependencies
<tutorial/setup:Optional Dependencies>` and :ref:`python versions
<tutorial/setup:Python Versions>` necessary for development.

Run the full validation suite via `nox
<https://nox.thea.codes/en/stable/>`_:

.. code-block:: console

   $ pip install --editable .[ci]
   $ nox

Run the full suite on every commit.

You can find more on specific topics below.


Tests
=====
Run tests with `pytest <https://docs.pytest.org/>`_:

.. code-block:: console

   $ pytest

Some tests use randomness. For reproducibility, the random seed prints
when a test fails if the log level is at least :py:data:`~logging.INFO`
(the default).

Tests are organized into levels. Lower levels run faster and are
suitable for quick feedback during development. To run the tests at and
below a specific level, use the ``--level`` option:

.. code-block:: console

   $ pytest --level 2

Tests up to level 0 are run by default. Tests without a specified level
are always run. To run all levels, use the ``--all-levels`` option:

.. code-block:: console

   $ pytest --all-levels

You can also use `nox <https://nox.thea.codes/en/stable/>`_ to run the
tests (e.g., in continuous integration):

.. code-block:: console

   $ nox --session test


Lint
====
Lint the repository using `ruff <https://docs.astral.sh/ruff/>`_:

.. code-block:: console

   $ ruff check .

Use ``ruff check --watch .`` to continually lint the repository with
updates on file changes.

This project does *not* use a formatter. Basic stylistic conventions are
enforced by the linter; otherwise, style should be used to maximize the
readability and communicate the intent of the code.

The linter can automatically fix many errors it identifies, which can be
helpful for formatting the more rote stylistic issues:

.. code-block:: console

   $ ruff check --fix .

For continuous integration, run the linter via `nox
<https://nox.thea.codes/en/stable/>`_:

.. code-block:: console

   $ nox --session lint

You can also use nox to verify that the repository conforms
to its target support policy for Python and core dependency versions:

.. code-block:: console

   $ nox --session support


Docs
====
Build the docs with `Sphinx
<https://www.sphinx-doc.org/en/master/index.html>`_.

First, generate the API reference documentation:

.. code-block:: console

   $ rm -rf docs/reference/  # delete existing files if necessary
   $ SPHINX_APIDOC_OPTIONS='members' \
     sphinx-apidoc \
       --separate \
       --no-toc \
       --maxdepth 1 \
       --module-first \
       --output-dir docs/reference/ \
       src/opda/

Then, build the documentation:

.. code-block:: console

    $ sphinx-build \
        --jobs auto \
        -W \
        --keep-going \
        -d "docs/_build/doctrees/" \
        -b html \
        docs/ docs/_build/html/

Finally, serve the documentation locally using Python's
:py:mod:`http.server`:

.. code-block:: console

   $ python -m http.server --directory docs/_build/html/

Now, you can navigate in your browser to the printed URL in order to
view the docs.

To validate the documentation, check for broken links using
:py:mod:`~sphinx.builders.linkcheck`:

.. code-block:: console

    $ sphinx-build \
        --jobs auto \
        -W \
        --keep-going \
        -d "docs/_build/doctrees/" \
        -b linkcheck \
        docs/ docs/_build/linkcheck/

And test the documentation's correctness by executing examples as
:py:mod:`doctests <doctest>`:

.. code-block:: console

   $ pytest \
       --doctest-modules \
       --doctest-glob "**/*.rst" \
       -- README.rst docs/ src/

``--doctest-modules`` runs doctests from the docstrings in any python
modules, while ``--doctest-globs "**/*.rst"`` searches reStructuredText
files for doctests. The arguments (``README.rst docs/ src/``) ensure
pytest looks at the right paths for these tests.

In continuous integration, we build and test the documentation via
`nox <https://nox.thea.codes/en/stable/>`_:

.. code-block:: console

   $ nox --session docs


Packaging
=========
Before building the package, you must preprocess
:source-file:`pyproject.toml` to remove parts specific to local
installations. The easiest way to do this is to run the ``package``
session using `nox <https://nox.thea.codes/en/stable/>`_:

.. code-block:: console

   $ nox --session package

After running this session, you'll find the ``dist/`` directory
containing the built distributions. See the ``package`` session in
:source-file:`noxfile.py` for further details.

You can test the package against all supported versions of Python and
the core dependencies using the ``testpackage`` nox session.

.. code-block:: console

   $ nox --session testpackage -- dist/*.whl

It takes one positional argument: the package to test. The separator for
options and arguments, ``--``, is required.

As there are many possible combinations of supported versions, running
all of these tests will take a long time. You might prefer to run a
particular combination instead:

.. code-block:: console

   $ nox \
       --session "testpackage-3.11(numpy='1.26', scipy='1.12')" \
       -- \
       dist/*.whl

Use ``nox --list`` to see all supported combinations.


Conventions
===========
This project uses the following unique conventions to help with
maintenance.

``# backwards compatibility``
  All backwards compatibility code should have a ``# backwards
  compatibility (${DEPENDENCY} < ${VERSION})`` comment either before:

  .. code-block:: python

     # backwards compatibility (Python < 3.11)

     import sys
     ...

  or on the same line:

  .. code-block:: python

     session.install("pip >= 21.2")  # backwards compatibility (pip < 21.2)

  That way, when dependencies are updated, it's easy to find and
  remove unnecessary backwards compatibility code.
``# build: local-only``
  Some lines in :source-file:`pyproject.toml` should only be used for
  local builds, and not the distribution package. Mark these lines
  with a ``# build: local-only`` comment at the end, or place these
  lines after the ``# -- build: local-only -----`` header.
Pull request conventions
  Merge new changes via pull requests. Use the branch name for the
  pull request's name. Merge commit messages should match git's
  default: ``"Merge branch '${BRANCH}'"`` with no further description.
