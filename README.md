# Paybility

## Prerequisites

- **[Docker](https://www.docker.com/) (recommended)**:
   - Install Docker and ensure it is running on your system.
   - [Docker Installation Guide](https://docs.docker.com/get-docker/)
- MSSQL

## Usage Instructions

1. **Mount to the Correct Directory**: Ensure that you are in the root directory of this project.
2. **Configuration**: Ensure the `config.ini` file is correctly configured according to your environment.
3. **Deployment and Execution**: 
    #### Deployment Options
    - Run with docker & docker compose
    ```bash
    docker compose up -d
    ```
    - Run without docker
    ```bash
    # install packages
    pip install --no-cache-dir -r requirements.txt

    # run the service
    python src/main.py
    ```
    > Please note that if you want to deploy the service without docker, it's recommended to use python virtual environment.

## UI test

- After installing streamlit, run:

```bash
streamlit run src/streamlit.py
```

## File structure
```plaintext
├── command.txt
├── config.ini
├── data
│   ├── mapping_rules.xlsx
│   └── std_template
│       ├── 增辦第4期-表4.xlsx
│       ├── 增辦第4期-表7.xlsx
│       └── 增辦第4期-表9.xlsx
├── docker-compose.yml
├── Dockerfile
├── output
│   ├── logs
│   │   ├── __main__.log
│   │   ├── file_validator.log
│   │   ├── logic_validator.log
│   │   ├── result.log
│   │   └── schema_validator.log
│   └── results
│       └── result.json
├── README.md
├── requirements.txt
├── src
│   ├── connect.py
│   ├── file_validator.py
│   ├── logger.py
│   ├── logic
│   │   ├── __init__.py
│   │   ├── date_logic.py
│   │   ├── matchnumber_logic.py
│   │   ├── period_logic.py
│   │   ├── recipient_logic.py
│   │   └── unique_logic.py
│   ├── logic_validator.py
│   ├── main.py
│   ├── result.py
│   ├── schema_validator.py
│   ├── streamlit.py
│   ├── test_schema.py
│   ├── test.db
│   ├── test.py
│   └── utils
│       ├── __init__.py
│       └── utils.py
└── system_architecture.drawio
```