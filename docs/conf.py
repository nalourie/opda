"""Configure Sphinx to build the documentation.

For the full list of built-in configuration values, see Sphinx's documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

import pathlib
import re
import sys
import warnings

# backwards compatibility

if sys.version_info < (3, 11, 0):
    import tomli as tomllib
else:
    import tomllib


# -- Setup -------------------------------------------------------------------

# constants

ROOT = pathlib.Path(__file__).resolve().parent.parent

PYPROJECT = tomllib.loads(ROOT.joinpath("pyproject.toml").read_text())

# global variables

rst_epilog = ""

# environment setup

sys.path.append(str(ROOT / "docs" / "_ext"))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# sphinx project metadata
project = PYPROJECT["project"]["name"]
author = PYPROJECT["project"]["authors"][0]["name"]
project_copyright = f"2023, {author}"
release = PYPROJECT["project"]["version"]
version = re.match(r"^(\d+\.\d+)\.\d+$", release).groups()[0]

# custom project metadata
description = PYPROJECT["project"]["description"]
minimum_python_version = re.match(
    r"^>=\s*(\d+\.\d+)$",
    PYPROJECT["project"]["requires-python"],
).groups()[0]

documentation_url = PYPROJECT["project"]["urls"]["Documentation"]
issues_url = PYPROJECT["project"]["urls"]["Issues"]
source_url = PYPROJECT["project"]["urls"]["Source"]

# custom substitutions
rst_epilog += f"""
.. |description| replace:: {description}
.. |minimum_python_version| replace:: {minimum_python_version}
"""

# social and search metadata
rst_epilog += f"""
.. meta::
   :property=og:title: {project}
   :property=og:type: website
   :property=og:image: {documentation_url}/_static/logo.png
   :property=og:image:alt: {project} logo
   :property=og:url: {documentation_url}
   :property=og:description: {description}
   :property=og:locale: en_US
   :property=og:site_name: {project}
"""


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.autosectionlabel",
    # sphinx.ext.coverage is unnecessary as missing docs are found by ruff.
    # sphinx.ext.doctest is unnecessary as doctests are run via pytest.
    "sphinx.ext.extlinks",
    "sphinx.ext.mathjax",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "numpydoc",
    "matplotlib.sphinxext.plot_directive",
    "toctreelinks",
]

templates_path = ["_templates"]
exclude_patterns = []

primary_domain = None
default_role = None

nitpicky = True

language = "en"

# NOTE: Treat all warnings as errors in documentation examples.
warnings.resetwarnings()
warnings.filterwarnings("error")


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_theme_options = {
    "announcement": None,
    "top_of_page_button": None,
}

html_title = f"{project} <small>v{release}</small>"

html_logo = "_static/logo.png"
html_favicon = "_static/favicon.ico"

html_static_path = ["_static"]

html_domain_indices = False

html_copy_source = False
html_show_sourcelink = False

htmlhelp_basename = "opdadoc"


# -- Options for the linkcheck builder ---------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-the-linkcheck-builder

linkcheck_anchors_ignore_for_url = [
    # linkcheck fails to validate anchor tags in GitHub READMEs, see
    # https://github.com/sphinx-doc/sphinx/issues/9016.
    r"https://github.com/.*",
]


# -- Extension configuration -------------------------------------------------

# sphinx.ext.autodoc
autodoc_default_options = {
    "member-order": "bysource",
    "no-value": True,
}

# sphinx.ext.autosectionlabel
autosectionlabel_prefix_document = True

# sphinx.ext.extlinks
extlinks = {
    "source-file": (f"{source_url}/blob/main/%s", "%s"),
    "source-dir": (f"{source_url}/tree/main/%s", "%s"),
}
extlinks_detect_hardcoded_links = True

# sphinx.ext.intersphinx
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "matplotlib": ("https://matplotlib.org/stable", None),
    "neps": ("https://numpy.org/neps", None),
    "numpy": ("https://numpy.org/devdocs", None),
    "scipy": ("https://docs.scipy.org/doc/scipy", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}

# numpydoc
numpydoc_use_plots = True
numpydoc_show_class_members = False
numpydoc_show_inherited_class_members = False
numpydoc_class_members_toctree = False
numpydoc_validation_checks = {
    "all",   # Enable all checks by default, then disable ones below.
    "ES01",  # No extended summary found.
    "EX01",  # No examples section found.
    "GL01",  # Summary should start in line after opening quotes.
    "SA01",  # See Also section not found.
}
numpydoc_validation_overrides = {
    # Return value has no description.
    "RT03": [
        r"Returns\n"
        r"-------\n"
        r"None\n?$",
    ],
}

# matplotlib.sphinxext.plot_directive
plot_include_source = True
plot_html_show_source_link = False
plot_pre_code = (
    f"from matplotlib.pyplot import style as _mpl_style\n"
    f"_mpl_style.use('{ROOT / 'docs' / 'docs.mplstyle'}')\n"
)

plot_formats = [("png", 96)]
plot_html_show_formats = False

# toctreelinks
toctreelinks_caption = "Links"
toctreelinks_urls = PYPROJECT["project"]["urls"]
