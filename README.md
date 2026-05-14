# Candies App

Aplicacion web en Django para una tienda de dulces. Incluye catalogo publico, registro e inicio de sesion, carrito en frontend y flujo de compra con historial de pedidos.

## Inicio rapido

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

La tienda queda disponible en `http://127.0.0.1:8000/`.

## Que incluye

- Catalogo de dulces con stock e imagenes.
- Registro, login y logout de usuarios.
- Checkout con creacion de pedidos y descuento de inventario.
- Pruebas basicas en `shop/tests.py`.

## Despliegue en PythonAnywhere

Este proyecto ya queda preparado para publicarse en PythonAnywhere con variables de entorno y `collectstatic`.

1. Sube el codigo a PythonAnywhere, idealmente con Git.
2. Crea una web app con `Manual configuration` y Python `3.12` en la imagen `innit`.
3. En una consola Bash, crea y activa un virtualenv:

```bash
mkvirtualenv --python=/usr/bin/python3.12 candies-app
workon candies-app
pip install -r requirements.txt
```

4. En la carpeta del proyecto crea un archivo `.env` basado en `.env.example`. El proyecto usa `python-decouple`, asi que Django leera ese archivo automaticamente. Como minimo define:

```env
SECRET_KEY=tu-clave-secreta-real
DEBUG=False
ALLOWED_HOSTS=tuusuario.pythonanywhere.com
STATIC_ROOT=/home/tuusuario/Candies_app/staticfiles
```

5. Edita el archivo WSGI de PythonAnywhere, el que aparece en el Web tab, no `sugar_rush/wsgi.py`, y dejalo apuntando al proyecto:

```python
import os
import sys

path = "/home/tuusuario/Candies_app"
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sugar_rush.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

6. Ejecuta las migraciones y los estaticos:

```bash
python manage.py migrate
python manage.py collectstatic
```

7. En el Web tab agrega el mapeo de archivos estaticos:

```text
URL: /static/
Path: /home/tuusuario/Candies_app/staticfiles
```

8. Recarga la web app.

Guias oficiales usadas:

- [Deploying an existing Django project on PythonAnywhere](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/)
- [How to setup static files in Django](https://help.pythonanywhere.com/pages/DjangoStaticFiles)
- [How to set environment variables for your web apps](https://help.pythonanywhere.com/pages/environment-variables-for-web-apps/)
