include .env

help:
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(firstword $(MAKEFILE_LIST)) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


reqs: ## Build requirements
	python -m piptools compile requirements.in > requirements.txt

install: ## Install
install:
	@echo "Installing dependencies..."
	python -m pip install --upgrade pip setuptools wheel
	python -m pip install pip-tools
	python -m piptools sync
	python -m pip install prodigy -f https://${PRODIGY_KEY}@download.prodi.gy
	python -m spacy download en_core_web_trf


fetch: ## Fetch data
fetch: data/01_raw/hackernews2021.parquet

data/01_raw/hackernews2021.parquet:
	@echo "Fetching source data..."
	kaggle datasets download -d edwardjross/hackernews-2021-comments-and-stories --unzip --path data/01_raw/

teach: ## Binary example annotation
teach:
	PRODIGY_CONFIG_OVERRIDES='{"batch_size": 100}' python -m prodigy ner.precise hnbook_ner_workofart_precise en_core_web_trf data/02_intermediate/sample_data.jsonl --label WORK_OF_ART -F ./bookfinder/recipe.py 

