import pkg_resources

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# sys.path.insert(0, os.path.abspath('.'))

project = "yamcs-pymdb"
copyright = "2024, Space Applications Services"
author = "Yamcs Team"

# The short X.Y version
version = ""

# The full version, including alpha/beta/rc tags
dist = pkg_resources.get_distribution("yamcs-pymdb")
release = dist.version

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.fulltoc",
]

source_suffix = ".rst"
master_doc = "index"
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "sphinx"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "nature"

latex_elements = {
    "papersize": "a4paper",
    "figure_align": "htbp",
}

latex_documents = [
    (
        master_doc,
        "pymdb.tex",
        "Yamcs PyMDB",
        "Space Applications Services",
        "manual",
    ),
]

autoclass_content = "both"
autodoc_class_signature = "separated"
autodoc_default_options = {
    # "member-order": "bysource",
    "undoc-members": True,
    "show-inheritance": True,
    "inherited-members": True,
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}
