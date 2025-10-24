# app.py
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from extensoes import db, login_manager
from models import Usuario, Aposta
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from threading import Thread
from telegram.ext import Application






app = Flask(__name__)
app.secret_key = 'segredo-super-seguro'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///apostas.db'

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('home.html', current_year=datetime.now().year)

@app.route('/dashboard')
@login_required

def dashboard():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    query = Aposta.query.filter_by(usuario_id=current_user.id)

    if data_inicio:
        data_inicio_obj = datetime.strptime(data_inicio, "%Y-%m-%d").date()
        query = query.filter(Aposta.data >= data_inicio_obj)

    if data_fim:
        data_fim_obj = datetime.strptime(data_fim, "%Y-%m-%d").date()
        query = query.filter(Aposta.data <= data_fim_obj)

    apostas = query.order_by(Aposta.data.asc()).all()
    banca = current_user.banca or 0

    valor_total_apostado = sum(float(a.valor_aposta.replace(',', '.')) for a in apostas)
    retorno_total = sum(float(a.retorno.replace(',', '.')) for a in apostas)
    lucro = retorno_total - valor_total_apostado
    lucro_percentual = round((lucro / banca) * 100, 2) if banca else 0
    roi = round((lucro / valor_total_apostado) * 100, 2) if valor_total_apostado else 0
    media_odd = round(sum(float(a.odd.replace(',', '.')) for a in apostas) / len(apostas), 2) if apostas else 0

    datas = list(set(a.data for a in apostas))
    dias_trabalho = len(datas)
    qtd_ganhos = sum(1 for a in apostas if a.resultado == 'Ganho')
    qtd_perdas = sum(1 for a in apostas if a.resultado == 'Perda')


    return render_template('dashboard.html',
        apostas=apostas,
        banca_atual=banca,
        lucro_bruto=f"{lucro:.2f}",
        lucro_percentual=lucro_percentual,
        roi=roi,
        media_odd=media_odd,
        dias_trabalho=dias_trabalho,
        qtd_ganhos=qtd_ganhos,
        qtd_perdas=qtd_perdas,
        data_inicio=data_inicio,
        data_fim=data_fim
    )

@app.route('/atualizar_banca', methods=['POST'])
@login_required
def atualizar_banca():
    nova_banca = request.form.get('banca')
    try:
        current_user.banca = float(nova_banca)
        db.session.commit()
        flash("Banca atualizada com sucesso!", "success")
    except:
        flash("Erro ao atualizar a banca.", "danger")
    return redirect(url_for('dashboard'))

# ... (configuração do app e db)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        telefone = request.form['telefone']
        senha_hash = generate_password_hash(senha)

        novo_usuario = Usuario(nome=nome, email=email, senha=senha_hash, tel=telefone)
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Cadastro realizado com sucesso!')
        return redirect(url_for('dashboard'))

    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha, senha):
            login_user(usuario)
            return redirect(url_for('dashboard'))
        else:
            flash('Login inválido')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/api/usuario", methods=["GET"])
def consultar_usuario():
    telefone = request.args.get("tel")
    if not telefone:
        return jsonify({"erro": "Telefone não informado"}), 400

    usuario = Usuario.query.filter_by(tel=telefone).first()
    if usuario:
        return jsonify({
            "id": usuario.id,
            "nome": usuario.nome,
            "telefone": usuario.tel
        })
    else:
        return jsonify({"erro": "Usuário não encontrado"}), 404
    
    
@app.route("/api/aposta", methods=["POST"])
def registrar_aposta():
    dados = request.get_json()

    # Validação básica
    campos_obrigatorios = ["data", "valor_aposta", "retorno", "odd", "resultado", "usuario_id"]
    if not all(campo in dados for campo in campos_obrigatorios):
        return jsonify({"erro": "Campos obrigatórios ausentes"}), 400

    try:
        nova_aposta = Aposta(
            data=dados["data"],
            valor_aposta=dados["valor_aposta"],
            retorno=dados["retorno"],
            odd=dados["odd"],
            resultado=dados["resultado"],
            usuario_id=dados["usuario_id"]
        )
        db.session.add(nova_aposta)
        db.session.commit()
        return jsonify({"mensagem": "Aposta registrada com sucesso"}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


if __name__ == '__main__':

    app.run()
    
