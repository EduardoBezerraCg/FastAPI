FROM python:3.11-slim

WORKDIR /app

# Instala o nano e outras dependências úteis
RUN apt update && \
    apt install -y nano && \
    apt clean

# Upgrade pip before installing requirements
RUN pip install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Importante: app.main:app por causa do novo caminho
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]
