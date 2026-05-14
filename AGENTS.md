# AGENTS

## Contexto

Este repositorio contiene una tienda de dulces hecha con Django. La app principal es `shop` y el proyecto se configura desde `sugar_rush`.

## Zonas clave

- `shop/models.py`: dulces, pedidos y lineas de pedido.
- `shop/views.py`: catalogo, autenticacion, checkout y cuenta.
- `templates/shop/`: vistas HTML.
- `static/`: estilos, scripts e imagenes.

## Forma de trabajo

- Haz cambios pequenos y consistentes con el estilo actual.
- Si tocas checkout, revisa tambien `shop/tests.py`.
- Usa `python manage.py migrate` antes de probar la app si la base local no esta al dia.
