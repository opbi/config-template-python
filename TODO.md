# TODOs

## Fixes

* CI build should distinguish PR or main branch
  * only push :latest on main branch

## Operation

* update python version to 3.11 in all repos
* confirm only install dev dependencies for code quality check in CI is sufficient
* confirm if cleaning up old images in ACR is necessary (is there a setting there already?)

## Possible Further Features

### 1. Better Automated Sync Mechanism

#### append and remove repeat approach

* `_config` folder in template for base
* `config` folder in downstream repos for repo-specific configs
* `just config` would pull files from `_config` and append the content of the same file in local `config`

#### config standardized across repos

* justfile
* .editorconfig
* .pre-commit-config.yaml
* .python-version

* gitattributes
* .gitignore
* azure-pipelines.yml
* pytest.ini
* ruff.toml

#### repo-specific config allowed files

* `cspell.config.yaml` - append the local to the template and remove repeated lines
* pyproject.toml - could we do append and remove repeat?
* Dockerfile - keep only local config and manual update when necessary?

### 2. Python version update

* `just python-version <version>`?
* .python-version
* Dockerfile args?
* azure-pipelines args?
* ruff.toml manual?
* pyproject.toml manual?

### 3. Pre-commit enhancement

* check credentials pre-commit
* can we check if configs have been synced pre-push? (require fully automated just config)
* is there a better place to sync the config regularly? (ci?)

### 4. Just Env-Pull

* pull secrets from Azure KeyVault

### 5. LFS confirmation

* is it enough to check large files pre-commit?
* is LFS supported everywhere? (local env of each dev, CI)
* what's the management overhead for adding that? does it require extra setup on remote repo as well?
