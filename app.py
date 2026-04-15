from datetime import date
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "kardex.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH.as_posix()}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "dev-secret-key"

db = SQLAlchemy(app)


class Person(db.Model):
    __tablename__ = "personas"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    fecha_nac = db.Column(db.Date, nullable=False)


@app.route("/")
def index():
    personas = Person.query.order_by(Person.id.asc()).all()
    return render_template("index.html", personas=personas)


@app.route("/create", methods=["GET", "POST"])
def create_person():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()
        fecha_nac = request.form.get("fecha_nac", "").strip()

        if not nombre or not telefono or not fecha_nac:
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for("create_person"))

        try:
            fecha_nac_date = date.fromisoformat(fecha_nac)
        except ValueError:
            flash("La fecha de nacimiento no tiene un formato valido.", "error")
            return redirect(url_for("create_person"))

        nueva_persona = Person(nombre=nombre, telefono=telefono, fecha_nac=fecha_nac_date)
        db.session.add(nueva_persona)
        db.session.commit()
        flash("Registro creado correctamente.", "success")
        return redirect(url_for("index"))

    return render_template("create.html")


@app.route("/edit/<int:persona_id>", methods=["GET", "POST"])
def edit_person(persona_id):
    persona = Person.query.get_or_404(persona_id)

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()
        fecha_nac = request.form.get("fecha_nac", "").strip()

        if not nombre or not telefono or not fecha_nac:
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for("edit_person", persona_id=persona.id))

        try:
            fecha_nac_date = date.fromisoformat(fecha_nac)
        except ValueError:
            flash("La fecha de nacimiento no tiene un formato valido.", "error")
            return redirect(url_for("edit_person", persona_id=persona.id))

        persona.nombre = nombre
        persona.telefono = telefono
        persona.fecha_nac = fecha_nac_date
        db.session.commit()
        flash("Registro actualizado correctamente.", "success")
        return redirect(url_for("index"))

    return render_template("edit.html", persona=persona)


@app.route("/delete/<int:persona_id>", methods=["POST"])
def delete_person(persona_id):
    persona = Person.query.get_or_404(persona_id)
    db.session.delete(persona)
    db.session.commit()
    flash("Registro eliminado correctamente.", "success")
    return redirect(url_for("index"))


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True, port=5005)
