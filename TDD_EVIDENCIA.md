# Evidencia de ciclos TDD

Este documento registra la evidencia de los ciclos Red -> Green -> Refactor utilizados durante el desarrollo del módulo de gestión de reservas de restaurante.

La evidencia fue reconstruida a partir del estado actual del repositorio, las pruebas en `tests/*`, el código de producción en `src/reservation/`, la configuración de `pytest` en `pyproject.toml` y el historial de Git.

## Ciclo 1 - Creación y validación de reservas (RF01)

### 1. Comportamiento a implementar

El comportamiento buscado era permitir crear una reserva de restaurante mediante `Restaurant.create_reservation`, indicando:

- nombre del cliente;
- cantidad de personas;
- fecha;
- hora.

Cuando la reserva se crea correctamente, el sistema devuelve una instancia de `Reservation` con los datos entregados y un código de reserva en el atributo `id`. Además, la creación debe rechazar datos obligatorios ausentes y cantidades de personas menores o iguales a cero.

Este ciclo no incluye disponibilidad, capacidad por horario, cancelaciones ni consultas de reservas.

### 2. RED - Prueba inicial

Commit RED: `09b3f1f` - `test: add RF01 red tests`

En esta etapa se ampliaron las pruebas de `tests/test_reservation.py` para expresar el comportamiento esperado antes de implementar las validaciones. El archivo incorporó una fixture `restaurant` y pruebas parametrizadas con `pytest.mark.parametrize`.

Pruebas relevantes escritas durante RED:

- `test_create_reservation_successfully`: verifica que una reserva válida conserve `customer_name`, `party_size`, `date`, `time`, tenga `id` y estado `active`.
- `test_create_reservation_without_customer_name_must_fail`: verifica rechazo con nombre `None`, vacío o compuesto solo por espacios.
- `test_create_reservation_with_invalid_party_size_must_fail`: verifica rechazo con cantidad de personas `None`, `0` o negativa.
- `test_create_reservation_without_date_must_fail`: verifica rechazo con fecha `None`, vacía o compuesta solo por espacios.
- `test_create_reservation_without_time_must_fail`: verifica rechazo con hora `None`, vacía o compuesta solo por espacios.
- `test_created_reservation_must_have_reservation_code`: verifica que el código de reserva exista y no esté vacío.
- `test_different_reservations_must_have_different_codes`: verifica que dos reservas distintas tengan códigos distintos.

Fragmento representativo del contrato definido por las pruebas:

```python
with pytest.raises(ValueError):
    restaurant.create_reservation(
        customer_name=customer_name,
        party_size=4,
        date="2026-09-01",
        time="20:00",
    )
```

### 3. ¿Por qué falló?

El fallo RED se reconstruye comparando el commit de pruebas `09b3f1f` con el commit de implementación `16b9903`. Antes de GREEN, `Restaurant.create_reservation` delegaba directamente en `Reservation.create`, agregaba la reserva a `_reservations` y la devolvía, pero no validaba los datos obligatorios ni la cantidad de personas.

Por esa razón, las pruebas que esperaban `ValueError` para nombre, fecha, hora o cantidad inválida fallaban porque la reserva se creaba igualmente. El problema representaba funcionalidad de RF01 todavía no implementada, no un error de sintaxis, imports o configuración de las pruebas.

No se encontró en el repositorio una salida guardada de `pytest` correspondiente al momento exacto del commit RED; la causa del fallo se identificó mediante el historial y las diferencias de código.

### 4. GREEN - Implementación mínima

Commit GREEN: `16b9903` - `feat: implement RF01 reservation creation and validation (green)`

La implementación mínima se realizó en `src/reservation/restaurant.py`, dentro de `Restaurant.create_reservation`. Se agregaron validaciones antes de crear la reserva:

- `customer_name` no puede ser `None`, vacío ni solo espacios.
- `party_size` no puede ser `None` ni menor o igual a cero.
- `date` no puede ser `None`, vacía ni solo espacios.
- `time` no puede ser `None`, vacía ni solo espacios.

Cuando los datos son válidos, el método conserva el flujo existente: llama a `Reservation.create(customer_name, party_size, date, time)`, agrega la reserva a `_reservations` y devuelve la instancia creada.

La entidad `Reservation`, definida en `src/reservation/models.py`, ya existía con los atributos `id`, `customer_name`, `party_size`, `date`, `time` y `status`. El código de reserva se genera en `Reservation.create` usando `uuid.uuid4()` y se almacena como cadena en `id`.

Esta implementación fue suficiente para satisfacer las pruebas de RF01 sin incorporar reglas de disponibilidad ni funcionalidades futuras.

### 5. REFACTOR - Mejora del código

Commit REFACTOR: `3ced9c9` - `refactor: improve RF01 reservation creation design`

Después de alcanzar GREEN, se detectó duplicación en las validaciones de campos obligatorios de texto. Las condiciones para `customer_name`, `date` y `time` repetían la misma regla: rechazar `None`, cadena vacía o cadena compuesta solo por espacios.

El cambio realizado fue extraer esa regla común a un método privado y estático de `Restaurant`:

```python
@staticmethod
def _validate_required_text(value: str | None, field_name: str) -> None:
    if value is None or value.strip() == "":
        raise ValueError(f"{field_name} is required")
```

Con esto, `create_reservation` quedó más legible y la validación de textos obligatorios quedó centralizada. El comportamiento observable se preservó porque se mantuvieron las mismas condiciones de rechazo y se continuó usando `ValueError`.

No se modificaron las pruebas durante REFACTOR y no se agregaron reglas nuevas de negocio.

### 6. Resultado del ciclo

Después de la refactorización, la suite completa continúa pasando con la configuración real del proyecto.

Comando ejecutado:

```powershell
python -m pytest
```

Resultado actual:

```text
collected 15 items
tests\test_reservation.py ............... [100%]
15 passed in 0.03s
```

| Etapa | Objetivo | Resultado |
| --- | --- | --- |
| RED | Definir el comportamiento mediante pruebas | Se agregaron pruebas para RF01 que exponían validaciones todavía ausentes |
| GREEN | Implementar el mínimo código requerido | Se agregaron validaciones en `Restaurant.create_reservation` y las pruebas pasaron |
| REFACTOR | Mejorar el diseño sin cambiar comportamiento | Se extrajo `_validate_required_text` y todas las pruebas continúan pasando |

## Funcionalidad: RF02 - Consultar Disponibilidad

### Ciclo 2 - Disponibilidad completa

#### 1. Comportamiento a implementar
El sistema debe permitir determinar la disponibilidad inicial del restaurante para una fecha y hora, devolviendo la capacidad máxima configurada (30 por defecto) cuando no hay reservas.

#### 2. RED - Prueba escrita inicialmente
Commit: `test: add RF02 red tests`
Se escribió la prueba `test_availability_is_full_when_no_reservations_exist` que verifica que `check_availability` retorne 30.
**Por qué falló:** Porque el método `check_availability` no estaba implementado y lanzaba un `NotImplementedError`.

#### 3. GREEN - Implementación mínima
Commit: `feat: implement availability calculation (green)`
Se modificó `check_availability` para que simplemente retornara `self.capacity_per_slot`. Esto fue suficiente para hacer pasar la prueba.

#### 4. REFACTOR - Mejora realizada
Debido a la simplicidad del código (una sola línea), no existía oportunidad real de refactorización matemática o estructural, por lo que se mantuvo el código intacto, respetando la regla de no sobre-diseñar.


### Ciclo 3 - Capacidad reducida

#### 1. Comportamiento a implementar
El sistema debe calcular las personas reservadas para una fecha/hora y restar esa cantidad a la capacidad total.

#### 2. RED - Prueba escrita inicialmente
Commit: `test: add capacity reduction red test`
Se agregó la prueba `test_availability_is_reduced_by_existing_reservations` donde se reserva para 26 personas y se espera que la disponibilidad baje a 4.
**Por qué falló:** Porque el código de la fase anterior devolvía siempre el número fijo 30.

#### 3. GREEN - Implementación mínima
Commit: `feat: implement capacity reduction calculation (green)`
Se agregó lógica dentro de `check_availability` para recorrer la lista `_reservations`, sumar el `party_size` de las reservas activas en esa fecha/hora, y restarlo del total.

#### 4. REFACTOR - Mejora realizada
Commit: `refactor: extract reserved capacity calculation`
Se identificó que `check_availability` estaba asumiendo mucha responsabilidad matemática. Se extrajo la lógica de suma y filtrado a un nuevo método privado `_get_reserved_capacity`, mejorando la legibilidad. Todas las pruebas siguieron pasando exitosamente.


### Ciclo 4 - Rechazo por capacidad insuficiente

#### 1. Comportamiento a implementar
El sistema debe bloquear la creación de una reserva si el número de personas solicitadas excede la capacidad disponible.

#### 2. RED - Prueba escrita inicialmente
Commit: `test: add capacity rejection red test`
Se agregó la prueba `test_create_reservation_exceeding_capacity_must_fail`, que intenta reservar para 6 personas cuando solo quedan 4, esperando un `ValueError`.
**Por qué falló:** Porque `create_reservation` no realizaba ninguna validación de capacidad antes de guardar la reserva.

#### 3. GREEN - Implementación mínima
Commit: `feat: implement capacity validation for new reservations (green)`
Se agregó un bloque condicional en `create_reservation` que lanza un `ValueError("Not enough capacity")` si `party_size > self.check_availability(date, time)`.

#### 4. REFACTOR - Mejora realizada
No se realizó refactorización adicional en este ciclo ya que la validación agregada era limpia, delegaba correctamente la verificación a `check_availability` y no introducía duplicación.

## Funcionalidad: RF03 - Cancelación de Reservas

Los siguientes 4 ciclos documentan el desarrollo de `Restaurant.cancel_reservation` y la verificación de liberación de capacidad mediante `check_availability`. La evidencia fue reconstruida ejecutando `pytest` sobre cada commit real del historial de la rama.

### Ciclo 1 - Cancelación exitosa de una reserva

#### 1. Comportamiento a implementar
Al cancelar una reserva existente indicando su código (`id`), el sistema debe cambiar su estado a `"cancelled"`.

#### 2. RED - Prueba escrita inicialmente
Commit: `test: verify successful cancellation changes status to cancelled` (`89be80b`)

```python
def test_cancel_valid_reservation_changes_status():
    restaurant = Restaurant(capacity_per_slot=30)
    reservation = restaurant.create_reservation("Cliente A", 5, "2026-08-30", "20:00")

    restaurant.cancel_reservation(reservation.id)

    updated_res = next(r for r in restaurant._reservations if r.id == reservation.id)
    assert updated_res.status == "cancelled"
```

**Por qué falló:** `cancel_reservation` todavía era `raise NotImplementedError` (heredado de `develop`). La ejecución mostró:

```text
    def cancel_reservation(self, reservation_id: str) -> bool:
>       raise NotImplementedError
E       NotImplementedError
src/reservation/restaurant.py:29: NotImplementedError
FAILED tests/test_cancellation.py::test_cancel_valid_reservation_changes_status
1 failed in 0.02s
```

#### 3. GREEN - Implementación mínima
Commit: `feat: implement basic cancel_reservation logic` (`b71450c`)

Se implementó la lógica mínima: buscar la reserva por `id` usando `next()`, y si existe, cambiar su `status` a `"cancelled"` y retornar `True`; si no existe, retornar `False`.

```python
def cancel_reservation(self, reservation_id: str) -> bool:
        reservation = next((r for r in self._reservations if r.id == reservation_id), None)
        if reservation:
            reservation.status = "cancelled"
            return True
        return False
```

Con este cambio, la prueba pasó (1 passed).

#### 4. REFACTOR - Mejora realizada
No se realizó una refactorización separada en este ciclo: la indentación irregular introducida en el paso GREEN (bloque `cancel_reservation` con sangría extra) se corrigió en el commit `feat: validate id existence in cancel_reservation` (`2cf96c6`), reordenando el método con *early return* (`if reservation is None: return False`) antes de continuar con la lógica de cancelación. Este ajuste de estilo se documenta también como parte del Ciclo 6, ya que no modificó comportamiento y las pruebas continuaron en verde.

---

### Ciclo 2 - Cancelación con código de reserva inexistente

#### 1. Comportamiento a implementar
Si el código de reserva (`id`) no corresponde a ninguna reserva registrada, `cancel_reservation` debe retornar `False` sin lanzar excepciones.

#### 2. RED - Prueba escrita inicialmente
Commit: `test: return false when cancelling non-existent reservation id` (`b759af3`)

```python
def test_cancel_nonexistent_code_returns_false():
    restaurant = Restaurant(capacity_per_slot=30)
    result = restaurant.cancel_reservation("FAKE-ID")

    assert result is False
```

**Resultado real al escribir la prueba:** a diferencia de los demás ciclos, esta prueba **ya pasaba** en el momento de escribirla (`2 passed`), porque la implementación mínima del Ciclo 1 (`b71450c`) ya cubría el caso "no encontrado" con `return False` como parte de su rama `if/else`. Es decir, la generalización natural del primer `GREEN` satisfizo este comportamiento antes de tener una prueba dedicada. Se documenta igualmente como ciclo porque agrega cobertura de prueba explícita y permanente sobre una regla de negocio distinta (RF03: "código de reserva inexistente").

#### 3. GREEN / consolidación
Commit: `feat: validate id existence in cancel_reservation` (`2cf96c6`)

Se reescribió el método con *early return* para dejar expreso el camino "no encontrado", mejorando la legibilidad sin cambiar el comportamiento:

```python
def cancel_reservation(self, reservation_id: str) -> bool:
    reservation = next((r for r in self._reservations if r.id == reservation_id), None)

    if reservation is None:
        return False

    reservation.status = "cancelled"
    return True
```

Las 2 pruebas de `test_cancellation.py` existentes hasta ese punto continuaron pasando.

#### 4. REFACTOR - Mejora realizada
El cambio de `2cf96c6` cumple el rol de refactorización de este ciclo: separa claramente el camino de "reserva no encontrada" del camino de "reserva encontrada" mediante un *guard clause*, en lugar de anidar la lógica dentro de un `if reservation:`. No se requirió refactorización adicional.

---

### Ciclo 3 - Cancelación de una reserva ya cancelada

#### 1. Comportamiento a implementar
Si se cancela dos veces la misma reserva, la segunda cancelación debe lanzar `ValueError`, en lugar de permitir una doble cancelación silenciosa.

#### 2. RED - Prueba escrita inicialmente
Commit: `test: raise ValueError when cancelling an already cancelled reservation` (`1592982`)

```python
def test_cancel_already_cancelled_raises_error():
    restaurant = Restaurant(capacity_per_slot=30)
    reservation = restaurant.create_reservation("Cliente B", 2, "2026-08-30", "21:00")

    restaurant.cancel_reservation(reservation.id)

    with pytest.raises(ValueError, match="ya está cancelada"):
        restaurant.cancel_reservation(reservation.id)
```

**Por qué falló:** la implementación del Ciclo 2 encontraba la reserva por `id` sin verificar su estado, y simplemente volvía a asignar `status = "cancelled"` y retornar `True`. La segunda llamada no lanzaba ninguna excepción:

```text
    with pytest.raises(ValueError, match="ya está cancelada"):
>       restaurant.cancel_reservation(reservation.id)
E       Failed: DID NOT RAISE ValueError
tests/test_cancellation.py:25: Failed
FAILED tests/test_cancellation.py::test_cancel_already_cancelled_raises_error
1 failed, 2 passed in 0.02s
```

#### 3. GREEN - Implementación mínima
Commit: `feat: verify reservation status before cancelling` (`221b6aa`)

Se agregó una verificación de estado antes de reasignar `status`: si la reserva ya estaba `"cancelled"`, se lanza `ValueError("La reserva ya está cancelada")`.

```python
def cancel_reservation(self, reservation_id: str) -> bool:
    reservation = next((r for r in self._reservations if r.id == reservation_id), None)

    if reservation is None:
        return False

    if reservation.status == "cancelled":
        raise ValueError("La reserva ya está cancelada")

    reservation.status = "cancelled"
    return True
```

Con este cambio, las 3 pruebas de `test_cancellation.py` pasaron.

#### 4. REFACTOR - Mejora realizada
No se realizó una refactorización estructural adicional en este ciclo: el bloque de validación agregado es pequeño, se ubica junto a la búsqueda de la reserva y no introduce duplicación. Se mantuvo el diseño simple, evitando sobre-ingeniería sobre un método que aún no lo justificaba.

---

### Ciclo 4 - Liberación de capacidad al cancelar

#### 1. Comportamiento a implementar
Al cancelar una reserva, la capacidad disponible para esa fecha y hora (consultada mediante `check_availability`) debe restaurarse, excluyendo la reserva cancelada del cálculo.

#### 2. RED - Prueba escrita inicialmente
Commit: `test: verify availability is restored after cancellation` (`6508fe9`)

```python
def test_cancel_reservation_frees_capacity():
    restaurant = Restaurant(capacity_per_slot=30)
    reservation = restaurant.create_reservation("Cliente C", 10, "2026-08-30", "19:00")

    initial_capacity = restaurant.check_availability("2026-08-30", "19:00")
    restaurant.cancel_reservation(reservation.id)
    restored_capacity = restaurant.check_availability("2026-08-30", "19:00")

    assert restored_capacity == initial_capacity + 10
```

**Por qué falló:** en ese punto de la rama `feature/rf-03-cancelacion`, `check_availability` aún era `raise NotImplementedError` (su implementación pertenece a RF02 y todavía no se había integrado a esta rama):

```text
    def check_availability(self, date: str, time: str) -> int:
>       raise NotImplementedError
E       NotImplementedError
src/reservation/restaurant.py:26: NotImplementedError
FAILED tests/test_cancellation.py::test_cancel_reservation_frees_capacity
1 failed, 3 passed in 0.02s
```

#### 3. GREEN - Implementación
La implementación de `check_availability` no se escribió en esta rama, sino que se incorporó al integrar la rama `feature/RF02` mediante el **merge** `Merge pull request #1 from Ertrax147/develop` (`68266ad`), que trajo la implementación desarrollada por el compañero de RF02:

```python
def check_availability(self, date: str, time: str) -> int:
    return self.capacity_per_slot - self._get_reserved_capacity(date, time)

def _get_reserved_capacity(self, date: str, time: str) -> int:
    return sum(
        res.party_size for res in self._reservations
        if res.date == date and res.time == time and res.status == "active"
    )
```

Como `cancel_reservation` cambia el `status` de la reserva a `"cancelled"`, y `_get_reserved_capacity` sólo suma reservas con `status == "active"`, la capacidad se libera automáticamente al cancelar. Tras el merge, la prueba `test_cancel_reservation_frees_capacity` pasó.

Posteriormente, en el commit `test: update capacity test to use official check_availability method` (`bfbde7a`), se ajustó la prueba para usar valores absolutos y explícitos en lugar de relativos, verificando puntualmente los números de negocio del enunciado (capacidad 30, reserva de 10 personas):

```python
def test_cancel_reservation_frees_capacity():
    restaurant = Restaurant(capacity_per_slot=30)
    reservation = restaurant.create_reservation("Cliente C", 10, "2026-08-30", "19:00")

    initial_capacity = restaurant.check_availability("2026-08-30", "19:00")
    assert initial_capacity == 20
    restaurant.cancel_reservation(reservation.id)
    restored_capacity = restaurant.check_availability("2026-08-30", "19:00")
    assert restored_capacity == 30
```

#### 4. REFACTOR - Mejora realizada
No se aplicó una refactorización adicional propia de RF03 en este ciclo, ya que la lógica de cálculo de capacidad (`_get_reserved_capacity`) fue diseñada y refactorizada por el compañero responsable de RF02 (commit `refactor: extract reserved capacity calculation`, en su propia rama). Del lado de RF03, el único ajuste posterior fue de precisión en la prueba (valores absolutos en `bfbde7a`), sin cambios en el código de producción.

**Nota de integración:** este ciclo evidencia un punto de coordinación real entre equipos: RF03 necesitaba `check_availability` (responsabilidad de RF02) para poder verificar la liberación de capacidad de punta a punta. La prueba quedó en estado RED durante el desarrollo aislado de la rama, y sólo se resolvió al integrar (merge) el trabajo de RF02.

---

### Resumen de RF03 (Cancelación de reservas)

| Ciclo | Comportamiento | Commit RED | Commit GREEN | Resultado |
| --- | --- | --- | --- | --- |
| 1 | Cancelación exitosa | `89be80b` | `b71450c` | 1 passed |
| 2 | Código inexistente → `False` | `b759af3` | `2cf96c6` | 2 passed |
| 3 | Ya cancelada → `ValueError` | `1592982` | `221b6aa` | 3 passed |
| 4 | Liberación de capacidad | `6508fe9` | integrado vía merge `68266ad`, ajustado en `bfbde7a` | 4 passed |

## Funcionalidad: RF04 - Consultar Reservas

Los siguientes 2 ciclos documentan el desarrollo de `Restaurant.get_reservations_by_date`. La evidencia fue reconstruida ejecutando pytest sobre cada commit real de la rama `feature/RF-04`.

### Ciclo 1 - Filtrar reservas por fecha

### 1. Comportamiento a implementar
El comportamiento buscado era permitir consultar todas las reservas asociadas a una fecha determinada mediante `Restaurant.get_reservations_by_date`, retornando únicamente las reservas cuya fecha coincide con la solicitada.

### 2. RED - Prueba inicial
Commit RED: `test: add test for filtering reservations by date`

Se creó el archivo `tests/test_queries.py` con la siguiente prueba:

​```python
def test_get_reservations_by_date_returns_only_matching_date(restaurant):
    restaurant.create_reservation("Juan Pérez", 4, "2026-09-01", "20:00")
    restaurant.create_reservation("Ana López", 2, "2026-09-01", "21:00")
    restaurant.create_reservation("Pedro Gómez", 3, "2026-09-01", "19:30")
    restaurant.create_reservation("Otro Cliente", 2, "2026-09-02", "20:00")

    reservations = restaurant.get_reservations_by_date("2026-09-01")

    assert len(reservations) == 3
    assert all(r.date == "2026-09-01" for r in reservations)
​```

### 3. ¿Por qué falló?
Comando ejecutado:

​```powershell
pytest tests/test_queries.py
​```

Resultado:

​```text
FAILED tests/test_queries.py::test_get_reservations_by_date_returns_only_matching_date - NotImplementedError
src\reservation\restaurant.py:32: NotImplementedError
1 failed in 0.10s
​```

El fallo ocurrió porque `Restaurant.get_reservations_by_date` todavía contenía `raise NotImplementedError`, es decir, el comportamiento de RF04 aún no estaba implementado. No se trató de un error de sintaxis, imports ni configuración: la prueba expuso correctamente una funcionalidad pendiente.

### 4. GREEN - Implementación mínima
Commit GREEN: `feat: implement get_reservations_by_date`

Se reemplazó el método en `src/reservation/restaurant.py` por coincidencia de fecha:

​```python
def get_reservations_by_date(self, date: str) -> list[Reservation]:
    return [r for r in self._reservations if r.date == date]
​```

Comando ejecutado:

​```powershell
pytest tests/test_queries.py
​```

Resultado:

​```text
collected 1 item                                                                                                                              

tests\test_queries.py .                                                                                                                 [100%]

=============================================================
 1 passed in 0.06s
==============================================================
​```
Con este cambio, la prueba pasó (1 passed).

#### 4. REFACTOR - Mejora realizada
El método resultante tenía una sola responsabilidad y una condición simple, por lo que en este ciclo puntual no se identificó una mejora estructural adicional.

---

### Ciclo 2 - Excluir reservas canceladas

#### 1. Comportamiento a implementar
Las reservas con `status == "cancelled"` no deben aparecer en el resultado de `get_reservations_by_date`, aunque coincidan con la fecha consultada. Para mantener esta prueba autocontenida y no depender de la implementación de `cancel_reservation` (responsabilidad de RF03), el estado cancelado se simula asignando directamente el atributo `status` de la reserva.

#### 2. RED - Prueba escrita inicialmente
Commit: `test: exclude cancelled reservations from date query`

```python
def test_get_reservations_by_date_excludes_cancelled(restaurant):
    active = restaurant.create_reservation("Juan Pérez", 4, "2026-09-01", "20:00")
    cancelled = restaurant.create_reservation("Ana López", 2, "2026-09-01", "21:00")
    cancelled.status = "cancelled"

    reservations = restaurant.get_reservations_by_date("2026-09-01")

    assert len(reservations) == 1
    assert reservations[0].id == active.id
```

**Por qué falló:**
```text
    assert len(reservations) == 1
E   AssertionError: assert 2 == 1
E    +  where 2 = len([Reservation(id='f86ab840-...', ..., status='active'), Reservation(id='ac06c961-...', ..., status='cancelled')])
tests\test_queries.py:28: AssertionError
1 failed, 1 passed in 0.10s
```
`get_reservations_by_date` filtraba únicamente por `date`, sin considerar el `status` de la reserva. Por eso la reserva cancelada seguía apareciendo en el resultado junto con la activa.

#### 3. GREEN - Implementación mínima
Commit: `feat: filter out cancelled reservations in date query`

```python
def get_reservations_by_date(self, date: str) -> list[Reservation]:
    return [
        r for r in self._reservations
        if r.date == date and r.status == "active"
    ]
```

```text
(venv) PS C:\Users\ASUS\Documents\GitHub\tarea-tdd-pruebas-de-software> pytest tests/test_queries.py -v
====================================================================== test session starts ======================================================================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\ASUS\Documents\GitHub\tarea-tdd-pruebas-de-software\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\ASUS\Documents\GitHub\tarea-tdd-pruebas-de-software
configfile: pyproject.toml
collected 2 items                                                                                                                                                

tests/test_queries.py::test_get_reservations_by_date_returns_only_matching_date PASSED                                                                     [ 50%]
tests/test_queries.py::test_get_reservations_by_date_excludes_cancelled PASSED                                                                             [100%]

======================================================================= 2 passed in 0.02s =======================================================================
```

#### 4. REFACTOR - Mejora realizada
Commit: - `refactor: extract active-date matching condition`

La condición combinaba dos criterios (`fecha` y `status`) dentro de la comprehension, lo que reducía su legibilidad. Se extrajo a un método privado con nombre expresivo:

```python
def get_reservations_by_date(self, date: str) -> list[Reservation]:
    return [r for r in self._reservations if self._matches_active_date(r, date)]

@staticmethod
def _matches_active_date(reservation: Reservation, date: str) -> bool:
    return reservation.date == date and reservation.status == "active"
```

El comportamiento observable no cambió; se confirmó ejecutando la suite completa, la cual continuó pasando en su totalidad.

```text
(venv) PS C:\Users\ASUS\Documents\GitHub\tarea-tdd-pruebas-de-software> pytest
====================================================================== test session starts ======================================================================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\ASUS\Documents\GitHub\tarea-tdd-pruebas-de-software
configfile: pyproject.toml
testpaths: tests
collected 17 items                                                                                                                                               

tests\test_queries.py ..                                                                                                                                   [ 11%]
tests\test_reservation.py ...............                                                                                                                  [100%]

====================================================================== 17 passed in 0.04s =======================================================================
```

---
