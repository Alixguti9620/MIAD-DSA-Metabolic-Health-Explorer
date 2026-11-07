# 4. Maqueta (mockup) del prototipo

**Proyecto:** Metabolic Health Explorer  
**Asignatura:** Despliegue de Soluciones Analíticas, MIAD  


## 4.1 Propósito de la maqueta

La maqueta representa el tablero que usará el usuario final y su relación con la API de inferencia. Cada elemento se diseñó para responder a la pregunta de negocio definida en 02_pregunta_de_negocio_y_alcance.md:

¿Es posible priorizar a los adultos con mayor probabilidad de tener diabetes o prediabetes diagnosticada, usando medidas sencillas y de bajo costo (con y sin laboratorio), de modo que se capture al menos el 75 % de los casos tamizando como máximo al 40 % de la población?

y a las preguntas de apoyo:

| Código | Pregunta de apoyo |
|---|---|
| P1 | ¿Cómo se distribuyen la edad, el IMC, la cintura, la presión arterial y el colesterol entre quienes reportan y no reportan diabetes o prediabetes? |
| P2 | ¿Cómo cambia la proporción de casos al segmentar por edad, IMC, género y otros grupos? |
| P3 | ¿Qué fracción de casos captura el modelo al tamizar a una fracción dada de la población, frente a la línea base de usar solo la edad? |
| P4 | ¿Cómo presentar comparaciones e inferencias de forma reproducible y comprensible? |

Se elaboraron **dos alternativas**. Ambas cubren los tres módulos del alcance funcional (sección 2.6): A (descriptivo), B (predictivo, vía API) y C (transparencia).

- **Opción A, por pestañas:** cada módulo en su propia pantalla, con filtros en una barra lateral.
- **Opción B, centrada en el perfil:** el usuario ingresa un perfil y todo el tablero se lee respecto a él. Incluye además una pantalla para comparar segmentos.

**Origen de las cifras.** Los conteos, medianas y tasas por categoría provienen del análisis exploratorio complementario sobre los 6.110 adultos del conjunto consolidado NHANES 2013-2014 (902 casos, 14,8 %). Las probabilidades, percentiles y coeficientes mostrados en las maquetas son **ilustrativos**, y las métricas del modelo se completan con los resultados de MLflow una vez entrenado.

**Nota sobre las capturas.** Las imágenes de las pantallas y los archivos HTML de las maquetas muestran todavía la versión de la Entrega 1 (glucosa, insulina, actividad física y 21 casos). Las tablas de esta sección ya describen el contenido actualizado, y las maquetas deben regenerarse con las variables y cifras nuevas antes de usarlas como referencia del tablero.

**Archivos fuente.** Las maquetas son HTML editables: [`mockup/maqueta_prototipo.html`](mockup/maqueta_prototipo.html) (opción A) y [`mockup/opcion_b/maqueta_opcion_b.html`](mockup/opcion_b/maqueta_opcion_b.html) (opción B). Si se añade al final de la URL `#p1`, `#p2`, `#p3`, `#arq` (A) o `#b1`, `#b2`, `#b3` (B), se muestra solo esa pantalla.

## 4.2 Opción A: tablero por pestañas

### Pantalla A1: Exploración descriptiva (Módulo A)

![Pantalla A1: Exploración descriptiva](mockup/img/pantalla_p1.png)

| # | Elemento | Qué hace | Relación con la pregunta |
|---|---|---|---|
| 1 | Filtros de segmento | Rango de edad y género. Deja explícita la definición del objetivo (`DIQ010` = 1 o 3 es positivo; se excluyen 7 y 9) y que solo se incluyen adultos. | P2 |
| 2 | Indicadores clave | Tamaño del segmento, casos positivos (902; 14,8 % en adultos) y medianas de edad e IMC por grupo. | Contexto y desbalance de clases |
| 3 | Distribución por indicador | Diagrama de caja o densidad de edad, IMC, cintura, presión sistólica y colesterol HDL por grupo. | P1 |
| 4 | Tasa por categoría | % con diabetes o prediabetes por grupo de edad (de 1,6 % a 30 %), categoría de IMC (de 7 % a 26 %), cintura elevada o presión sistólica. | P1, P2 |
| 5 | Tabla comparativa | Medianas y medias por grupo; descarga en CSV. | P1, P4 |
| 6 | Aviso de tamaño muestral | Se muestra cuando el segmento seleccionado tiene pocos casos. | P4 |

### Pantalla A2: Simulador de clasificación (Módulo B)

![Pantalla A2: Simulador de clasificación](mockup/img/pantalla_p2.png)

| # | Elemento | Qué hace | Relación con la pregunta |
|---|---|---|---|
| 1 | Formulario de entrada | Selector de escenario (sin laboratorio / con laboratorio). Campos: edad, género, IMC, cintura y presión arterial; con laboratorio se habilitan colesterol total y HDL. Con validación de tipos, rangos y categorías. | P3 |
| 2 | Botón «Consultar modelo» | Envía el JSON a `POST /predict` y muestra los errores de validación (422). | Criterio de éxito 4: el tablero usa el modelo **solo** vía API |
| 3 | Resultado | Probabilidad, si el perfil queda dentro del grupo priorizado (40 % de mayor probabilidad), umbral de decisión, versión del modelo y estado de `GET /health`. | P3 |
| 4 | Ubicación del perfil | Percentil de cada valor ingresado frente al conjunto de datos. | Une lo descriptivo (P1) con lo predictivo (P3) |
| 5 | Detalle técnico | Petición y respuesta JSON (sección desplegable). | P4; usuario docente o técnico |
| 6 | Historial de la sesión | Permite comparar escenarios cambiando una sola variable. | P3 |

### Pantalla A3: Acerca del modelo y de los datos (Módulo C)

![Pantalla A3: Transparencia](mockup/img/pantalla_p3.png)

| # | Elemento | Qué hace | Relación con la pregunta |
|---|---|---|---|
| 1 | Ficha de datos | Fuente (seis tablas NHANES 2013-2014), población adulta, definición del objetivo y versión de datos en DVC. | Criterio de éxito 1 (reproducibilidad), P4 |
| 2 | Métricas frente al modelo base | Recall, precisión, F1, ROC-AUC y PR-AUC, por escenario, frente al clasificador de clase mayoritaria y a la regla de solo edad. Incluye el promedio de 20 semillas y no solo una partición. | P3 |
| 3 | Curva de captura y matriz de confusión | Casos capturados según la fracción tamizada (por ejemplo 30 %, 40 % y 50 %), con la meta de 75 % al 40 %, y errores por clase. | P3 |
| 4 | Limitaciones | Advertencias de interpretación y uso. | Sección 2.9 y criterio de éxito 6 |

## 4.3 Opción B: tablero centrado en el perfil

### Pantalla B1: Perfil frente a los datos (Módulos A y B integrados)

![Pantalla B1: Perfil frente a los datos](mockup/opcion_b/img/pantalla_b1.png)

| # | Elemento | Qué hace | Relación con la pregunta |
|---|---|---|---|
| 1 | Formulario de perfil | Las variables del modelo, con perfiles de ejemplo precargados. | P3 |
| 2 | Resultado del modelo | Probabilidad en una escala continua con el umbral marcado y si queda en el grupo priorizado; respuesta de `POST /predict`. | P3; criterio de éxito 4 |
| 3 | Distribuciones con el perfil marcado | Curvas No/Sí de cada indicador con una línea en el valor ingresado. | P1 |
| 4 | Tasas por categoría | % con diabetes o prediabetes por grupo de edad, categoría de IMC y género (15,2 % hombres / 14,4 % mujeres), con el grupo del perfil resaltado. | P2 |
| 5 | Franja del modelo | Métricas clave frente al modelo base y aviso de uso. | P3, P4 |

### Pantalla B2: Comparar segmentos (Módulo A)

![Pantalla B2: Comparar segmentos](mockup/opcion_b/img/pantalla_b2.png)

| # | Elemento | Qué hace | Relación con la pregunta |
|---|---|---|---|
| 1 | Definición de segmentos A y B | Filtros independientes de edad, género e IMC para cada segmento. | P2 |
| 2 | Resumen comparativo | Registros, casos y % de positivos, con la diferencia y la advertencia de n pequeño (ejemplo real: mujeres 14,4 %, n = 3.194, frente a hombres 15,2 %, n = 2.916; diferencia no significativa). | P2, P4 |
| 3 | Medianas por indicador | Barras pareadas A/B por indicador (IMC, cintura, presión sistólica, colesterol). | P1 |
| 4 | Predicción por segmento | Distribución de las probabilidades del modelo en cada segmento (endpoint opcional `POST /predict/batch`). | P3 |
| 5 | Exportar | Descarga de la comparación en CSV. | P4 |

### Pantalla B3: Modelo y datos (Módulo C)

![Pantalla B3: Modelo y datos](mockup/opcion_b/img/pantalla_b3.png)

| # | Elemento | Qué hace | Relación con la pregunta |
|---|---|---|---|
| 1 | Métricas frente al modelo base | Recall, precisión, F1, ROC-AUC y PR-AUC; la exactitud (≈ 85 % del modelo base) se muestra como advertencia. | P3 |
| 2 | Explorador de umbral | Al mover el umbral se ven el balance entre recall y precisión y la matriz de confusión. | P3, P4 |
| 3 | Peso de las variables | Coeficientes estandarizados de la regresión logística, con su signo. | P1, P3 |
| 4 | Origen y evaluación de los datos | Recorrido desde las seis tablas NHANES hasta los adultos del conjunto de modelado (9.763 → 6.110 registros). | Criterio de éxito 1; riesgos de la sección 2.11 |
| 5 | Trazabilidad | Versiones de los datos (DVC), del modelo y del código; endpoints de la API. | Criterios de éxito 1, 2 y 3 |
| 6 | Limitaciones | Advertencias de interpretación y uso. | Sección 2.9 y criterio de éxito 6 |

## 4.4 Comparación de las opciones

| Criterio | Opción A: por pestañas | Opción B: centrada en el perfil |
|---|---|---|
| Relación descriptivo–predictivo | Pantallas separadas; la conexión es el panel de percentiles (A2.4) | Integrada: el perfil aparece en cada gráfica (B1) |
| Segmentación (P2) | Filtros globales en la barra lateral | Pantalla dedicada que compara dos segmentos (B2) |
| Explicación del desbalance | Avisos y tabla de métricas | Además, explorador de umbral interactivo (B3.2) |
| Complejidad de implementación | Menor: estructura nativa de Streamlit (barra lateral + pestañas) | Mayor: estado compartido entre gráficas y endpoint por lotes opcional |
| Usuario que más se beneficia | Analista que explora la muestra | Docente o estudiante que quiere entender el modelo |

## 4.5 Arquitectura y flujo

![Arquitectura del prototipo](mockup/img/pantalla_arq.png)

1. El usuario interactúa con el **tablero** (Streamlit, propuesto) desde el navegador.
2. Las vistas descriptivas leen agregados del conjunto de datos y las métricas guardadas (`metrics.json`). El simulador llama a la **API** (FastAPI, propuesta) mediante `POST /predict` y `GET /health`.
3. La API carga el **pipeline de scikit-learn** serializado (`model.joblib`), que incluye el preprocesamiento y el modelo.
4. El modelo se entrena a partir de los datos versionados con **DVC**.
5. El tablero y la API se ejecutan en contenedores separados, orquestados con **Docker Compose**.

La arquitectura es la misma para ambas opciones; solo cambia la organización de las pantallas.

## 4.6 Decisiones de diseño

- **Hacer visible el desbalance.** El 14,8 % de positivos aparece en los indicadores, en los avisos de tamaño muestral y en las métricas, donde la exactitud se muestra como advertencia y no como criterio.
- **Umbral explícito.** El umbral no será 0,5 por defecto. Se define en la evaluación para cumplir la meta de capturar el 75 % de los casos tamizando como máximo al 40 % de la población.
- **Priorización, no diagnóstico.** El resultado se expresa como «perfil dentro del grupo priorizado para tamizaje», no como un diagnóstico.
- **Variables sensibles.** Raza/etnia e ingreso se muestran en lo descriptivo, pero no se ofrecen como entrada de priorización.
- **Dos escenarios.** El usuario elige si dispone de resultados de laboratorio. El colesterol requiere sangre, así que no se presenta como medida no invasiva, y los resultados se muestran por separado para cada escenario.
- **Probabilidades creíbles.** Los modelos entrenados con pesos de clase inflan las probabilidades; antes de mostrar una probabilidad en el simulador hay que usar un modelo sin pesos o calibrarla.
- **Resultado con su variabilidad.** Se muestra el promedio de varias particiones junto con el de la partición base, porque el recall cambia varios puntos de una partición a otra.
- **Trazabilidad.** Se muestran la versión del modelo y de los datos (DVC) y el estado de la API.

