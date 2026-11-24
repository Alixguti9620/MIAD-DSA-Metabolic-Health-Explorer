# Manual de instalación del tablero y la API

**Producto:** Metabolic Health Explorer
**Componentes:** API de inferencia (FastAPI, puerto 8000) y tablero (Streamlit, puerto 8501), empaquetados en dos contenedores Docker.

Hay tres formas de instalarlo:

| Opción | Cuándo usarla | Sección |
|---|---|---|
| A. Docker en un computador local | Probar la solución completa | 2 |
| B. Docker en AWS EC2 | Despliegue en la nube | 3 |
| C. Python sin Docker | Desarrollo o revisión del código | 4 |

---

## 1. Requisitos

| Requisito | Opciones A y B | Opción C |
|---|---|---|
| Git | Sí | Sí |
| Docker Engine 24+ con Docker Compose v2 | Sí | No |
| Python 3.10 o superior (se recomienda 3.11) | No | Sí |
| Memoria RAM | 2 GB o más | 2 GB o más |
| Disco libre | 3 GB | 1 GB |
| Puertos libres | 8000 y 8501 | 8000 y 8501 |

**Arquitectura:**

```text
Navegador ──► Tablero (Streamlit :8501) ──HTTP──► API (FastAPI :8000) ──► Modelos (.joblib)
```

El tablero pide las predicciones a la API por medio de la variable `API_URL`. Los modelos no están en Git: se entrenan automáticamente al construir las imágenes (tarda unos segundos) con `src/entrenar_modelos.py`, a partir de `data/raw/NHANES_consolidado.csv`, que sí está en el repositorio.

---

## 2. Opción A: Docker en un computador local

### 2.1 Instalar Docker

- **Windows / macOS:** instale [Docker Desktop](https://www.docker.com/products/docker-desktop/) y ábralo antes de continuar.
- **Linux:** siga la sección 3.3.

Verifique la instalación:

```bash
docker --version
docker compose version
```

### 2.2 Descargar el código

```bash
git clone https://github.com/Alixguti9620/MIAD-DSA-Metabolic-Health-Explorer.git
cd MIAD-DSA-Metabolic-Health-Explorer
```

### 2.3 Construir y levantar

Desde la raíz del repositorio:

```bash
docker compose up --build -d
```

La primera vez tarda unos minutos: descarga la imagen de Python, instala las dependencias y entrena los modelos. El tablero espera a que la API esté sana antes de arrancar.

Opcional: para que la versión del modelo muestre el commit de Git, defina esta variable antes de construir:

```bash
# Linux / macOS / Git Bash
export VERSION_CODIGO=$(git rev-parse --short HEAD)
# PowerShell
$env:VERSION_CODIGO = git rev-parse --short HEAD
```

### 2.4 Verificar

```bash
docker compose ps
```

Los dos servicios, `api` y `tablero`, deben aparecer con estado `healthy` (puede tardar hasta un minuto).

| Servicio | Dirección |
|---|---|
| Tablero | http://localhost:8501 |
| API (documentación interactiva) | http://localhost:8000/docs |
| Estado de la API | http://localhost:8000/health |

Prueba rápida de la API:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"Edad": 55, "Mujer": 1, "IMC": 31.2, "Cintura_cm": 104, "Presion_Sistolica": 132, "Presion_Diastolica": 82}'
```

La respuesta debe traer `probabilidad`, `umbral`, `prioriza` y `aportes`.

### 2.5 Detener y actualizar

```bash
docker compose down                          # detener y eliminar los contenedores
git pull && docker compose up --build -d     # actualizar a la última versión
docker compose logs -f api                   # ver los registros (o: tablero)
```

---

## 3. Opción B: despliegue en AWS EC2

Configuración usada en la entrega: instancia **t3.small**, **Ubuntu 24.04**, región `us-east-1`.

### 3.1 Crear la instancia

1. En la consola de AWS, vaya a **EC2 → Launch instance**.
2. AMI: **Ubuntu Server 24.04 LTS**. Tipo: **t3.small**, con 2 GB de RAM. En una t2.micro la construcción puede quedarse sin memoria.
3. Par de llaves: cree uno o elija uno existente y guarde el archivo `.pem`.
4. Almacenamiento: 16 GB o más.

### 3.2 Abrir los puertos (security group)

Agregue estas **reglas de entrada**:

| Puerto | Protocolo | Origen | Uso |
|---|---|---|---|
| 22 | TCP | Su IP | SSH |
| 8000 | TCP | 0.0.0.0/0 | API |
| 8501 | TCP | 0.0.0.0/0 | Tablero |
| 8050 | TCP | 0.0.0.0/0 | MLflow (solo si se usa en la misma máquina) |

### 3.3 Conectarse e instalar Docker

```bash
ssh -i <llave>.pem ubuntu@<IP_PUBLICA>

sudo apt-get update
curl -fsSL https://get.docker.com | sudo sh     # instala Docker Engine y el plugin Compose
sudo usermod -aG docker ubuntu                   # permite usar docker sin sudo
exit                                             # salga y vuelva a entrar para aplicar el grupo
```

Vuelva a conectarse y verifique con `docker --version` y `docker compose version`.

### 3.4 Desplegar

```bash
git clone https://github.com/Alixguti9620/MIAD-DSA-Metabolic-Health-Explorer.git
cd MIAD-DSA-Metabolic-Health-Explorer
export VERSION_CODIGO=$(git rev-parse --short HEAD)
docker compose up --build -d
docker compose ps        # espere a que api y tablero estén "healthy"
```

Abra en su navegador:

- Tablero: `http://<IP_PUBLICA>:8501`
- API: `http://<IP_PUBLICA>:8000/docs`

Los contenedores tienen `restart: unless-stopped`, así que vuelven a arrancar solos cuando la instancia se reinicia.

### 3.5 Detener sin perder el despliegue

En la consola de EC2 use **Instance state → Stop instance** (no *Terminate*). Al encenderla de nuevo con **Start instance**, los contenedores arrancan solos, pero **la IP pública cambia** a menos que se le asocie una IP elástica. Consulte la nueva IP en la consola y compártala con los usuarios.

---

## 4. Opción C: Python sin Docker

```bash
git clone https://github.com/Alixguti9620/MIAD-DSA-Metabolic-Health-Explorer.git
cd MIAD-DSA-Metabolic-Health-Explorer

python -m venv .venv
# Windows (PowerShell): .venv\Scripts\Activate.ps1
# Linux / macOS:        source .venv/bin/activate

python -m pip install -r requirements.txt
python src/entrenar_modelos.py          # entrena y guarda los modelos en models/
```

**Solo el tablero** (usa el modelo dentro del mismo proceso, sin la API):

```bash
streamlit run app/tablero.py            # http://localhost:8501
```

**Tablero y API por separado** (en dos terminales):

```bash
# Terminal 1
uvicorn api.main:app --port 8000        # http://127.0.0.1:8000/docs

# Terminal 2 (Linux / macOS / Git Bash)
API_URL=http://127.0.0.1:8000 streamlit run app/tablero.py
# Terminal 2 (PowerShell)
$env:API_URL = "http://127.0.0.1:8000"; streamlit run app/tablero.py
```

En la pantalla *Priorización por lotes*, el tablero indica si las predicciones vienen de la API o del modelo local.

**Pruebas automáticas de la API:**

```bash
python -m pip install -r requirements-dev.txt
pytest                                   # 20 pruebas
```

---

## 5. Variables de entorno

| Variable | Dónde | Valor por defecto | Uso |
|---|---|---|---|
| `API_URL` | Tablero | `http://api:8000` en Docker; vacía en local | Dirección de la API. Si está vacía, el tablero usa el modelo local. |
| `VERSION_CODIGO` | Construcción de las dos imágenes | `sin_git` | Versión del modelo que muestran la API y el tablero. |

---

## 6. Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `port is already allocated` | Otro programa usa el puerto 8000 o el 8501 | Cierre ese programa o cambie el puerto de la izquierda en `docker-compose.yml` (por ejemplo, `"8502:8501"`). |
| El tablero no arranca y la API aparece `unhealthy` | La API falló al iniciar | Ejecute `docker compose logs api` para ver el error. |
| *No se pudo obtener la predicción… Revisa que la API esté activa* | La API está caída o `API_URL` es incorrecta | Ejecute `docker compose ps`; si la API no está `healthy`, ejecute `docker compose restart api`. |
| Error al cargar el modelo (`InconsistentVersionWarning`, `AttributeError`) | Los `.joblib` se entrenaron con otra versión de scikit-learn | Use `scikit-learn==1.6.1` (ya está fijado en los requirements) y vuelva a ejecutar `python src/entrenar_modelos.py`. |
| No abre `http://<IP>:8501` en EC2 | El puerto está cerrado o la IP cambió | Revise el security group (sección 3.2) y la IP actual en la consola. |
| La construcción se detiene en EC2 | Falta memoria | Use una t3.small o una instancia mayor. |
| `permission denied` al usar `docker` en Ubuntu | El usuario no está en el grupo `docker` | Ejecute `sudo usermod -aG docker $USER` y vuelva a iniciar sesión. |

---

## 7. Archivos de despliegue

| Archivo | Función |
|---|---|
| `Dockerfile.api` | Imagen de la API: instala `requirements-api.txt`, entrena los modelos y expone el puerto 8000 con `HEALTHCHECK`. |
| `Dockerfile.tablero` | Imagen del tablero: instala `requirements-tablero.txt`, copia los datos y las figuras y expone el puerto 8501 con `HEALTHCHECK`. |
| `docker-compose.yml` | Levanta los dos servicios; el tablero espera a que la API esté sana y le habla por `http://api:8000`. |
| `requirements-api.txt` / `requirements-tablero.txt` | Dependencias de cada imagen. |
| `.dockerignore` | Excluye del contexto de construcción los archivos que no se necesitan. |