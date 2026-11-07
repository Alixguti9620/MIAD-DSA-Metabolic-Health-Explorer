# 2. Pregunta de negocio y alcance del proyecto

**Proyecto:** Metabolic Health Explorer  
**Asignatura:** Despliegue de Soluciones Analíticas — MIAD  

## 2.1 Necesidad y propósito del producto

Como se plantea en 01_problema_y_contexto.md, un equipo de salud pública que diseña una campaña de tamizaje de diabetes y prediabetes no puede aplicar pruebas de laboratorio a toda la población y necesita decidir **a quién priorizar**. El producto ofrece un criterio de priorización basado en medidas sencillas y de bajo costo, y lo expone mediante un tablero y una API. Se manejan dos escenarios: **sin laboratorio** (edad, género, IMC, cintura y presión arterial) y **con laboratorio**, que suma colesterol total y HDL y por eso requiere una muestra de sangre.

El objetivo de producto es **apoyar la planificación de campañas de tamizaje poblacional**, no diagnosticar ni apoyar decisiones clínicas individuales.

## 2.2 Pregunta de negocio principal

**¿Es posible priorizar a los adultos con mayor probabilidad de tener diabetes o prediabetes diagnosticada, usando medidas sencillas y de bajo costo (sin laboratorio o, como variante, con colesterol), de modo que se capture al menos el 75 % de los casos tamizando como máximo al 40 % de la población?**

La pregunta orienta una decisión concreta: **qué fracción de la población adulta priorizar para la prueba de laboratorio** y con qué cobertura esperada de casos.

### Preguntas analíticas de apoyo

1. ¿Qué población corresponde al problema y con cuántos casos se cuenta? (EDA: adultos, 6.110 registros, 902 positivos, 14,8 %)
2. ¿Qué tan completos y confiables son los datos (nulos, aberrantes, atípicos, redundancias)?
3. ¿Cómo se distribuyen y cómo cambia la proporción de casos según edad, IMC, cintura, presión arterial, colesterol y otros segmentos?
4. ¿Qué tan bien captura casos una regla de una sola variable y cuánto mejora un modelo que combine varias?
5. ¿Cómo presentar las comparaciones y las inferencias de forma reproducible y comprensible para el usuario?

## 2.3 Criterio de éxito de negocio

Sobre el conjunto de prueba (partición estratificada que el modelo no vio en el entrenamiento), el modelo seleccionado debe cumplir:

1. **Recall >= 75 %** señalando como máximo al **40 %** de los adultos con mayor probabilidad.
2. **Superar la línea base de usar solo la edad**, que en el EDA captura 72,3 % de los casos con el mismo esfuerzo de tamizaje (la selección aleatoria captura 40 %).
3. Métricas complementarias que se reportarán siempre: ROC-AUC, PR-AUC, precisión y F1.
4. El criterio se evalúa por separado en los dos escenarios (sin y con laboratorio).
5. Como el resultado de una sola partición varía varios puntos, se reporta el promedio de 20 particiones distintas además de la partición base (semilla 7).



## 2.4 Objetivos

### Objetivo general

**Desarrollar y desplegar un prototipo funcional que permita explorar el perfil de las personas con diabetes o prediabetes reportada en NHANES 2013-2014 y consultar, mediante una API REST, un modelo supervisado que priorice a los adultos para el tamizaje.**

### Objetivos específicos

1. Preparar y describir el conjunto de datos consolidado, verificando la codificación, los nulos y los valores atípicos, y documentando la población y la variable objetivo.
2. Entrenar y evaluar un clasificador de referencia y modelos candidatos con partición estratificada, registrando los experimentos en MLflow.
3. Verificar el criterio de éxito de negocio sobre el conjunto de prueba, en los dos escenarios, y fijar el umbral de decisión.
4. Empaquetar el preprocesamiento y el modelo seleccionado y exponer una ruta de predicción.
5. Desarrollar un tablero que consulte el modelo exclusivamente a través de la API y muestre estadísticas descriptivas.
6. Contenerizar el prototipo con Docker y mantener trazabilidad de código y datos mediante Git/GitHub y DVC.

## 2.5 Usuarios y decisiones que facilita

| Usuario previsto | Necesidad | Funcionalidad del producto |
|---|---|---|
| Analista o equipo de salud pública (usuario principal) | Decidir a quién priorizar en una campaña de tamizaje y con qué cobertura de casos | Simulador de priorización, métricas y curva de captura de casos |
| Estudiante o investigador | Examinar diferencias entre perfiles en una muestra histórica | Filtros, distribuciones y tasas por segmento |

## 2.6 Alcance funcional

### Módulo A: exploración descriptiva

- Visualizar el número de registros y la proporción de casos de diabetes o prediabetes en adultos.
- Comparar las distribuciones de edad, IMC, cintura, presión arterial y colesterol entre los grupos.
- Mostrar la tasa de casos por grupo de edad, categoría de IMC, género, raza/etnia, ingreso, cintura elevada y presión sistólica.
- Aplicar filtros por grupo de edad y género, según la disponibilidad de datos.

### Módulo B: simulador de priorización

- Introducir manualmente los valores exigidos por el modelo final mediante un formulario.
- Validar tipos, rangos y categorías aceptadas antes de solicitar una predicción.
- Consultar a través de la API la probabilidad estimada y si el perfil queda dentro del grupo priorizado según el umbral definido.

### Módulo C: transparencia del prototipo

- Exponer el origen y periodo de los datos, las variables utilizadas y las métricas calculadas en la evaluación.
- Mostrar la curva de captura de casos frente a la línea base de edad y la matriz de confusión.
- Describir las limitaciones del modelo y de los datos.

## 2.7 Alcance analítico y modelado

**Fuente de datos:** NHANES 2013-2014 (CDC), seis tablas unidas por `SEQN`: `DIQ_H` (diabetes, que aporta el objetivo), `DEMO_H` (demografía), `BMX_H` (medidas corporales), `BPX_H` (presión arterial), `TCHOL_H` (colesterol total) y `HDL_H` (colesterol HDL). El conjunto consolidado se guarda en `data/raw/NHANES_consolidado.csv`.

**Población:** adultos (>= 18 años). Del total de 9.763 participantes con respuesta válida, quedan 6.110, de los cuales 902 son positivos (14,8 %). Entre los menores solo hay 20 positivos (0,5 %).

**Variable objetivo:** `Diabetes` = 1 si `DIQ010` es 1 (Sí) o 3 (Borderline, prediabetes) y 0 si es 2 (No). Las respuestas "Rehusó" y "No sabe" no se tratan como negativas. Se descartan las variables de la tabla DIQ que solo existen para quienes responden "Sí", porque su presencia delata la clase (fuga de información).

**Variables explicativas:** dos escenarios. *Sin laboratorio*: edad, género, IMC, cintura, presión sistólica y presión diastólica. *Con laboratorio*: las anteriores más colesterol total y colesterol HDL (requieren una muestra de sangre). Raza/etnia e ingreso se emplean para describir y controlar, no como criterio de priorización, por equidad. No se usan glucosa ni insulina: la glucosa es criterio diagnóstico de la diabetes y haría la clasificación circular.

**Decisiones de preparación (según el EDA):**
- Los valores de presión diastólica cercanos a 0 son lecturas no válidas y se convierten en nulos.
- Los nulos (entre 4 % y 12 % por variable, similares entre clases) se imputan con la mediana dentro de un `Pipeline`, ajustada solo con datos de entrenamiento.
- Los valores atípicos son clínicamente plausibles y no se eliminan.
- IMC y cintura tienen una correlación de 0,91; se probó usar solo una de las dos y el desempeño es prácticamente el mismo.

**Modelos:** clasificador de referencia (clase mayoritaria), regla de solo edad, regresión logística con ponderación de clases (con y sin laboratorio), regresión logística con splines en edad y cintura (con y sin la interacción edad por cintura), Random Forest y HistGradientBoosting. Se evalúan con validación cruzada de 5 particiones y una partición de prueba estratificada (20 %, semilla 7). Entre los modelos sin laboratorio no hay diferencias distinguibles dentro del ruido de la validación cruzada, por lo que se prefiere el más simple: la regresión logística.

**Evaluación:** recall, precisión, F1, ROC-AUC y PR-AUC, y la captura de casos según la fracción de población tamizada. No se usa la exactitud como criterio, por el desbalance de 5,8 a 1. El intervalo del recall en la prueba se obtiene por bootstrap, y la estabilidad del resultado se revisa repitiendo la evaluación con 20 semillas distintas.

**Revisión de supuestos:** se verificó, en los dos escenarios, el número de casos por parámetro, la independencia, los datos faltantes, la multicolinealidad (VIF), la linealidad en el logit (Box-Tidwell), las observaciones influyentes (distancia de Cook) y la fuga de información. Los resultados están en el cuaderno `08_validacion_supuestos.ipynb`.

**Gestión de experimentos:** cada corrida se registra en MLflow (parámetros, métricas y modelo) y el modelo seleccionado se registra en el Model Registry.

## 2.8 Alcance tecnológico

| Componente | Tecnología propuesta | Resultado verificable |
|---|---|---|
| Preparación y entrenamiento | Python, pandas, scikit-learn | `Pipeline` y modelo serializado |
| Seguimiento de experimentos | MLflow (servidor en AWS EC2) | Corridas, métricas y modelo registrado |
| Servicio de inferencia | FastAPI (propuesto) | `POST /predict`, `GET /health` y documentación de la API |
| Tablero | Streamlit (propuesto) | Gráficas y formulario que invoca la API |
| Empaquetamiento | Docker / Docker Compose | Aplicación reproducible en contenedores |
| Código y colaboración | Git / GitHub | Commits, ramas y Pull Requests |
| Versionamiento de datos | DVC | Datos rastreados mediante metadatos DVC |

## 2.9 Fuera de alcance

- Diagnosticar diabetes, prediabetes o enfermedades cardiovasculares.
- Detectar diabetes no diagnosticada: el objetivo es un diagnóstico autorreportado.
- Predecir incidencia futura de diabetes o recomendar tratamientos.
- Utilizar el resultado para clasificar pacientes reales o decidir prioridades de atención médica individual.
- Integrar historias clínicas, datos personales identificables o fuentes de información en tiempo real.
- Replicar los modelos complejos o las métricas publicadas por Dinh et al. (2019).
- Inferir tasas representativas de la población estadounidense sin aplicar el diseño muestral y los ponderadores de NHANES.

## 2.10 Criterios de éxito del prototipo

El proyecto se considerará funcional cuando se pueda demostrar que:

1. Los datos y el procesamiento pueden reproducirse desde el repositorio y DVC.
2. El modelo se entrena, evalúa y guarda con un procedimiento documentado, y los experimentos quedan registrados en MLflow.
3. La API recibe entradas válidas, responde a la inferencia y maneja errores de validación.
4. El tablero ofrece visualizaciones y consume las predicciones **a través de la API**, no cargando el modelo directamente.
5. Los contenedores pueden construirse y ejecutarse siguiendo instrucciones de configuración.
6. Se presentan métricas reales, el resultado frente al criterio de éxito de negocio (sección 2.3) y las limitaciones, sin afirmaciones clínicas o de representatividad que los datos no sustenten.

## 2.11 Riesgos y validación pendiente

- **Riesgo de la Entrega 1 (resuelto):** el conjunto original tenía solo 21 positivos. Se resolvió cambiando de datos y de objetivo, como se documenta en `01_problema_y_contexto.md` (sección 1.6).
- **Desbalance de clases (5,8 a 1):** se mitiga con partición estratificada, ponderación de clases, métricas adecuadas y un umbral definido en la evaluación.
- **Señal limitada:** ninguna variable aislada supera un AUC univariado de 0,74 y, con las variables disponibles, el recall parece tener un techo cerca de 0,80 a 0,81 sin importar el algoritmo. La meta se cumple en promedio pero con poco margen (ver sección 2.12).
- **Variabilidad por partición:** con 20 semillas distintas, el recall de la regresión sin laboratorio va de 0,717 a 0,850. Por eso se reporta el promedio de 20 semillas y no el resultado de una sola partición.
- **Colesterol y sangre:** el colesterol no es una medida no invasiva, y su coeficiente negativo probablemente refleja el tratamiento de quienes ya están diagnosticados. Por eso los resultados se presentan en dos escenarios.
- **Pesos de clase:** los modelos usan `class_weight="balanced"`, que infla las probabilidades. Si el simulador va a mostrar una probabilidad, hay que usar un modelo sin pesos o calibrarla.
- **Objetivo autorreportado y tratamiento:** el modelo aprende el perfil asociado a un diagnóstico previo, y los valores de laboratorio pueden estar modificados por el tratamiento. Se documenta como limitación y no se interpreta de forma causal.
- **Sesgo:** raza/etnia e ingreso muestran diferencias significativas en la tasa de casos por lo que se evita usarlos como criterio de priorización, por equidad y porque pueden reflejar el acceso a un diagnóstico y no el riesgo.

## 2.12 Estado actual de los resultados

Los resultados provienen de los cuadernos `07_modelos_iniciales_v1.ipynb` (validación cruzada, elección del modelo y evaluación final en la prueba) y `08_validacion_supuestos.ipynb` (revisión de supuestos y evaluación con 20 particiones). La partición base usa la semilla 7 y las 20 particiones adicionales usan las semillas 1 a 21 (sin la 7).

Recall al 40 % de la población, en 20 particiones distintas:

| Modelo | Media | Mínimo - máximo | Semillas con recall >= 0,75 |
|---|---|---|---|
| Solo edad | 0,731 | 0,678 - 0,800 | 6 de 20 |
| Regresión logística, sin laboratorio | 0,782 | 0,717 - 0,850 | 17 de 20 |
| Splines + interacción, sin laboratorio | 0,792 | 0,750 - 0,861 | 20 de 20 |
| Regresión logística, con laboratorio | 0,806 | 0,739 - 0,872 | 19 de 20 |
| Splines + interacción, con laboratorio | 0,805 | 0,744 - 0,856 | 19 de 20 |

Lo que muestran:

- **La meta se cumple en promedio, con poco margen.** Sin laboratorio el promedio queda entre 0,78 y 0,79; con laboratorio, en 0,81. En la partición base (cuaderno 07), la regresión sin laboratorio da 0,750 con un intervalo del 95 % de 0,698 a 0,823, así que en esa partición no se puede asegurar que se cumpla. En esa misma partición supera a la edad sola (0,728) por 2,2 puntos, pero el intervalo de esa mejora incluye el cero.
- **Los modelos superan a la edad sola de forma consistente entre semillas**, por unos 5 puntos de recall sin laboratorio y unos 7,5 con laboratorio (regresión logística).
- **El escenario con laboratorio rinde entre 1 y 2,5 puntos más** que el escenario sin laboratorio.
- **Los splines ayudan alrededor de 1 punto sin laboratorio** y no cambian el resultado con laboratorio.
- **El resultado de una sola partición varía varios puntos** (por ejemplo, el de la regresión logística sin laboratorio va de 0,717 a 0,850), por lo que se reporta el promedio de las 20 particiones junto con el de la partición base.

## Referencias

[1] CDC, National Center for Health Statistics. *NHANES 2013–2014 Overview*. https://wwwn.cdc.gov/Nchs/Nhanes/continuousnhanes/overview.aspx?BeginYear=2013

[2] CDC, National Center for Health Statistics. *NHANES 2013-2014 Data Files* (DIQ_H, DEMO_H, BMX_H, BPX_H, TCHOL_H, HDL_H). https://wwwn.cdc.gov/nchs/nhanes/ContinuousNhanes/Default.aspx?BeginYear=2013

[3] Dinh, A., Miertschin, S., Young, A., & Mohanty, S. D. (2019). *A data-driven approach to predicting diabetes and cardiovascular disease with machine learning*. *BMC Medical Informatics and Decision Making*, 19, 211. https://doi.org/10.1186/s12911-019-0918-5
