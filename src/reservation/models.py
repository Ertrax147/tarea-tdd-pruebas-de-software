import uuid
from dataclasses import dataclass


@dataclass
class Reservation:
    id: str
    customer_name: str
    party_size: int
    date: str
    time: str
    status: str = "active"

    @staticmethod
    def create(customer_name: str, party_size: int, date: str, time: str) -> "Reservation":
        return Reservation(
            id=str(uuid.uuid4()),
            customer_name=customer_name,
            party_size=party_size,
            date=date,
            time=time,
        )
