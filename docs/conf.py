# -*- coding: utf-8 -*-
import sys
import os

ROOT_DIR = os.path.join(os.path.dirname(__file__), '../')


def extract_version():
    context = {}
    init_path = 'src_py/async_rest/__init__.py'
    try:
        with open(os.path.join(ROOT_DIR, init_path)) as fd:
            code = fd.read()
            exec(compile(code, init_path, "exec"), context)
        return context.get('__version__')
    except:
        return '0.0.1a0'

extensions = [
    'sphinxcontrib.httpdomain',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

project = u'async-rest'
copyright = u'All rights reserved. NetSach 2016.'

version = extract_version()
release = extract_version()

exclude_patterns = ['_build']

pygments_style = 'sphinx'

modindex_common_prefix = ['async-rest.']

try:
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
except:
    pass
html_static_path = ['_static']

htmlhelp_basename = 'async-rest-doc'

latex_elements = {
}

latex_documents = [
  ('index', 'async-rest.tex', u'async-rest Documentation',
   u'P.A. SCHEMBRI - Netsach 2016', 'manual'),
]
