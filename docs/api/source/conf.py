import os
import sys

sys.path.insert(0, os.path.abspath('../../..'))

project = 'Adoptive Market Crawler'
copyright = '2025, Development Team'
author = 'Development Team'
version = '1.1.0'
release = '1.1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
]

templates_path = ['_templates']
exclude_patterns = []
language = 'ja'

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
autodoc_docstring_signature = True
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None 