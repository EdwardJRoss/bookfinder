include .env

PYTHON_DIRS = bookfinder test

.PHONY: test

help:
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(firstword $(MAKEFILE_LIST)) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## Install
install:
	@echo "Installing dependencies..."
	python -m pip install --upgrade pip setuptools wheel
	python -m pip install pip-tools
	python -m piptools sync requirements.txt requirements-model.txt
	python -m pip install prodigy -f https://${PRODIGY_KEY}@download.prodi.gy

requirements.txt: requirements.in
	python -m piptools compile requirements.in

reqs: ## Update and sync requirements
reqs: requirements.txt requirements-model.txt
	python -m piptools sync requirements.txt requirements-model.txt

format: ## Format code
	@echo "Formatting code..."
	python -m black $(PYTHON_DIRS)
	python -m autoflake --in-place --recursive --remove-all-unused-imports $(PYTHON_DIRS)

lint:   ## Static analysis
	@echo "Linting code..."
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

teach: ## Binary NER annotation for precision 
teach:
	python -m prodigy ner.precise hnbook_ner_workofart_precise en_core_web_trf data/02_intermediate/sample_data.jsonl --label WORK_OF_ART -F ./bookfinder/recipe.py 

