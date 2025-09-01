# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
import os
import datetime
sys.path.insert(0, os.path.abspath(".."))

project = 'GeoProb-Pipe'
copyright = f'{datetime.date.today().year}, WSRL & WSHD'
author = 'WSRL & WSHD'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autosummary",
    "autoapi.extension",
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinx_mdinclude",
    "sphinxcontrib.jquery",
    "sphinxcontrib.bibtex",
]

bibtex_bibfiles = 'bibliography.bib'

source_suffix = [".rst", ".md"]

templates_path = ['_templates']
autosummary_generate = True
add_module_names = False
autoapi_type = "python"
autodoc_typehints = "description"
autoapi_dirs = ["../geoprob_pipe"]
autoapi_template_dir = "autoapi/templates"
autoapi_output_dir = "autoapi"
autoapi_keep_files = True
autoapi_python_class_content = "both"
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_theme_options = {
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 5,
    "titles_only": True,
    "display_version": True,
}


# -- Hooks ---------------------------------------------------------------------

# def shorten_titles(app, pagename, templatename, context, doctree):
#     pass
#
# def setup(app):
#     app.connect("html-page-context", shorten_titles)
#     pass
def setup(app):
    def on_build_finished(app, exception):
        if exception is None:
            print("SUCCESSFULLY BUILD!")
        else:
            print("NOT SUCCESSFULLY BUILD!")

    app.connect("build-finished", on_build_finished)
