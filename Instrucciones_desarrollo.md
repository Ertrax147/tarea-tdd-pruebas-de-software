# Instrucciones para el Equipo

## Flujo de trabajo

1. Actualizar `develop`:
```bash
git checkout develop
git pull
```

2. Crear tu branch feature:
```bash
git checkout -b feature/rf-0x-descripcion
```

3. Desarrollar usando TDD (ciclos RED → GREEN → REFACTOR)

4. Cuando termines, hacer merge a `develop`:
```bash
git checkout develop
git merge feature/rf-0x-descripcion
git push
```

## Convenciones de commits

Commits en inglés: `type: short description`

Tipos permitidos:
- `test:` — para tests nuevos
- `feat:` — para implementación de código
- `refactor:` — para mejoras de estructura sin cambiar comportamiento
- `docs:` — para documentación

Ejemplo:
```
test: add validation for empty customer name
feat: implement input validation in create_reservation
refactor: extract validation helper method
```

---

## Compañero 1: RF01 - Validaciones de creación

**Branch:** `feature/rf-01-validaciones`

**Archivos a modificar:**
- `src/reservation/restaurant.py`
- `tests/test_reservation.py`

**Funcionalidad:**
El sistema debe rechazar la creación de una reserva cuando:
- El nombre del cliente está vacío
- La cantidad de personas es menor o igual a 0
- Falta la fecha o la hora

**Ciclos TDD:**

| # | Comportamiento | Prueba | Implementación |
|---|---------------|--------|----------------|
| 1 | Rechazo por nombre vacío | Test que espere `ValueError` con `customer_name=""` | Agregar validación en `create_reservation` |
| 2 | Rechazo por personas ≤ 0 | Test que espere `ValueError` con `party_size=0` y `-1` | Agregar validación de `party_size` |
| 3 | IDs únicos | Test que cree 2 reservas y verifique que sus `id` son distintos | Verificar que `uuid4` funciona (probablemente ya pase) |

---

## Compañero 2: RF02 - Disponibilidad

**Branch:** `feature/rf-02-disponibilidad`

**Archivos a crear/modificar:**
- `src/reservation/restaurant.py`
- `tests/test_availability.py` (nuevo)

**Funcionalidad:**
El sistema debe:
- Saber cuántas personas caben en un horario (capacidad configurable, default 30)
- Retornar la capacidad disponible para fecha/hora dada
- Rechazar reserva que exceda la capacidad

**Ciclos TDD:**

| # | Comportamiento | Prueba | Implementación |
|---|---------------|--------|----------------|
| 1 | Capacidad completa disponible | Test: sin reservas, `check_availability` retorna 30 | Implementar `check_availability` |
| 2 | Capacidad reducida | Test: reserva de 26 personas, disponibilidad es 4 | Calcular personas reservadas para esa fecha/hora |
| 3 | Rechazo por capacidad insuficiente | Test: con 26 reservadas, reserva de 6 debe fallar | Validar capacidad en `create_reservation` |

---

## Compañero 3: RF03 - Cancelación

**Branch:** `feature/rf-03-cancelacion`

**Archivos a crear/modificar:**
- `src/reservation/restaurant.py`
- `tests/test_cancellation.py` (nuevo)

**Funcionalidad:**
El sistema debe:
- Cancelar una reserva existente por su código (id)
- Retornar `False` si el código no existe
- Lanzar error si la reserva ya está cancelada
- Liberar la capacidad al cancelar

**Ciclos TDD:**

| # | Comportamiento | Prueba | Implementación |
|---|---------------|--------|----------------|
| 1 | Cancelación exitosa | Test: crear, cancelar, verificar status `"cancelled"` | Implementar `cancel_reservation` |
| 2 | Código inexistente | Test: cancelar con id inventado, retornar `False` | Validar existencia del id |
| 3 | Ya cancelada | Test: cancelar 2 veces, lanzar `ValueError` | Verificar status antes de cancelar |
| 4 | Liberar capacidad | Test: cancelar reserva, verificar disponibilidad restaurada | Filtrar solo reservas `active` en `check_availability` |

---

## Compañero 4: RF04 - Consultas + Reporte

**Branch:** `feature/rf-04-consultas`

**Archivos a crear/modificar:**
- `src/reservation/restaurant.py`
- `tests/test_queries.py` (nuevo)

**Funcionalidad:**
El sistema debe:
- Retornar todas las reservas activas para una fecha dada
- Excluir reservas canceladas del listado
- Retornar lista vacía si no hay reservas para esa fecha

**Ciclos TDD:**

| # | Comportamiento | Prueba | Implementación |
|---|---------------|--------|----------------|
| 1 | Filtrar por fecha | Test: 3 reservas en una fecha, 1 en otra, verificar filtrado | Implementar `get_reservations_by_date` |
| 2 | Excluir canceladas | Test: cancelar 1 reserva, verificar que no aparece | Filtrar por `status == "active"` |
| 3 | Fecha sin reservas | Test: consultar fecha vacía, retornar `[]` | Verificar que retorna lista vacía |

**Además:** Crear el archivo `REPORTE.md` con la documentación final del proyecto.

---

## Verificación final

Antes de hacer merge, ejecutar en tu branch:
```bash
python -m pytest -v
```

Todas las pruebas deben pasar. Incluye las tuyas y las que ya existían.
