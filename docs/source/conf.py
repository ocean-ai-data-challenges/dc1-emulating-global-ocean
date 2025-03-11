# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'dc1'
copyright = '2025, Kamel Ait Mohand, Guillermo Cossio'
author = 'Kamel Ait Mohand, Guillermo Cossio'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
]
autosummary_generate = True

templates_path = ['_templates']
exclude_patterns = []

# MyST Options
# https://myst-parser.readthedocs.io/en/latest/configuration.html

myst_heading_anchors = 2
myst_links_external_new_tab = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']