# Registro de cambios

Este archivo resume hitos del proyecto. Las fechas y versiones se actualizarán cuando el equipo apruebe cada entrega.

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

## Próximas versiones (plan, aún no implementado)

- `0.2.0`: preparación y modelado supervisado.
- `0.3.0`: API de inferencia.
- `0.4.0`: dashboard.
- `0.5.0`: pruebas y contenedorización.
- `1.0.0`: prototipo desplegado.

> El número de versión describe el estado documental del paquete y no certifica que la aplicación esté desplegada.
