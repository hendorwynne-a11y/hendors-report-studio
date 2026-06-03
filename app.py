```python
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

database_url = os.getenv("DATABASE_URL")

if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )
else:
    database_url = "sqlite:///v17_bookings.db"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    patient_name = db.Column(db.String(200))
    dob = db.Column(db.String(50))
    contact = db.Column(db.String(100))
    email = db.Column(db.String(200))

    payment_type = db.Column(db.String(100))
    branch = db.Column(db.String(200))
    scan_type = db.Column(db.String(200))

    appointment_date = db.Column(db.String(100))
    appointment_time = db.Column(db.String(100))

    history = db.Column(db.Text)
    referrer = db.Column(db.String(200))
    notes = db.Column(db.Text)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("landing.html")


@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/patient-portal")
def patient_portal():
    return render_template("patient_portal.html")


@app.route("/reporting")
def reporting():
    return render_template("reporting.html")


@app.route("/admin-bookings")
def admin_bookings():
    return render_template("admin_bookings.html")


@app.route("/api/bookings", methods=["GET"])
def get_bookings():

    bookings = Booking.query.order_by(
        Booking.id.desc()
    ).all()

    return jsonify([
        {
            "id": booking.id,
            "patientName": booking.patient_name,
            "dob": booking.dob,
            "contact": booking.contact,
            "email": booking.email,
            "paymentType": booking.payment_type,
            "branch": booking.branch,
            "scanType": booking.scan_type,
            "appointmentDate": booking.appointment_date,
            "appointmentTime": booking.appointment_time,
            "history": booking.history,
            "referrer": booking.referrer,
            "notes": booking.notes
        }
        for booking in bookings
    ])


@app.route("/api/bookings", methods=["POST"])
def add_booking():

    data = request.get_json()

    booking = Booking(
        patient_name=data.get("patientName"),
        dob=data.get("dob"),
        contact=data.get("contact"),
        email=data.get("email"),
        payment_type=data.get("paymentType"),
        branch=data.get("branch"),
        scan_type=data.get("scanType"),
        appointment_date=data.get("appointmentDate"),
        appointment_time=data.get("appointmentTime"),
        history=data.get("history"),
        referrer=data.get("referrer"),
        notes=data.get("notes")
    )

    db.session.add(booking)
    db.session.commit()

    return jsonify({
        "message": "Booking saved successfully"
    })


@app.route("/api/bookings/<int:booking_id>", methods=["DELETE"])
def delete_booking(booking_id):

    booking = Booking.query.get_or_404(
        booking_id
    )

    db.session.delete(booking)
    db.session.commit()

    return jsonify({
        "message": "Booking deleted"
    })


if __name__ == "__main__":
    app.run(debug=True)
```
