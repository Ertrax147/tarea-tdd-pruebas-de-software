from src.reservation.restaurant import Restaurant


def test_create_reservation_successfully():
    restaurant = Restaurant(capacity_per_slot=30)
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
