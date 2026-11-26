
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from app.database import get_db
from app.auth import login_required


parking_bp = Blueprint("parking", __name__)

VEHICLE_TYPES = ("bike", "car", "truck", "other")
SLOT_TYPES = ("any", "bike", "car", "truck", "other")

@parking_bp.route("/vehicles", methods=["GET", "POST"])
@login_required
def vehicles():

    db = get_db()

    if request.method == "POST":

        vehicle_number = request.form.get(
            "vehicle_number", ""
        ).strip().upper()

        owner_name = request.form.get(
            "owner_name", ""
        ).strip()

        vehicle_type = request.form.get(
            "vehicle_type", ""
        ).strip().lower()

        if not vehicle_number or not owner_name:
            flash("All vehicle details are required.", "danger")

        elif vehicle_type not in VEHICLE_TYPES:
            flash("Invalid vehicle type.", "danger")

        else:
            try:
                with db.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO vehicles
                        (vehicle_number, owner_name, vehicle_type)
                        VALUES (%s, %s, %s)
                        """,
                        (
                            vehicle_number,
                            owner_name,
                            vehicle_type
                        )
                    )

                db.commit()
                flash("Vehicle registered successfully!", "success")

            except Exception:
                db.rollback()
                flash(
                    "Vehicle registration failed. "
                    "Check whether the vehicle number already exists.",
                    "danger"
                )

            return redirect(url_for("parking.vehicles"))

    try:
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM vehicles
                ORDER BY id DESC
                """
            )
            vehicle_list = cursor.fetchall()

    finally:
        db.close()

    return render_template(
        "vehicles.html",
        vehicles=vehicle_list
    )


@parking_bp.route("/slots", methods=["GET", "POST"])
@login_required
def slots():

    db = get_db()

    if request.method == "POST":

        slot_number = request.form.get(
            "slot_number", ""
        ).strip().upper()

        allowed_type = request.form.get(
            "allowed_vehicle_type", "any"
        ).strip().lower()

        if not slot_number:
            flash("Slot number is required.", "danger")

        elif allowed_type not in SLOT_TYPES:
            flash("Invalid vehicle type.", "danger")

        else:
            try:
                with db.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO parking_slots
                        (slot_number, allowed_vehicle_type)
                        VALUES (%s, %s)
                        """,
                        (slot_number, allowed_type)
                    )

                db.commit()
                flash("Parking slot added successfully!", "success")

            except Exception:
                db.rollback()
                flash(
                    "Could not add slot. "
                    "The slot number may already exist.",
                    "danger"
                )

            return redirect(url_for("parking.slots"))

    try:
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM parking_slots
                ORDER BY slot_number
                """
            )
            slot_list = cursor.fetchall()

    finally:
        db.close()

    return render_template(
        "slots.html",
        slots=slot_list
    )

@parking_bp.route("/entry", methods=["GET", "POST"])
@login_required
def entry():

    db = get_db()

    if request.method == "POST":

        vehicle_id = request.form.get("vehicle_id", type=int)
        slot_id = request.form.get("slot_id", type=int)

        if not vehicle_id or not slot_id:
            flash("Please select a vehicle and parking slot.", "danger")
            return redirect(url_for("parking.entry"))

        try:
            with db.cursor() as cursor:

                
                cursor.execute(
                    """
                    SELECT *
                    FROM vehicles
                    WHERE id = %s
                    FOR UPDATE
                    """,
                    (vehicle_id,)
                )
                vehicle = cursor.fetchone()

                if not vehicle:
                    raise ValueError("Vehicle not found.")

                
                cursor.execute(
                    """
                    SELECT id
                    FROM parking_records
                    WHERE vehicle_id = %s
                    AND status = 'active'
                    FOR UPDATE
                    """,
                    (vehicle_id,)
                )

                if cursor.fetchone():
                    raise ValueError(
                        "This vehicle is already parked."
                    )

                
                cursor.execute(
                    """
                    SELECT *
                    FROM parking_slots
                    WHERE id = %s
                    FOR UPDATE
                    """,
                    (slot_id,)
                )
                slot = cursor.fetchone()

                if not slot:
                    raise ValueError("Parking slot not found.")

                if slot["status"] != "available":
                    raise ValueError("This parking slot is unavailable.")

                if slot["allowed_vehicle_type"] not in (
                    "any", vehicle["vehicle_type"]
                ):
                    raise ValueError(
                        "This parking slot is not suitable "
                        "for the selected vehicle."
                    )

                
                cursor.execute(
                    """
                    INSERT INTO parking_records
                    (vehicle_id, slot_id, entry_time, status)
                    VALUES (%s, %s, NOW(), 'active')
                    """,
                    (vehicle_id, slot_id)
                )

                
                cursor.execute(
                    """
                    UPDATE parking_slots
                    SET status = 'occupied'
                    WHERE id = %s
                    """,
                    (slot_id,)
                )

            db.commit()
            flash("Vehicle entry recorded successfully!", "success")

        except Exception as error:
            db.rollback()
            flash(str(error), "danger")

        return redirect(url_for("parking.entry"))

    try:
        with db.cursor() as cursor:

            
            cursor.execute(
                """
                SELECT v.*
                FROM vehicles v
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM parking_records pr
                    WHERE pr.vehicle_id = v.id
                    AND pr.status = 'active'
                )
                ORDER BY v.vehicle_number
                """
            )
            vehicle_list = cursor.fetchall()

           
            cursor.execute(
                """
                SELECT *
                FROM parking_slots
                WHERE status = 'available'
                ORDER BY slot_number
                """
            )
            slot_list = cursor.fetchall()

    finally:
        db.close()

    return render_template(
        "entry.html",
        vehicles=vehicle_list,
        slots=slot_list
    )


@parking_bp.route("/exit", methods=["GET", "POST"])
@login_required
def exit_vehicle():

    db = get_db()

    if request.method == "POST":

        record_id = request.form.get("record_id", type=int)

        payment_method = request.form.get(
            "payment_method", "cash"
        ).strip().lower()

        if not record_id:
            flash("Please select a parking record.", "danger")
            return redirect(url_for("parking.exit_vehicle"))

        if payment_method not in ("cash", "card", "online"):
            flash("Invalid payment method.", "danger")
            return redirect(url_for("parking.exit_vehicle"))

        try:
            with db.cursor() as cursor:

                
                cursor.execute(
                    """
                    SELECT
                        pr.id,
                        pr.vehicle_id,
                        pr.slot_id,
                        pr.entry_time,
                        v.vehicle_type
                    FROM parking_records pr
                    JOIN vehicles v ON pr.vehicle_id = v.id
                    WHERE pr.id = %s
                    AND pr.status = 'active'
                    FOR UPDATE
                    """,
                    (record_id,)
                )

                record = cursor.fetchone()

                if not record:
                    raise ValueError(
                        "Active parking record not found."
                    )

                
                cursor.execute(
                    """
                    SELECT GREATEST(
                        1,
                        TIMESTAMPDIFF(
                            MINUTE,
                            entry_time,
                            NOW()
                        )
                    ) AS duration
                    FROM parking_records
                    WHERE id = %s
                    """,
                    (record_id,)
                )

                duration = cursor.fetchone()["duration"]

                
                billed_hours = max(
                    1,
                    (duration + 59) // 60
                )

                
                cursor.execute(
                    """
                    SELECT hourly_rate
                    FROM pricing
                    WHERE vehicle_type = %s
                    """,
                    (record["vehicle_type"],)
                )

                pricing = cursor.fetchone()

                if not pricing:
                    raise ValueError(
                        "Parking price is not configured "
                        "for this vehicle type."
                    )

                total_amount = (
                    pricing["hourly_rate"] * billed_hours
                )

                
                cursor.execute(
                    """
                    UPDATE parking_records
                    SET
                        exit_time = NOW(),
                        duration_minutes = %s,
                        total_amount = %s,
                        status = 'completed'
                    WHERE id = %s
                    AND status = 'active'
                    """,
                    (
                        duration,
                        total_amount,
                        record_id
                    )
                )

                if cursor.rowcount != 1:
                    raise ValueError(
                        "Could not complete this parking record."
                    )

                
                cursor.execute(
                    """
                    UPDATE parking_slots
                    SET status = 'available'
                    WHERE id = %s
                    AND status = 'occupied'
                    """,
                    (record["slot_id"],)
                )

                if cursor.rowcount != 1:
                    raise ValueError(
                        "Could not release the parking slot."
                    )

                
                cursor.execute(
                    """
                    INSERT INTO payments
                    (
                        record_id,
                        amount,
                        payment_method,
                        payment_status,
                        paid_at
                    )
                    VALUES (%s, %s, %s, 'paid', NOW())
                    """,
                    (
                        record_id,
                        total_amount,
                        payment_method
                    )
                )

            db.commit()

            flash(
                f"Vehicle exit completed. "
                f"Parking fee: NPR {total_amount:.2f}",
                "success"
            )

        except Exception as error:
            db.rollback()
            flash(str(error), "danger")

        return redirect(url_for("parking.exit_vehicle"))

    try:
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    pr.id AS record_id,
                    v.vehicle_number,
                    v.owner_name,
                    v.vehicle_type,
                    ps.slot_number,
                    pr.entry_time
                FROM parking_records pr
                JOIN vehicles v ON pr.vehicle_id = v.id
                JOIN parking_slots ps ON pr.slot_id = ps.id
                WHERE pr.status = 'active'
                ORDER BY pr.entry_time ASC
                """
            )

            active_records = cursor.fetchall()

    finally:
        db.close()

    return render_template(
        "exit.html",
        active_records=active_records
    )

@parking_bp.route("/history")
@login_required
def history():

    db = get_db()

    try:
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    pr.id,
                    v.vehicle_number,
                    v.owner_name,
                    v.vehicle_type,
                    ps.slot_number,
                    pr.entry_time,
                    pr.exit_time,
                    pr.duration_minutes,
                    pr.total_amount,
                    pr.status,
                    p.payment_method,
                    p.payment_status
                FROM parking_records pr
                JOIN vehicles v ON pr.vehicle_id = v.id
                JOIN parking_slots ps ON pr.slot_id = ps.id
                LEFT JOIN payments p ON pr.id = p.record_id
                ORDER BY pr.id DESC
                LIMIT 200
                """
            )

            records = cursor.fetchall()

    finally:
        db.close()

    return render_template(
        "history.html",
        records=records
    )
