from datetime import datetime
from Flask_attempts import db, login_manager,app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(60), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post',backref='author', lazy = True)
#δεαδ κόουντ μπιλόου
    def get_reset_token(self,expires_sec=1800):
        s = Serial(app.config['SECRET_KEY'],expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s =Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

# τελος του dead code
    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.image_file}')"




class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100),nullable= False)
    date_posted = db.Column(db.DateTime,nullable=False,default = datetime.utcnow) #vs datetime.now i diafora einai oti i 2i apo8ikeuei local times,i 1i greenwich,kaliteri praktiki gia database storing
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"Post('{self.title}','{self.date_posted}')"
                                                                     

