"""Modelos de base de datos."""
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Numeric, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.extensions import db


class VehicleType(str, enum.Enum):
    """Tipos de vehículo soportados."""
    BICYCLE = "bicycle"
    MOTORCYCLE = "motorcycle"


class CreditApplication(db.Model):
    """Solicitud de crédito registrada por un usuario."""

    __tablename__ = "credit_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Datos personales
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)

    # Datos de la simulación
    vehicle_type: Mapped[VehicleType] = mapped_column(
        Enum(VehicleType, name="vehicle_type_enum"),
        nullable=False,
    )
    vehicle_value: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    down_payment: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    term_months: Mapped[int] = mapped_column(Integer, nullable=False)

    # Resultados calculados
    financed_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    monthly_payment: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    total_interest: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    total_to_pay: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    annual_interest_rate: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        """Serializa el objeto a un diccionario JSON-friendly."""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "city": self.city,
            "vehicle_type": self.vehicle_type.value,
            "vehicle_value": float(self.vehicle_value),
            "down_payment": float(self.down_payment),
            "term_months": self.term_months,
            "financed_amount": float(self.financed_amount),
            "monthly_payment": float(self.monthly_payment),
            "total_interest": float(self.total_interest),
            "total_to_pay": float(self.total_to_pay),
            "annual_interest_rate": float(self.annual_interest_rate),
            "created_at": self.created_at.isoformat(),
        }