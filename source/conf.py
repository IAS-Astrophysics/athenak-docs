from __future__ import annotations

project = "AthenaK"
author = "AthenaK contributors"
copyright = "2026, AthenaK contributors"
release = "latest"

extensions = [
    "sphinx.ext.mathjax",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_title = "AthenaK documentation"
