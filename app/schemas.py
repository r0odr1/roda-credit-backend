"""Esquemas Pydantic para validación de entrada y salida."""
from typing import Literal
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class SimulationRequest(BaseModel):
    """Petición de simulación de crédito."""

    vehicle_type: Literal["bicycle", "motorcycle"]
    vehicle_value: float = Field(..., gt=0, description="Valor del vehículo en COP")
    down_payment: float = Field(..., ge=0, description="Cuota inicial en COP")
    term_months: int = Field(..., ge=6, le=60, description="Plazo en meses")

    @field_validator("vehicle_value")
    @classmethod
    def validate_min_vehicle_value(cls, v: float) -> float:
        if v < 500_000:
            raise ValueError("El valor del vehículo debe ser mayor o igual a $500.000 COP")
        return v

    @model_validator(mode="after")
    def validate_down_payment_lte_value(self) -> "SimulationRequest":
        if self.down_payment > self.vehicle_value:
            raise ValueError("La cuota inicial no puede ser mayor al valor del vehículo")
        if self.down_payment >= self.vehicle_value:
            raise ValueError("La cuota inicial debe ser menor al valor del vehículo (debe haber monto a financiar)")
        return self


class ApplicationRequest(SimulationRequest):
    """Solicitud formal de crédito (incluye datos personales)."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=7, max_length=20)
    city: str = Field(..., min_length=1, max_length=100)

    @field_validator("phone")
    @classmethod
    def validate_phone_digits(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned.isdigit():
            raise ValueError("El teléfono debe contener únicamente números")
        return cleaned

    @field_validator("first_name", "last_name", "city")
    @classmethod
    def strip_strings(cls, v: str) -> str:
        return v.strip()