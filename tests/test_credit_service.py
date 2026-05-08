"""Tests básicos del servicio de cálculo de crédito."""
import pytest
from app.services.credit_service import calculate_credit, build_amortization_schedule


def test_calculate_credit_basic():
    """Cálculo básico con tasa positiva."""
    result = calculate_credit(
        vehicle_value=2_000_000,
        down_payment=500_000,
        term_months=12,
        annual_rate=0.18,
    )
    assert result["financed_amount"] == 1_500_000.00
    assert result["monthly_payment"] > 0
    assert result["total_to_pay"] > result["financed_amount"]
    assert result["total_interest"] == pytest.approx(
        result["total_to_pay"] - result["financed_amount"], abs=0.01
    )


def test_calculate_credit_zero_rate():
    """Con tasa 0% la cuota es financed/term."""
    result = calculate_credit(
        vehicle_value=1_200_000,
        down_payment=200_000,
        term_months=10,
        annual_rate=0.0,
    )
    assert result["financed_amount"] == 1_000_000.00
    assert result["monthly_payment"] == 100_000.00
    assert result["total_interest"] == 0.0


def test_calculate_credit_invalid_down_payment():
    """Cuota inicial mayor o igual al valor del vehículo lanza error."""
    with pytest.raises(ValueError):
        calculate_credit(
            vehicle_value=1_000_000,
            down_payment=1_000_000,
            term_months=12,
            annual_rate=0.18,
        )


def test_amortization_schedule_consistency():
    """La suma de abonos a capital debe igualar al monto financiado."""
    result = calculate_credit(
        vehicle_value=3_000_000,
        down_payment=500_000,
        term_months=24,
        annual_rate=0.18,
    )
    schedule = build_amortization_schedule(
        financed_amount=result["financed_amount"],
        monthly_payment=result["monthly_payment"],
        monthly_rate=result["monthly_rate"],
        term_months=24,
    )
    assert len(schedule) == 24
    total_principal = sum(row["principal"] for row in schedule)
    assert total_principal == pytest.approx(result["financed_amount"], abs=1.0)
    # Saldo final debe ser 0
    assert schedule[-1]["balance"] == 0.0
