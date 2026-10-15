# Procedencia y uso de los datos

## Estado

La procedencia pública, licencia y condiciones de redistribución del archivo
`data/raw/car_data.csv` todavía no están confirmadas en este repositorio. Por
ello, el conjunto se conserva como evidencia de trabajo reproducible, pero no
debe presentarse como libre de restricciones ni redistribuirse fuera del ámbito
autorizado hasta verificar su fuente original.

## Identidad del insumo actual

| Elemento | Valor |
|---|---|
| Archivo | `data/raw/car_data.csv` |
| SHA-256 | `fbe6fc8bf597d30c26f810e4768244776b65248b9617069e803b42e9515e10b0` |
| Ventana temporal observada | 5 de marzo a 7 de abril de 2016 |
| Unidad | Observación histórica de un vehículo/anuncio; no hay VIN, ID estable ni confirmación de cierre de venta |
| Campo de precio | `Price` en EUR, interpretado como precio registrado en la observación, no como venta final verificable |

## Pendiente antes de una publicación pública

La persona responsable del repositorio debe registrar aquí:

1. URL o referencia de la fuente original y fecha de descarga.
2. Titular, licencia y condiciones de redistribución/atribución.
3. Alcance del muestreo y transformaciones aplicadas antes de recibir el CSV.
4. Decisión explícita: versionar el CSV en GitHub, ofrecer instrucciones de
   descarga desde la fuente permitida, o publicar una muestra anonimizada.

Mientras esos puntos no estén resueltos, una publicación pública debe excluir
el archivo crudo si los derechos de redistribución no están claros. Los datos
procesados, el modelo y las conclusiones heredan esta misma restricción.

## Relación con la licencia del código

El archivo `LICENSE` aplica al código y la documentación creada para este
proyecto, no al CSV crudo ni a sus derivados. El dataset se mantiene en el
repositorio como insumo histórico y educativo de la demo; quien quiera
reutilizarlo o redistribuirlo por separado debe verificar primero la licencia
de su fuente original.

## Trazabilidad dentro del proyecto

El notebook `notebooks/analisis_integral_rusty_baregain.ipynb` transforma el
insumo crudo y genera los artefactos en `data/processed/` y `reports/`. El
reporte `reports/rusty_baregain_data_lineage.json` conserva la trazabilidad
técnica del flujo; el diccionario está en
`reports/rusty_baregain_data_dictionary.csv`.
