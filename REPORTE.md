# Reporte: Sistema de Gestión de Reservas de Restaurante

## 1. Descripción del Módulo

Sistema para gestionar reservas de un restaurante, implementado en Python con almacenamiento en memoria. Permite crear reservas con validación de datos, verificar disponibilidad por horario, cancelar reservas existentes y consultar reservas por fecha.

**Componentes principales:**

- `Reservation` (src/reservation/models.py): Modelo de datos con campos id, customer_name, party_size, date, time y status. Genera IDs únicos con UUID.
- `Restaurant` (src/reservation/restaurant.py): Clase principal con la lógica de negocio. Gestiona reservas con capacidad configurable por horario (default: 30 personas).

**Ejecutar pruebas:**

```bash
python -m pytest -v
```

## 2. Requerimientos Implementados

| RF | Descripción | Estado |
|----|-------------|--------|
| RF01 | Crear reserva con validación de datos | Implementado |
| RF02 | Consultar disponibilidad por horario | Implementado |
| RF03 | Cancelar reserva con validación de estado | Implementado |
| RF04 | Consultar reservas por fecha | Implementado |

**Reglas de negocio:**

- No se permiten reservas con campos obligatorios vacíos o nulos
- La cantidad de personas debe ser mayor a 0
- No se puede reservar si excede la capacidad del horario
- Una reserva cancelada no se puede cancelar nuevamente
- Cancelar una reserva libera la capacidad del horario
- Las consultas por fecha excluyen reservas canceladas

## 3. Aplicación de TDD — 4 Ciclos Red → Green → Refactor

La evidencia completa de cada ciclo, incluyendo fragmentos de código y salidas de pytest, se encuentra en `TDD_EVIDENCIA.md`.

### Ciclo 1: Creación y validación de reservas (RF01)

**Comportamiento:** Permitir crear una reserva con nombre, personas, fecha y hora. Rechazar datos obligatorios ausentes y cantidades de personas menores o iguales a cero.

**RED** (commit `09b3f1f`):

Se ampliaron las pruebas en `tests/test_reservation.py` con una fixture `restaurant` y pruebas parametrizadas. Tests escritos:
- `test_create_reservation_successfully`: verifica creación válida con todos los campos
- `test_create_reservation_without_customer_name_must_fail`: rechazo con nombre None, vacío o espacios
- `test_create_reservation_with_invalid_party_size_must_fail`: rechazo con personas None, 0 o negativa
- `test_create_reservation_without_date_must_fail`: rechazo con fecha None, vacía o espacios
- `test_create_reservation_without_time_must_fail`: rechazo con hora None, vacía o espacios
- `test_different_reservations_must_have_different_codes`: IDs únicos

El método `create_reservation` no validaba datos, por lo que las pruebas de validación fallaban esperando `ValueError`.

**GREEN** (commit `16b9903`):

Se agregaron validaciones en `create_reservation` para cada campo obligatorio. Se mantuvo `Reservation.create()` con UUID para generar códigos únicos.

**REFACTOR** (commit `3ced9c9`):

Se extrajo la validación de campos de texto a un método privado estático:

```python
@staticmethod
def _validate_required_text(value: str | None, field_name: str) -> None:
    if value is None or value.strip() == "":
        raise ValueError(f"{field_name} is required")
```

### Ciclo 2: Capacidad y disponibilidad (RF02)

**Comportamiento:** El sistema debe calcular la capacidad disponible para una fecha/hora y rechazar reservas que la excedan.

**RED** (commit `89df8a9`):

Tests escritos:
- `test_availability_is_full_when_no_reservations_exist`: sin reservas, disponibilidad = 30
- `test_availability_is_reduced_by_existing_reservations`: reserva de 26 personas, disponibilidad = 4
- `test_create_reservation_exceeding_capacity_must_fail`: con 26 reservadas, reserva de 6 debe fallar

`check_availability` lanzaba `NotImplementedError`.

**GREEN** (commits `208f9b8`, `83a41d5`, `588f87b`):

Se implementó `check_availability` calculando la diferencia entre capacidad total y personas reservadas. Se agregó validación en `create_reservation` para rechazar reservas que excedan la capacidad.

**REFACTOR** (commit `067b566`):

Se extrajo el cálculo de capacidad reservada a `_get_reserved_capacity`, que filtra solo reservas activas para la fecha/hora dada.

### Ciclo 3: Cancelación de reservas (RF03)

**Comportamiento:** Cancelar reservas con validación de código existente, estado previo, y liberación de capacidad.

**RED** (commits `89be80b`, `b759af3`, `1592982`, `6508fe9`):

Tests escritos:
- `test_cancel_valid_reservation_changes_status`: cancelar reserva activa
- `test_cancel_nonexistent_code_returns_false`: código inexistente retorna False
- `test_cancel_already_cancelled_raises_error`: doble cancelación lanza ValueError
- `test_cancel_reservation_frees_capacity`: capacidad se restaura tras cancelar

**GREEN** (commits `b71450c`, `2cf96c6`, `221b6aa`):

Se implementó `cancel_reservation` con early return para código inexistente, verificación de estado previo, y cambio de status a "cancelled". La liberación de capacidad se resolvió al integrar la implementación de RF02 (commit `68266ad`).

**REFACTOR**:

Se reestructuró el método con guard clauses para separar claramente los caminos: reserva no encontrada, ya cancelada, y cancelación exitosa.

### Ciclo 4: Consultar reservas por fecha (RF04)

**Comportamiento:** Retornar solo reservas activas para una fecha dada, excluyendo canceladas.

**RED** (commits `9ec60a9`, `8809321`):

Tests escritos:
- `test_get_reservations_by_date_returns_only_matching_date`: filtrado por fecha
- `test_get_reservations_by_date_excludes_cancelled`: excluir canceladas

`get_reservations_by_date` lanzaba `NotImplementedError`.

**GREEN** (commits `5cf91da`, `4e1d570`):

Se implementó el filtrado por fecha, y luego se agregó la condición `status == "active"` para excluir canceladas.

**REFACTOR** (commit `a646727`):

Se extrajo la condición de filtrado a un método privado:

```python
@staticmethod
def _matches_active_date(reservation: Reservation, date: str) -> bool:
    return reservation.date == date and reservation.status == "active"
```

## 4. Resultados de las Pruebas

```
tests/test_availability.py  — 3 passed
tests/test_cancellation.py  — 4 passed
tests/test_queries.py       — 2 passed
tests/test_reservation.py   — 15 passed

Total: 24 tests, 24 passed, 0 failed
Tiempo: 0.03s
```

## 5. Reflexión

**¿Cómo influyó TDD en el diseño del módulo?**

TDD obligó a pensar en la interfaz del sistema antes de la implementación. Los métodos de `Restaurant` se definieron primero como stubs, lo que permitió tener clara la API pública desde el inicio. El diseño quedó naturalmente separado en modelo (`Reservation`) y lógica de negocio (`Restaurant`).

**¿Qué cambios surgieron durante las refactorizaciones?**

Los cambios más significativos fueron la extracción de métodos privados (`_get_reserved_capacity`, `_validate_required_text`, `_matches_active_date`) que mejoraron la legibilidad sin cambiar el comportamiento. La refactorización fue más intencionada que reactiva, ya que el enfoque TDD tiende a producir código limpio desde el primer green.

**¿Qué dificultades encontraron al desarrollar primero las pruebas?**

La principal dificultad fue resistir la tentación de implementar más de lo necesario para pasar cada test. TDD requiere disciplina para escribir solo el código mínimo que haga pasar la prueba actual, y luego refactorizar. También fue un desafío coordinar el trabajo entre 5 personas, asegurando que las branches feature no generaran conflictos al hacer merge. Un caso concreto fue RF03, que necesitaba `check_availability` de RF02 para verificar la liberación de capacidad; la prueba quedó en estado RED hasta que se integró la rama de RF02 mediante merge.
