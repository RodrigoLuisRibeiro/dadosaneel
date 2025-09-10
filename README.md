# Projeto de Análise de Indicadores de Continuidade - ANEEL

## Descrição
Este projeto realiza a extração, tratamento e visualização de dados de indicadores de continuidade (DEC, FEC, etc.) da ANEEL. O pipeline de dados unifica informações de arquivos locais e da API da ANEEL, valida a qualidade dos dados e os armazena em um Data Lakehouse no formato Delta Lake. O dashboard interativo é construído com Streamlit.

## Estrutura de Pastas
- `dados_brutos/`: Local para arquivos CSV históricos.
- `dados_processados/`: Data Lakehouse no formato Delta Lake, particionado por Ano e Distribuidora.
- `logs/`: Arquivos de log gerados pelo pipeline.

## Como Configurar o Projeto
1. Clone este repositório.
2. Crie e ative um ambiente virtual: `python -m venv venv`
3. Instale as dependências: `pip install -r requirements.txt`

## Como Executar
1. **Para executar o pipeline de dados:**
   ```bash
   python processar_dados.py

2. **Para executar o dashboard:**
3. ```bash
   streamlit run dashboard_integrado.py