from app import app
from models import db, seed_database

with app.app_context():
    db.create_all()
    seed_database()
    print("Banco ClassSync criado e dados demonstrativos carregados.")
