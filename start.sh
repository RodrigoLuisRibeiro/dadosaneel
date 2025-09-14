#!/bin/sh
# Este script garante que o pipeline de dados seja executado e verificado antes de iniciar o dashboard.

# Garante que o script pare se algum comando falhar
set -e

echo ">>> (1/3) Iniciando o pipeline de processamento de dados..."
python processar_dados.py

echo ">>> (2/3) Verificando se os dados foram processados com sucesso..."
# Verifica se a pasta 'dados_processados' existe E se o log do Delta Lake foi criado (sinal de sucesso)
if [ ! -d "dados_processados/_delta_log" ]; then
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "ERRO CRÍTICO: O pipeline de dados falhou em gerar a tabela Delta."
    echo "A pasta 'dados_processados/_delta_log' não foi encontrada."
    echo "Causa provável: O contêiner não conseguiu acesso à internet para baixar os dados da API da ANEEL."
    echo "Verifique sua conexão, VPN ou configurações de firewall."
    echo "O dashboard não será iniciado."
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    exit 1
fi

echo ">>> (3/3) Verificação concluída. Iniciando o dashboard Streamlit..."
# O comando 'exec' substitui o processo do script pelo do Streamlit
exec streamlit run dashboard_integrado.py