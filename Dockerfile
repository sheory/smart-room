# Usando a imagem oficial do Python
FROM python:3.11

# Definindo o diretório de trabalho
WORKDIR /app

# Copiando dependências primeiro para otimizar cache
COPY requirements.txt .

# Instalando dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiando o código para o contêiner
COPY . .

# Expondo a porta do FastAPI
EXPOSE 8000

# Comando para rodar a API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
