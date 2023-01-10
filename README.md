# legendhpges

![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/legend-exp/legend-geom-hpges?logo=git)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/legend-exp/legend-geom-hpges/legendhpges/main?label=main%20branch&logo=github)](https://github.com/legend-exp/legend-geom-hpges/actions)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Codecov](https://img.shields.io/codecov/c/github/legend-exp/legend-geom-hpges?logo=codecov)](https://app.codecov.io/gh/legend-exp/legend-geom-hpges)
![GitHub issues](https://img.shields.io/github/issues/legend-exp/legend-geom-hpges?logo=github)
![GitHub pull requests](https://img.shields.io/github/issues-pr/legend-exp/legend-geom-hpges?logo=github)
![License](https://img.shields.io/github/license/legend-exp/legend-geom-hpges)
[![Read the Docs](https://img.shields.io/readthedocs/legend-geom-hpges?logo=readthedocs)](https://legend-geom-hpges.readthedocs.io)

Geometry management and builder package for LEGEND HPGE detectors using [pyg4ometry](https://pypi.org/project/pyg4ometry/)

## Quick start
```console
# Create, activate a virtualenv for local development
$ python3 -m venv env
$ source ./env/bin/activate

# Create editable install with development packages
(env) $ python3 -m pip install -e '.[all]'
...

# Run tests, coverage
(env) $ pytest
...

(env) $ pytest --cov=legendhpges
... edit/test/repeat ...

# Build/Check docs
(env) $ cd docs
(env) $ make
... open build/html/index.html in browser of your choice ..

# Run checks before committing
(env) $ pre-commit run --all-files
```
