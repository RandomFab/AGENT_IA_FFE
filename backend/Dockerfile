FROM python:3.13-slim
WORKDIR /api
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . .

# Commande par défaut pour lancer l'API
CMD ["uv", "run", "uvicorn", "backend.api.main:api", "--host", "0.0.0.0", "--port", "8000"]
