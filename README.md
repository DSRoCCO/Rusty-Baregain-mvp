# Rusty_Baregain_mvp

Demo analítica en español para que una persona compradora consulte una
**referencia histórica** de precio de un vehículo usado. No es una tasación
actual, una garantía de precio ni evidencia de una venta final.

La evidencia procede de observaciones históricas capturadas entre el 5 de marzo
y el 7 de abril de 2016. El MVP limita la interacción a vehículos ordinarios
matriculados entre 1991 y 2016 para no extrapolar a coches de colección ni a
años que la fuente no cubre.

## Qué incluye

- Análisis reproducible en dos etapas: datos y modelado.
- Artefactos procesados, linaje y diccionario de datos.
- Modelo `HistGradientBoosting` y módulo de comparables por marca y modelo.
- Aplicación Streamlit con análisis descriptivo y estimación interactiva.
- Pruebas de integración para el contrato mínimo de datos, modelo y
  comparables.

## Estructura

```text
app.py                                      # interfaz Streamlit
src/rusty_baregain_mvp/                     # carga, modelo y comparables
notebooks/analisis_integral_rusty_baregain.ipynb
notebooks/analisis_integral_modelado_rusty_baregain.ipynb
data/raw/car_data.csv                       # insumo original (ver procedencia)
data/processed/                             # artefactos reproducibles
models/                                     # estimador y metadatos
reports/                                    # linaje y diccionario
tests/                                      # pruebas automatizadas
docs/data_provenance.md                     # procedencia y uso de los datos
```

## Requisitos

- Python 3.12 o compatible con el rango indicado en `pyproject.toml`.
- [uv](https://docs.astral.sh/uv/) para instalar exactamente las dependencias
  descritas por `uv.lock`.

## Ejecutar la demo

Desde la raíz del repositorio:

```bash
uv sync --frozen
PYTHONPATH=src uv run streamlit run app.py
```

Streamlit mostrará la URL local, normalmente `http://localhost:8501`.
La interfaz solicita características completas del vehículo y muestra una
estimación histórica, un intervalo empírico y el nivel de evidencia de
comparables. El selector de año se limita deliberadamente a 1991–2016.

## Reproducir el análisis y el modelo

1. Verifique la identidad del insumo con el hash y las restricciones de uso en
   [docs/data_provenance.md](docs/data_provenance.md).
2. Instale el entorno de análisis con `uv sync --frozen --group analysis`.
3. Inicie Jupyter y ejecute en orden ambos notebooks, de arriba abajo:

   ```bash
   uv run jupyter lab
   ```

   - `notebooks/analisis_integral_rusty_baregain.ipynb` produce los datasets
     procesados, el diccionario y el reporte de linaje.
   - `notebooks/analisis_integral_modelado_rusty_baregain.ipynb` evalúa el
     enfoque predictivo y deja documentada la evidencia del modelo.

4. Entrene y persista el estimador que consume la aplicación:

   ```bash
   PYTHONPATH=src uv run python -m rusty_baregain_mvp.train
   ```

5. Ejecute las pruebas y luego la interfaz:

   ```bash
   PYTHONPATH=src uv run python -m unittest discover -s tests -v
   PYTHONPATH=src uv run streamlit run app.py
   ```

El comando de entrenamiento debe ejecutarse después de regenerar los datos si
estos cambian; así se actualizan en conjunto el archivo `.joblib` y sus
métricas en `models/price_estimator_metadata.json`.

## Evidencia actual del modelo

Evaluación temporal sobre la población del MVP (matriculación 1991–2016):

| Medida | Resultado |
|---|---:|
| Filas de prueba temporal | 51,706 |
| MAE | EUR 1,003.89 |
| RMSE | EUR 1,598.78 |
| Semiancho del intervalo empírico | EUR 2,277.25 |
| Cobertura observada del intervalo | 89.41% |

El error no es uniforme: crece para rangos de precio más altos. Estas métricas
describen el periodo histórico disponible; no son desempeño en el mercado
actual.

## Alcance y límites

- `Price` es el precio registrado en la observación. La fuente no confirma que
  sea el precio final de una transacción.
- La fuente no contiene promociones, descuentos, equipamiento detallado,
  estado mecánico real, VIN ni identificador estable de anuncio.
- Las comparaciones se limitan a la misma marca y modelo; si no hay evidencia
  suficiente, la interfaz lo comunica como confianza baja.
- Las asociaciones descriptivas no demuestran causalidad ni sirven para
  recomendar una compra, un crédito o una reparación.

## Datos, licencia y publicación

El código se distribuye bajo [MIT](LICENSE): puede usarse, copiarse,
modificarse y redistribuirse conservando el aviso de licencia. El valor de este
proyecto de portafolio está en su flujo reproducible, análisis, validación
temporal, modelo y aplicación; no en usar el dataset como tasador comercial
actual.

`data/raw/car_data.csv` y sus derivados se incluyen exclusivamente como
evidencia educativa e histórica para reproducir esta demo. La licencia MIT no
se aplica a esos datos. Consulte [docs/data_provenance.md](docs/data_provenance.md)
antes de reutilizarlos o redistribuirlos por separado.

`docs/data_provenance.md` se publica como documentación de transparencia y
reproducibilidad. La especificación de trabajo `project_spec.md` se conserva
localmente y está excluida de Git, ya que no es necesaria para usar ni revisar
el proyecto publicado.

## Empaquetado y Docker

`pyproject.toml` declara las dependencias de ejecución y `uv.lock` fija sus
versiones. Las dependencias de notebooks y análisis están separadas en el grupo
`analysis`, por lo que no se incorporan a la imagen de la aplicación.

Construya y ejecute el contenedor desde la raíz del repositorio:

```bash
docker build --tag rusty-baregain-mvp:latest .
docker run --rm --publish 127.0.0.1:8501:8501 rusty-baregain-mvp:latest
```

Abra `http://localhost:8501`. El puerto queda limitado a la máquina local. La imagen se ejecuta con un usuario sin
privilegios, expone el puerto 8501 y comprueba el endpoint interno de salud de
Streamlit. Su contexto conserva únicamente `app.py`, `src/`, el modelo y los
dos artefactos procesados que consume la interfaz; `.dockerignore` excluye
secretos, dato crudo, notebooks, pruebas y reportes.

Si una construcción falla por un timeout temporal al descargar una imagen o un
paquete, inténtelo de nuevo: el comando de ejecución debe hacerse sólo después
de que `docker build` termine correctamente.
