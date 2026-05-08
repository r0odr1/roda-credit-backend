"""Lógica de negocio: cálculo de cuotas y plan de amortización (sistema francés)."""
from decimal import Decimal, ROUND_HALF_UP


def _round_money(value: float) -> float:
    """Redondea a 2 decimales usando ROUND_HALF_UP (estándar financiero)."""
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def calculate_credit(
    vehicle_value: float,
    down_payment: float,
    term_months: int,
    annual_rate: float,
) -> dict:
    """
    Calcula los valores principales del crédito usando el sistema de amortización francés
    (cuota fija). Convierte la tasa efectiva anual (EA) a tasa mensual equivalente.

    Args:
        vehicle_value: valor del vehículo en COP.
        down_payment: cuota inicial en COP.
        term_months: plazo en meses.
        annual_rate: tasa de interés efectiva anual (ej. 0.18 = 18% EA).

    Returns:
        dict con: financed_amount, monthly_payment, total_interest, total_to_pay,
        monthly_rate, annual_rate.
    """
    if term_months <= 0:
        raise ValueError("El plazo debe ser positivo")
    if vehicle_value <= 0:
        raise ValueError("El valor del vehículo debe ser positivo")
    if down_payment < 0:
        raise ValueError("La cuota inicial no puede ser negativa")
    if down_payment >= vehicle_value:
        raise ValueError("La cuota inicial debe ser menor al valor del vehículo")

    financed = vehicle_value - down_payment

    # Tasa mensual equivalente a partir de la EA: (1 + EA)^(1/12) - 1
    monthly_rate = (1 + annual_rate) ** (1 / 12) - 1

    # Fórmula de cuota fija (sistema francés)
    if monthly_rate == 0:
        monthly_payment = financed / term_months
    else:
        factor = (1 + monthly_rate) ** term_months
        monthly_payment = financed * (monthly_rate * factor) / (factor - 1)

    total_to_pay = monthly_payment * term_months
    total_interest = total_to_pay - financed

    return {
        "financed_amount": _round_money(financed),
        "monthly_payment": _round_money(monthly_payment),
        "total_interest": _round_money(total_interest),
        "total_to_pay": _round_money(total_to_pay),
        "monthly_rate": round(monthly_rate, 6),
        "annual_rate": annual_rate,
    }


def build_amortization_schedule(
    financed_amount: float,
    monthly_payment: float,
    monthly_rate: float,
    term_months: int,
) -> list[dict]:
    """
    Construye la tabla de amortización mes a mes.

    Returns:
        Lista de filas con: number, payment, interest, principal, balance.
    """
    schedule: list[dict] = []
    balance = financed_amount

    for month in range(1, term_months + 1):
        interest = balance * monthly_rate
        principal = monthly_payment - interest

        # Última cuota: ajustamos para evitar saldo negativo por redondeo
        if month == term_months:
            principal = balance
            payment = principal + interest
            new_balance = 0.0
        else:
            payment = monthly_payment
            new_balance = balance - principal

        schedule.append({
            "number": month,
            "payment": _round_money(payment),
            "interest": _round_money(interest),
            "principal": _round_money(principal),
            "balance": _round_money(max(new_balance, 0)),
        })

        balance = new_balance

    return schedule
