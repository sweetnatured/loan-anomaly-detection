# Synopsis

This repository detects data-quality issues and business-rule anomalies in loan datasets (e.g., XLSX exports) and produce a machine‑readable report.

Use [Poetry](https://python-poetry.org/) to install dependencies defined in [pyproject.toml](pyproject.toml) into a new virtual environment.

```sh
# Install poetry on your system if you haven't yet
pip install poetry

# Install dependencies as declared
poetry install 

# Set necessary environment variables (e.g., for passwords and config)
export FILE_PATH=/path/to/loans.xlsx
export OUTPUT_PATH=/path/to/anomaly_report.csv

# You may also need to add the project to your PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

This project provides a CLI app, you can run it directly via Poetry:
```sh

# Run
poetry run python anomaly_detector/main.py \
--file-path ~/home/user/path/to/loans.xlsx \
--output-path ~/home/user/path/to/anomaly_report.csv
```
#### Running the tests
```sh 
poetry run pytest
```

The Docker image would be built and run locally as follows:
```sh
# Build the Docker image
docker build --network=host -t loan_anomaly_detector .

# Run the container with the following options and mounted volume
docker run --rm \
-v /file/path/on/host:/data \
loan_anomaly_detector \
--file-path /data/loans.xlsx \
--output-path /data/anomaly_report.csv
```

Usage: main.py [**OPTIONS**]
~~~
Options:
  --file-path TEXT                    [env var: FILE_PATH; required]
  --output-path TEXT                  [env var: OUTPUT_PATH; required]
  
  --dry-run / --no-dry-run            [env var: DRY_RUN; default: no-dry-run]
  --logging-format TEXT               [env var: LOGGING_FORMAT; default: 
                                      '[%(asctime)s] [%(threadName)s] %(levelname)s %(name)s - %(message)s']
  --logging-level TEXT                [env var: LOGGING_LEVEL; default: INFO]
  --help                              