# 1. Problema que abordará el proyecto y su contexto

**Proyecto:** Metabolic Health Explorer  
**Asignatura:** Despliegue de Soluciones Analíticas — MIAD 
**Estado:** Propuesta inicial, pendiente de análisis exploratorio

## 1.1 Contexto general

La diabetes constituye un tema relevante para la salud pública debido a la necesidad de conocer cómo se distribuyen sus antecedentes y los indicadores de salud relacionados en diferentes grupos de población. Para estudiar estos patrones, las encuestas poblacionales permiten combinar respuestas proporcionadas por las personas con mediciones físicas y resultados de laboratorio.

En Estados Unidos, la *National Health and Nutrition Examination Survey* (NHANES), coordinada por el National Center for Health Statistics de los Centers for Disease Control and Prevention (CDC), recopila información por medio de entrevistas, exámenes físicos y pruebas de laboratorio. La edición 2013–2014 es una fuente pública de información histórica sobre salud y nutrición de la población civil no institucionalizada de Estados Unidos [1].

El proyecto utilizará el conjunto **NHANES 2013–2014 Age Prediction Subset**, publicado en UCI Machine Learning Repository. Este subconjunto contiene 6.287 registros con variables demográficas, de actividad física y mediciones metabólicas [2]. Su objetivo original es distinguir dos grupos de edad; para este proyecto se propone una **nueva tarea académica**, centrada en diferenciar participantes según su respuesta a la pregunta de diagnóstico de diabetes reportado (`DIQ010`), sujeta a revisión de los códigos y la distribución de clases.

## 1.2 Problema específico

Aunque los datos públicos de salud pueden explorarse mediante herramientas estadísticas, **comparar de forma integrada los perfiles de participantes que reportan y que no reportan un diagnóstico de diabetes requiere preparar, interpretar y visualizar variables de diferentes tipos**. Sin una herramienta específica, esa exploración puede resultar poco accesible para estudiantes y analistas que buscan comprender los datos sin reproducir manualmente cada consulta.

El problema que abordará el proyecto es, por tanto, **la falta de un prototipo sencillo y reproducible que permita explorar los indicadores metabólicos del subconjunto seleccionado y demostrar cómo un clasificador supervisado diferencia los perfiles asociados con el antecedente de diabetes reportado**.

No se plantea que la edad o los resultados de laboratorio sean suficientes para diagnosticar diabetes. El objetivo es analizar **patrones en una muestra histórica** y construir un producto analítico educativo; no detectar casos clínicos, estimar riesgo futuro ni recomendar decisiones médicas.

## 1.3 Evidencia y antecedentes

Dinh et al. (2019) estudiaron el uso de algoritmos supervisados sobre datos NHANES para clasificar diabetes, prediabetes y enfermedad cardiovascular. Compararon variables obtenidas mediante cuestionarios y pruebas de laboratorio, y evaluaron modelos como regresión logística, SVM, Random Forest y métodos de ensamble [3]. Su trabajo respalda el interés académico de analizar cómo los indicadores y las respuestas de NHANES se relacionan con tareas de clasificación.

**Diferencia fundamental:** el artículo trabajó con conjuntos de datos más amplios, periodos y etiquetas distintos. Sus resultados de desempeño **no son resultados de UCI 887 ni se pueden reproducir o prometer con el subconjunto escogido**. El artículo se utilizará como antecedente metodológico, no como validación del modelo de este proyecto.

## 1.4 Usuarios y necesidad concreta

**Usuarios propuestos:** estudiantes e investigadores de analítica de datos, analistas de salud pública en contextos exploratorios y docentes que necesitan demostrar el ciclo de vida de una solución analítica.

Se busca que estos usuarios puedan:

- Comparar la distribución del IMC, glucosa, insulina y actividad física entre grupos definidos por la respuesta sobre diabetes.
- Explorar cómo cambian los resultados al aplicar filtros demográficos y de actividad física.
- Introducir los valores de un perfil hipotético y consultar la clasificación producida por un modelo supervisado a través de una API.
- Consultar de forma clara las limitaciones del conjunto de datos y del resultado predictivo.

## 1.5 Justificación del proyecto

La propuesta tiene dos aportes complementarios:

1. **Analítico:** facilitar la exploración reproducible de un subconjunto público de NHANES y la comparación descriptiva de perfiles asociados con diabetes reportada.
2. **Tecnológico y académico:** demostrar el diseño, empaquetamiento y despliegue de un modelo supervisado mediante una API y un tablero web, con versionamiento de datos y código.

## 1.6 Delimitaciones del problema

- **Población y periodo:** registros del subconjunto NHANES 2013–2014 disponible en UCI, no pacientes de una institución ni datos actuales.
- **Etiqueta propuesta:** respuesta sobre diagnóstico de diabetes (`DIQ010`), previa verificación de valores válidos, respuestas especiales y número de registros por clase. No se asumirá que la variable representa una confirmación diagnóstica independiente.
- **Indicadores disponibles:** variables presentes en el subconjunto, sin incorporar fuentes adicionales durante el alcance inicial.
- **Naturaleza del resultado:** clasificación exploratoria de *diabetes reportada*, no diagnóstico, tamizaje validado ni estimación causal.
- **Generalización:** sin verificar las ponderaciones y el diseño complejo de NHANES, no se presentarán proporciones del subconjunto como estimaciones representativas de toda la población estadounidense.
- **Ética:** el prototipo no tomará decisiones automatizadas sobre personas ni ofrecerá recomendaciones médicas.

## 1.7 Resultado que se espera obtener

Se espera construir un prototipo denominado **Metabolic Health Explorer** que integre un tablero con análisis descriptivos y un componente de inferencia mediante API. El producto permitirá ilustrar cómo se utiliza información estructurada de salud en una aplicación analítica desplegada, sin confundir una predicción estadística con una conclusión clínica.

La utilidad del producto se evaluará por el cumplimiento de requisitos funcionales y técnicos (reproducibilidad, acceso a visualizaciones, disponibilidad de la API y correcto funcionamiento del flujo de predicción), y por métricas de clasificación calculadas sobre una partición de prueba. **No se anticipan métricas ni hallazgos antes de analizar los datos.**

## Referencias

[1] Centers for Disease Control and Prevention (CDC), National Center for Health Statistics. *NHANES 2013–2014 Overview*. https://wwwn.cdc.gov/Nchs/Nhanes/continuousnhanes/overview.aspx?BeginYear=2013

[2] UCI Machine Learning Repository. *National Health and Nutrition Health Survey 2013–2014 (NHANES) Age Prediction Subset*. https://archive.ics.uci.edu/dataset/887/national+health+and+nutrition+health+survey+2013-2014+(nhanes)+age+prediction+subset. DOI: 10.24432/C5BS66.

[3] Dinh, A., Miertschin, S., Young, A., & Mohanty, S. D. (2019). *A data-driven approach to predicting diabetes and cardiovascular disease with machine learning*. BMC Medical Informatics and Decision Making, 19, 211. https://doi.org/10.1186/s12911-019-0918-5
