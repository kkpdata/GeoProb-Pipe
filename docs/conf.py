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
import os
import inflection
from bs4 import BeautifulSoup
from typing import Optional


class BColors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def should_be_reformatted(value: Optional[str]) -> bool:
    if value is None:
        return False
    if "geoprob_pipe" not in value:
        return False
    if value.split(sep=".").__len__() <= 1:
        return False
    return True


def reformat(value: str):
    return inflection.humanize(value.split(sep=".")[-1])


def simplify_anchor_text_in_file(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    changed = False

    # Hyperlinks
    for a in soup.find_all("a"):
        if not should_be_reformatted(a.string):
            continue
        a.string = reformat(a.string)
        changed = True

    # For navigation items
    for nav in soup.find_all("div", {"role": "navigation"}):
        for li in nav.find_all("li", class_="breadcrumb-item active"):
            if not should_be_reformatted(li.string):
                continue
            li.string = reformat(li.string)
            changed = True

    # For h1
    for h1 in soup.find_all("h1"):

        # Check if h1 to format
        if "geoprob_pipe." not in h1.contents[0]:
            continue

        # Reformat
        new_elements = []
        for element in h1.contents:
            if "geoprob_pipe." in element:
                new_elements.append(reformat(element.text))
                continue
            new_elements.append(element)

        # Update
        h1.clear()
        for item in new_elements:
            h1.append(item)
        changed = True

    if changed:
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(str(soup))


def run_post_processing():
    conf_dir = os.path.dirname(os.path.abspath(__file__))
    html_dir = os.path.join(conf_dir, "_build", "html")
    for root, _, files in os.walk(html_dir):
        for filename in files:
            if filename.endswith(".html"):
                file_path = os.path.join(root, filename)
                simplify_anchor_text_in_file(file_path)


project = "GeoProb-Pipe"
copyright = f"{datetime.date.today().year}, WSRL & WSHD"
author = "WSRL & WSHD"


# Get release version
import tomllib
import pathlib
pyproject_path = pathlib.Path(__file__).resolve().parents[1] / "pyproject.toml"
with pyproject_path.open("rb") as f:
    pyproject = tomllib.load(f)
release = pyproject["project"]["version"]


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autosummary",
    "autoapi.extension",
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinx_mdinclude",
    "sphinxcontrib.jquery",
    "sphinx.ext.napoleon",
    "sphinxcontrib.bibtex",
]

bibtex_bibfiles = ["bibliography.bib"]


source_suffix = [".rst", ".md"]

templates_path = ["_templates"]
autosummary_generate = True
add_module_names = False
autoapi_type = "python"
autodoc_typehints = "description"
autoapi_dirs = ["../geoprob_pipe"]
autoapi_template_dir = "autoapi/templates"
autoapi_output_dir = "autoapi"
autoapi_keep_files = True
autoapi_python_class_content = "both"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
numfig = True
numfig_format = {"figure": "Figuur %s"}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_theme_options = {
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 5,
    "titles_only": True,
    "display_version": True,
}
bibtex_ignore_labels = {
    "trw_2004)"
}

# -- Hooks ---------------------------------------------------------------------


# def shorten_titles(app, pagename, templatename, context, doctree):
#     pass
#
# def setup(app):
#     app.connect("html-page-context", shorten_titles)
#     pass
def setup(app):

    # noinspection PyUnusedLocal
    def on_build_finished(app_obj, exception):
        if exception is not None:
            print(
                BColors.WARNING,
                "Documentation build was not successful. The following exception was given. \n",
                exception,
                BColors.ENDC,
            )
            return
        run_post_processing()

    app.connect("build-finished", on_build_finished)
