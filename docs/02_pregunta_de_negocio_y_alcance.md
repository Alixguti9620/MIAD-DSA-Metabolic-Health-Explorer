# 2. Pregunta de negocio y alcance del proyecto

**Proyecto:** Metabolic Health Explorer  
**Asignatura:** Despliegue de Soluciones Analíticas — MIAD 
**Estado:** Propuesta inicial; sujeta a validación exploratoria del conjunto de datos

## 2.1 Necesidad y propósito del producto

A partir del problema documentado en [`01_problema_y_contexto.md`](01_problema_y_contexto.md), el proyecto busca facilitar a estudiantes, investigadores y analistas la exploración de perfiles metabólicos en el subconjunto NHANES 2013–2014 disponible en UCI. En particular, se compararán personas que **reportaron** haber recibido un diagnóstico de diabetes con quienes **no lo reportaron**, siempre que la codificación de `DIQ010` permita definir ambos grupos de forma válida.

La solución combinará un tablero de indicadores descriptivos con un modelo supervisado sencillo, accesible por una API. El objetivo de producto es facilitar la **consulta, comparación y demostración técnica** de resultados, no apoyar decisiones clínicas individuales.

## 2.2 Pregunta de negocio principal

**¿Cómo facilitar la identificación y exploración de patrones en indicadores metabólicos y características demográficas asociados con el antecedente de diabetes reportada en el subconjunto NHANES 2013–2014, mediante una aplicación interactiva que integre análisis descriptivo y clasificación supervisada?**

Esta pregunta se traduce en una necesidad concreta del usuario: explorar diferencias entre grupos y consultar el resultado de un modelo sin tener que ejecutar manualmente el procesamiento de datos y el código de inferencia.

### Preguntas analíticas de apoyo

1. ¿Cómo se distribuyen el índice de masa corporal (IMC), la glucosa y la insulina entre quienes reportan y quienes no reportan un diagnóstico de diabetes?
2. ¿Qué diferencias descriptivas se observan al segmentar por edad, sexo registrado y actividad física reportada?
3. ¿Qué capacidad tienen las variables disponibles para distinguir **la respuesta sobre diagnóstico reportado** mediante un clasificador supervisado sencillo?
4. ¿Cómo presentar las comparaciones descriptivas y las inferencias de un modo reproducible y comprensible para el usuario?

Las respuestas se obtendrán **después** de realizar el análisis exploratorio y entrenar los modelos.

## 2.3 Objetivos

### Objetivo general

**Desarrollar y desplegar un prototipo funcional que permita explorar indicadores metabólicos del subconjunto NHANES 2013–2014 y consultar, mediante una API REST, un modelo supervisado para clasificar el antecedente de diabetes reportada.**

### Objetivos específicos

1. Preparar y describir el conjunto de datos, verificando la codificación y distribución de `DIQ010` y de las variables explicativas.
2. Diseñar visualizaciones interactivas para comparar indicadores metabólicos entre los grupos de respuesta válidos.
3. Entrenar y evaluar un clasificador de referencia y un modelo, con una partición adecuada de entrenamiento y prueba.
4. Empaquetar el preprocesamiento y modelo seleccionado, y exponer una ruta de predicción.
5. Desarrollar un tablero que consulte el modelo exclusivamente a través de la API y muestre estadísticas descriptivas.
6. Contenerizar el prototipo con Docker y mantener trazabilidad de código y datos mediante Git/GitHub y DVC.

## 2.4 Usuarios y decisiones que facilita

| Usuario previsto | Necesidad | Funcionalidad del producto |
|---|---|---|
| Estudiante o investigador | Examinar diferencias entre perfiles en una muestra histórica | Filtros, distribuciones y estadísticas descriptivas |
| Analista de salud pública, en contexto exploratorio | Consultar patrones y segmentos del conjunto de datos | Tablero comparativo y descripción de limitaciones |
| Docente o equipo técnico | Demostrar un sistema analítico integrado | Formulario de inferencia, API REST, contenedores y evidencias reproducibles |


## 2.5 Alcance funcional

### Módulo A: exploración descriptiva

- Visualizar el número de registros por categoría válida de `DIQ010`.
- Comparar distribuciones de IMC, glucosa e insulina entre los grupos.
- Aplicar filtros por grupos de edad, sexo registrado y actividad física, según disponibilidad y validez de las categorías.

### Módulo B: simulador de clasificación

- Introducir manualmente los valores exigidos por el modelo final mediante un formulario.
- Validar tipos, rangos y categorías aceptadas antes de solicitar una predicción.
- Consultar a través de la API una clasificación del **antecedente de diabetes reportada** y, si está disponible y adecuadamente evaluada, una probabilidad estimada.

### Módulo C: transparencia del prototipo

- Exponer el origen y periodo de los datos, variables utilizadas y métricas calculadas en evaluación.
- Describir las limitaciones del modelo y del conjunto de datos.

## 2.6 Alcance analítico y modelado

**Fuente de datos:** únicamente *NHANES 2013–2014 Age Prediction Subset* (UCI 887), sin integrar tablas adicionales en esta fase.

**Objetivo predictivo propuesto:** una etiqueta binaria derivada de `DIQ010`, que diferencia respuestas afirmativas y negativas a la pregunta sobre diagnóstico de diabetes. Se verificarán primero los códigos originales: las respuestas especiales, ambiguas o no válidas **no se tratarán automáticamente como negativas**.

**Candidatos a variables explicativas:** edad (`RIDAGEYR`), sexo registrado (`RIAGENDR`), actividad física (`PAQ605`), IMC (`BMXBMI`), glucosa (`LBXGLU`), prueba oral de glucosa (`LBXGLT`) e insulina (`LBXIN`). La selección definitiva dependerá de la revisión de datos, de las categorías y de la evaluación de posibles fugas de información. 

**Modelo:** regresión logística como primera opción, comparada contra un clasificador base y, solo si aporta valor, un árbol de decisión pequeño. Los cambios de preprocesamiento se ajustarán únicamente con datos de entrenamiento, usando un `Pipeline` de Scikit-learn.

**Evaluación:** partición de entrenamiento/prueba y métricas apropiadas al balance observado de clases (matriz de confusión, precisión, recall, F1 y ROC-AUC cuando corresponda). No se fijarán metas numéricas antes de verificar la distribución de los datos.


## 2.7 Alcance tecnológico

| Componente | Tecnología propuesta | Resultado verificable |
|---|---|---|
| Preparación y entrenamiento | Python, pandas, Scikit-learn | Pipeline y modelo serializado |
| Servicio de inferencia | Por Definir | `POST /predict`, `GET /health` y documentación de API |
| Tablero | Por Definir | Gráficas y formulario que invoca la API |
| Empaquetamiento | Docker / Docker Compose | Aplicación reproducible en contenedores |
| Código y colaboración | Git / GitHub | Commits, ramas y Pull Requests |
| Versionamiento de datos | DVC | Datos rastreados mediante metadatos DVC |


## 2.8 Fuera de alcance

- Diagnosticar diabetes, prediabetes o enfermedades cardiovasculares.
- Predecir incidencia futura de diabetes o recomendar tratamientos.
- Utilizar el resultado para clasificar pacientes reales o decidir prioridades de atención médica.
- Integrar historias clínicas, datos personales identificables o fuentes de información en tiempo real.
- Replicar los modelos complejos o las métricas publicadas por Dinh et al. (2019).
- Inferir tasas representativas de la población estadounidense sin revisar el diseño muestral y las ponderaciones de NHANES.

## 2.9 Criterios de éxito del prototipo

El proyecto se considerará funcional cuando se pueda demostrar que:

1. Los datos y el procesamiento pueden reproducirse desde el repositorio y DVC.
2. El modelo se entrena, evalúa y guarda con un procedimiento documentado.
3. La API recibe entradas válidas, responde a la inferencia y maneja errores de validación.
4. El tablero ofrece visualizaciones y consume las predicciones **a través de la API**, no cargando el modelo directamente.
5. Los contenedores pueden construirse y ejecutarse siguiendo instrucciones de configuración.
6. Se presentan métricas reales y limitaciones, sin afirmaciones clínicas o de representatividad que los datos no sustenten.

## 2.10 Riesgo inicial y validación pendiente

El principal riesgo analítico es que, tras recodificar `DIQ010`, el número de respuestas positivas válidas sea pequeño o que algunas variables introduzcan confusión interpretativa. Antes de comprometer el modelo final, se verificará el balance de clases y se documentará la exclusión de respuestas especiales. Si la clasificación resulta poco viable, el equipo deberá revisar formalmente el alcance y justificar cualquier cambio de etiqueta; no se asumirá de antemano un buen desempeño.

## Referencias

[1] UCI Machine Learning Repository. *National Health and Nutrition Health Survey 2013–2014 (NHANES) Age Prediction Subset*. https://archive.ics.uci.edu/dataset/887/national+health+and+nutrition+health+survey+2013-2014+(nhanes)+age+prediction+subset. DOI: 10.24432/C5BS66.

[2] Dinh, A., Miertschin, S., Young, A., & Mohanty, S. D. (2019). *A data-driven approach to predicting diabetes and cardiovascular disease with machine learning*. *BMC Medical Informatics and Decision Making*, 19, 211. https://doi.org/10.1186/s12911-019-0918-5.

[3] Centers for Disease Control and Prevention, National Center for Health Statistics. *NHANES 2013–2014 Overview*. https://wwwn.cdc.gov/Nchs/Nhanes/continuousnhanes/overview.aspx?BeginYear=2013.
