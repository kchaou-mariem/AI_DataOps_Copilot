FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir --default-timeout=120 -r backend/requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]


# FROM
#  ↓
# image de base

# WORKDIR
#  ↓
# répertoire de travail

# COPY
#  ↓
# copier les fichiers

# RUN
#  ↓
# installer/configurer quelque chose

# CMD
#  ↓
# commande à exécuter lorsque le conteneur démarre