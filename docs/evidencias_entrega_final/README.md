# Evidencias de la entrega final

Capturas del despliegue en AWS EC2 y de los experimentos en MLflow, tomadas el 23 de noviembre.

- **Instancia:** `i-05bc6845800f510b8`, t3.small, us-east-1a, Ubuntu 24.04, usuario `ubuntu`, hostname `ip-172-31-24-150` (IP privada 172.31.24.150).
- **IP pública:** `54.167.5.59` en las capturas del navegador y de la consola. Las capturas `03` a `05` de despliegue muestran `3.93.59.179`, la IP que tenía la misma instancia antes de reiniciarse: AWS asigna una IP pública nueva cada vez que se detiene y se vuelve a encender una instancia sin IP elástica. El hostname es el mismo en todas.
- **Servicios:** API en el puerto 8000, tablero en el 8501 y MLflow en el 8050, todos en la misma instancia. La API y el tablero corren con `docker compose`.

## Despliegue en AWS (`despliegue_aws/`)

| Archivo | Qué muestra |
|---|---|
| [01_consola_aws_instancia_ec2](despliegue_aws/01_consola_aws_instancia_ec2.png) | Consola de EC2: instancia en *Running*, t3.small, 3/3 checks, IP pública 54.167.5.59 |
| [02_terminal_usuario_ip_contenedores_mlflow](despliegue_aws/02_terminal_usuario_ip_contenedores_mlflow.png) | `ubuntu`, `ip-172-31-24-150`, IP 54.167.5.59, contenedores `api` y `tablero` *healthy* y proceso `mlflow server` |
| [03_terminal_identificacion_ec2](despliegue_aws/03_terminal_identificacion_ec2.png) | `whoami`, `hostname`, IP pública y kernel de AWS |
| [04_terminal_docker_instalado](despliegue_aws/04_terminal_docker_instalado.png) | Docker 29.10.0, Docker Compose v5.8.0 y servicio activo |
| [05_terminal_contenedores_healthy](despliegue_aws/05_terminal_contenedores_healthy.png) | `docker compose ps` con los dos servicios *healthy* |
| [06_security_group_reglas_entrada](despliegue_aws/06_security_group_reglas_entrada.png) | Reglas de entrada: 8000 (API), 8501 (tablero), 8050 (MLflow) y 22 (SSH) |

## Tablero en la nube (`tablero/`, `http://54.167.5.59:8501`)

| Archivo | Qué muestra |
|---|---|
| [01_exploracion](tablero/01_exploracion.png) | Pantalla de exploración: 6.110 adultos y 902 casos |
| [02_simulador_sin_laboratorio](tablero/02_simulador_sin_laboratorio.png) | Simulador sin laboratorio (modelo con splines e interacción) |
| [03_simulador_con_laboratorio](tablero/03_simulador_con_laboratorio.png) | Simulador con laboratorio, mismo perfil |
| [04_lotes_carga_archivo](tablero/04_lotes_carga_archivo.png) | Priorización por lotes: carga del CSV; las predicciones vienen de la API |
| [05_lotes_ranking](tablero/05_lotes_ranking.png) | Ranking de 5 personas con el 40 % de la lista marcado |
| [06_lotes_histograma_y_descarga](tablero/06_lotes_histograma_y_descarga.png) | Histograma de probabilidades y descarga del ranking |
| [07_modelo_resultados](tablero/07_modelo_resultados.png) | Recall@40 % en prueba: 76,1 % sin laboratorio y 78,9 % con laboratorio |
| [08_modelo_matriz_confusion](tablero/08_modelo_matriz_confusion.png) | Priorizados y no priorizados por escenario |
| [09_modelo_curva_de_captura](tablero/09_modelo_curva_de_captura.png) | Curva de captura frente a la edad sola y al azar |
| [10_modelo_estabilidad_20_semillas](tablero/10_modelo_estabilidad_20_semillas.png) | Estabilidad en 20 particiones (cuadernos 07 y 08, con pesos de clase) |
| [11_modelo_eleccion_splines_vs_logistica](tablero/11_modelo_eleccion_splines_vs_logistica.png) | Elección del modelo servido: splines frente a logística, Wilcoxon |
| [12_modelo_efecto_de_cada_variable](tablero/12_modelo_efecto_de_cada_variable.png) | Odds ratio de cada variable entre los percentiles 25 y 75 |

## API en la nube (`api/`, `http://54.167.5.59:8000/docs`)

| Archivo | Qué muestra |
|---|---|
| [01_docs_endpoints](api/01_docs_endpoints.png) | Endpoints: `/health`, `/predict`, `/model/info`, `/predict/batch`, `/predict/batch/csv` |
| [02_docs_esquemas](api/02_docs_esquemas.png) | Esquemas de entrada y salida |
| [03_predict_peticion](api/03_predict_peticion.png) | Petición a `/predict` con un perfil sin laboratorio |
| [04_predict_respuesta_200](api/04_predict_respuesta_200.png) | Respuesta 200 desde `54.167.5.59`: probabilidad, umbral, aportes y `tipo_modelo` |

## MLflow en EC2 (`mlflow/`, `http://54.167.5.59:8050`)

Experimento `MIAD-Metabolic-Health-Explorer-final` (`src/experimentos_mlflow.py`): 8 corridas, partición 60/20/20 y búsqueda de hiperparámetros con validación cruzada.

| Archivo | Qué muestra |
|---|---|
| [01_final_lista_8_corridas](mlflow/01_final_lista_8_corridas.png) | Las 8 corridas (4 modelos × 2 escenarios) |
| [02_final_splines_sin_lab_metricas](mlflow/02_final_splines_sin_lab_metricas.png) | Métricas de entrenamiento, validación y prueba; creada por `ubuntu` |
| [03_final_splines_con_lab_metricas](mlflow/03_final_splines_con_lab_metricas.png) | Igual, escenario con laboratorio |
| [04_final_splines_sin_lab_hiperparametros](mlflow/04_final_splines_sin_lab_hiperparametros.png) | `GridSearchCV`, espacio de búsqueda y mejores parámetros |
| [05_final_splines_con_lab_hiperparametros](mlflow/05_final_splines_con_lab_hiperparametros.png) | Igual, escenario con laboratorio |
| [06_final_cv_results_busqueda](mlflow/06_final_cv_results_busqueda.png) | Artefacto `cv_results.csv` con la búsqueda completa |
| [07_final_comparacion_8_corridas](mlflow/07_final_comparacion_8_corridas.png) | Comparación de las 8 corridas |

Experimento `MIAD-Metabolic-Health-Explorer-robustez` (`src/experimentos_robustez.py`): 20 particiones, 11 corridas (5 modelos × 2 escenarios y la comparación pareada).

| Archivo | Qué muestra |
|---|---|
| [08_robustez_comparacion_pareada_1](mlflow/08_robustez_comparacion_pareada_1.png) | Artefacto `comparacion_pareada.csv`: diferencia media y particiones ganadas |
| [09_robustez_comparacion_pareada_2](mlflow/09_robustez_comparacion_pareada_2.png) | Sin laboratorio: los splines ganan 15, empatan 4 y pierden 1 (Wilcoxon p = 0,0043) |
| [10_robustez_splines_sin_lab_metricas](mlflow/10_robustez_splines_sin_lab_metricas.png) | Recall@40 % promedio 0,792, mínimo 0,756, 20 de 20 particiones sobre la meta |
| [11_robustez_splines_sin_lab_parametros](mlflow/11_robustez_splines_sin_lab_parametros.png) | 20 semillas, partición 80/20 y CV de 5 pliegues dentro del entrenamiento |
| [12_robustez_graficas_de_metricas](mlflow/12_robustez_graficas_de_metricas.png) | Ganancia frente a la edad y particiones sobre la meta |
| [13_robustez_recall_por_semilla](mlflow/13_robustez_recall_por_semilla.png) | Recall@40 % en cada una de las 20 particiones |
