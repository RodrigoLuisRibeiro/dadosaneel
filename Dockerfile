# --- Estágio 1: Base e Instalação de Dependências ---

# Começa com uma imagem oficial do Python. A versão "slim" é menor e otimizada.
FROM python:3.9-slim

# Define o diretório de trabalho dentro do contêiner.
WORKDIR /app

# Copia APENAS o arquivo de dependências primeiro.
COPY requirements.txt .

# Instala as dependências.
RUN pip install --no-cache-dir -r requirements.txt

# --- Estágio 2: Cópia do Código da Aplicação ---

# Agora, copia todo o resto do código do projeto para o diretório de trabalho.
COPY . .

# --- Estágio 3: Execução ---

# Torna o nosso script de inicialização executável.
RUN chmod +x start.sh

# Informa ao Docker que a aplicação dentro do contêiner usará a porta 8501.
EXPOSE 8501

CMD ["./start.sh"]