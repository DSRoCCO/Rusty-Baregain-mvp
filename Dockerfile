# Imagen de ejecución del MVP; los notebooks y el dato crudo no forman parte
# del contexto gracias a .dockerignore.
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PATH=/app/.venv/bin:$PATH

WORKDIR /app

# Se instala uv desde PyPI para no depender de GHCR durante la construcción.
# uv instala después exactamente las versiones fijadas en uv.lock.
RUN pip install --no-cache-dir "uv==0.9.4"

# La interfaz no se ejecuta como root. El entorno virtual puede mantenerse de
# sólo lectura: el usuario de la aplicación sólo necesita importarlo y usarlo.
RUN useradd --create-home --uid 10001 appuser

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Sólo se incluye lo que necesita la aplicación en tiempo de ejecución.
COPY --chown=appuser:appuser app.py ./
COPY --chown=appuser:appuser src ./src
COPY --chown=appuser:appuser data/processed/rusty_baregain_modeling_base.csv ./data/processed/rusty_baregain_modeling_base.csv
COPY --chown=appuser:appuser data/processed/rusty_baregain_descriptive.csv ./data/processed/rusty_baregain_descriptive.csv
COPY --chown=appuser:appuser models ./models
USER appuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3)"

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
