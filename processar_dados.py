# processar_dados.py
import pandas as pd
import os
import requests
import json
import yaml  # Para ler o config
import logging  # Para logging profissional
import glob
import pandera as pa  # Para validação de dados
from pandera.typing import Series
from deltalake.writer import write_deltalake  # Para escrever em Delta Lake

# --- 1. CONFIGURAÇÃO E LOGGING ---
# Carrega as configurações do arquivo YAML
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Cria a pasta de logs se ela não existir
os.makedirs('logs', exist_ok=True)

# Configura o sistema de logging para salvar em um arquivo e exibir no console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/pipeline.log"),
        logging.StreamHandler()
    ]
)


# --- 2. ESQUEMA DE VALIDAÇÃO DE DADOS ---
class SchemaDados(pa.DataFrameModel):
    Ano: Series[int] = pa.Field(ge=config['data_quality']['valid_year_range'][0],
                                le=config['data_quality']['valid_year_range'][1])
    DEC: Series[float] = pa.Field(ge=0, nullable=True)
    FEC: Series[float] = pa.Field(ge=0, nullable=True)
    DIC: Series[float] = pa.Field(ge=0, nullable=True)
    FIC: Series[float] = pa.Field(ge=0, nullable=True)
    Distribuidora: Series[str] = pa.Field(nullable=False)


# --- 3. FUNÇÕES DO PIPELINE ---
def limpar_e_padronizar_dataframe(df_bruto: pd.DataFrame) -> pd.DataFrame:
    logging.info("Iniciando limpeza e padronização...")
    # ... (a lógica interna desta função permanece a mesma da versão anterior)
    df_bruto = df_bruto.rename(columns={
        'SigAgente': 'Distribuidora', 'NumCNPJ': 'CNPJ', 'IdeConjUndConsumidoras': 'ConjuntoID',
        'DscConjUndConsumidoras': 'NomConjunto', 'AnoIndice': 'Ano', 'NumPeriodoIndice': 'Mes',
        'VlrIndiceEnviado': 'Valor', 'SigIndicador': 'Indicador'
    })
    colunas_essenciais = ['Distribuidora', 'CNPJ', 'ConjuntoID', 'NomConjunto', 'Ano', 'Mes', 'Valor', 'Indicador']
    for col in colunas_essenciais:
        if col not in df_bruto.columns:
            df_bruto[col] = None
    df_bruto['Valor'] = pd.to_numeric(df_bruto['Valor'].astype(str).str.replace(',', '.', regex=False), errors='coerce')
    df_bruto.dropna(subset=['Valor', 'Ano', 'Mes', 'Indicador', 'Distribuidora', 'ConjuntoID', 'NomConjunto'],
                    inplace=True)
    df_bruto['Ano'] = pd.to_numeric(df_bruto['Ano'], errors='coerce', downcast='integer')
    df_bruto['Mes'] = pd.to_numeric(df_bruto['Mes'], errors='coerce', downcast='integer')
    df_bruto['ConjuntoID'] = df_bruto['ConjuntoID'].astype(str).str.strip()
    df_bruto['NomConjunto'] = df_bruto['NomConjunto'].astype(str).str.strip()

    mapa_nomes = df_bruto[['ConjuntoID', 'NomConjunto']].drop_duplicates(subset=['ConjuntoID'], keep='last')

    df_pivotado = df_bruto.pivot_table(
        index=['Distribuidora', 'CNPJ', 'ConjuntoID', 'Ano', 'Mes'],
        columns='Indicador', values='Valor'
    ).reset_index()

    df_pivotado = df_pivotado.rename_axis(None, axis=1)
    indicadores_possiveis = ['DEC', 'FEC', 'DIC', 'FIC']
    for ind in indicadores_possiveis:
        if ind not in df_pivotado.columns:
            df_pivotado[ind] = 0.0  # Adiciona a coluna se não existir
    df_pivotado.fillna({k: 0.0 for k in indicadores_possiveis}, inplace=True)

    df_final = pd.merge(df_pivotado, mapa_nomes, on='ConjuntoID', how='left')
    df_final['NomConjunto'] = df_final['NomConjunto'].fillna('Não identificado')

    logging.info("Limpeza e padronização concluídas.")
    return df_final


def processar_dados_locais():
    path_dados_brutos = config['paths']['raw_data']
    if not os.path.exists(path_dados_brutos):
        logging.warning(f"A pasta '{path_dados_brutos}' não foi encontrada. Pulando processamento local.")
        return pd.DataFrame()
    # ... (resto da função igual, trocando prints por logging)
    arquivos_csv = glob.glob(os.path.join(path_dados_brutos, '*.csv'))
    if not arquivos_csv:
        logging.info(f"Nenhum arquivo .csv encontrado na pasta '{path_dados_brutos}'.")
        return pd.DataFrame()
    logging.info(f"Encontrados {len(arquivos_csv)} arquivos locais para processamento...")
    lista_dfs = []
    for arquivo in arquivos_csv:
        try:
            df_temp = pd.read_csv(arquivo, encoding='latin1', sep=';')
            lista_dfs.append(df_temp)
        except Exception as e:
            logging.error(f"Erro ao ler o arquivo {arquivo}: {e}")
    if not lista_dfs: return pd.DataFrame()
    df_completo = pd.concat(lista_dfs, ignore_index=True)
    logging.info(f"Arquivos locais unificados. Total de {len(df_completo):,} linhas.")
    return limpar_e_padronizar_dataframe(df_completo)


def processar_dados_api():
    logging.info("Iniciando carregamento de dados da API da ANEEL...")
    # ... (resto da função igual, trocando prints por logging e usando config)
    all_records = []
    offset = 0
    limit = 32000
    while True:
        params = {"resource_id": config['api']['resource_id'], "limit": limit, "offset": offset}
        try:
            response = requests.get(config['api']['base_url'], params=params, timeout=config['api']['timeout_seconds'])
            response.raise_for_status()
            data = response.json()
            records = data.get("result", {}).get("records", [])
            if not records: break
            all_records.extend(records)
            logging.info(f"Carregados {len(all_records)} registros da API...")
            offset += len(records)
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro na requisição à API: {e}")
            break
    if not all_records:
        logging.warning("Nenhum registro carregado da API.")
        return pd.DataFrame()
    df_api = pd.DataFrame(all_records)
    logging.info(f"Carregamento da API concluído. Total de {len(df_api):,} linhas.")
    return limpar_e_padronizar_dataframe(df_api)


def criar_pipeline_unificado():
    """Executa o pipeline completo: processa, unifica, valida e salva em Delta Lake."""
    logging.info("=" * 50)
    logging.info("INICIANDO PIPELINE DE PROCESSAMENTO DE DADOS")

    df_local = processar_dados_locais()
    df_api = processar_dados_api()
    df_final = pd.concat([df_local, df_api], ignore_index=True)

    if df_final.empty:
        logging.warning("Nenhum dado foi processado. Encerrando o pipeline.")
        return

    logging.info(f"Total de {len(df_final):,} linhas antes da remoção de duplicatas.")
    df_final.drop_duplicates(subset=['Distribuidora', 'ConjuntoID', 'Ano', 'Mes'], keep='last', inplace=True)
    logging.info(f"Total de {len(df_final):,} linhas após a remoção de duplicatas.")
    df_final['Ano'] = df_final['Ano'].astype(int)

    # --- 4. VALIDAÇÃO DOS DADOS PROCESSADOS ---
    try:
        logging.info("Validando o esquema e a qualidade dos dados finais...")
        SchemaDados.validate(df_final, lazy=True)
        logging.info("Validação de dados concluída com sucesso.")
    except pa.errors.SchemaErrors as err:
        logging.error("Falha na validação de qualidade de dados! Verifique os erros abaixo:")
        logging.error(err.failure_cases)
        logging.warning("Os dados NÃO serão salvos devido a falhas de qualidade.")
        return  # Interrompe a execução se os dados estiverem ruins

    # --- 5. SALVANDO EM FORMATO DELTA LAKE ---
    path_dados_processados = config['paths']['processed_data']
    logging.info(f"Salvando os dados processados em '{path_dados_processados}' no formato Delta Lake...")
    write_deltalake(
        path_dados_processados,
        df_final,
        mode='overwrite',
        partition_by=['Ano', 'Distribuidora']
    )
    logging.info("Pipeline de dados concluído com sucesso!")
    logging.info("=" * 50)


if __name__ == "__main__":
    criar_pipeline_unificado()