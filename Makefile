include .env

PYTHON_DIRS = bookfinder test get_spacy_model_links.py

.PHONY: test

help:
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(firstword $(MAKEFILE_LIST)) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## Install
install:
	@echo "Installing dependencies..."
	python -m ensurepip --upgrade
	python -m pip install --upgrade setuptools wheel
	python -m pip install -f spacy_model_links.html -r requirements.txt

spacy_model_links.html:
	python ./get_spacy_model_links.py

requirements.txt: requirements.in spacy_model_links.html
	python -m piptools compile -q --no-emit-find-links \
        --find-links spacy_model_links.html


update:
	python ./get_spacy_model_links.py
	python -m piptools compile --no-emit-find-links \
        --find-links spacy_model_links.html \
        --upgrade

reqs: ## Update and sync requirements
reqs: requirements.txt
	python -m piptools sync --find-links links.html requirements.txt

format: ## Format code
	@echo "Formatting code..."
	python -m isort --profile black $(PYTHON_DIRS)
	python -m black $(PYTHON_DIRS)
	python -m autoflake --in-place --recursive --remove-all-unused-imports $(PYTHON_DIRS)

lint:   ## Static analysis
	@echo "Linting code..."
	python -m isort --profile black --check-only $(PYTHON_DIRS)
	python -m black --check $(PYTHON_DIRS)
	python -m pyflakes $(PYTHON_DIRS)
	python -m mypy $(PYTHON_DIRS)

test: ## Run unit tests
	python -m pytest test/

fetch: ## Fetch data
fetch: data/01_raw/hackernews2021.parquet

data/01_raw/hackernews2021.parquet:
	@echo "Fetching source data..."
	kaggle datasets download -d edwardjross/hackernews-2021-comments-and-stories --unzip --path data/01_raw/

data/02_intermediate/sample_data.jsonl:
	python -m bookfinder ./data/01_raw/hackernews2021.parquet ./data/02_intermediate/sample_data.jsonl

teach: ## Binary NER annotation for precision
teach: data/02_intermediate/sample_data.jsonl
	python -m prodigy ner.precise hnbook_ner_workofart_precise en_core_web_trf data/02_intermediate/sample_data.jsonl --label WORK_OF_ART -F ./bookfinder/recipe.py
