# Evidencia de ciclos TDD

Este documento registra la evidencia de los ciclos Red -> Green -> Refactor utilizados durante el desarrollo del módulo de gestión de reservas de restaurante. Por ahora se documenta únicamente el primer ciclo, correspondiente a RF01.

La evidencia fue reconstruida a partir del estado actual del repositorio, las pruebas en `tests/test_reservation.py`, el código de producción en `src/reservation/`, la configuración de `pytest` en `pyproject.toml` y el historial de Git.

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
