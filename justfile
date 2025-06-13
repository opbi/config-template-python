# LINKS
#
# justfile docs: https://just.systems/man/en/
# cheat sheet: https://cheatography.com/linux-china/cheat-sheets/justfile/
#
# FUNCTIONS
#
# justfile functions are preferred over shell functions for cross-platform compatibility
# justfile function docs: https://just.systems/man/en/chapter_31.html
#
# FEATURES
#
# - prepend hyphen to command to ignore errors: https://just.systems/man/en/chapter_30.html
#   e.g. `-rm .env` wouldn't throw error if .env file doesn't exist
#
# - variadic parameters *PARAMETERS accepts zero ro more arguments, passing them as string
#   e.g. *FLAGS, *PARAMETERS, $FLAGS, $PARAMETERS to access
#
# CAVEATS - DIFFERENT SYNTAXES INSIDE/OUTSIDE RECIPE
#
#  - outside recipe: just syntax, e.g. `PROJECT_NAME := file_stem(PYTHONPATH)` [referenced by VAR_NAME]
#  - inside recipe: shell syntax, e.g. `ipykernel install --name $PROJECT_NAME` [referenced by $VAR_NAME]
#    - inside recipe, use "$VAR_NAME" to interpolate strings correctly
#
# CAVEATS - RECIPE NAME
#
# - recipe name with leading underscore `_` is private, e.g. `@_env_clean` is not listed in `just --list`
# - recipe name can't start with a dot, e.g. `@.env` is not valid
#
# -----------------------------------------------------------------------------------------------

#
#   SETUP
#

### CONFIG
set ignore-comments := true
# load .env file
set dotenv-load := true
# export env vars
set export := true
# -u to throw errors for unset variables
# -c so that string commands can be run
set shell := ["bash", "-uc"]
set windows-shell := ["bash", "-uc"]

### VARIABLES
PYTHONPATH := invocation_directory()
PROJECT_NAME := file_stem(PYTHONPATH)
LOCAL_TEST_SCOPE := "not complex and not benchmark and not online"

### default recipe #keep on top

# list available commands
@list:
    just --list --unsorted

#
#   RECIPE GROUP - DEVELOPMENT
#

### Install

# install python, create .env, install deps & pre-commit hooks
[group('dev')]
@install:
    uv python install
    just env
    uv lock --upgrade
    uv sync
    uv run pre-commit install --install-hooks # --install-hooks setup pre-commit cache
    uv run nbstripout --install --python .venv/bin/python

# create the default .env from template and cache, -f to create new .env file
[group('dev')]
@env *FLAGS:
    # remove existing .env file if -f is set
    if [ "$FLAGS" = "-f" ]; then rm -f .env; fi; \
    if [ -f ".env" ]; then echo "existing .env found:"; cat .env; else \
        cp .env-template .env; echo "" >> .env; \
        if [ -f ".env-cache" ]; then cat .env-cache >> .env; fi; \
        just _use_last_key_value .env; \
        echo "new .env created:"; \
        cat .env; \
    fi

### Cleanup

# remove .venv, python & tooling cache, test reports; -a to remove .env, run & test output
[confirm("cleanup .venv, build & tooling caches? (y/n)")]
[group('dev')]
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

# bash doesn't support recursive ** resolution
@_cleanup_pycache:
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

#
#   RECIPE GROUP - Code Quality
#

# run code quality checks
[group('quality')]
@check:
    just format lint type-check

# run code quality checks with file watcher
[group('quality')]
@check-watch:
    watchexec -n -r -w src -w tests -w mypy.ini -w ruff.toml --clear -- just check

# format code using ruff
[group('quality')]
@format:
    uv run ruff format src tests

# lint code using ruff
[group('quality')]
@lint:
    uv run ruff check src tests --fix

# run mypy type checks
[group('quality')]
@type-check:
    uv run mypy src

# run pre-commit hooks manually
[group('quality')]
@pre-commit:
    uv run pre-commit run --hook-stage pre-commit

# run pre-push hooks manually
[group('quality')]
@pre-push:
    uv run pre-commit run --hook-stage pre-push

## RECIPE GROUP - CREDENTIALS

# TODO
@_fetch_credentials:
    echo "fetching credentials from remote sources"

#
#   RECIPE GROUP - Test
#

# run the src as a module, cli arguments can be passed
[group('test')]
@run *PARAMETERS:
    uv run dotenv run -- python -m src $PARAMETERS

# run test cases with scope
[group('test')]
@test SCOPE=LOCAL_TEST_SCOPE:
    uv run pytest tests/ -vv -s -m "$SCOPE"

# run test coverage with scope
[group('test')]
@test-coverage SCOPE=LOCAL_TEST_SCOPE:
    uv run pytest tests/ -vv -s -m "$SCOPE" --cov=src --cov-report=term-missing

# run test on changed files with scope
[group('test')]
@test-watch SCOPE=LOCAL_TEST_SCOPE:
    # watchexec config details
    # -n: don't spawn another shell for speed
    # -r: restart the process on busy update
    watchexec -nr -w src -w tests -e py --clear -- \
        uv run pytest tests/ -vv -s -m "$SCOPE" --picked \
        --cov=src \
        --cov-report=term-missing \
        --benchmark-columns=mean,median,max,stddev,rounds,iterations \
        --benchmark-sort=mean \

#
#   RECIPE GROUP - Docker
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

# run the tests in docker image
[group('docker')]
@docker-test SCOPE=LOCAL_TEST_SCOPE:
    docker run --env-file .env $PROJECT_NAME pytest tests/ -vv -s -m "$SCOPE"

#
#   RECIPE GROUP - Cython
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
#   RECIPE GROUP - Rust
#

# build rust script
[group('rust')]
@rust-build:
    maturin develop --manifest-path=rust/Cargo.toml

#
#   RECIPE GROUP - Template
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


## UTILITY RECIPES

# keep the last occurrence of each line in the file, drop empty lines
@_use_last_key_value file:
    # -F= use = as the separator, NF checks for non-empty lines
    # $1 is the key name before =, $0 is the whole line, stored in an associative array `lines`
    awk -F= 'NF && $1 {lines[$1] = $0} END {for (key in lines) print lines[key]}' {{file}} > {{file}}.tmp
    mv {{file}}.tmp {{file}}
    sort {{file}} -o {{file}}
