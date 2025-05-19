# ------------------------------------- NOTES ------------------------------------- #

## LINKS
#
# * justfile docs: https://just.systems/man/en/
# * cheat sheet: https://cheatography.com/linux-china/cheat-sheets/justfile/

## DIFFERENT SYNTAXES - INSIDE/OUTSIDE RECIPE
#
# justfile syntax applies outside recipe (command level), shell syntax applies within recipe
#
# example - reference variable
# outside recipe - referenced by VAR_NAME: `PROJECT_NAME := file_stem(PYTHONPATH)`
# inside recipe - referenced by $VAR_NAME: `ipykernel install --name $PROJECT_NAME`

## FUNCTIONS
# justfile functions are preferred over shell functions for cross-platform compatibility
# justfile function docs: https://just.systems/man/en/chapter_31.html

## TIPS
# - prepend hyphen to command to ignore errors: https://just.systems/man/en/chapter_30.html
#   e.g. `-rm .env` wouldn't throw error if .env file doesn't exist
#
# - variadic parameters *PARAMETERS accepts zero ro more arguments, passing them as string
#   e.g. *FLAGS, *PARAMETERS, $FLAGS, $PARAMETERS to access

# ----------------------------------------------------------------------------------- #

#
## SETUP
#

### CONFIG
set ignore-comments
set dotenv-load # load .env file
set export # export env vars
set shell := ["bash", "-uc"] # -u to throw errors for unset variables, -c so that string commands can be run
set windows-shell := ["bash", "-uc"]

### VARS
PYTHONPATH := invocation_directory()
PROJECT_NAME := file_stem(PYTHONPATH)

#
## COMMANDS - Development
#

# list available commands
[group('dev')]
@default:
    just --list --unsorted

### Install
@_install_python:
    uv python install

# install python, create .env, install packages & pre-commit hooks
[group('dev')]
@install:
    just _install_python
    just env
    uv lock --upgrade
    uv sync
    uv run pre-commit install --install-hooks # --install-hooks setup pre-commit cache
    uv run nbstripout --install --python .venv/bin/python

### Cleanup

@_cleanup_output:
    rm -rf output/**
    touch output/.gitkeep

@_cleanup_test_report:
    rm -rf .benchmarks/
    rm -rf .coverage
    rm -rf .coverage.*
    rm -rf report/

@_cleanup_tooling_cache:
    rm -rf .mypy_cache
    rm -rf .pytest_cache
    rm -rf .ruff_cache

@_cleanup_pycache:
    # bash doesn't support recursive ** resolution
    rm -rf src/__pycache__
    rm -rf src/**/__pycache__
    rm -rf tests/__pycache__
    rm -rf tests/**/__pycache__

@_cleanup_cython:
    rm -rf src/**/*.c
    rm -rf src/**/*.so
    rm -rf src/**/*.pyd
    rm -rf build/

@_cleanup_rust:
    rm -rf rust/target/

# remove .venv, python & tooling cache, test reports; -a to remove .env, run & test output
[group('dev')]
[confirm("cleanup .venv, build & tooling caches? (y/n)")]
cleanup *FLAGS:
    if [ "$FLAGS" == "-a" ]; then \
        -uv run nbstripout --uninstall; \
        -uv run pre-commit uninstall; \
        just _cleanup_test_report; \
        just _cleanup_output; \
        rm -f .env; \
    fi; \
    just _cleanup_tooling_cache
    just _cleanup_pycache
    just _cleanup_cython
    just _cleanup_rust
    rm -rf .venv/

### Check

# format code using ruff
[group('dev')]
@format:
    uv run ruff format src tests

# lint code using ruff
[group('dev')]
@lint:
    uv run ruff check src tests --fix

# run mypy type checks
[group('dev')]
@type-check:
    uv run mypy src

# run code quality checks
[group('dev')]
@check:
    just format lint type-check

# run code quality checks with file watcher
[group('dev')]
@check-watch:
    watchexec -n -r -w src -w tests -w mypy.ini -w ruff.toml --clear -- just check

# run pre-commit hooks manually
[group('dev')]
@pre-commit:
    uv run pre-commit run --hook-stage pre-commit

# run pre-push hooks manually
[group('dev')]
@pre-push:
    uv run pre-commit run --hook-stage pre-push


#
## COMMANDS - Test
#

# run the src as a module, cli arguments can be passed
[group('test')]
@run *PARAMETERS:
    uv run dotenv run -- python -m src $PARAMETERS

# run simple test cases (exclude complex and benchmark tests)
[group('test')]
@test:
    uv run pytest tests/ -vv -s -m "not complex and not benchmark"

# run all tests
[group('test')]
@test-all:
    uv run pytest tests/ -vv -s

# run test with coverage report (exclude benchmark tests)
[group('test')]
@test-coverage:
    uv run pytest tests/ -vv -s -m "not benchmark" \
    --cov=src --cov-report=term-missing


# run test files changed since last commit with file watcher, flags can be passed to pytest
[group('test')]
@test-watch *FLAGS:
    # watchexec config details
    # -n: don't spawn another shell for speed
    # -r: restart the process on busy update
    watchexec -nr -w src -w tests -e py --clear -- \
        uv run pytest tests/ -vv -s --picked \
        --cov=src \
        --cov-report=term-missing \
        --benchmark-columns=mean,median,max,stddev,rounds,iterations \
        --benchmark-sort=mean \
        $FLAGS

#
## COMMANDS - Docker
#

# build the docker image
[group('docker')]
@docker-build:
    uv lock
    just _cleanup_pycache
    docker build --build-arg PYTHON_VERSION=$(cat .python-version) -t $PROJECT_NAME .

# run the docker image, cli arguments can be passed, container /output is mounted to ./output
[group('docker')]
@docker-run *PARAMETERS:
    docker run --env-file .env -v ./output:/output $PROJECT_NAME python -m src $PARAMETERS

# run the tests in docker image (exclude benchmark tests)
[group('docker')]
@docker-test:
    docker run --env-file .env $PROJECT_NAME pytest tests/ -vv -s -m "not benchmark"

#
## COMMANDS - Cython
#

# build cython script
[group('cython')]
@cython-build:
    uv run python setup.py build_ext --inplace

# run cython-lint
[group('cython')]
@cython-check:
    -uv run cython-lint src --max-line-length 110

#
## COMMANDS - Rust
#

# build rust script
[group('rust')]
@rust-build:
    maturin develop --manifest-path=rust/Cargo.toml

#
## COMMANDS - Template
#

# remove all the template files when init a repo
[group('template')]
@_init:
    -rm -rf src/api
    -rm -rf src/lib
    -rm -rf src/service
    -rm -rf src/data.py
    -rm -rf tests/__fixtures__/*
    -rm -rf tests/api
    -rm -rf tests/lib
    -rm -rf tests/service
    -rm -rf tests/shared
    -rm -rf tests/test_args.py
    rm README.md
    echo "# $PROJECT_NAME" > README.md
    just env

# copy the latest config files from CONFIG_TEMPLATE_PATH#main
[group('template')]
@config:
    echo "coping config files from $CONFIG_TEMPLATE_PATH#main"
    # check out template repo and pull the latest config
    git -C $CONFIG_TEMPLATE_PATH checkout -q main
    git -C $CONFIG_TEMPLATE_PATH pull -q
    # create the convention folders if not exists
    mkdir -p ./output
    touch ./output/.gitkeep
    mkdir -p ./artefacts
    touch ./artefacts/.gitkeep
    # copy the folders and files
    cp -r $CONFIG_TEMPLATE_PATH/.vscode .
    # cp $CONFIG_TEMPLATE_PATH/.env-template .

    cp $CONFIG_TEMPLATE_PATH/justfile .
    cp $CONFIG_TEMPLATE_PATH/.editorconfig .
    cp $CONFIG_TEMPLATE_PATH/.pre-commit-config.yaml .
    # cp $CONFIG_TEMPLATE_PATH/cspell.config.yaml .

    # cp $CONFIG_TEMPLATE_PATH/pyproject.toml .
    cp $CONFIG_TEMPLATE_PATH/.coveragerc .
    cp $CONFIG_TEMPLATE_PATH/.gitattributes .
    cp $CONFIG_TEMPLATE_PATH/.gitignore .
    cp $CONFIG_TEMPLATE_PATH/.python-version .
    cp $CONFIG_TEMPLATE_PATH/azure-pipelines.yml .
    # cp $CONFIG_TEMPLATE_PATH/Dockerfile .
    cp $CONFIG_TEMPLATE_PATH/mypy.ini .
    cp $CONFIG_TEMPLATE_PATH/pytest.ini .
    cp $CONFIG_TEMPLATE_PATH/ruff.toml .

# remove all the template files that could be copied
[group('template')]
@eject:
    rm -rf .vscode

    rm -rf .pre-commit-config.yaml
    # rm -rf cspell.config.yaml

    rm -rf .coveragerc
    rm -rf .gitattributes
    rm -rf .gitignore
    rm -rf .python-version
    rm -rf azure-pipelines.yml
    # rm -rf Dockerfile
    rm -rf mypy.ini
    rm -rf pytest.ini
    rm -rf ruff.toml

# copy the latest shared lib from CONFIG_TEMPLATE_PATH#main
[group('template')]
@shared:
    echo "coping /shared from $CONFIG_TEMPLATE_PATH#main"
    git -C $CONFIG_TEMPLATE_PATH checkout -q main
    git -C $CONFIG_TEMPLATE_PATH pull -q
    rm -rf ./src/shared
    cp -r $CONFIG_TEMPLATE_PATH/src/shared ./src

# sync config and shared lib with the latest from $CONFIG_TEMPLATE_PATH
[group('template')]
@sync:
    just config
    just shared


#
## COMMANDS - EnvVars & Credentials
#

@_env_clean:
    # remove duplicate lines and empty lines in .env
    awk -F= 'NF && $1 {lines[$1] = $0} END {for (name in lines) print lines[name]}' .env > .env.tmp && mv .env.tmp .env
    sort .env -o .env

# NOTE: command can't start with .
# create the default .env from template and cache, -f to create new .env file
[group('credentials')]
@env *FLAGS:
    # remove existing .env file if -f is set
    if [ "$FLAGS" = "-f" ] && [ -f ".env" ]; then \
        rm .env; \
    fi; \
    if [ ! -f ".env" ]; then \
        cp .env-template .env; \
        echo "" >> .env; \
        if [ -f .env-cache ]; then cat .env-cache >> .env; fi; \
        just _env_clean; \
        echo "new .env file created:"; \
        cat .env; \
    else \
        echo ".env file already exists."; \
    fi
