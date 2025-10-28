.PHONY: setup setup-conda data train test infer ui clean help

help:
	@echo "Badminton Wind Predictor - Available commands:"
	@echo ""
	@echo "  make setup-conda - Create conda environment (recommended for Windows)"
	@echo "  make setup       - Create pip virtual environment"
	@echo "  make data        - Generate sample weather data"
	@echo "  make train       - Train both baseline and LSTM models"
	@echo "  make test        - Run test suite"
	@echo "  make infer       - Run inference with trained model"
	@echo "  make ui          - Launch Gradio UI"
	@echo "  make clean       - Remove generated files and artifacts"

setup-conda:
	conda env create -f environment.yml
	@echo ""
	@echo "Conda environment 'badminton-wind' created!"
	@echo "Activate with: conda activate badminton-wind"

setup:
	python -m venv venv
	@echo "Virtual environment created. Activate with:"
	@echo "  Windows (PowerShell): .\\venv\\Scripts\\Activate.ps1"
	@echo "  Linux/Mac: source venv/bin/activate"
	@echo ""
	@echo "Then run: pip install -r requirements.txt"

data:
	python scripts/make_sample_data.py

train:
	python -m src.cli.train --model baseline
	python -m src.cli.train --model lstm --epochs 5

test:
	pytest -v

infer:
	python -m src.cli.infer --model experiments/latest/model.h5

ui:
	cd deployment/hf_space && python app.py

clean:
	rm -rf experiments/
	rm -rf data/sample_station.csv
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
