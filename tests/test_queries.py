import pytest
from src.reservation.restaurant import Restaurant


@pytest.fixture
def restaurant():
    return Restaurant(capacity_per_slot=30)


def test_get_reservations_by_date_returns_only_matching_date(restaurant):
    restaurant.create_reservation("Juan Pérez", 4, "2026-09-01", "20:00")
    restaurant.create_reservation("Ana López", 2, "2026-09-01", "21:00")
    restaurant.create_reservation("Pedro Gómez", 3, "2026-09-01", "19:30")
    restaurant.create_reservation("Otro Cliente", 2, "2026-09-02", "20:00")

    reservations = restaurant.get_reservations_by_date("2026-09-01")

    assert len(reservations) == 3
    assert all(r.date == "2026-09-01" for r in reservations)

def test_get_reservations_by_date_excludes_cancelled(restaurant):
    active = restaurant.create_reservation("Juan Pérez", 4, "2026-09-01", "20:00")
    cancelled = restaurant.create_reservation("Ana López", 2, "2026-09-01", "21:00")
    cancelled.status = "cancelled"

    reservations = restaurant.get_reservations_by_date("2026-09-01")

    assert len(reservations) == 1
    assert reservations[0].id == active.id