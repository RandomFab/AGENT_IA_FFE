FROM python:3.13-slim
WORKDIR /api

RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . .

# Commande par défaut pour lancer l'API
CMD ["uv", "run", "uvicorn", "backend.api.main:api", "--host", "0.0.0.0", "--port", "8000"]
