import pytest
from src.reservation.restaurant import Restaurant

def test_cancel_valid_reservation_changes_status():
    restaurant = Restaurant(capacity_per_slot=30)
    reservation = restaurant.create_reservation("Cliente A", 5, "2026-08-30", "20:00")
    
    restaurant.cancel_reservation(reservation.id)
    
    updated_res = next(r for r in restaurant._reservations if r.id == reservation.id)
    assert updated_res.status == "cancelled"

def test_cancel_nonexistent_code_returns_false():
    restaurant = Restaurant(capacity_per_slot=30)
    result = restaurant.cancel_reservation("FAKE-ID")
    
    assert result is False

def test_cancel_already_cancelled_raises_error():
    restaurant = Restaurant(capacity_per_slot=30)
    reservation = restaurant.create_reservation("Cliente B", 2, "2026-08-30", "21:00")
    
    restaurant.cancel_reservation(reservation.id)
    
    with pytest.raises(ValueError, match="ya está cancelada"):
        restaurant.cancel_reservation(reservation.id)

def test_cancel_reservation_frees_capacity():
    restaurant = Restaurant(capacity_per_slot=30)
    reservation = restaurant.create_reservation("Cliente C", 10, "2026-08-30", "19:00")
    
    initial_capacity = restaurant.check_availability("2026-08-30", "19:00")
    assert initial_capacity == 20
    restaurant.cancel_reservation(reservation.id)
    restored_capacity = restaurant.check_availability("2026-08-30", "19:00")
    assert restored_capacity == 30