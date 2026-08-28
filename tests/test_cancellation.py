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