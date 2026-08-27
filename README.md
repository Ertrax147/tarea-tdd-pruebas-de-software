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
python -m pytest
```

## Estructura del proyecto

```
src/reservation/
├── models.py        # Modelo de Reservation
└── restaurant.py    # Lógica de negocio (Restaurant)

tests/
└── test_reservation.py
```
