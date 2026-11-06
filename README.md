# Metabolic Health Explorer

**Proyecto académico — Maestría en Inteligencia Analítica de Datos (MIAD), Universidad de los Andes**  
**Materia:** Despliegue de Soluciones Analíticas  
**Repositorio:** [MIAD-DSA-Metabolic-Health-Explorer](https://github.com/Alixguti9620/MIAD-DSA-Metabolic-Health-Explorer)

> **Estado: Entrega 2 en desarrollo.** Están completos el problema, la pregunta de negocio con criterio de éxito, la consolidación de datos NHANES 2013-2014 y el análisis exploratorio. El modelo supervisado, el seguimiento en MLflow, la API REST, el tablero y Docker son **componentes en desarrollo**, no funcionalidades implementadas.

## 1. Contexto y propósito

National Health and Nutrition Examination Survey (NHANES) es la encuesta de salud y nutrición nacional de Estados Unidos, regulada por el Centro de Control y Prevención de Enfermedades (CDC). Sus datos permiten monitorear el estado de salud y nutricional de la población y los factores de riesgo de enfermedades crónicas (NCHS, 2024).

La diabetes y la prediabetes se detectan con pruebas de laboratorio que son costosas de aplicar a toda la población. Los programas de tamizaje con recursos limitados necesitan decidir **a quién ofrecerle primero la prueba**. Medidas no invasivas como la edad, el IMC, la cintura y la presión arterial se toman en cualquier consulta y pueden usarse para ordenar a las personas por prioridad.

**Pregunta de negocio**

> ¿Es posible priorizar a los adultos con mayor probabilidad de tener diabetes o prediabetes diagnosticada, usando solo medidas no invasivas y de bajo costo, de modo que se capture al menos el 75 % de los casos tamizando como máximo al 40 % de la población?

**Criterio de éxito** (sobre el conjunto de prueba): recall >= 75 % señalando como máximo al 40 % de los adultos, superando la línea base de usar solo la edad (72,3 % en el EDA). Esta meta está **pendiente de verificación** con el modelo entrenado.

**Usuario principal:** analista o equipo de salud pública que planifica campañas de tamizaje. **No es un dispositivo de diagnóstico, una predicción de enfermedad futura ni una herramienta validada de decisión médica.**

Documentación:

- [01 — Problema y contexto](docs/01_problema_y_contexto.md)
- [02 — Pregunta de negocio y alcance](docs/02_pregunta_de_negocio_y_alcance.md)
- [04 — Maqueta del prototipo](docs/04_maqueta_prototipo.md)
- [05 — Estructura y trabajo en equipo](docs/05_estructura_y_trabajo_en_equipo.md)
- Exploración inicial de la Entrega 1: [`scripts/03_exploracion_inicial_nhanes.ipynb`](scripts/03_exploracion_inicial_nhanes.ipynb)
- Exploración complementaria de la Entrega 2: [`scripts/06_Exploracion_complementaria_nhanes.ipynb`](scripts/06_Exploracion_complementaria_nhanes.ipynb)

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

## 5. Estructura del repositorio

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
├── docs/
│   ├── 01_problema_y_contexto.md
│   ├── 02_pregunta_de_negocio_y_alcance.md
│   ├── 04_maqueta_prototipo.md
│   ├── 05_estructura_y_trabajo_en_equipo.md
│   └── mockup/                           # Maquetas HTML y capturas (opciones A y B)
├── scripts/
│   ├── 03_exploracion_inicial_nhanes.ipynb          # EDA de la Entrega 1 (conjunto UCI)
│   └── 06_Exploracion_complementaria_nhanes.ipynb   # Consolidación de datos y EDA de la Entrega 2
├── reports/
│   └── figures/                          # Figuras y tablas del EDA (eda_*.png = Entrega 2)
├── .dvcignore
├── .env.example
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── pyproject.toml
├── README.md
└── requirements.txt
```

Las figuras sin prefijo `eda_` y el notebook 03 corresponden al conjunto de la Entrega 1 y se conservan como referencia histórica. Las carpetas de modelado, API, tablero y Docker se agregarán conforme se implementen.

## 6. Configuración local

Desde la raíz del proyecto:

```bash
conda create -n miad-despliegue-proyecto python=3.10 -y
conda activate miad-despliegue-proyecto
python -m pip install -r requirements.txt
python -m pip install ipykernel dvc seaborn scipy
```

`requirements.txt` incluye `pandas`, `matplotlib` y `ucimlrepo`. El notebook 06 requiere además `seaborn` y `scipy`, y la lectura de archivos `.xpt` se hace con `pandas.read_sas`. En VS Code selecciona el intérprete del entorno `miad-despliegue-proyecto`.

## 7. Exploración de datos

Abre [`scripts/06_Exploracion_complementaria_nhanes.ipynb`](scripts/06_Exploracion_complementaria_nhanes.ipynb) y ejecútalo de arriba abajo. Sus secciones son:

1. **Preparación de los datos:** carga de `DIQ_H`, definición de la variable objetivo, variables descartadas por fuga de información, incorporación de cuatro tablas adicionales y generación de `NHANES_consolidado.csv`.
2. **Primera mirada a la base completa:** tipos de datos y estadísticas descriptivas.
3. **Exploración de los adultos:** población, limpieza, balance del objetivo, calidad de los datos, diferencias entre positivos y negativos, porcentaje de casos por grupo, correlaciones, interacción edad × IMC y una referencia previa al modelo.
4. **Conclusiones:** hallazgos, decisiones para el modelado y limitaciones.

**Nota:** los resultados son exploratorios; no son una validación del desempeño predictivo.

## 8. Versionamiento de datos con DVC

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

## 9. Colaboración

El desarrollo se hace mediante ramas, commits individuales y Pull Requests revisados hacia `main`, para mantener trazabilidad académica.

- [Guía del equipo](CONTRIBUTING.md): flujo Git, convenciones y DVC.
- [Plantilla de Pull Request](.github/pull_request_template.md).
- [Historial de hitos](CHANGELOG.md).
- [Estructura y guía de integración](docs/05_estructura_y_trabajo_en_equipo.md).

## 10. Hoja de ruta

| Hito | Estado |
|---|---|
| Contexto, problema, pregunta de negocio y criterio de éxito | Actualizados para la Entrega 2 |
| Datos consolidados y exploración (EDA) | Completos (notebook 06) |
| Maqueta del prototipo | Dos opciones documentadas; **capturas y HTML pendientes de actualizar** con las variables nuevas |
| DVC | Seguimiento del conjunto de la Entrega 1; remoto y datos nuevos por configurar |
| Modelos supervisados (referencia, regresión logística, árboles) | Pendiente |
| Experimentos en MLflow (servidor en AWS EC2) | Pendiente |
| API con FastAPI | Pendiente |
| Tablero con Streamlit | Pendiente |
| Contenedores Docker | Pendiente |

Versionado propuesto: `0.1.0` documentación inicial, `0.2.0` modelado, `0.3.0` API, `0.4.0` tablero, `0.5.0` Docker y `1.0.0` prototipo final. Las versiones futuras **no están liberadas**.

## 11. Referencias

- [CDC — NHANES 2013–2014](https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=2013).
- [CDC — Documentación de DIQ_H (diabetes)](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/DIQ_H.htm).
- [UCI — NHANES Age Prediction Subset (ID 887)](https://archive.ics.uci.edu/dataset/887/national+health+and+nutrition+health+survey+2013-2014+(nhanes)+age+prediction+subset), conjunto usado en la Entrega 1. DOI: [10.24432/C5BS66](https://doi.org/10.24432/C5BS66).
- Dinh, A. et al. (2019). *A data-driven approach to predicting diabetes and cardiovascular disease with machine learning*. *BMC Medical Informatics and Decision Making*. [DOI: 10.1186/s12911-019-0918-5](https://doi.org/10.1186/s12911-019-0918-5).

---

*Uso académico y exploratorio. Las clasificaciones no constituyen diagnóstico, tamizaje clínico ni asesoramiento médico.*
