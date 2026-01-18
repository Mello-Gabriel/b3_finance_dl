# Tech Challenge - Arquitetura de Big Data

Este projeto é um pipeline de Big Data que extrai dados financeiros da API do Yahoo Finance, os processa usando AWS Glue e os disponibiliza para consulta via AWS Athena.

## Arquitetura

O diagrama a seguir ilustra a arquitetura do pipeline:

```mermaid
flowchart TD
    %% Definição de Estilos
    classDef storage fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef compute fill:#fff3e0,stroke:#ff6f00,stroke-width:2px;
    classDef serverless fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px;
    classDef external fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,stroke-dasharray: 5 5;

    %% Nós - Camada de Origem
    subgraph Origem ["1. Ingestão (Local/Python)"]
        YFinance[("API Yahoo Finance")]:::external
        ScriptPython["Script Python<br/>(awswrangler)"]:::external
    end

    %% Nós - Armazenamento
    subgraph Storage ["2. Data Lake (S3)"]
        S3Raw[("Bucket S3<br/>/raw<br/>(Parquet Partitioned)")]:::storage
        TriggerFile["Arquivo de Controle<br/>trigger_lambda.txt"]:::storage
        S3Refined[("Bucket S3<br/>/refined<br/>(Parquet Aggregated)")]:::storage
    end

    %% Nós - Processamento
    subgraph Process ["3. Processamento & Orquestração"]
        Lambda["AWS Lambda<br/>(glue_starter)"]:::serverless
        Glue["AWS Glue Job<br/>(Spark/SQL)"]:::compute
    end

    %% Nós - Consumo
    subgraph Serving ["4. Consumo & Catálogo"]
        Catalog[("Glue Data Catalog")]:::storage
        Athena["AWS Athena<br/>(Consultas SQL)"]:::serverless
    end

    %% Conexões - Fluxo
    YFinance --> |Extração| ScriptPython
    ScriptPython --> |"1. Salva Dados (partitioned)"| S3Raw
    ScriptPython --> |"2. Salva Gatilho (vazio)"| TriggerFile
    
    TriggerFile -.-> |"Notificação de Evento (Sufixo .txt)"| Lambda
    Lambda --> |"boto3.start_job_run()"| Glue
    
    Glue --> |"Lê Dados (Fonte)"| S3Raw
    Glue --> |"Transforma (SQL) & Grava (Destino)"| S3Refined
    
    %% Conexões - Catálogo
    Glue -- "Atualiza Tabela (b3_analytics)" --> Catalog
    S3Raw -.-> |"Projeção de Partição (DDL)"| Catalog
    
    %% Conexões - Athena
    Catalog --- Athena
    Athena --> |"SELECT * FROM acoes_b3_raw"| S3Raw
    Athena --> |"SELECT * FROM b3_analytics"| S3Refined

    %% Links invisíveis para layout
    S3Raw ~~~ S3Refined

```

### Fluxo de Dados

1.  **Ingestão**: O script `extrator.py`, executado localmente, busca dados diários de ações da API do Yahoo Finance para uma lista predefinida de tickers.
2.  **Armazenamento (Raw)**: O script usa a biblioteca `awswrangler` para salvar os dados no formato Parquet em um bucket S3 no diretório `/raw`, particionado por data.
3.  **Gatilho**: Após salvar os dados, o script cria um arquivo vazio chamado `trigger_lambda.txt` no diretório `/raw`. A criação deste arquivo aciona uma função AWS Lambda.
4.  **Orquestração**: A função AWS Lambda, definida em `glue_starter.py`, inicia um trabalho AWS Glue chamado `tech_challenge_job`.
5.  **Processamento**: O trabalho AWS Glue, definido em `tech_challenge_job.py`, lê os dados brutos do diretório `/raw`, agrega os dados para calcular o preço médio de fechamento mensal para cada ação e salva o resultado no formato Parquet no diretório `/refined` no mesmo bucket S3.
6.  **Catálogo de Dados**: O trabalho do Glue também atualiza o AWS Glue Data Catalog com uma tabela chamada `b3_analytics` que aponta para os dados refinados no S3.
7.  **Consulta**: Os dados refinados podem ser consultados usando AWS Athena.

## Pré-requisitos

*   Python 3.12
*   Conta AWS
*   AWS CLI configurado
*   Gerenciador de pacotes `uv`

## Como Executar

1.  **Clonar o repositório**:
    ```bash
    git clone <url-do-repositorio>
    cd <nome-do-repositorio>
    ```
2.  **Sincronizar dependências**:
    ```bash
    uv sync
    ```
3.  **Configurar variáveis de ambiente**:
    Crie um arquivo `.env` com o seguinte conteúdo:
    ```
    AMBIENTE=dev
    S3_BUCKET=<nome-do-seu-bucket-s3>
    ```
4.  **Executar o extrator**:
    ```bash
    uv run extrator.py
    ```
    Isso acionará todo o pipeline.

## Estrutura do Projeto

```
├───.gitignore
├───.python-version
├───extrator.py
├───glue_starter.py
├───pyproject.toml
├───tech_challenge_job.py
├───uv.lock
├───.git/
└───.venv/
```

*   `extrator.py`: Extrai dados do Yahoo Finance e os salva no S3.
*   `glue_starter.py`: Função AWS Lambda que inicia o trabalho Glue.
*   `tech_challenge_job.py`: Trabalho AWS Glue que processa os dados.
*   `pyproject.toml`: Configuração do projeto Python.
*   `uv.lock`: Arquivo de bloqueio do `uv`.
*   `.python-version`: Especifica a versão do Python para o ambiente `uv`.