
# Projeto de Análise de Indicadores de Continuidade - ANEEL

## 🎯 Descrição
Este projeto realiza a extração, tratamento e visualização de dados de indicadores de continuidade (DEC, FEC, etc.) da ANEEL. O pipeline de dados unifica informações de arquivos locais e da API da ANEEL, valida a qualidade dos dados e os armazena em um Data Lakehouse no formato Delta Lake. O dashboard interativo é construído com Streamlit.

---

## ⚙️ Instalação (Passos Obrigatórios)

Estes são os primeiros passos que **todos** devem seguir, independentemente de como escolherão executar o projeto depois.

#### Passo 1: Pré-requisitos
Garanta que você tenha os seguintes programas instalados:
- **Python** (versão 3.9 ou superior) - [Link para download](https://www.python.org/downloads/)
- **Git** - [Link para download](https://git-scm.com/downloads)
- **Docker Desktop** (Obrigatório apenas se for usar o Método Docker) - [Link para download](https://www.docker.com/products/docker-desktop/)

#### Passo 2: Baixe o Projeto (Clone o Repositório)
Este comando irá criar uma cópia de todos os arquivos do projeto no seu computador.
1.  Abra seu terminal (Prompt de Comando, PowerShell ou Terminal).
2.  Execute o comando:
    ```bash
    git clone https://github.com/RodrigoLuisRibeiro/dadosaneel.git
    ```
3.  Após o download, entre na pasta do projeto:
    ```bash
    cd dadosaneel
    ```

---

## ▶️ Como Executar o Projeto

Com o projeto baixado, escolha **uma** das duas opções abaixo para executá-lo.

### Opção A: Execução Padrão (com Ambiente Virtual)

Este método é ideal para desenvolvimento e para entender o funcionamento de cada parte do projeto.

1.  **Crie e Ative o Ambiente Virtual:**
    ```bash
    # Criar
    python -m venv venv
    
    # Ativar (Windows)
    .\venv\Scripts\activate
    
    # Ativar (macOS/Linux)
    source venv/bin/activate
    ```

2.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Execute o Pipeline de Dados:**
    ```bash
    python processar_dados.py
    ```

4.  **Execute o Dashboard:**
    ```bash
    streamlit run dashboard_integrado.py
    ```
    > Acesse o dashboard no seu navegador em **http://localhost:8501**.

### Opção B: Execução com Docker (Recomendado para Simplicidade)

Este método executa o projeto inteiro dentro de um contêiner isolado. É a forma mais simples de rodar a aplicação sem se preocupar com instalação de Python ou bibliotecas.

1.  **Construa a Imagem Docker:**
    Certifique-se de que o Docker Desktop esteja em execução. No terminal, na pasta do projeto, execute:
    ```bash
    docker build -t aneel-dashboard .
    ```

2.  **Execute o Contêiner:**
    Este comando inicia o contêiner. Ele irá rodar o pipeline de dados e, em seguida, iniciar o dashboard automaticamente.
    ```bash
    docker run -p 8501:8501 aneel-dashboard
    ```

3.  **Acesse o Dashboard:**
    > Abra seu navegador e acesse **http://localhost:8501**.

---

## 📂 Estrutura do Projeto
-   `dados_dashboard.py`: Leitura da versão atual da tabela Delta, respeitando os arquivos ativos e as variações de espaços nos nomes das distribuidoras.
-   `processar_dados.py`: O "cérebro" do projeto. Script responsável por toda a extração, tratamento e armazenamento dos dados.
-   `dashboard_integrado.py`: A "interface" do projeto. Contém todo o código do dashboard interativo.
-   `config.yaml`: O "painel de controle". Arquivo de configuração para alterar facilmente caminhos e URLs.
-   `requirements.txt`: A "lista de compras" de bibliotecas Python.
-   `Dockerfile`: A "receita" para construir o contêiner do projeto.
-   `dados_brutos/`: A "caixa de entrada" para seus arquivos CSV.
-   `dados_processados/`: O "armazém" onde os dados limpos são salvos.
-   `logs/`: O "diário de bordo" do pipeline.

## Testes

Com as dependências instaladas, execute na raiz do projeto:

```bash
python -m unittest discover -v
```

Os testes usam tabelas temporárias para validar a substituição do esquema Delta,
a exclusão do índice do pandas e a leitura sem registros de versões antigas.

O dashboard deve ler `dados_processados/` pelo Delta Lake. Ler todos os arquivos
Parquet diretamente inclui versões antigas preservadas no disco. Ao publicar os
dados no Git, inclua os arquivos de dados e o diretório `_delta_log` juntos.
