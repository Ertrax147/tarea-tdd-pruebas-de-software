from src.reservation.models import Reservation


class Restaurant:
    def __init__(self, capacity_per_slot: int = 30):
        self.capacity_per_slot = capacity_per_slot
        self._reservations: list[Reservation] = []

    def create_reservation(self, customer_name: str, party_size: int, date: str, time: str) -> Reservation:
        self._validate_required_text(customer_name, "customer_name")
        if party_size is None or party_size <= 0:
            raise ValueError("party_size must be greater than zero")
        self._validate_required_text(date, "date")
        self._validate_required_text(time, "time")

        if party_size > self.check_availability(date, time):
            raise ValueError("Not enough capacity")

        reservation = Reservation.create(customer_name, party_size, date, time)
        self._reservations.append(reservation)
        return reservation

    @staticmethod
    def _validate_required_text(value: str | None, field_name: str) -> None:
        if value is None or value.strip() == "":
            raise ValueError(f"{field_name} is required")

    def check_availability(self, date: str, time: str) -> int:
        return self.capacity_per_slot - self._get_reserved_capacity(date, time)

    def _get_reserved_capacity(self, date: str, time: str) -> int:
        return sum(
            res.party_size for res in self._reservations
            if res.date == date and res.time == time and res.status == "active"
        )

    def cancel_reservation(self, reservation_id: str) -> bool:
        reservation = next((r for r in self._reservations if r.id == reservation_id), None)
        
        if reservation is None:
            return False
            
        if reservation.status == "cancelled":
            raise ValueError("La reserva ya está cancelada")
            
        reservation.status = "cancelled"
        return True

    def get_reservations_by_date(self, date: str) -> list[Reservation]:
        raise NotImplementedError
