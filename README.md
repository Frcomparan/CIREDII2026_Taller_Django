# Taller de Django: sistema de comandas

Repositorio base para desarrollar, durante el taller, una aplicación web sencilla de comandas para un restaurante.

El proyecto permitirá practicar los elementos principales de Django: modelos, migraciones, administración, formularios, vistas, rutas, plantillas y relaciones entre entidades.

## Contenido del repositorio

- `documentacion/`: definición del proyecto, modelo de datos, casos de uso, rutas y pantallas.
- `documentacion/diagramas/`: diagramas en formato PlantUML y SVG.
- `extras/`: plantillas, estilos y un comando de apoyo para cargar datos iniciales.
- `requirements.txt`: dependencias de Python necesarias para el taller.

> Este repositorio contiene únicamente el material y el esqueleto base. El proyecto y la aplicación de Django se crearán como parte del taller.

## Requisitos

- Python 3.10 o superior.
- `pip`.
- Un entorno virtual de Python (recomendado).

## Preparación del entorno

```bash
python -m venv .venv
```

Activa el entorno virtual:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Linux o macOS
source .venv/bin/activate
```

Instala las dependencias:

```bash
python -m pip install -r requirements.txt
```

## Punto de partida

Antes de escribir código, consulta:

1. [`documentacion/MODELADO.md`](documentacion/MODELADO.md), para conocer el alcance, las reglas de negocio y el modelo de datos.
2. [`documentacion/RUTAS_Y_PANTALLAS.md`](documentacion/RUTAS_Y_PANTALLAS.md), para revisar el flujo de navegación y las vistas sugeridas.
3. [`extras/`](extras/), para identificar los archivos de apoyo que se integrarán durante el desarrollo.

## Alcance

El resultado esperado es un MVP que permita seleccionar un mesero, consultar mesas, abrir una comanda, agregar productos, calcular la cuenta, cerrar el servicio y mostrar un ticket.

