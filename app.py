import os
import re
from datetime import datetime
from functools import wraps

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from models import AcademicEvent, Class, User, db, seed_database

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///classsync.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()
    seed_database()


def current_user():
    user_id = session.get("user_id")
    return db.session.get(User, user_id) if user_id else None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            flash("Faça login para continuar.", "warning")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user().is_admin:
            flash("Apenas líderes podem gerenciar compromissos.", "danger")
            return redirect(url_for("index"))
        return view(*args, **kwargs)
    return wrapped


def parse_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def valid_email(value):
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value or ""))


def event_form_data(form):
    title = (form.get("title") or "").strip()
    description = (form.get("description") or "").strip()
    category = form.get("category") or ""
    start_at = parse_datetime(form.get("start_at"))
    end_at = parse_datetime(form.get("end_at"))
    errors = []
    if not title or len(title) > 160:
        errors.append("O título é obrigatório e deve ter até 160 caracteres.")
    if category not in AcademicEvent.CATEGORY_COLORS:
        errors.append("Selecione uma categoria válida.")
    if not start_at:
        errors.append("Informe uma data e hora de início válidas.")
    if form.get("end_at") and not end_at:
        errors.append("Informe uma data e hora de término válida.")
    if start_at and end_at and end_at < start_at:
        errors.append("O término não pode ser anterior ao início.")
    return {"title": title, "description": description, "category": category, "start_at": start_at, "end_at": end_at}, errors


@app.context_processor
def inject_context():
    return {"active_class": Class.query.first(), "user": current_user(), "is_admin": bool(current_user() and current_user().is_admin)}


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", code=404, message="A página ou registro não foi encontrado."), 404


@app.errorhandler(500)
def server_error(error):
    db.session.rollback()
    return render_template("error.html", code=500, message="Ocorreu um erro inesperado. Tente novamente."), 500


@app.get("/")
def index():
    classroom = Class.query.first()
    events = AcademicEvent.query.filter_by(class_id=classroom.id).order_by(AcademicEvent.start_at).all()
    return render_template("index.html", events=events)


@app.get("/api/events")
def api_events():
    classroom = Class.query.first()
    return jsonify([event.to_calendar_event() for event in AcademicEvent.query.filter_by(class_id=classroom.id).all()])


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user():
        return redirect(url_for("index"))
    if request.method == "POST":
        name, email, password = (request.form.get("name") or "").strip(), (request.form.get("email") or "").strip().lower(), request.form.get("password") or ""
        errors = []
        if len(name) < 2 or len(name) > 120: errors.append("Informe um nome entre 2 e 120 caracteres.")
        if not valid_email(email): errors.append("Informe um e-mail válido.")
        if len(password) < 8: errors.append("A senha deve ter pelo menos 8 caracteres.")
        if User.query.filter_by(email=email).first(): errors.append("Este e-mail já está cadastrado.")
        if not errors:
            classroom = Class.query.first()
            new_user = User(name=name, email=email, role="student", class_id=classroom.id)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash("Cadastro realizado. Agora faça login.", "success")
            return redirect(url_for("login"))
        for error in errors: flash(error, "danger")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session.clear()
            session["user_id"] = user.id
            flash("Login realizado com sucesso.", "success")
            return redirect(request.args.get("next") or url_for("index"))
        flash("E-mail ou senha inválidos.", "danger")
    return render_template("login.html")


@app.get("/logout")
def logout():
    session.clear()
    flash("Sessão encerrada.", "success")
    return redirect(url_for("index"))


@app.get("/admin")
@admin_required
def admin():
    events = AcademicEvent.query.order_by(AcademicEvent.start_at).all()
    return render_template("admin.html", events=events)


@app.route("/admin/events/new", methods=["GET", "POST"])
@admin_required
def new_event():
    if request.method == "POST":
        data, errors = event_form_data(request.form)
        if errors:
            for error in errors: flash(error, "danger")
            return render_template("event_form.html", event=None, form_title="Novo compromisso", form_data=request.form), 422
        classroom = current_user().classroom
        event = AcademicEvent(**data, class_id=classroom.id, created_by_id=current_user().id)
        db.session.add(event)
        db.session.commit()
        flash("Compromisso criado no calendário.", "success")
        return redirect(url_for("admin"))
    return render_template("event_form.html", event=None, form_title="Novo compromisso", form_data={})


@app.route("/admin/events/<int:event_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_event(event_id):
    event = db.get_or_404(AcademicEvent, event_id)
    if request.method == "POST":
        data, errors = event_form_data(request.form)
        if errors:
            for error in errors: flash(error, "danger")
            return render_template("event_form.html", event=event, form_title="Editar compromisso", form_data=request.form), 422
        for key, value in data.items(): setattr(event, key, value)
        db.session.commit()
        flash("Compromisso atualizado.", "success")
        return redirect(url_for("admin"))
    return render_template("event_form.html", event=event, form_title="Editar compromisso", form_data={})


@app.post("/admin/events/<int:event_id>/delete")
@admin_required
def delete_event(event_id):
    event = db.get_or_404(AcademicEvent, event_id)
    db.session.delete(event)
    db.session.commit()
    flash("Compromisso removido.", "success")
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=os.environ.get("FLASK_DEBUG", "0") == "1")
