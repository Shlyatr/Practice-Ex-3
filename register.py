from flask import Flask, request, jsonify, redirect, render_template, Response
from flask_sqlalchemy import SQLAlchemy
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()


@app.route('/register', methods=['POST'])
def register():
    login = request.json.get('login')
    password = request.json.get('password')

    if not login or not password:
        return {"error": "Логин или пароль обязателен"}, 400

    if Data.query.filter_by(login=login).first():
        return {"error": "Пользователь уже есть"}, 400
    
    datas = Data(login=login, password=password)
    db.session.add(datas)
    db.session.commit()

    return {"id": datas.id}, 201



@app.route('/get', methods=['GET'])
def list_data():
    all_data = Data.query.all()
    result = [
        {'id': d.id, 'Login': d.login, 'password': d.password}
        for d in all_data
    ]
    return jsonify(result)

'''
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        if Data.query.filter_by(login=login).first():
            return "<h1>Пользователь уже есть</h1>"

        datas = Data(login=login, password=password)
        db.session.add(datas)
        db.session.commit()
        return redirect('/Log-in')

    return render_template("register.html")'''


def auth():
    return Response(
        "Требуется авторизация", 401,
        {"WWW-Authenticate": 'Basic realm="Login Required"'}
    )

@app.route("/Log-in")
def secret():
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Basic "):
        return auth()

    try:
        encoded_credentials = auth_header.split(" ")[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
        login, password = decoded_credentials.split(":", 1)
    except Exception:
        return auth()

    user = Data.query.filter_by(login=login, password=password).first()

    if user:
        return f"<h1>Добро пожаловать {login}!</h1>"
    else:
        return auth()

if __name__ == '__main__':
    app.run(debug=True)
