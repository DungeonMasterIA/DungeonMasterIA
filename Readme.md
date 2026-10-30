# DungeonMasterIA

Proyecto base para una aplicación con un backend en FastAPI, un frontend JavaScript y una base de datos MySQL, preparado para ejecutarse con Docker Compose.

## Estructura del proyecto

- `/API`: contiene el API desarrollado con [FastAPI](https://fastapi.tiangolo.com/). Su contenedor escucha en el puerto `8000`.
- `/FRONT`: contiene el proyecto frontend. Docker levanta un entorno Node.js para alojar una aplicación creada con un framework como Angular, React o Vue. Su contenedor escucha en el puerto `3000`.
- `docker-compose.yml`: configura todos los servicios necesarios para el entorno de desarrollo.

## Requisitos

- [Docker](https://docs.docker.com/get-docker/)
- Docker Compose, incluido en Docker Desktop y en las versiones actuales de Docker mediante el comando `docker compose`

## Starter pack: puesta en marcha desde cero

Copia y pega estos comandos **desde la raíz del proyecto** (donde está `docker-compose.yml`). Con esto ya puedes empezar a desarrollar.

```bash
# 1. Levantar backend y base de datos (construye las imágenes si hace falta)
#    Añade `front` al final cuando el frontend tenga su package.json
docker compose up --build -d db phpmyadmin api

# 2. Esperar a que MySQL esté listo
until docker compose exec -T db mysqladmin ping -h localhost -u root -proot_password --silent; do
  echo "Esperando a MySQL..."
  sleep 2
done

# 3. Aplicar las migraciones de Alembic (crea las tablas)
docker compose exec api alembic upgrade head

# 4. Comprobar que todo está arriba y que la BD está al día
docker compose ps
docker compose exec api alembic current
```

Servicios disponibles tras el arranque:

| Servicio | URL |
| --- | --- |
| API FastAPI | http://localhost:8000 |
| Documentación de la API | http://localhost:8000/docs |
| Frontend | http://localhost:3000 |
| phpMyAdmin | http://localhost:8080 |
| MySQL (desde el host) | `localhost:3307` |

Credenciales de MySQL: usuario `platano_user`, contraseña `platano_password`, base de datos `mi_base_datos`.

> El frontend todavía no tiene `package.json`, así que el starter pack solo levanta backend y base de datos. Cuando el frontend esté listo, ejecuta `docker compose up --build -d` para levantar todo.

### Comandos del día a día

```bash
# Ver logs en vivo (todos o de un servicio concreto)
docker compose logs -f
docker compose logs -f api

# Reiniciar un servicio tras cambiar código/dependencias
docker compose restart api
docker compose up --build -d api

# Entrar a una shell dentro del contenedor del API
docker compose exec api bash

# Abrir la consola de MySQL
docker compose exec db mysql -u platano_user -pplatano_password mi_base_datos

# Ejecutar la suite de tests (registro, login y JWT)
docker compose exec api pytest

#Ejecutar los tests de el backend
docker exec -it fastapi_backend pytest

# Parar todo (conserva los datos)
docker compose down

# Parar todo y borrar la base de datos (empezar de cero)
docker compose down -v
```

### Tras cambiar los modelos de SQLAlchemy

```bash
# 1. Generar la migración automáticamente
docker compose exec api alembic revision --autogenerate -m "descripcion_del_cambio"

# 2. Revisar el archivo generado en API/alembic/versions/ y aplicarlo
docker compose exec api alembic upgrade head
```

### Reset completo de la base de datos

```bash
docker compose down -v
docker compose up --build -d db phpmyadmin api
until docker compose exec -T db mysqladmin ping -h localhost -u root -proot_password --silent; do sleep 2; done
docker compose exec api alembic upgrade head
```

### Ejecutar el API o Alembic en local (sin Docker para el API)

```bash
cd API
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Crear el .env (MySQL del compose se expone en el puerto 3307 del host)
cat > .env <<'EOF'
DATABASE_URL=mysql+aiomysql://platano_user:platano_password@localhost:3307/mi_base_datos
SECRET_KEY=secret
EOF

alembic upgrade head
fastapi dev main.py --host 0.0.0.0 --port 8000
```

## Levantar el proyecto

Desde la carpeta raíz del proyecto, donde se encuentra `docker-compose.yml`, ejecuta:

```bash
docker compose up --build
```

La opción `--build` construye o actualiza las imágenes de los servicios. Para iniciar los contenedores en segundo plano:

```bash
docker compose up --build -d
```

Una vez levantado el entorno, los servicios estarán disponibles en:

- API FastAPI: http://localhost:8000
- Documentación interactiva de FastAPI: http://localhost:8000/docs
- Frontend: http://localhost:3000
- phpMyAdmin: http://localhost:8080
- MySQL desde el equipo local: puerto `3307`

## Detener el proyecto

Para detener los contenedores sin eliminar los datos de MySQL:

```bash
docker compose down
```

Para detenerlos y eliminar también el volumen de la base de datos:

```bash
docker compose down -v
```

## Servicios configurados

| Servicio | Tecnología | Puerto local | Descripción |
| --- | --- | --- | --- |
| `db` | MySQL 8.0 | `3307` | Base de datos de la aplicación |
| `phpmyadmin` | phpMyAdmin | `8080` | Gestión de MySQL desde el navegador |
| `api` | FastAPI + Python 3.11 | `8000` | API backend |
| `front` | Node.js 20 | `3000` | Aplicación frontend |

El backend se conecta a MySQL usando la siguiente configuración interna de Docker Compose:

```text
Host: db
Puerto: 3306
Base de datos: mi_base_datos
Usuario: platano_user
Contraseña: platano_password
```

Los directorios `/API` y `/FRONT` están montados como volúmenes, por lo que los cambios realizados localmente se reflejan dentro de los contenedores durante el desarrollo.

## Comandos útiles

Ver el estado de los servicios:

```bash
docker compose ps
```

Ver los logs de todos los servicios:

```bash
docker compose logs -f
```

Ver únicamente los logs del API o del frontend:

```bash
docker compose logs -f api
docker compose logs -f front
```
