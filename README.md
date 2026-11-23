# Metabolic Health Explorer

**Proyecto académico — Maestría en Inteligencia Analítica de Datos (MIAD), Universidad de los Andes**  
**Materia:** Despliegue de Soluciones Analíticas  
**Repositorio:** [MIAD-DSA-Metabolic-Health-Explorer](https://github.com/Alixguti9620/MIAD-DSA-Metabolic-Health-Explorer)

> **Estado: Entrega final (prototipo funcional).** Incluye modelos entrenados, experimentos en MLflow, una API REST con FastAPI, un tablero con Streamlit y contenedores Docker para desplegar ambos. Los soportes del despliegue en AWS y los manuales se agregan en `docs/` al completarse (ver la sección 15).

## 1. Contexto y propósito

National Health and Nutrition Examination Survey (NHANES) es la encuesta de salud y nutrición nacional de Estados Unidos, regulada por el Centro de Control y Prevención de Enfermedades (CDC). Sus datos permiten monitorear el estado de salud y nutricional de la población y los factores de riesgo de enfermedades crónicas (NCHS, 2024).

La diabetes y la prediabetes se detectan con pruebas de laboratorio que son costosas de aplicar a toda la población. Los programas de tamizaje con recursos limitados necesitan decidir **a quién ofrecerle primero la prueba**. Medidas no invasivas como la edad, el IMC, la cintura y la presión arterial se toman en cualquier consulta y pueden usarse para ordenar a las personas por prioridad.

**Pregunta de negocio**

> ¿Es posible priorizar a los adultos con mayor probabilidad de tener diabetes o prediabetes diagnosticada, usando solo medidas no invasivas y de bajo costo, de modo que se capture al menos el 75 % de los casos tamizando como máximo al 40 % de la población?

**Criterio de éxito** (sobre el conjunto de prueba): recall >= 75 % señalando como máximo al 40 % de los adultos, superando la línea base de usar solo la edad (72,3 % en el EDA). En la partición de prueba el modelo queda cerca de la meta con poco margen y su intervalo de confianza baja del 75 % (ver la pantalla "Modelo y datos" y la sección 6).

**Alcance y limitaciones de la variable objetivo.** `Diabetes` se construye con el diagnóstico **autorreportado** (`DIQ010`), así que el modelo aprende el perfil de quienes *ya* tienen un diagnóstico. El tamizaje busca a quienes aún no lo tienen, y eso este modelo **no lo mide**. NHANES 2013-2014 incluye hemoglobina glicosilada (`LBXGH`, tabla `GHB_H`), con la que se podrían definir también los casos no diagnosticados; no se incorporó en esta entrega y queda como trabajo futuro. Tampoco se usan los ponderadores muestrales de NHANES: el "40 %" se refiere a la **muestra**, no a la población de Estados Unidos.

**Usuario principal:** analista o equipo de salud pública que planifica campañas de tamizaje. **No es un dispositivo de diagnóstico, una predicción de enfermedad futura ni una herramienta validada de decisión médica.**

Documentación:

- [01 — Problema y contexto](docs/01_problema_y_contexto.md)
- [02 — Pregunta de negocio y alcance](docs/02_pregunta_de_negocio_y_alcance.md)
- [04 — Maqueta del prototipo](docs/04_maqueta_prototipo.md)
- [05 — Estructura y trabajo en equipo](docs/05_estructura_y_trabajo_en_equipo.md)
- Exploración inicial de la Entrega 1: [`scripts/03_exploracion_inicial_nhanes.ipynb`](scripts/03_exploracion_inicial_nhanes.ipynb)
- Exploración complementaria de la Entrega 2: [`scripts/06_Exploracion_complementaria_nhanes.ipynb`](scripts/06_Exploracion_complementaria_nhanes.ipynb)
- Modelos iniciales de la Entrega 2 (con y sin laboratorio): [`scripts/07_modelos_iniciales_v1.ipynb`](scripts/07_modelos_iniciales_v1.ipynb)
- Validación de supuestos de esos modelos: [`scripts/08_validacion_supuestos.ipynb`](scripts/08_validacion_supuestos.ipynb)

## 2. Cambios respecto a la Entrega 1

| Aspecto | Entrega 1 | Entrega 2 | Motivo |
|---|---|---|---|
| Datos | Subconjunto UCI 887 (2.278 registros de los 6.287 declarados) | Seis tablas NHANES 2013-2014 unidas por `SEQN` (9.763 registros con `DIQ010` válido) | El subconjunto anterior tenía solo 21 positivos |
| Objetivo | Diabetes reportada (21 casos) | Diabetes o prediabetes reportada (922 casos; 902 en adultos) | Más casos y coherencia con el tamizaje |
| Variables | Incluían glucosa en ayunas, prueba oral e insulina | Solo medidas no invasivas | La glucosa es criterio diagnóstico y hacía la clasificación casi circular |
| Fuga de información | No identificada | Se descartan variables de DIQ que solo existen para quienes responden "Sí" | Su presencia delataba la clase |
| Población | Todas las edades | Adultos (>= 18 años), 6.110 registros | Entre los menores solo 0,5 % es positivo |
| Pregunta de negocio | Cómo facilitar la exploración mediante una aplicación | Cómo priorizar el tamizaje, con meta medible | La anterior justificaba la herramienta, no una decisión |

## 3. Datos y variable objetivo

- **Fuente:** [NHANES 2013-2014, CDC](https://wwwn.cdc.gov/nchs/nhanes/ContinuousNhanes/Default.aspx?BeginYear=2013). Archivos en formato SAS Transport (`.xpt`) en `data/raw/`.
- **Tablas utilizadas:**

| Archivo | Contenido | Variables empleadas |
|---|---|---|
| `DIQ_H.xpt` | Cuestionario de diabetes | `DIQ010` (objetivo) |
| `DEMO_H.xpt` | Demografía | `RIDAGEYR`, `RIAGENDR`, `RIDRETH3`, `INDHHIN2`, `INDFMIN2` |
| `BMX_H.xpt` | Medidas corporales | `BMXBMI`, `BMXWAIST` |
| `BPX_H.xpt` | Presión arterial | `BPXSY1`, `BPXDI1` |
| `TCHOL_H.xpt` | Colesterol total | `LBXTC` |
| `HDL_H.xpt` | Colesterol HDL | `LBDHDD` |

- **Conjunto consolidado:** `data/raw/NHANES_consolidado.csv` (9.763 filas), generado por el notebook 06 con nombres legibles: `Diabetes`, `Edad`, `Genero`, `Raza_Etnia`, `Ingreso_Hogar`, `Ingreso_Familia`, `IMC`, `Cintura_cm`, `Presion_Sistolica`, `Presion_Diastolica`, `Colesterol_Total` y `Colesterol_HDL`.
- **Variable objetivo:** `Diabetes` = 1 si `DIQ010` es 1 (Sí) o 3 (Borderline, prediabetes), y 0 si es 2 (No). Las respuestas "Rehusó" (7) y "No sabe" (9) se excluyen y **no** se tratan como negativas.

| Etapa | Registros | Detalle |
|---|---|---|
| Tabla `DIQ_H` completa | 9.770 | 54 variables |
| `DIQ010` válido (1, 2 o 3) | 9.763 | 737 Sí · 8.841 No · 185 Borderline |
| Objetivo = 1 (Sí o Borderline) | 922 | 9,4 % del total |
| **Adultos (>= 18 años)** | **6.110** | **902 positivos (14,8 %)**, relación 5,8 a 1 |

**Limitaciones de los datos:**

- El diagnóstico es **autorreportado**: el modelo aprende el perfil asociado a un diagnóstico previo y no detecta diabetes sin diagnosticar.
- Las personas ya diagnosticadas pueden estar en tratamiento, lo que altera valores como el colesterol (en el EDA, el colesterol total fue menor en los positivos).
- No se aplicaron los ponderadores del diseño muestral de NHANES: las proporciones **no** son estimaciones representativas de la población de Estados Unidos.
- Raza/etnia e ingreso se usan para describir y controlar, no como criterio de priorización.

## 4. Hallazgos principales del EDA

El análisis completo está en las secciones 3 y 4 del notebook 06, con comentarios en cada gráfica. Las figuras `eda_*.png` están en `reports/figures/`.

- **Edad** es la variable más discriminante (AUC univariado 0,74); la mediana es 62 años en positivos frente a 43 en negativos.
- La tasa de casos sube de 1,6 % (18-29 años) a cerca de 30 % (60-69 años), y de 7 % en peso normal a 26 % con obesidad II o mayor.
- **IMC y cintura** están muy correlacionados (0,91), lo que se considerará en el modelado.
- La presión diastólica casi no discrimina; el género tampoco.
- Edad e IMC se refuerzan entre sí, por lo que conviene un modelo que combine variables.
- La regla de solo edad captura 72,3 % de los casos al tamizar al 40 % de la población; ninguna otra regla simple llega a 63 %.
- Valores nulos entre 4 % y 12 % por variable, similares entre clases; la presión diastólica ~0 es un artefacto de codificación y se trata como nulo.

## 5. Cambios respecto a la Entrega 2

| Aspecto | Entrega 2 | Entrega final |
|---|---|---|
| API | No existía | API REST con FastAPI (`api/`): predicción individual, por lotes (JSON y CSV), información del modelo y 20 pruebas automáticas |
| Tablero | Un perfil a la vez; modelos cargados desde archivo | Pantalla de **priorización por lotes** (CSV, ranking con recorte del 40 %, descarga); las predicciones se piden a la API (`API_URL`) |
| Despliegue | Pendiente | `Dockerfile.api`, `Dockerfile.tablero` y `docker-compose.yml` |
| MLflow | Corridas desde un cuaderno | Script reproducible `src/experimentos_mlflow.py`: partición 60/20/20, búsqueda de hiperparámetros documentada y métricas en entrenamiento, validación y prueba |
| Alcance | Sin declarar la limitación del objetivo | Limitaciones del objetivo autorreportado y de los pesos muestrales declaradas (sección 1) |

## 6. Modelos y experimentos

Se comparan, para los escenarios **sin laboratorio** (6 variables) y **con laboratorio** (8 variables): la edad como único puntaje (referencia), regresión logística, regresión logística con splines en edad y cintura más la interacción edad × cintura, y HistGradientBoosting. La métrica del proyecto es **recall@40 %**; también se reportan ROC-AUC y PR-AUC.

`src/experimentos_mlflow.py` hace lo siguiente:

- Parte los datos en entrenamiento, validación y prueba (60/20/20, estratificado, semilla 7).
- Busca hiperparámetros **solo** con validación cruzada de 5 pliegues dentro del entrenamiento, optimizando recall@40 %: `GridSearchCV` para las logísticas (C y número de nudos de los splines) y `RandomizedSearchCV` de 30 iteraciones para HistGradientBoosting (tasa de aprendizaje, iteraciones, profundidad, hojas mínimas y regularización L2).
- Registra en cada corrida el espacio de búsqueda, los mejores parámetros, la tabla completa de la búsqueda (`cv_results.csv`), las métricas de los tres conjuntos y el modelo.

```bash
# registra en el servidor MLflow de EC2
MLFLOW_TRACKING_URI=http://<IP_EC2>:<puerto> python src/experimentos_mlflow.py
# sin variable, registra en una base local mlflow.db (no se sube a git)
python src/experimentos_mlflow.py
```

Resultado de una ejecución local de verificación (recall@40 %, semilla 7; una sola partición, que varía varios puntos con otra semilla):

| Escenario | Modelo | Entrenamiento | Validación | Prueba |
|---|---|---|---|---|
| Sin laboratorio | Solo edad | 0,708 | 0,762 | 0,728 |
| Sin laboratorio | Logística | 0,784 | 0,790 | 0,761 |
| Sin laboratorio | Logística con splines e interacción | 0,786 | 0,796 | 0,761 |
| Sin laboratorio | HistGradientBoosting | 0,826 | 0,796 | 0,756 |
| Con laboratorio | Solo edad | 0,708 | 0,762 | 0,728 |
| Con laboratorio | Logística | 0,797 | 0,818 | 0,772 |
| Con laboratorio | Logística con splines e interacción | 0,800 | 0,823 | 0,783 |
| Con laboratorio | HistGradientBoosting | 0,852 | 0,834 | 0,761 |

### Elección del modelo servido (robustez en 20 particiones)

La retroalimentación de la Entrega 2 señaló que los splines con interacción eran más robustos que la logística simple. `src/experimentos_robustez.py` lo verifica con 20 particiones 80/20, sin pesos de clase y buscando los hiperparámetros dentro de cada entrenamiento (recall@40 % en prueba):

| Escenario | Modelo | Promedio | Mínimo | Particiones ≥ 75 % | PR-AUC |
|---|---|---|---|---|---|
| Sin laboratorio | Solo edad | 0,731 | 0,678 | 6/20 | 0,272 |
| Sin laboratorio | Logística simple | 0,782 | 0,733 | 19/20 | 0,371 |
| Sin laboratorio | **Splines con interacción** | **0,792** | 0,756 | **20/20** | 0,382 |
| Con laboratorio | **Logística simple** | 0,806 | 0,744 | 19/20 | 0,421 |
| Con laboratorio | Splines con interacción | 0,805 | 0,750 | 20/20 | 0,434 |

En comparación pareada (misma partición), sin laboratorio los splines ganan en 15 particiones, empatan en 4 y pierden en 1 (+1,0 punto, Wilcoxon p = 0,004). Con laboratorio no hay diferencia (−0,1 puntos, p = 0,55). Por eso la API y el tablero (`src/entrenar_modelos.py`) sirven:

- **Sin laboratorio:** regresión logística con splines en edad y cintura e interacción edad × cintura. C y número de nudos se eligen con validación cruzada en el entrenamiento.
- **Con laboratorio:** regresión logística simple, porque es más sencilla y rinde igual.

Ambos van **sin** pesos de clase para que la probabilidad mostrada no salga inflada. Frente a la edad sola, los modelos ganan de 5 a 8 puntos de recall en promedio y cumplen la meta en 19 o 20 de 20 particiones; la edad sola la cumple en 6. Los resultados están en `reports/figures/robustez_*.csv`.

Los experimentos oficiales de la entrega son los registrados en el servidor MLflow de AWS EC2 (capturas en `docs/evidencias_mlflow/`).

### Evidencias finales de MLflow

Los ocho experimentos finales (cuatro modelos en los escenarios sin y con laboratorio) se ejecutaron con `src/experimentos_mlflow.py` en una instancia de AWS EC2 (usuario `ubuntu`, commit `689ea9d`) y quedaron registrados en el experimento `MIAD-Metabolic-Health-Explorer-final`.

- [Lista de las 8 corridas finales](docs/evidencias_entrega_final/mlflow/01_final_lista_8_corridas.png), con la IP pública de la instancia EC2 en la URL del servidor MLflow (`54.167.5.59:8050`)
- [Logística con splines e interacción, sin laboratorio](docs/evidencias_entrega_final/mlflow/02_final_splines_sin_lab_metricas.png): recall@40 % en prueba 0,761
- [Logística con splines e interacción, con laboratorio](docs/evidencias_entrega_final/mlflow/03_final_splines_con_lab_metricas.png): recall@40 % en prueba 0,783

El experimento de robustez (`src/experimentos_robustez.py`, 20 particiones) también quedó registrado en el MLflow de EC2, como `MIAD-Metabolic-Health-Explorer-robustez`, con 11 corridas.

### Evidencias de la entrega final

[`docs/evidencias_entrega_final/`](docs/evidencias_entrega_final/README.md) reúne las capturas del despliegue en AWS EC2 (consola, terminal, Docker y security group), del tablero y la API funcionando con la IP pública de la instancia, y de los dos experimentos en MLflow. El índice de esa carpeta describe qué muestra cada imagen.

## 7. API

API REST con FastAPI en `api/`, desarrollada por **Antonio Agudelo** (`/health`, `/predict`, `/model/info`, validación de entradas y pruebas). Sobre ella se agregó la priorización por lotes.

| Método y ruta | Qué hace |
|---|---|
| `GET /health` | Estado de la API y versión del modelo |
| `POST /predict` | Probabilidad de un perfil, si queda priorizado, aporte de cada variable y advertencias de rango |
| `POST /predict/batch` | Ranking de una lista de perfiles en JSON, con el 40 % de la lista marcado |
| `POST /predict/batch/csv` | Lo mismo, cargando un archivo CSV (parámetro `escenario`: `auto`, `sin_lab` o `con_lab`) |
| `GET /model/info` | Métricas, umbral y rangos del modelo |

Si se envían los dos colesterol se usa el escenario con laboratorio; si no se envía ninguno, el escenario sin laboratorio. La documentación interactiva queda en `/docs`.

```bash
python -m pip install -r requirements-api.txt -r requirements-dev.txt
uvicorn api.main:app --reload      # http://127.0.0.1:8000/docs
pytest                             # 20 pruebas
```

Requiere Python 3.10 o superior. `scikit-learn` está fijado en 1.6.1: los modelos guardados con otra versión no cargan.

## 8. Tablero

Tablero hecho con Streamlit, siguiendo la opción A de la maqueta (`docs/04_maqueta_prototipo.md`). Tiene cuatro pantallas:

- **Exploración:** casos de diabetes o prediabetes por edad, IMC y otras variables, con filtros.
- **Simulador:** ingresa un perfil (sin o con laboratorio) y mira si queda dentro del 40 % de adultos que se priorizaría, con una explicación de qué pesa en el resultado.
- **Priorización por lotes:** carga un CSV con una lista de personas y obtén el ranking, con el 40 % de la lista marcado, un histograma y la descarga del resultado.
- **Modelo y datos:** resultados, curva de captura, estabilidad con 20 semillas, coeficientes y la evidencia de MLflow en EC2.

Las predicciones salen de la API cuando existe la variable de entorno `API_URL`; si no existe, el tablero usa el mismo servicio dentro del proceso, para poder abrirlo sin levantar la API.

```bash
python -m pip install -r requirements.txt
streamlit run app/tablero.py                                  # modo local, sin API
API_URL=http://127.0.0.1:8000 streamlit run app/tablero.py    # con la API en otra terminal
```

La primera vez entrena los modelos (unos 5 segundos) y los guarda en `models/`. También se pueden entrenar a mano con `python src/entrenar_modelos.py`. Los archivos `.joblib` no se suben al repo (están en el `.gitignore`). Cada pantalla se puede abrir directo con `?pantalla=Simulador` en la URL.

## 9. Despliegue con Docker

Desde la raíz del repositorio (requiere Docker):

```bash
export VERSION_CODIGO=$(git rev-parse --short HEAD)   # opcional, queda como versión del modelo
docker compose up --build -d
```

| Servicio | Dirección | Imagen |
|---|---|---|
| API | http://localhost:8000/docs | `Dockerfile.api` |
| Tablero | http://localhost:8501 | `Dockerfile.tablero` |

Las imágenes entrenan los modelos al construirse (los `.joblib` no están en git), corren con un usuario sin privilegios y tienen `HEALTHCHECK`. El tablero espera a que la API esté sana y le habla por `API_URL=http://api:8000`. Para detener: `docker compose down`. En una instancia EC2 son los mismos comandos; hay que abrir los puertos 8000 y 8501 en el *security group*.

## 10. Estructura del repositorio

```text
MIAD-DSA-Metabolic-Health-Explorer/
├── .github/
│   └── pull_request_template.md          # Plantilla para revisar cambios
├── .dvc/
│   ├── config                            # Remoto DVC todavía sin configurar
│   └── .gitignore
├── data/
│   └── raw/
│       ├── DIQ_H.xpt, DEMO_H.xpt, BMX_H.xpt,
│       │   BPX_H.xpt, TCHOL_H.xpt, HDL_H.xpt   # Tablas NHANES 2013-2014
│       ├── NHANES_consolidado.csv        # Conjunto consolidado (Entrega 2)
│       ├── NHANES_age_prediction.csv.dvc # Referencia DVC del conjunto de la Entrega 1
│       └── .gitignore
├── api/
│   ├── main.py                           # Endpoints (FastAPI)
│   ├── schemas.py                        # Contratos de entrada y salida
│   └── servicio.py                       # Carga del modelo e inferencia
├── tests/
│   ├── conftest.py
│   └── test_api.py                       # 20 pruebas de la API
├── app/
│   ├── tablero.py                        # Tablero (Streamlit)
│   └── predictor.py                      # Capa de predicción (API si existe API_URL)
├── src/
│   ├── entrenar_modelos.py               # Entrena los modelos que sirven la API y el tablero
│   ├── experimentos_mlflow.py            # Experimentos y búsqueda de hiperparámetros en MLflow
│   └── experimentos_robustez.py          # Logística frente a splines en 20 particiones
├── Dockerfile.api                        # Imagen de la API
├── Dockerfile.tablero                    # Imagen del tablero
├── docker-compose.yml                    # Levanta API y tablero
├── .dockerignore
├── models/                               # Modelos entrenados (no se suben al repo)
├── .streamlit/config.toml                # Tema del tablero
├── docs/
│   ├── 01_problema_y_contexto.md
│   ├── 02_pregunta_de_negocio_y_alcance.md
│   ├── 04_maqueta_prototipo.md
│   ├── 05_estructura_y_trabajo_en_equipo.md
│   └── mockup/                           # Maquetas HTML y capturas (opciones A y B)
├── scripts/
│   ├── 03_exploracion_inicial_nhanes.ipynb          # EDA de la Entrega 1 (conjunto UCI)
│   ├── 06_Exploracion_complementaria_nhanes.ipynb   # Consolidación de datos y EDA de la Entrega 2
│   ├── 07_modelos_iniciales_v1.ipynb                # Modelos con y sin laboratorio
│   └── 08_validacion_supuestos.ipynb                # Supuestos de los modelos y 20 semillas
├── reports/
│   └── figures/                          # Figuras y tablas del EDA (eda_*.png = Entrega 2)
├── .dvcignore
├── .env.example
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── pyproject.toml
├── README.md
├── requirements.txt                      # Todo (desarrollo y cuadernos)
├── requirements-api.txt                  # Solo la API (imagen Docker)
├── requirements-tablero.txt              # Solo el tablero (imagen Docker)
└── requirements-dev.txt                  # Pruebas (pytest, httpx)
```

Las figuras sin prefijo `eda_` y el notebook 03 corresponden al conjunto de la Entrega 1 y se conservan como referencia histórica. Los modelos entrenados (`models/`) se generan al construir la imagen o con `src/entrenar_modelos.py`.

## 11. Configuración local

Desde la raíz del proyecto:

```bash
conda create -n miad-despliegue-proyecto python=3.11 -y
conda activate miad-despliegue-proyecto
python -m pip install -r requirements.txt
python -m pip install ipykernel dvc seaborn scipy
```

`requirements.txt` instala lo necesario para los cuadernos, el tablero y la API (la API requiere Python 3.10 o superior). El notebook 06 requiere además `seaborn` y `scipy`, y la lectura de archivos `.xpt` se hace con `pandas.read_sas`. En VS Code selecciona el intérprete del entorno `miad-despliegue-proyecto`.

## 12. Exploración de datos

Abre [`scripts/06_Exploracion_complementaria_nhanes.ipynb`](scripts/06_Exploracion_complementaria_nhanes.ipynb) y ejecútalo de arriba abajo. Sus secciones son:

1. **Preparación de los datos:** carga de `DIQ_H`, definición de la variable objetivo, variables descartadas por fuga de información, incorporación de cuatro tablas adicionales y generación de `NHANES_consolidado.csv`.
2. **Primera mirada a la base completa:** tipos de datos y estadísticas descriptivas.
3. **Exploración de los adultos:** población, limpieza, balance del objetivo, calidad de los datos, diferencias entre positivos y negativos, porcentaje de casos por grupo, correlaciones, interacción edad × IMC y una referencia previa al modelo.
4. **Conclusiones:** hallazgos, decisiones para el modelado y limitaciones.

**Nota:** los resultados son exploratorios; no son una validación del desempeño predictivo.

## 13. Versionamiento de datos con DVC

El conjunto de la Entrega 1 está identificado por `data/raw/NHANES_age_prediction.csv.dvc`. Para verificar:

```bash
dvc version
dvc status
```

Los archivos `.xpt` y `NHANES_consolidado.csv` de la Entrega 2 están actualmente versionados en Git; migrarlos a DVC es una tarea pendiente del equipo. Si se modifican datos rastreados por DVC:

```bash
dvc add data/raw/<archivo>
git add data/raw/<archivo>.dvc
```

- `git push` publica commits de código y metadatos.
- `dvc push` y `dvc pull` publican y recuperan datos **si existe un remoto DVC configurado y tienes permisos**.

`.dvc/config` está vacío, por lo que **no se declara aún un remoto compartido operativo**. Nunca subas tokens o llaves de AWS a GitHub. Para pautas, consulta [CONTRIBUTING.md](CONTRIBUTING.md).

## 14. Colaboración

El desarrollo se hace mediante ramas, commits individuales y Pull Requests revisados hacia `main`, para mantener trazabilidad académica.

- [Guía del equipo](CONTRIBUTING.md): flujo Git, convenciones y DVC.
- [Plantilla de Pull Request](.github/pull_request_template.md).
- [Historial de hitos](CHANGELOG.md).
- [Estructura y guía de integración](docs/05_estructura_y_trabajo_en_equipo.md).

## 15. Hoja de ruta

| Hito | Estado |
|---|---|
| Contexto, problema, pregunta de negocio y criterio de éxito | Actualizados para la Entrega 2 |
| Datos consolidados y exploración (EDA) | Completos (notebook 06) |
| Maqueta del prototipo | Dos opciones documentadas; **capturas y HTML pendientes de actualizar** con las variables nuevas |
| DVC | Seguimiento del conjunto de la Entrega 1; remoto y datos nuevos por configurar |
| Modelos supervisados (referencia, regresión logística, splines, árboles) | Listos (cuadernos 07 y 08) |
| Experimentos en MLflow (servidor en AWS EC2) | Registrados (cuaderno `07_modelos_mlflow_ec2`; capturas en `docs/evidencias_mlflow/`) |
| API con FastAPI | Lista (`api/`, 20 pruebas), con priorización por lotes |
| Tablero con Streamlit | Listo (`app/tablero.py`), con pantalla de lotes; consume la API |
| Contenedores Docker | Listos y probados en local (`docker-compose.yml`) |
| Despliegue en AWS (EC2) | Hecho: API y tablero con Docker en EC2 (evidencias en `docs/evidencias_entrega_final/`) |
| Experimentos oficiales en MLflow (EC2) con `experimentos_mlflow.py` y `experimentos_robustez.py` | Hechos: 8 corridas finales y 11 de robustez |
| Manual de usuario y manual de instalación | Pendientes |
| Variable objetivo con hemoglobina glicosilada | Trabajo futuro (limitación declarada) |

Versionado propuesto: `0.1.0` documentación inicial, `0.2.0` modelado, `0.3.0` API, `0.4.0` tablero, `0.5.0` Docker y `1.0.0` prototipo final. Las versiones no están liberadas todavía.

## 16. Referencias

- [CDC — NHANES 2013–2014](https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=2013).
- [CDC — Documentación de DIQ_H (diabetes)](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/DIQ_H.htm).
- [UCI — NHANES Age Prediction Subset (ID 887)](https://archive.ics.uci.edu/dataset/887/national+health+and+nutrition+health+survey+2013-2014+(nhanes)+age+prediction+subset), conjunto usado en la Entrega 1. DOI: [10.24432/C5BS66](https://doi.org/10.24432/C5BS66).
- Dinh, A. et al. (2019). *A data-driven approach to predicting diabetes and cardiovascular disease with machine learning*. *BMC Medical Informatics and Decision Making*. [DOI: 10.1186/s12911-019-0918-5](https://doi.org/10.1186/s12911-019-0918-5).
