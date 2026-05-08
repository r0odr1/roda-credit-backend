"""Endpoints de simulación de crédito."""
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError

from app.schemas import SimulationRequest
from app.services.credit_service import calculate_credit, build_amortization_schedule

simulation_bp = Blueprint("simulation", __name__, url_prefix="/api")


@simulation_bp.post("/simulate")
def simulate_credit():
    """
    POST /api/simulate
    Body: { vehicle_type, vehicle_value, down_payment, term_months }
    Response: resumen del crédito + plan de amortización.
    """
    try:
        data = SimulationRequest.model_validate(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify({"error": "validation_error", "details": e.errors()}), 400

    annual_rate = current_app.config["ANNUAL_INTEREST_RATE"]

    result = calculate_credit(
        vehicle_value=data.vehicle_value,
        down_payment=data.down_payment,
        term_months=data.term_months,
        annual_rate=annual_rate,
    )

    schedule = build_amortization_schedule(
        financed_amount=result["financed_amount"],
        monthly_payment=result["monthly_payment"],
        monthly_rate=result["monthly_rate"],
        term_months=data.term_months,
    )

    return jsonify({
        "summary": {
            "vehicle_type": data.vehicle_type,
            "vehicle_value": data.vehicle_value,
            "down_payment": data.down_payment,
            "term_months": data.term_months,
            "financed_amount": result["financed_amount"],
            "monthly_payment": result["monthly_payment"],
            "total_interest": result["total_interest"],
            "total_to_pay": result["total_to_pay"],
            "annual_interest_rate": result["annual_rate"],
        },
        "schedule": schedule,
    }), 200
