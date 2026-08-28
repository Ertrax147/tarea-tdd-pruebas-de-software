from src.reservation.models import Reservation


class Restaurant:
    def __init__(self, capacity_per_slot: int = 30):
        self.capacity_per_slot = capacity_per_slot
        self._reservations: list[Reservation] = []

    def create_reservation(self, customer_name: str, party_size: int, date: str, time: str) -> Reservation:
        if customer_name is None or customer_name.strip() == "":
            raise ValueError("customer_name is required")
        if party_size is None or party_size <= 0:
            raise ValueError("party_size must be greater than zero")
        if date is None or date.strip() == "":
            raise ValueError("date is required")
        if time is None or time.strip() == "":
            raise ValueError("time is required")

        reservation = Reservation.create(customer_name, party_size, date, time)
        self._reservations.append(reservation)
        return reservation

    def check_availability(self, date: str, time: str) -> int:
        raise NotImplementedError

    def cancel_reservation(self, reservation_id: str) -> bool:
        raise NotImplementedError

    def get_reservations_by_date(self, date: str) -> list[Reservation]:
        raise NotImplementedError
