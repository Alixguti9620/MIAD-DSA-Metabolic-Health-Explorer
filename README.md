# Metabolic Health Explorer

**Proyecto académico — Maestría en Inteligencia Analítica de Datos (MIAD), Universidad de los Andes**  
**Materia:** Despliegue de Soluciones Analíticas  
**Repositorio:** [MIAD-DSA-Metabolic-Health-Explorer](https://github.com/Alixguti9620/MIAD-DSA-Metabolic-Health-Explorer)

> **Estado: versión documental 0.1.0.** Se cuenta con definición inicial del problema y del alcance, un notebook de exploración, resultados descriptivos, maquetas del prototipo y seguimiento local de datos con DVC. El modelo supervisado, la API REST, el tablero y Docker son **componentes futuros**, no funcionalidades implementadas.

## 1. Contexto y propósito

NHANES es una encuesta de salud y nutrición de Estados Unidos. Este proyecto utiliza el subconjunto **NHANES 2013–2014 Age Prediction Subset** publicado en UCI para estudiar diferencias entre indicadores metabólicos asociados con la **diabetes previamente reportada**. A diferencia del uso original de UCI para predecir un grupo de edad, nuestro objetivo propuesto es la respuesta a la pregunta de diabetes reportada (`DIQ010`).

**Pregunta de negocio**

> ¿Cómo facilitar la identificación y exploración de patrones en indicadores metabólicos y características demográficas asociados con el antecedente de diabetes reportada en el subconjunto NHANES 2013–2014, mediante una aplicación interactiva que integre análisis descriptivo y clasificación supervisada?

El producto se orienta a la exploración por parte de estudiantes, investigadores y analistas de salud pública. **No es un dispositivo de diagnóstico, una predicción de enfermedad futura ni una herramienta validada de decisión médica.**

Documentación de la Entrega 1:

- [01 — Problema y contexto](docs/01_problema_y_contexto.md)
- [02 — Pregunta de negocio y alcance](docs/02_pregunta_de_negocio_y_alcance.md)
- [03 — Exploración inicial (notebook)](scripts/03_exploracion_inicial_nhanes.ipynb)
- [04 — Maqueta del prototipo](docs/04_maqueta_prototipo.md)

## 2. Datos y variable objetivo

- **Fuente:** [UCI Machine Learning Repository, dataset 887](https://archive.ics.uci.edu/dataset/887/national+health+and+nutrition+health+survey+2013-2014+(nhanes)+age+prediction+subset).
- **Ciclo original:** NHANES 2013–2014.
- **Tamaño:** la ficha de UCI declara 6.287 instancias, pero el archivo publicado contiene **2.278 registros** (versionado con DVC). Ver la nota sobre el tamaño del dataset más abajo.
- **Objetivo de origen:** `age_group`.
- **Objetivo propuesto del equipo:** `DIQ010`, recodificado para clasificar **diabetes reportada**.

| Variable | Interpretación en este proyecto |
|---|---|
| `SEQN` | Identificador; no predictor |
| `age_group` | Etiqueta de edad del dataset original |
| `RIDAGEYR` | Edad |
| `RIAGENDR` | Sexo registrado |
| `PAQ605` | Actividad física vigorosa recreativa reportada |
| `BMXBMI` | Índice de masa corporal |
| `LBXGLU` | Glucosa en ayunas |
| `LBXGLT` | Glucosa en prueba de tolerancia oral |
| `LBXIN` | Insulina |
| `DIQ010` | Diagnóstico de diabetes previamente reportado |

La codificación a verificar para `DIQ010` incluye 1 = sí, 2 = no, 3 = borderline/prediabetes y códigos de respuesta especial. **El notebook explora las respuestas y restringe ciertas comparaciones a 1 y 2.** No afirmar que «no reportada» significa clínicamente «no tiene diabetes».

**Nota sobre el tamaño del dataset**

| Etapa | Registros | Detalle |
|---|---|---|
| Ficha de UCI («# Instances») | 6.287 | Cifra declarada en la página del dataset 887 |
| Archivo publicado y cargado en el EDA | 2.278 | 10 columnas, sin valores nulos |
| Respuestas de `DIQ010` | 2.278 | 21 Sí (1) · 2.199 No (2) · 58 prediabetes/borderline (3); no aparecen los códigos 7 ni 9 |
| Comparaciones Sí/No del EDA y la maqueta | 2.220 | Se excluyen los 58 registros con `DIQ010 = 3` (0,95% de positivos) |
| Tabla de actividad vigorosa | 2.219 | Se excluye además 1 registro con `PAQ605 = 7` |

La diferencia entre 6.287 y 2.278 no proviene del procesamiento del equipo: el archivo descargado de UCI ya tiene 2.278 filas, y la ficha no describe cómo se seleccionaron los registros del subconjunto. El notebook lo advierte al cargar los datos. Todas las cifras del proyecto se calculan sobre el archivo real.

Los resultados proceden de este **subconjunto**, no representan por sí solos estimaciones nacionales ponderadas de Estados Unidos.

## 3. Estructura actual del repositorio

```text
MIAD-DSA-Metabolic-Health-Explorer/
├── .github/
│   └── pull_request_template.md          # Plantilla para revisar cambios
├── .dvc/
│   ├── config                            # Remoto DVC todavía sin configurar
│   └── .gitignore
├── data/
│   └── raw/
│       ├── NHANES_age_prediction.csv    # Archivo local; no subirlo directamente a Git
│       ├── NHANES_age_prediction.csv.dvc # Referencia versionada con DVC
│       └── .gitignore
├── docs/
│   ├── 01_problema_y_contexto.md
│   ├── 02_pregunta_de_negocio_y_alcance.md
│   ├── 04_maqueta_prototipo.md
│   ├── 05_estructura_y_trabajo_en_equipo.md
│   └── mockup/
│       ├── maqueta_prototipo.html       # Opción A: tablero por pestañas
│       ├── img/                         # Capturas de la opción A y de la arquitectura
│       └── opcion_b/
│           ├── maqueta_opcion_b.html    # Opción B: tablero centrado en el perfil
│           └── img/                     # Capturas de la opción B
├── scripts/
│   └── 03_exploracion_inicial_nhanes.ipynb
├── reports/
│   └── figures/                         # Gráficas y tablas exportadas del EDA
├── .dvcignore
├── .env.example
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── pyproject.toml
├── README.md
└── requirements.txt
```

El contenido previo de `docs/`, `scripts/`, `data/` y `reports/` se conserva. Se añadieron documentos organizativos sin mover el notebook. Los archivos `.git/` y las cachés no forman parte del paquete compartido.

## 4. Configuración local

Desde la raíz del proyecto:

```bash
conda create -n miad-despliegue-proyecto python=3.10 -y
conda activate miad-despliegue-proyecto
python -m pip install -r requirements.txt
python -m pip install ipykernel dvc
```

El archivo original `requirements.txt` incluye `pandas`, `matplotlib` y `ucimlrepo` y **se ha mantenido intacto**. La instalación adicional permite abrir el notebook desde Jupyter/VS Code y utilizar DVC. En VS Code selecciona el intérprete del entorno `miad-despliegue-proyecto`.

## 5. Exploración inicial

Abre el notebook existente:

[`scripts/03_exploracion_inicial_nhanes.ipynb`](scripts/03_exploracion_inicial_nhanes.ipynb)

Sus secciones documentan la carga del CSV (o su recuperación desde UCI 887 si no está disponible), dimensiones y nulos, distribución de `DIQ010`, comparaciones de indicadores metabólicos y actividad física reportada. El notebook puede exportar los resultados a `reports/figures/`.

En la copia compartida se incluyen, entre otros:

- `conteo_diabetes.csv` y `conteo_diabetes.png`.
- `indicadores_por_diabetes.csv`.
- `actividad_por_diabetes.csv`.
- `boxplot_BMXBMI.png` y `boxplot_LBXGLU.png`.

**Nota:** los gráficos existentes son resultados de exploración, no validaciones del desempeño predictivo. El equipo debe revisar supuestos, codificaciones e interpretaciones antes del reporte final.

## 6. Versionamiento de datos con DVC

El dataset está identificado por `data/raw/NHANES_age_prediction.csv.dvc`. La versión local del CSV estaba disponible en el ZIP original y el archivo `.dvc` conserva su referencia. Para verificar:

```bash
dvc version
dvc status
```

Si modificas los datos:

```bash
dvc add data/raw/NHANES_age_prediction.csv
git add data/raw/NHANES_age_prediction.csv.dvc
```

- `git push` publica commits de código y metadatos Git.
- `dvc push` publica los datos en un remoto DVC **si existe y está configurado**.
- `dvc pull` los recupera desde el remoto DVC **si existe y tienes permisos**.

En la copia revisada, `.dvc/config` está vacío; por eso **no se declara aún un remoto compartido operativo**. Nunca subas tokens o llaves de AWS a GitHub. Para pautas de contribución, consulta [CONTRIBUTING.md](CONTRIBUTING.md).

## 7. Colaboración

El desarrollo se hará mediante ramas, commits individuales y Pull Requests revisados hacia `main`. El objetivo es mantener trazabilidad académica y evitar que los cambios de una persona sobrescriban los de otra.

- [Guía del equipo](CONTRIBUTING.md): flujo Git, convenciones y DVC.
- [Plantilla de Pull Request](.github/pull_request_template.md): explicación, pruebas y pendientes.
- [Historial de hitos](CHANGELOG.md): versiones del proyecto.
- [Estructura y guía de integración](docs/05_estructura_y_trabajo_en_equipo.md).

## 8. Hoja de ruta

| Hito | Estado en esta copia |
|---|---|
| Contexto, problema y pregunta de negocio | Documentados inicialmente |
| Dataset y exploración inicial | Notebook y salidas disponibles; ampliación pendiente |
| Maqueta del prototipo | Dos opciones documentadas (A y B) |
| DVC | Seguimiento local incluido; remoto por configurar |
| Modelo supervisado (regresión logística o árbol pequeño) | Pendiente |
| API con FastAPI | Pendiente |
| Tablero con Streamlit | Pendiente |
| Contenedores Docker y despliegue | Pendiente |

Versionado propuesto: `0.1.0` documentación inicial, `0.2.0` modelo, `0.3.0` API, `0.4.0` tablero, `0.5.0` Docker y `1.0.0` prototipo final. Las versiones futuras **no están liberadas**.

## 9. Referencias

- [UCI — NHANES Age Prediction Subset (ID 887)](https://archive.ics.uci.edu/dataset/887/national+health+and+nutrition+health+survey+2013-2014+(nhanes)+age+prediction+subset). DOI: [10.24432/C5BS66](https://doi.org/10.24432/C5BS66).
- [CDC — NHANES 2013–2014](https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=2013).
- Dinh, A. et al. (2019). *A data-driven approach to predicting diabetes and cardiovascular disease with machine learning*. *BMC Medical Informatics and Decision Making*. [DOI: 10.1186/s12911-019-0918-5](https://doi.org/10.1186/s12911-019-0918-5).

---

*Uso académico y exploratorio. Las clasificaciones no constituyen diagnóstico, tamizaje clínico ni asesoramiento médico.*
