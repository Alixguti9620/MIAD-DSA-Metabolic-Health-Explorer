# Registro de cambios

Este archivo resume hitos del proyecto. Las fechas y versiones se actualizarán cuando el equipo apruebe cada entrega.

## [1.0.0] — Entrega final (prototipo desplegado)
- Modelos servidos: logística con splines en edad y cintura e interacción edad × cintura (sin laboratorio) y logística simple (con laboratorio), elegidos con 20 particiones (`src/experimentos_robustez.py`).
- Experimentos en MLflow sobre AWS EC2: experimento final (8 corridas, partición 60/20/20) y de robustez (11 corridas).
- API REST con FastAPI (`api/`): predicción individual, por lotes (JSON y CSV), información del modelo y 20 pruebas.
- Tablero con Streamlit (`app/tablero.py`): exploración, simulador, priorización por lotes y modelo y datos; consume la API.
- Contenedores Docker (`Dockerfile.api`, `Dockerfile.tablero`, `docker-compose.yml`) desplegados en AWS EC2.
- Evidencias del despliegue en `docs/evidencias_entrega_final/`.
- Manual de usuario (`docs/06_manual_de_usuario.md`) y manual de instalación (`docs/07_manual_de_instalacion.md`).

## [0.1.1] — Replanteamiento del problema y EDA de la Entrega 2
- Nueva pregunta de negocio (priorización para tamizaje) con criterio de éxito medible: recall >= 75 % revisando como máximo al 40 % de los adultos.
- Nuevos datos: seis tablas NHANES 2013-2014 consolidadas en `data/raw/NHANES_consolidado.csv` (reemplazan al subconjunto UCI 887, que tenía 21 positivos).
- Nuevo objetivo: diabetes o prediabetes reportada (`DIQ010` = 1 o 3); población adulta (6.110 registros, 902 positivos).
- Sin glucosa ni insulina como variables explicativas (clasificación circular) y sin variables de DIQ que filtran la respuesta.
- Cuaderno `06_Exploracion_complementaria_nhanes.ipynb` unificado: preparación de datos, exploración de adultos y conclusiones. Figuras `eda_*.png` en `reports/figures/`.
- Documentos `docs/01`, `docs/02` y `docs/04`, README y CONTRIBUTING actualizados.
- Pendiente: capturas y HTML de la maqueta, modelos, MLflow, API, tablero y Docker.

## [0.1.0] — Organización inicial (propuesta)

- Conservada la documentación original del problema y alcance de la Entrega 1.
- Conservados el notebook de exploración, los resultados generados y los metadatos DVC incluidos en el ZIP de partida.
- Añadida guía de colaboración y plantilla de Pull Request.
- Añadidos archivos de configuración de proyecto y README alineado con los archivos reales.

## Plan de versiones (cumplido en 1.0.0)

> El número de versión describe el estado documental del paquete y no certifica que la aplicación esté desplegada.
