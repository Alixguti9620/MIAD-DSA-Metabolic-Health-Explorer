# Organización de equipo y estructura

## Estado de la copia revisada

Se preservaron los dos documentos académicos originales, el notebook ubicado en `scripts/`, los resultados exploratorios en `reports/figures/`, el CSV local y sus metadatos DVC. **No se modificó el contenido de esos archivos.**

Los archivos `.git/`, los objetos de caché y archivos temporales internos de DVC y los metadatos de macOS no se distribuyen en este ZIP. La carpeta `.git/` existente en el ZIP de origen contiene el historial y configuraciones locales, que no deben trasladarse al repositorio de otros integrantes. Es preferible trabajar en un clon limpio.

## Estructura

- `docs/`: documentos académicos y esta guía.
- `scripts/`: notebook exploratorio ya existente (el nombre de la carpeta se conserva para no romper rutas).
- `data/raw/`: CSV local versionado con DVC y su archivo `.dvc`.
- `reports/figures/`: tablas y gráficas exploratorias incluidas en la copia.
- `.dvc/` y `.dvcignore`: configuración y exclusiones de DVC.
- `.github/pull_request_template.md`: estructura base para los PR.
- `CONTRIBUTING.md`: reglas acordables por el equipo.
- `requirements.txt`: dependencias originales conservadas.
- `pyproject.toml`: metadatos del proyecto; **no** reemplaza requirements.txt.
- `CHANGELOG.md`: registro de versiones y próximos hitos.
- `.env.example` y `.gitignore`: convenciones para secretos, entornos y archivos temporales.

## Cómo integrarlo sin perder el historial

1. No uses este ZIP para reemplazar la carpeta `.git/` de tu repositorio local.
2. Abre tu clon actual, crea una rama a partir de `main` actualizado.
3. Copia los archivos nuevos y el README; no reemplaces automáticamente otros archivos cuyos cambios hayas hecho después de generar el ZIP original.
4. Comprueba `git status` y `git diff` antes del commit.
5. Haz commit y PR de los cambios de organización del equipo.

**Aviso DVC:** el ZIP incluye el CSV de origen para respetar el contenido aportado, pero el repositorio Git debe seguir ignorándolo. El remoto DVC compartido no está configurado en la copia revisada (`.dvc/config` estaba vacío).
