# Rutas y pantallas

## Flujo principal

```text
Seleccionar mesero → Tablero de mesas → Abrir/ver comanda
                                      → Capturar consumo
                                      → Consultar cuenta
                                      → Confirmar cierre
                                      → Ver ticket
```

## Contratos HTTP

| Método | Ruta sugerida | Nombre Django | Propósito |
|---|---|---|---|
| `GET`, `POST` | `/meseros/seleccionar/` | `seleccionar_mesero` | Mostrar meseros activos y guardar la selección en sesión. |
| `POST` | `/meseros/cambiar/` | `cambiar_mesero` | Limpiar o reemplazar al mesero activo. |
| `GET` | `/mesas/` | `tablero_mesas` | Mostrar mesas activas y su ocupación. |
| `POST` | `/mesas/<int:mesa_id>/abrir/` | `abrir_comanda` | Crear una comanda para una mesa disponible. |
| `GET` | `/comandas/<int:pk>/` | `detalle_comanda` | Mostrar consumo y formulario de captura. |
| `POST` | `/comandas/<int:pk>/detalles/agregar/` | `agregar_detalle` | Agregar o acumular un producto. |
| `POST` | `/detalles/<int:pk>/actualizar/` | `actualizar_detalle` | Cambiar la cantidad. |
| `POST` | `/detalles/<int:pk>/eliminar/` | `eliminar_detalle` | Retirar un producto. |
| `GET` | `/comandas/<int:pk>/cuenta/` | `consultar_cuenta` | Mostrar la vista previa del ticket. |
| `POST` | `/comandas/<int:pk>/cerrar/` | `cerrar_comanda` | Confirmar y ejecutar el cierre. |
| `GET` | `/comandas/<int:pk>/ticket/` | `ver_ticket` | Consultar una comanda cerrada. |

Las rutas que cambian datos usan exclusivamente `POST`. Después de un `POST` exitoso se aplica el patrón POST/Redirect/GET para evitar reenvíos accidentales.

## Pantallas

### Selección de mesero

- Lista únicamente meseros activos.
- Rechaza en el servidor un ID inexistente o inactivo.
- Guarda `mesero_id` en sesión y redirige al tablero.
- Explica que la selección no equivale a iniciar sesión.

### Tablero de mesas

- Muestra al mesero seleccionado y permite cambiarlo.
- Muestra mesas activas, capacidad y estado derivado.
- En una mesa libre presenta “Abrir comanda”.
- En una mesa ocupada presenta “Ver comanda”.
- Como defensa, mantiene visible una mesa inactiva que aún tenga una comanda abierta.

### Captura de comanda

- Muestra mesa, mesero responsable, fecha y estado.
- Lista productos disponibles: producto activo y categoría activa.
- Acepta cantidades enteras positivas.
- Permite actualizar y eliminar renglones únicamente si está abierta.
- Muestra subtotales y total calculados.

### Cuenta y cierre

- Presenta el desglose completo.
- Deshabilita el cierre si no hay detalles.
- Solicita confirmación mediante un formulario `POST`.
- Si otro proceso ya la cerró, redirige al ticket existente con un mensaje.

### Ticket

- Muestra folio, mesa, mesero, fechas, detalles y total.
- Es de solo lectura.
- Aclara en la documentación del MVP que los nombres proceden de catálogos vivos.

## Formularios mínimos

| Formulario | Campos recibidos | Validaciones principales |
|---|---|---|
| Selección de mesero | `mesero` | Existe y está activo. |
| Agregar detalle | `producto`, `cantidad` | Comanda abierta; producto y categoría activos; cantidad positiva. |
| Actualizar detalle | `cantidad` | Detalle de una comanda abierta; cantidad positiva. |
| Cerrar comanda | Confirmación explícita | Comanda abierta y con al menos un detalle. |

La mesa, la comanda, el precio y el estado nunca se confían a campos ocultos: se obtienen y validan nuevamente en el servidor.
