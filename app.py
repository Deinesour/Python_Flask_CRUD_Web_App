from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import *

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(40), nullable=False)
    name = db.Column(db.String(40), nullable=False)
    boards = db.relationship('Board', backref='user')


class Board(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    size = db.Column(db.Integer)
    price = db.Column(db.Integer)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


app.config['SECRET_KEY'] = 'hiWelcomeToChilis'
login_manager = LoginManager(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(uid):
    user = User.query.get(uid)
    return user


@app.route('/')
def index():
    db.create_all()
    if current_user.is_authenticated:
        return render_template('index_log.html')
    else:
        return render_template('index.html')


@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'GET':
        return render_template('create_user.html')
    elif request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(name=name, username=username, password=password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect('/')
        else:
            return render_template('create_user_incorrect.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is not None and password == user.password:
            login_user(user)
            return redirect('/')
        else:
            return render_template('login_incorrect.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/add_board', methods=['GET', 'POST'])
@login_required
def add_boards():
    if request.method == 'GET':
        return render_template('add_board.html')
    elif request.method == 'POST':
        name = request.form['name']
        size = request.form['size']
        price = request.form['price']
        x = Board(name=name, size=size, price=price)
        x.user = current_user
        db.session.add(x)
        db.session.commit()
        return redirect('/view_boards')


@app.route('/view_boards')
@login_required
def view_boards():
    return render_template('view_boards.html', board=current_user.boards)


@app.route('/update/<id>', methods=['GET', 'POST'])
@login_required
def update(id):
    if request.method == 'POST':
        name = request.form['name']
        size = request.form['size']
        price = request.form['price']
        x = Board.query.filter_by(id=id).first()
        x.name = name
        x.size = size
        x.price = price
        db.session.commit()
        return redirect('/view_boards')
    x = Board.query.filter_by(id=id).first()
    return render_template('update.html', name=x.name, size=x.size, price=x.price, id=id)


@app.route('/delete/<id>')
def delete(id):
    x = Board.query.filter_by(id=id).first()
    db.session.delete(x)
    db.session.commit()
    return redirect('/view_boards')


@app.errorhandler(404)
def err404(err):
    return render_template('404.html', err=err)


@app.errorhandler(401)
def err401(err):
    return render_template('401.html', err=err)


if __name__ == '__main__':
    app.run(debug=True)
