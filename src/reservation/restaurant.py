from src.reservation.models import Reservation


class Restaurant:
    def __init__(self, capacity_per_slot: int = 30):
        self.capacity_per_slot = capacity_per_slot
        self._reservations: list[Reservation] = []

    def create_reservation(self, customer_name: str, party_size: int, date: str, time: str) -> Reservation:
        raise NotImplementedError

    def check_availability(self, date: str, time: str) -> int:
        raise NotImplementedError

    def cancel_reservation(self, reservation_id: str) -> bool:
        raise NotImplementedError

    def get_reservations_by_date(self, date: str) -> list[Reservation]:
        raise NotImplementedError
