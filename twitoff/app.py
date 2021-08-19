from flask import Flask
from flask import render_template
from flask import request
from .models import db, User
import os
from .predict import predict_user
from .twitter import add_or_update_user, update_all_users

def create_app():    
    app = Flask(__name__)

    # Setup database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    # Create tables
    with app.app_context():
        db.create_all()



    @app.route('/')
    def root():
        return render_template('base.html', title='Home', users=User.query.all())
    # @app.route("/", methods=["GET", "POST"])
    # def home():
    #     name = request.form.get("name")
    #     if name:
    #         user = User(name=name)
    #         db.session.add(user)
    #         db.session.commit()
    #     users = User.query.all()
    #     return render_template("home.html", users=users)


    @app.route('/user', methods=['POST'])
    @app.route('/user/<name>', methods=['GET'])
    def user(name=None, message=''):
        name = name or request.values['user_name']
        try:
            if request.method == 'POST':
                add_or_update_user(name)
                message = f"User @{name} successfully added!"
            tweets = User.query.filter(User.name == name).one().tweets
        except Exception as e:
            message = f"Error adding @{name}: {e}"
            tweets = []
        return render_template('user.html', title=name, tweets=tweets, message=message)

    
    @app.route('/compare', methods=['POST'])
    def compare(message=''):
        user1, user2 = sorted([request.values['user1'],
                               request.values['user2']])
        if user1 == user2:
            message = 'Cannot compare a user to themselves!'
        else:
            prediction = predict_user(user1, user2,
                                      request.values['tweet_text'])
            message = '"{}" is more likely to be said by @{} than @{}'.format(
                request.values['tweet_text'], user1 if prediction else user2,
                user2 if prediction else user1
            )
        return render_template('predict.html', title='Prediction',
                               message=message)


    @app.route('/reset')
    def reset():
        db.drop_all()
        db.create_all()
        return render_template('base.html', title='Reset Database!')


    @app.route('/update')
    def update():
        update_all_users()
        return render_template('base.html', users=User.query.all(), title='All users and tweets updated!')


    @app.route('/compare', methods=['POST'])
    def compare_text(message=''):
        user1, user2 = sorted([request.values['user1'],
                               request.values['user2']])
        if user1 == user2:
            message = 'Cannot compare a user to themselves!'
        else:
            prediction = predict_user(user1, user2,
                                      request.values['tweet_text'])
            message = '"{}" is more likely to be said by @{} than @{}'.format(
                request.values['tweet_text'], user1 if prediction else user2,
                user2 if prediction else user1
            )
        return render_template('predict.html', title='Prediction',
                               message=message)


    return app