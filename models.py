from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash


db = SQLAlchemy()


class Class(db.Model):
    __tablename__ = "classes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    school_year = db.Column(db.String(20), nullable=False, default="2026")
    term = db.Column(db.String(40), nullable=False, default="1º semestre")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    users = db.relationship("User", back_populates="classroom", cascade="all, delete-orphan")
    events = db.relationship("AcademicEvent", back_populates="classroom", cascade="all, delete-orphan")


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")
    class_id = db.Column(db.Integer, db.ForeignKey("classes.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    classroom = db.relationship("Class", back_populates="users")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role in {"leader", "admin"}


class AcademicEvent(db.Model):
    __tablename__ = "academic_events"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_at = db.Column(db.DateTime, nullable=False)
    end_at = db.Column(db.DateTime, nullable=True)
    category = db.Column(db.String(40), nullable=False, default="Evento")
    class_id = db.Column(db.Integer, db.ForeignKey("classes.id"), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    classroom = db.relationship("Class", back_populates="events")
    created_by = db.relationship("User")
    CATEGORY_COLORS = {"Prova": "#e76f51", "Trabalho": "#2a9d8f", "Apresentação": "#8064a2", "Evento": "#f4a261", "Outro": "#457b9d"}

    @property
    def color(self):
        return self.CATEGORY_COLORS.get(self.category, self.CATEGORY_COLORS["Outro"])

    def to_calendar_event(self):
        return {"id": self.id, "title": self.title, "start": self.start_at.isoformat(), "end": self.end_at.isoformat() if self.end_at else None, "backgroundColor": self.color, "borderColor": self.color, "extendedProps": {"description": self.description or "", "category": self.category, "className": self.classroom.name}}


def seed_database():
    if Class.query.count() > 0:
        return
    classroom = Class(name="3º Ano B — Informática", school_year="2026", term="1º semestre")
    db.session.add(classroom)
    db.session.flush()
    leader = User(name="Líder da turma", email="lider@classsync.local", role="leader", class_id=classroom.id)
    leader.set_password("demo-password")
    student = User(name="Estudante Demo", email="aluno@classsync.local", role="student", class_id=classroom.id)
    student.set_password("demo-password")
    db.session.add_all([leader, student])
    db.session.flush()
    samples = [
        AcademicEvent(title="Prova de Banco de Dados", description="Avaliação sobre modelagem relacional e SQL.", start_at=datetime(2026, 9, 22, 8, 0), category="Prova", class_id=classroom.id, created_by_id=leader.id),
        AcademicEvent(title="Entrega do trabalho em grupo", description="Enviar o projeto pelo ambiente virtual.", start_at=datetime(2026, 9, 25, 23, 59), category="Trabalho", class_id=classroom.id, created_by_id=leader.id),
        AcademicEvent(title="Apresentação — Projeto Final", description="Apresentações dos grupos 1 a 4.", start_at=datetime(2026, 9, 29, 9, 0), category="Apresentação", class_id=classroom.id, created_by_id=leader.id),
        AcademicEvent(title="Reunião da turma", description="Alinhamento sobre a semana de provas.", start_at=datetime(2026, 10, 2, 13, 30), category="Evento", class_id=classroom.id, created_by_id=leader.id),
    ]
    db.session.add_all(samples)
    db.session.commit()
