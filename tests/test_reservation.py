import pytest

from src.reservation.restaurant import Restaurant


@pytest.fixture
def restaurant():
    return Restaurant(capacity_per_slot=30)


def test_create_reservation_successfully(restaurant):
    reservation = restaurant.create_reservation(
        customer_name="Juan Pérez",
        party_size=4,

        date="2026-09-01",
        time="20:00",
    )
    assert reservation.id is not None
    assert reservation.customer_name == "Juan Pérez"
    assert reservation.party_size == 4
    assert reservation.date == "2026-09-01"
    assert reservation.time == "20:00"
    assert reservation.status == "active"


@pytest.mark.parametrize("customer_name", [None, "", "   "])
def test_create_reservation_without_customer_name_must_fail(restaurant, customer_name):
    with pytest.raises(ValueError):
        restaurant.create_reservation(
            customer_name=customer_name,
            party_size=4,
            date="2026-09-01",
            time="20:00",
        )


@pytest.mark.parametrize("party_size", [None, 0, -1])
def test_create_reservation_with_invalid_party_size_must_fail(restaurant, party_size):
    with pytest.raises(ValueError):
        restaurant.create_reservation(
            customer_name="Juan Pérez",
            party_size=party_size,
            date="2026-09-01",
            time="20:00",
        )


@pytest.mark.parametrize("date", [None, "", "   "])
def test_create_reservation_without_date_must_fail(restaurant, date):
    with pytest.raises(ValueError):
        restaurant.create_reservation(
            customer_name="Juan Pérez",
            party_size=4,
            date=date,
            time="20:00",
        )


@pytest.mark.parametrize("time", [None, "", "   "])
def test_create_reservation_without_time_must_fail(restaurant, time):
    with pytest.raises(ValueError):
        restaurant.create_reservation(
            customer_name="Juan Pérez",
            party_size=4,
            date="2026-09-01",
            time=time,
        )


def test_created_reservation_must_have_reservation_code(restaurant):
    reservation = restaurant.create_reservation(
        customer_name="Ana López",
        party_size=2,
        date="2026-09-02",
        time="21:00",
    )

    assert reservation.id is not None
    assert str(reservation.id).strip() != ""


def test_different_reservations_must_have_different_codes(restaurant):
    first_reservation = restaurant.create_reservation(
        customer_name="Ana López",
        party_size=2,
        date="2026-09-02",
        time="21:00",
    )
    second_reservation = restaurant.create_reservation(
        customer_name="Pedro Gómez",
        party_size=3,
        date="2026-09-03",
        time="19:30",
    )

    assert first_reservation.id != second_reservation.id