"""Endpoints de registro y consulta de solicitudes de crédito."""
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError

from app.extensions import db
from app.models import CreditApplication, VehicleType
from app.schemas import ApplicationRequest
from app.services.credit_service import calculate_credit, build_amortization_schedule

applications_bp = Blueprint("applications", __name__, url_prefix="/api")


@applications_bp.post("/applications")
def create_application():
    """
    POST /api/applications
    Body: datos de simulación + datos personales.
    Response: solicitud creada y persistida.
    """
    try:
        data = ApplicationRequest.model_validate(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify({"error": "validation_error", "details": e.errors()}), 400

    annual_rate = current_app.config["ANNUAL_INTEREST_RATE"]

    # Recalculamos en backend para evitar manipulación desde el cliente
    result = calculate_credit(
        vehicle_value=data.vehicle_value,
        down_payment=data.down_payment,
        term_months=data.term_months,
        annual_rate=annual_rate,
    )

    application = CreditApplication(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        phone=data.phone,
        city=data.city,
        vehicle_type=VehicleType(data.vehicle_type),
        vehicle_value=data.vehicle_value,
        down_payment=data.down_payment,
        term_months=data.term_months,
        financed_amount=result["financed_amount"],
        monthly_payment=result["monthly_payment"],
        total_interest=result["total_interest"],
        total_to_pay=result["total_to_pay"],
        annual_interest_rate=result["annual_rate"],
    )

    db.session.add(application)
    db.session.commit()

    return jsonify({
        "message": "Solicitud registrada exitosamente",
        "application": application.to_dict(),
    }), 201


@applications_bp.get("/applications")
def list_applications():
    """GET /api/applications - lista todas las solicitudes (útil para verificación)."""
    applications = (
        CreditApplication.query
        .order_by(CreditApplication.created_at.desc())
        .limit(100)
        .all()
    )
    return jsonify([a.to_dict() for a in applications]), 200


@applications_bp.get("/applications/<int:application_id>")
def get_application(application_id: int):
    """
    GET /api/applications/<id>
    Devuelve la solicitud individual junto con su plan de amortización
    reconstruido a partir de los datos persistidos.
    """
    application = db.session.get(CreditApplication, application_id)
    if application is None:
        return jsonify({
            "error": "not_found",
            "message": f"No se encontró la solicitud #{application_id}",
        }), 404

    # Reconstruimos la tasa mensual y el plan de pagos a partir de los datos persistidos
    annual_rate = float(application.annual_interest_rate)
    monthly_rate = (1 + annual_rate) ** (1 / 12) - 1

    schedule = build_amortization_schedule(
        financed_amount=float(application.financed_amount),
        monthly_payment=float(application.monthly_payment),
        monthly_rate=monthly_rate,
        term_months=application.term_months,
    )

    return jsonify({
        "application": application.to_dict(),
        "schedule": schedule,
    }), 200
