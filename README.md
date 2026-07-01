# AthenaK documentation

User-facing documentation for [AthenaK](https://github.com/IAS-Astrophysics/athenak),
built with [Sphinx](https://www.sphinx-doc.org/) and the
[Furo](https://pradyunsg.me/furo/) theme. This site is intended to replace the
project's GitHub wiki.

The published site is hosted on GitHub Pages:
<https://ias-astrophysics.github.io/athenak-docs/>.

## Building locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

sphinx-build -b html source build/html
```

Then open `build/html/index.html` in a browser. Alternatively, use `make html`.

## Contents

This first version covers:

- **Getting Started**: requirements, download, and build instructions.
- **Quickstart: Run a Sod Shock Tube**: a short end-to-end tutorial (compile, run,
  visualize).
- **Running**: running the code, the input file, outputs, analysis, and notes for
  specific machines.

## Continuous integration

The [`Docs` workflow](.github/workflows/docs.yml) runs on every push and pull request:

- **Build (strict)**: builds the site with `sphinx-build -W --keep-going`, so any
  Sphinx warning fails the check and broken docs cannot be merged.
- **Deploy**: on `main`, the built site is published to GitHub Pages.
