import pytest
from app import app, db
from models import AcademicEvent, User


@pytest.fixture()
def client():
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with app.test_client() as client:
        with app.app_context():
            yield client
            db.session.rollback()


def login(client, email="lider@classsync.local", password="demo-password"):
    return client.post("/login", data={"email": email, "password": password}, follow_redirects=True)


def test_public_home(client):
    assert client.get("/").status_code == 200


def test_calendar_api_returns_events(client):
    response = client.get("/api/events")
    assert response.status_code == 200 and len(response.get_json()) >= 4


def test_login_page(client):
    assert client.get("/login").status_code == 200


def test_register_page(client):
    assert client.get("/register").status_code == 200


def test_invalid_login_rejected(client):
    response = client.post("/login", data={"email": "lider@classsync.local", "password": "wrong"}, follow_redirects=True)
    assert b"inv\xc3\xa1lidos" in response.data


def test_leader_login_succeeds(client):
    response = login(client)
    assert b"Login realizado" in response.data


def test_student_login_succeeds(client):
    response = login(client, "aluno@classsync.local")
    assert b"Login realizado" in response.data


def test_logout_clears_session(client):
    login(client)
    response = client.get("/logout", follow_redirects=True)
    assert b"Sess\xc3\xa3o encerrada" in response.data


def test_admin_requires_login(client):
    assert client.get("/admin").status_code == 302


def test_student_cannot_access_admin(client):
    login(client, "aluno@classsync.local")
    assert client.get("/admin").status_code == 302


def test_leader_can_access_admin(client):
    login(client)
    assert client.get("/admin").status_code == 200


def test_register_new_student(client):
    email = "novo.aluno@example.com"
    response = client.post("/register", data={"name": "Novo Aluno", "email": email, "password": "senha-segura-123"}, follow_redirects=True)
    assert b"Cadastro realizado" in response.data
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        assert user and user.password_hash != "senha-segura-123" and user.check_password("senha-segura-123")
        db.session.delete(user)
        db.session.commit()


def test_register_rejects_short_password(client):
    response = client.post("/register", data={"name": "Aluno", "email": "short@example.com", "password": "123"})
    assert response.status_code == 200 and b"pelo menos 8" in response.data


def test_register_rejects_invalid_email(client):
    response = client.post("/register", data={"name": "Aluno", "email": "invalido", "password": "senha-segura"})
    assert b"e-mail v\xc3\xa1lido" in response.data


def test_register_rejects_duplicate_email(client):
    response = client.post("/register", data={"name": "Duplicado", "email": "aluno@classsync.local", "password": "senha-segura"})
    assert b"j\xc3\xa1 est\xc3\xa1 cadastrado" in response.data


def test_leader_can_create_event(client):
    login(client)
    before = AcademicEvent.query.count()
    response = client.post("/admin/events/new", data={"title": "Evento de teste", "description": "Detalhe", "category": "Evento", "start_at": "2026-11-10T10:00"}, follow_redirects=True)
    assert response.status_code == 200 and b"Evento de teste" in response.data
    assert AcademicEvent.query.count() == before + 1


def test_event_validation_rejects_empty_title(client):
    login(client)
    response = client.post("/admin/events/new", data={"title": "", "category": "Evento", "start_at": "2026-11-10T10:00"})
    assert response.status_code == 422 and b"t\xc3\xadtulo" in response.data


def test_event_validation_rejects_bad_date(client):
    login(client)
    response = client.post("/admin/events/new", data={"title": "Teste", "category": "Evento", "start_at": "data-invalida"})
    assert response.status_code == 422 and b"data e hora" in response.data


def test_event_validation_rejects_invalid_category(client):
    login(client)
    response = client.post("/admin/events/new", data={"title": "Teste", "category": "Categoria-X", "start_at": "2026-11-10T10:00"})
    assert response.status_code == 422 and b"categoria v\xc3\xa1lida" in response.data


def test_leader_can_edit_event(client):
    login(client)
    event = AcademicEvent.query.first()
    response = client.post(f"/admin/events/{event.id}/edit", data={"title": "Título atualizado", "description": "Atualizado", "category": "Prova", "start_at": "2026-11-11T10:00"}, follow_redirects=True)
    assert response.status_code == 200 and b"T\xc3\xadtulo atualizado" in response.data


def test_leader_can_delete_event(client):
    login(client)
    event = AcademicEvent(title="Apagar", description="", category="Outro", start_at=__import__("datetime").datetime(2026, 12, 1, 10), class_id=1, created_by_id=1)
    db.session.add(event); db.session.commit(); event_id = event.id
    response = client.post(f"/admin/events/{event_id}/delete", follow_redirects=True)
    assert response.status_code == 200 and db.session.get(AcademicEvent, event_id) is None


def test_missing_event_returns_404(client):
    login(client)
    assert client.get("/admin/events/999999/edit").status_code == 404


def test_data_persists_in_database(client):
    assert User.query.filter_by(email="lider@classsync.local").first().check_password("demo-password")
