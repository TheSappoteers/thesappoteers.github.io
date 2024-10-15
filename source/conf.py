# Configuration file for the Sphinx documentation builder.
import pydata_sphinx_theme
import os
import sys

# -- Project information -----------------------------------------------------
project = 'The SAPPOteers'
copyright = '2024, The SAPPOteers'
author = 'Ankit Bhandekar'

# -- General configuration ---------------------------------------------------
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("_ext"))  # Add this line for the timeline extension

extensions = [
    "sphinx_favicon",
    "timeline_directive",  # Add this line for the timeline extension
]

source_dir = 'source'
templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static', '_images']  # Add '_images' for flyer images
html_sidebars = {
  "**": []
}

html_title = "The SAPPOteers"
html_logo = '_static/logo.svg'
html_baseurl = 'https://thesappoteers.github.io/'
html_show_sourcelink = False

html_theme_options = {
    "logo": {
        "text": "The SAPPOteers",
        "image_dark": "_static/logo.svg",
        "alt_text": "The SAPPOteers",
    },
    "footer_end": ["combined_footer.html"],
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "navbar_persistent": [],
    "icon_links": [
        {
            "name": "Join the conversation on WhatsApp",
            "url": "https://chat.whatsapp.com/CgYkOZiabKv4fy38PAJTJp",
            "icon": "fa-brands fa-whatsapp",
        },
        {
            "name": "Share your ideas, suggestions and contribute on Github",
            "url": "https://github.com/TheSappoteers/thesappoteers.github.io",
            "icon": "fa-brands fa-github",
        },        
    ],
}

html_show_sphinx = False

html_context = {
    "default_mode": "light",
}

# -- Option for favicons -------------------------------------------------------
favicons = [
    "logo.svg"
]

# -- Additional files for timeline functionality -------------------------------
html_js_files = [
    'https://unpkg.com/vis-timeline@latest/standalone/umd/vis-timeline-graph2d.min.js',
]
html_css_files = [
    'https://unpkg.com/vis-timeline@latest/styles/vis-timeline-graph2d.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css',
    'custom.css',
    'basic.css',
]

def setup(app):
    pass  # Remove the previous setup function as we've moved its contents to html_css_files