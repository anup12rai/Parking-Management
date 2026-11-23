
from flask import Blueprint, render_template

from app.database import get_db
from app.auth import login_required


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def index():

    db = get_db()

    try:
        with db.cursor() as cursor:

            # Total registered vehicles
            cursor.execute(
                "SELECT COUNT(*) AS total FROM vehicles"
            )
            total_vehicles = cursor.fetchone()["total"]

            # Total parking slots
            cursor.execute(
                "SELECT COUNT(*) AS total FROM parking_slots"
            )
            total_slots = cursor.fetchone()["total"]

            # Available parking slots
            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM parking_slots
                WHERE status = 'available'
                """
            )
            available_slots = cursor.fetchone()["total"]

            # Occupied parking slots
            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM parking_slots
                WHERE status = 'occupied'
                """
            )
            occupied_slots = cursor.fetchone()["total"]

            # Currently parked vehicles
            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM parking_records
                WHERE status = 'active'
                """
            )
            active_vehicles = cursor.fetchone()["total"]

            # Today's revenue
            cursor.execute(
                """
                SELECT COALESCE(SUM(amount), 0) AS revenue
                FROM payments
                WHERE payment_status = 'paid'
                AND DATE(paid_at) = CURDATE()
                """
            )
            today_revenue = cursor.fetchone()["revenue"]

            # Recent parking activity
            cursor.execute(
                """
                SELECT
                    pr.id,
                    v.vehicle_number,
                    v.vehicle_type,
                    ps.slot_number,
                    pr.entry_time,
                    pr.exit_time,
                    pr.status
                FROM parking_records pr
                JOIN vehicles v ON pr.vehicle_id = v.id
                JOIN parking_slots ps ON pr.slot_id = ps.id
                ORDER BY pr.id DESC
                LIMIT 10
                """
            )
            recent_records = cursor.fetchall()

    finally:
        db.close()

    return render_template(
        "dashboard.html",
        total_vehicles=total_vehicles,
        total_slots=total_slots,
        available_slots=available_slots,
        occupied_slots=occupied_slots,
        active_vehicles=active_vehicles,
        today_revenue=today_revenue,
        recent_records=recent_records
    )
