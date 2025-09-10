# Projeto de Análise de Indicadores de Continuidade - ANEEL

## 🎯 Descrição

Este projeto é uma solução completa para extração, tratamento e visualização de dados abertos de energia da ANEEL. O pipeline de dados unifica informações de arquivos locais e da API da ANEEL, valida a qualidade dos dados e os armazena em um Data Lakehouse no formato Delta Lake, os processa e os apresenta em um dashboard interativo.

O objetivo final é permitir que qualquer pessoa possa explorar e entender os indicadores de continuidade (DEC, FEC, etc.) de diferentes distribuidoras de energia do Brasil de forma simples e visual.

----------

## 🚀 Guia de Instalação e Execução (Passo a Passo)

Siga esta sequência para configurar e rodar o projeto do zero.

### Passo 1: Verifique os Pré-requisitos

Antes de começar, garanta que você tenha os seguintes programas instalados no seu computador:

-   **Python** (versão 3.9 ou superior) - [Link para download](https://www.python.org/downloads/)
    
-   **Git** - [Link para download](https://git-scm.com/downloads)
    

### Passo 2: Baixe o Projeto (Clone o Repositório)

Este comando irá criar uma cópia exata do projeto no seu computador.

1.  Abra seu terminal (Prompt de Comando, PowerShell ou Terminal).
    
2.  Execute o comando abaixo:
    
    Bash
    
    ```
    git clone https://github.com/RodrigoLuisRibeiro/dadosaneel.git
    
    ```
    
3.  Após o download, entre na pasta do projeto:
    
    Bash
    
    ```
    cd nome-da-pasta-do-projeto
    
    ```
    

### Passo 3: Crie o Ambiente Virtual

Isso cria uma "bolha" para o projeto, evitando que as bibliotecas dele se misturem com outras do seu sistema.

Bash

```
python -m venv venv

```

### Passo 4: Ative o Ambiente Virtual

Este comando "liga" a bolha que criamos.

-   **No Windows:**
    
    Bash
    
    ```
    .\venv\Scripts\activate
    
    ```
    
-   **No macOS ou Linux:**
    
    Bash
    
    ```
    source venv/bin/activate
    
    ```
    

> **Dica:** Você saberá que funcionou quando vir `(venv)` aparecer no início da linha do seu terminal.

### Passo 5: Instale as Dependências

Este comando lê o arquivo `requirements.txt` e instala todas as "peças" (bibliotecas) que o projeto precisa para funcionar.

Bash

```
pip install -r requirements.txt

```

> Se tudo correu bem, todas as dependências necessárias estarão instaladas!

### Passo 6: Adicione seus Dados (Opcional)

O pipeline pode buscar dados da internet, mas se você tiver arquivos CSV históricos da ANEEL, pode adicioná-los para uma análise mais completa.

-   Encontre a pasta `dados_brutos/` no projeto.
    
-   Coloque seus arquivos `.csv` dentro dela.
    

### Passo 7: Execute o Pipeline de Dados

Este script fará todo o trabalho pesado: ler os arquivos locais, buscar dados na API da ANEEL, limpar tudo e salvar de forma otimizada.

-   No seu terminal (com o ambiente `(venv)` ainda ativado), execute:
    
    Bash
    
    ```
    python processar_dados.py
    
    ```
    

> **Atenção:** Este processo pode demorar alguns minutos, especialmente na primeira vez. Você verá mensagens de log aparecendo no seu terminal, informando sobre o progresso. Ao final, você verá uma mensagem de sucesso.

### Passo 8: Inicie o Dashboard Interativo

Agora, a parte divertida! Este comando inicia o servidor local e abre o dashboard.

-   No mesmo terminal, execute:
    
    Bash
    
    ```
    streamlit run dashboard_integrado.py
    
    ```
    

> Após alguns segundos, seu navegador de internet deverá abrir automaticamente em uma nova aba, mostrando o dashboard. Se não abrir, você pode acessar manualmente pelo endereço `http://localhost:8501`.

Para desligar o dashboard, volte ao terminal e pressione `Ctrl + C`.

----------

## 📂 Estrutura do Projeto

Uma visão geral dos principais arquivos e pastas.

-   `processar_dados.py`: O "cérebro" do projeto. Script responsável por toda a extração, tratamento e armazenamento dos dados.
    
-   `dashboard_integrado.py`: A "interface" do projeto. Contém todo o código do dashboard interativo que você vê no navegador.
    
-   `config.yaml`: O "painel de controle". Arquivo de configuração para alterar facilmente caminhos e URLs sem mexer no código.
    
-   `requirements.txt`: A "lista de compras". Lista todas as bibliotecas externas que o projeto precisa.
    
-   `README.md`: Este arquivo. A documentação do projeto.
    
-   `dados_brutos/`: A "caixa de entrada". Onde você pode colocar seus próprios arquivos CSV para serem processados.
    
-   `dados_processados/`: O "armazém". Onde os dados limpos e otimizados são salvos no formato Delta Lake.
    
-   `logs/`: O "diário de bordo". Onde o pipeline salva um registro de tudo o que aconteceu durante sua execução.