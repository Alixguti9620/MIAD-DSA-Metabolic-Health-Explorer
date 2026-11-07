# 1. Problema que abordará el proyecto y su contexto

**Proyecto:** Metabolic Health Explorer  
**Asignatura:** Despliegue de Soluciones Analíticas — MIAD  


## 1.1 Contexto general

National Health and Nutrition Examination Survey (NHANES) es la encuesta de salud y nutrición nacional de Estados Unidos, regulada por el Centro de Control y Prevención de Enfermedades (CDC).

A través de esta encuesta se recolectan datos que establecen una base, proporcionan inferencias y ayudan a detallar estadísticamente los factores de riesgo de diversas enfermedades en la población estadounidense, en especial en la población vulnerable o que no hace parte del sistema institucional de protección pública. De esta forma se monitorea el estado de salud y nutricional de la población, incluyendo exposición ambiental, crecimiento, nutrición y enfermedades crónicas (NCHS, 2024).

La diabetes y la prediabetes son condiciones metabólicas crónicas cuya detección depende de pruebas de laboratorio (glucosa o HbA1c). Aplicar esas pruebas a toda la población es costoso, y los programas de tamizaje con recursos limitados necesitan decidir **a quién ofrecerle primero la prueba**. En cambio, medidas como la edad, el índice de masa corporal (IMC), la circunferencia de cintura y la presión arterial son no invasivas y se toman en cualquier consulta, por lo que pueden usarse para ordenar a las personas según su prioridad de tamizaje.

Este proyecto utiliza las tablas de NHANES 2013-2014 (diabetes, demografía, medidas corporales, presión arterial y colesterol) para estudiar si esas medidas permiten priorizar a los adultos con mayor probabilidad de tener diabetes o prediabetes diagnosticada.

Como el colesterol requiere una muestra de sangre, el estudio se plantea en dos escenarios: **sin laboratorio** (edad, género, IMC, cintura y presión arterial), que usa solo medidas sencillas de una consulta, y **con laboratorio**, que suma colesterol total y HDL.

## 1.2 Problema específico

Un equipo de salud pública que diseña una campaña de tamizaje no puede realizar pruebas de laboratorio a toda la población y necesita un criterio objetivo, económico y reproducible para decidir a quién priorizar. Sin una herramienta que combine las medidas disponibles en una consulta básica, la selección depende de reglas de una sola variable (por ejemplo, solo la edad) o del criterio individual del profesional.

El problema que aborda el proyecto es, por tanto, **la falta de un criterio de priorización para el tamizaje de diabetes y prediabetes en adultos basado en medidas sencillas y de bajo costo (en un escenario sin laboratorio y en otro que suma colesterol), y de una herramienta que lo exponga a analistas y equipos de salud pública**.

### Por qué un clasificador supervisado

Se utiliza un clasificador porque la necesidad es **ordenar a las personas por la probabilidad de pertenecer al grupo de interés**, no medir una cantidad. La probabilidad que entrega el modelo permite fijar un umbral y decidir a qué fracción de la población se ofrece la prueba. El modelo se evalúa por su capacidad de capturar casos con un esfuerzo de tamizaje acotado.

### Qué no pretende hacer

El resultado es una **priorización poblacional**, no un diagnóstico ni una estimación de riesgo clínico individual. El modelo aprende el perfil de las personas que reportaron un diagnóstico previo; por eso no detecta diabetes sin diagnosticar y debe usarse como apoyo a la planificación de campañas, no como decisión médica.

## 1.3 Evidencia y antecedentes

Dinh et al. (2019) estudiaron el uso de algoritmos supervisados sobre datos NHANES para clasificar diabetes, prediabetes y enfermedad cardiovascular. Compararon variables obtenidas mediante cuestionarios y pruebas de laboratorio, y evaluaron modelos como regresión logística, SVM, Random Forest y métodos de ensamble [3]. Su trabajo respalda el interés de analizar cómo los indicadores de NHANES se relacionan con tareas de clasificación.

**Diferencia fundamental:** el artículo trabajó con conjuntos de datos, periodos y etiquetas distintos. Sus resultados de desempeño no se pueden reproducir ni prometer con los datos de este proyecto. Se utiliza como antecedente metodológico, no como validación del modelo.

## 1.4 Usuarios y necesidad concreta

**Usuario principal:** analista o equipo de salud pública que planifica campañas de tamizaje y debe decidir qué fracción de la población priorizar.


Se busca que estos usuarios puedan:

- Comparar el perfil (edad, IMC, cintura, presión arterial, colesterol) de las personas con y sin diabetes o prediabetes reportada.
- Explorar cómo cambia la proporción de casos según edad, IMC y otros segmentos.
- Ingresar los valores de un perfil y consultar, mediante una API, la probabilidad que asigna el modelo y si queda dentro del grupo priorizado.
- Consultar las métricas del modelo, sus limitaciones y la trazabilidad de los datos.

## 1.5 Justificación del proyecto

La propuesta tiene dos aportes complementarios:

1. **Aplicado:** ofrecer un criterio de priorización de tamizaje basado en medidas simples, que supere a la regla de usar solo la edad, con una meta medible de casos capturados frente al esfuerzo de tamizaje.
2. **Tecnológico y académico:** demostrar el diseño, empaquetamiento y despliegue de un modelo supervisado mediante una API y un tablero web, con experimentos versionados en MLflow y trazabilidad de datos y código.


## 1.6 Delimitaciones del problema

- **Población y periodo:** adultos del ciclo NHANES 2013-2014, no pacientes de una institución ni datos actuales.
- **Etiqueta:** respuesta a la pregunta sobre diagnóstico de diabetes (`DIQ010`); se agrupan "Sí" y "Borderline" (prediabetes) en la clase positiva, y se excluyen las respuestas "Rehusó" y "No sabe", que no se tratan como negativas.
- **Autorreporte:** el objetivo es un diagnóstico declarado por el participante, no una confirmación de laboratorio.
- **Tratamiento:** las personas ya diagnosticadas pueden estar en tratamiento, lo que altera sus valores de laboratorio. En el EDA, el colesterol total resultó menor en los positivos, un posible efecto de ese tratamiento.
- **Generalización:** no se aplicaron los ponderadores del diseño muestral de NHANES, por lo que las proporciones no son estimaciones representativas de la población estadounidense.
- **Laboratorio:** el colesterol (total y HDL) requiere una muestra de sangre, por lo que no es una medida no invasiva. Por eso se evalúan dos escenarios, sin y con laboratorio, y se reportan por separado.
- **Variables sensibles:** raza/etnia e ingreso se usan para describir y controlar, no como criterio de priorización de personas. Se decidió no usarlas: priorizar según la raza es delicado en términos de equidad y, como el objetivo es un diagnóstico previo, pueden reflejar el acceso a un diagnóstico y no solo el riesgo.

## 1.7 Resultado que se espera obtener

Un prototipo denominado **Metabolic Health Explorer** que integra un tablero con análisis descriptivo y un simulador de priorización que consulta un modelo mediante una API, desplegado con Docker. El simulador ofrecerá los dos escenarios (sin y con laboratorio). La utilidad se evalúa por el cumplimiento del criterio de éxito de la sección 2.3 (casos capturados frente a esfuerzo de tamizaje, medido sobre una partición de prueba) y por requisitos técnicos de reproducibilidad y disponibilidad de la API.

## Referencias

[1] Centers for Disease Control and Prevention (CDC), National Center for Health Statistics. *NHANES 2013–2014 Overview*. https://wwwn.cdc.gov/Nchs/Nhanes/continuousnhanes/overview.aspx?BeginYear=2013

[2] CDC, National Center for Health Statistics. *NHANES 2013-2014 Data Files* (DIQ_H, DEMO_H, BMX_H, BPX_H, TCHOL_H, HDL_H). https://wwwn.cdc.gov/nchs/nhanes/ContinuousNhanes/Default.aspx?BeginYear=2013

[3] Dinh, A., Miertschin, S., Young, A., & Mohanty, S. D. (2019). *A data-driven approach to predicting diabetes and cardiovascular disease with machine learning*. BMC Medical Informatics and Decision Making, 19, 211. https://doi.org/10.1186/s12911-019-0918-5
