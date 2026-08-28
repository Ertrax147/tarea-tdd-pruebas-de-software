# tarea-tdd-pruebas-de-software

Sistema de gestión de reservas para restaurante, desarrollado con TDD.

## Requisitos

- Python >= 3.10

## Instalación

```bash
pip install -e ".[test]"
```

## Ejecutar pruebas

```bash
python -m pytest -v
```

## Estructura del proyecto

```
src/reservation/
├── models.py        # Modelo de Reservation
└── restaurant.py    # Lógica de negocio (Restaurant)

tests/
├── test_reservation.py   # Tests de creación y validación (RF01)
├── test_availability.py  # Tests de disponibilidad (RF02)
├── test_cancellation.py  # Tests de cancelación (RF03)
└── test_queries.py       # Tests de consultas por fecha (RF04)

REPORTE.md           # Reporte del proyecto y reflexión de actividad
TDD_EVIDENCIA.md     # Evidencia detallada de ciclos TDD
```
