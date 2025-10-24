# models.py
from extensoes import db
from flask_login import UserMixin
from datetime import date

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    senha = db.Column(db.String(200))
    tel = db.Column(db.String(20))
    banca = db.Column(db.Float, default=0.0)

    # Flask-Login exige esses métodos:
    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class Aposta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date) 
    valor_aposta = db.Column(db.String(20))
    retorno = db.Column(db.String(20))
    odd = db.Column(db.String(10))
    resultado = db.Column(db.String(20))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))


