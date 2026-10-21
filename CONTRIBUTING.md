# Guía de contribución — Metabolic Health Explorer

Este repositorio se desarrolla en equipo para la asignatura **Despliegue de Soluciones Analíticas (MIAD)**. Todos los integrantes deben dejar aportes trazables mediante commits y Pull Requests (PR).

## 1. Preparar el entorno

```bash
conda create -n miad-despliegue-proyecto python=3.10 -y
conda activate miad-despliegue-proyecto
python -m pip install -r requirements.txt
python -m pip install ipykernel dvc
```

El paquete no incluye los entornos de cada integrante. Si se necesita usar DVC con S3, instalar `dvc[s3]` después de acordar un remoto autorizado.

## 2. Flujo de ramas

**No desarrollar directamente sobre `main`.** Antes de iniciar una tarea:

```bash
git checkout main
git pull origin main
git checkout -b nombre/tarea-descriptiva
```

Ejemplos: `alix/readme-colaboracion`, `integrante2/eda-avanzado`, `integrante3/modelo-base`. Si existen cambios locales sin guardar, completar el commit o guardarlos antes de cambiar de rama.

Hacer commits acotados con mensajes claros:

- `docs: documentar variables y alcance`
- `feat: agregar exploración de glucosa`
- `fix: corregir mapeo de DIQ010`
- `chore: actualizar metadatos DVC`
- `test: validar carga del dataset`

Para publicar:

```bash
git push -u origin nombre/tarea-descriptiva
```

Crear un PR **desde la rama de trabajo hacia `main`**. Otro integrante revisa los cambios antes de fusionar. En el PR, explicar qué se hizo, cómo se validó y qué falta.

## 3. Normas para notebooks y análisis

- Conservar las secciones Markdown que explican preguntas, métodos y limitaciones.
- Ejecutar las celdas en orden y evitar rutas absolutas de cada computador.
- No reemplazar resultados exploratorios por valores inventados.
- Trabajar sobre el subconjunto UCI 887; documentar cualquier ampliación de datos.
- Para `DIQ010`, separar las respuestas distintas de 1 (sí) y 2 (no) al formar una etiqueta binaria; no presentar el clasificador como diagnóstico.
- Evitar modificar el mismo notebook simultáneamente sin coordinación, para reducir conflictos JSON al fusionar.

## 4. Git y DVC

- **Git:** código, notebooks, documentos y metadatos `.dvc`.
- **DVC:** contenido versionado de los archivos de datos.
- No hacer `git add` al CSV `data/raw/NHANES_age_prediction.csv`; el `.gitignore` existente en `data/raw/` lo protege.
- Ejecutar `dvc status` antes de hacer commit de modificaciones al dataset. Si cambian los datos, utilizar `dvc add` y registrar el archivo `.dvc` actualizado.
- Un `git push` **no sube** el contenido a un remoto DVC. Primero debe existir un almacenamiento compartido y usarse `dvc push`.
- No publicar credenciales, tokens, archivos `.env`, claves SSH ni archivos de configuración privada de AWS.

## 5. Revisión mínima del PR

- [ ] Cambios explicados y relacionados con una tarea del proyecto.
- [ ] Archivos académicos existentes respetados.
- [ ] Notebook ejecutable (o limitación documentada).
- [ ] Sin datos personales nuevos, credenciales, cachés o entornos.
- [ ] Si cambia el CSV, archivo `.dvc` actualizado.
- [ ] PR revisado por otra persona antes del merge.

## 6. Registro de participación

Cada integrante debe utilizar su propia cuenta e identidad Git. La evidencia de participación se obtiene de commits, PR y revisiones, complementada con el reporte de trabajo en equipo exigido por la materia.
