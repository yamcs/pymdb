from importlib.metadata import version as get_pkg_version

project = "Yamcs PyMDB"
copyright = "2026, Space Applications Services"
author = "Yamcs Team"

release = get_pkg_version("yamcs-pymdb")
version = release

source_suffix = ".rst"
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "sphinx"

extensions = [
    "sphinxcontrib.fulltoc",
    "sphinx.ext.intersphinx",
]

html_theme = "alabaster"
html_theme_options = {
    "fixed_sidebar": False,
    "show_powered_by": False,
    "font_family": "Helvetica,Arial,sans-serif",
    "font_size": "15px",
}
html_show_sourcelink = False

latex_elements = {
    "papersize": "a4paper",
    "preamble": r"""
\setcounter{tocdepth}{2}
\usepackage{colortbl}
""",
    "figure_align": "htbp",
}

latex_documents = [
    (
        "index",
        f"pymdb-{release}.tex",
        "Yamcs PyMDB",
        "Yamcs Team",
        "manual",
    ),
]

latex_show_pagerefs = True
latex_show_urls = "footnote"

latex_appendices = [
    "appendices/names",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}
