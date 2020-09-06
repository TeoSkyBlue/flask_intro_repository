from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField,PasswordField,SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo,ValidationError,NoneOf
from Flask_attempts.models import User

class RegistrationForm(FlaskForm):
    username = StringField('όνομα χρήστη', validators=[DataRequired(), Length(min=2,max=20)])
    email = StringField('e-mail',validators=[DataRequired(), Email()])
    password = PasswordField('κωδικός',validators=[DataRequired(), Length(min=5,max=100)])
    password_confirm = PasswordField('επιβεβαίωση κωδικού',validators=[DataRequired(), Length(min=5,max=100), EqualTo('password')])
    submit = SubmitField('Εγγραφή')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Κάποιος χρήστης ήδη χρησιμοποιεί το συγκεκριμένο όνομα!Δοκίμασε ένα άλλο!')

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Αυτό το email χρησιμοποιείται ήδη.')

        
class LoginForm(FlaskForm):
    email = StringField('e-mail',validators=[DataRequired(), Email()])
    password = PasswordField('κωδικός',validators=[DataRequired(), Length(min=5,max=100)])
    memory = BooleanField('θυμήσου με')
    submit = SubmitField('Σύνδεση')
    
class PostForm(FlaskForm):
    title = StringField('Τίτλος', validators=[DataRequired()])
    content = TextAreaField('Περιεχόμενο',validators=[DataRequired()])
    submit = SubmitField('Post')
    

class UpdateForm(FlaskForm):
    username = StringField('όνομα χρήστη', validators=[DataRequired(), Length(min=2,max=20)])
    email = StringField('e-mail',validators=[DataRequired(), Email()])
    prof_pic = FileField('Αλλαγή φωτογραφίας προφίλ',validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Αποθήκευση αλλαγών')

    def validate_username(self, username):
        if username.data!=current_user.username:
            
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Κάποιος χρήστης ήδη χρησιμοποιεί το συγκεκριμένο όνομα!Δοκίμασε ένα άλλο!')

    def validate_email(self,email):
        if email.data!=current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Αυτό το email χρησιμοποιείται ήδη.')

    
    def validate_email(self,email):
        if email.data!=current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user is None:
                raise ValidationError('Aυτό το email δεν υπάρχει.')
    



