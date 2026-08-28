import pytest

from src.reservation.restaurant import Restaurant


@pytest.fixture
def restaurant():
    return Restaurant(capacity_per_slot=30)


def test_availability_is_full_when_no_reservations_exist(restaurant):
    availability = restaurant.check_availability(date="2026-09-01", time="20:00")
    
    assert availability == 30
