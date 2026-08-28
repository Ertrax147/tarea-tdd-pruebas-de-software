import pytest

from src.reservation.restaurant import Restaurant


@pytest.fixture
def restaurant():
    return Restaurant(capacity_per_slot=30)


def test_availability_is_full_when_no_reservations_exist(restaurant):
    availability = restaurant.check_availability(date="2026-09-01", time="20:00")
    
    assert availability == 30


def test_availability_is_reduced_by_existing_reservations(restaurant):
    # Creamos una reserva de 26 personas
    restaurant.create_reservation(
        customer_name="Familia Pérez",
        party_size=26,
        date="2026-09-01",
        time="20:00",
    )
    
    # Revisamos la disponibilidad
    availability = restaurant.check_availability(date="2026-09-01", time="20:00")
    
    # Como habían 30 espacios y se ocuparon 26, deberían quedar 4
    assert availability == 4


def test_create_reservation_exceeding_capacity_must_fail(restaurant):
    # Llenamos casi todo el restaurante
    restaurant.create_reservation(
        customer_name="Familia Pérez",
        party_size=26,
        date="2026-09-01",
        time="20:00",
    )
    
    # Intentar reservar para 6 debe fallar, porque solo quedan 4 espacios
    with pytest.raises(ValueError, match="Not enough capacity"):
        restaurant.create_reservation(
            customer_name="Familia González",
            party_size=6,
            date="2026-09-01",
            time="20:00",
        )
