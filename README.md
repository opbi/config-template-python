# config-template-python

the uni-directional config template repo for all downstream repos

## Use Cases

* __config template__: fork this repo to inherit the standardised configuration to start a new repo
* __config sync__: clone this template repo to the same parent folder of a project repo and run `just config`
* __shared lib__: clone this template repo to the same parent folder of a project repo and run `just shared`
* __repo specific configs__: explicitly annotated with comments and keep during merge
  * `# * <-- repo specific config`
  * `# * repo specific config -->`

## Setup

To start using the base configs, you will need to install the following system packages:

MacOs:
> packages: `brew install uv just watchexec`

Windows:
> git bash: `winget install --id Git.Git -e --source winget`
>
> packages: `scoop install uv just watchexec`

* [uv](https://github.com/astral-sh/uv) - python version & dependency/virtualenv manager `@1.8`
* [just](https://github.com/casey/just) - programmatic command runner `@1.25`
* [watchexec](https://github.com/watchexec/watchexec) - file watcher `@1.25`
* [bash](https://git-scm.com/downloads) - the shell for running just commands (available on MacOS by default)

Other tooling:

* [VSCode](https://code.visualstudio.com/download) - IDE for sharing extensions with configs
* [aws-connect](https://aws-admin.bp.com/cli/downloads) - BP AWS Token Broker CLI (not used after migrating to Azure)

System Bin Dependencies:

* pyenv > python-build
  * [openssl@1.1](https://formulae.brew.sh/formula/openssl@1.1) or [openssl@3](https://formulae.brew.sh/formula/openssl@3)
  * [readline](https://formulae.brew.sh/formula/readline#default)
  * [ncurses](https://formulae.brew.sh/formula/ncurses#default)
  * [zlib](https://formulae.brew.sh/formula/zlib#default)
* [azure-blob-storage](https://github.com/Azure/azure-storage-python) > [requests](https://github.com/psf/requests) > [urllib3](https://github.com/urllib3/urllib3/blob/main/pyproject.toml)
  * [openssl@1.1](https://formulae.brew.sh/formula/openssl@1.1)

## Usage

### Commands

To view the list of available commands, simply run `just` in your terminal. Commands that require setups:

### Conventions

* `/artefacts` holds all large file assets, e.g. model, image, data
* `/output` holds all temporary outputs that would be ignored by git
* `/notebook` for any .ipynb notebooks (VSCode recommended for handling .env)
* `/src/shared` shared libraries across repos

### Python Version

To update python version the following items would need to be updated to use the same version:

* `.python-version` - local development python version
* `pyproject.toml` - `[project]requires-python` version range for dependency resolution
* `ruff.toml` - `target-version` python legacy and future features check
* `azure-pipelines.yml` - `variables:PYTHON_VERSION` ci python version
* `Dockerfile` - `FROM python:` production python version

We use Python 3.10 instead of newer versions for the following reasons:

* use the same version of python in all our repos as much as possible
* could be updated to Python 3.11 now

## Details

### General Patterns

* pipeline(src)
  * `__main__.py` - the entrypoint file for `just run` or `python -m src` in Docker image
  * `args.py` - cli arguments definition for input parameters
  * `process.py` - the available processes of the pipeline
  * `validators.py` - [pydantic](https://github.com/pydantic/pydantic) validators
  * `types.py` - type definitions

### Test Markers

check [pytest.ini](.pytest.ini)

### Python Tools

* type checker - [mypy](https://github.com/python/mypy)
* notebook clean commit - [nbstripout](https://github.com/kynan/nbstripout)
* pre-commit hooks - [pre-commit](https://github.com/pre-commit/pre-commit)
* dotenv cli - [python-dotenv](https://github.com/theskumar/python-dotenv)
* linter & formatter - [ruff](https://github.com/astral-sh/ruff)
* ~~code vulnerability scanner~~ - [bandit](https://github.com/PyCQA/bandit)
* ~~doc site generation~~ - [sphinx](https://github.com/sphinx-doc/sphinx)
* ~~docker image scan~~ - [docker scout](https://docs.docker.com/scout/)

### Config Files

> the files are folded by these categories in VSCode

#### IDE

* `.vscode` - shared VSCode extensions and settings

#### Local Development

* `justfile` - scripted command for development
* `.editorconfig` - editor config
* `.pre-commit-config.yaml` - pre-commit config
* `.python-version` - pyenv local python version
* `cspell.config.yaml` - code spell config for VSCode extension

#### Credentials

* `.env-cache` - local dev env vars that would go into `.env`
* `.env-template` - shared dev env vars that would go into `.env`

#### All Stages

* `pyproject.toml` - dependency specification
* `.coveragerc` - pytest coverage config
* `.gitattributes` - git attributes
* `.gitignore` - gitignore
* `azure-pipeline.yml` - azure pipeline config
* `Dockerfile` - Dockerfile for production builds
* `mypy.ini` - mypy type safety check config
* `pytest.ini` - pytest config
* `ruff.toml` - ruff linter, formatter config

#### Documentation

* `README.md` - documentation
* `*.md` - further documentations
