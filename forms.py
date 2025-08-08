from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, TextAreaField, BooleanField
from flask_ckeditor import CKEditorField
from wtforms.validators import Email, equal_to, DataRequired, Length, ValidationError
from flask_wtf.file import FileField
from models.user import User
class RegisterForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=3, max=25)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    pasw = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    enviar = SubmitField('Registrarse')


class LoginForm(FlaskForm):
    correo = EmailField('Correo', validators=[DataRequired(), Email()])
    pasw = PasswordField('contraseña', validators=[DataRequired(), Length(min=6)])
    recordar = BooleanField('Recordarme')
    enviar = SubmitField('Ingresar')

class EntradaForm(FlaskForm):
    titulo = StringField('Titulo', validators=[DataRequired(), Length(min=3, max=100)])
    contenido = CKEditorField('Contenido', validators=[DataRequired(), Length(min=6)])
    enviar = SubmitField('Publicar')



class EditarPerfilForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=3, max=25)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    foto = FileField('Foto de perfil')
    enviar = SubmitField('Actualizar Perfil')

class ComentForm(FlaskForm):
    contenido = TextAreaField('Comentario', validators=[DataRequired(), Length(min=1, max=500)])
    comentar = SubmitField('Comentar')


class RequestResetForm(FlaskForm):
    email = StringField('Correo Electrónico', 
                        validators=[DataRequired(), Email()],
                        render_kw={"placeholder": "Ingresa tu correo electrónico"})
    submit = SubmitField('Solicitar Restablecimiento de Contraseña')

    def validate_email(self, email):
        user = User.get_user_by_email(email.data)
        if user is None:
            raise ValidationError('No hay una cuenta con ese correo electrónico. Por favor, regístrate primero.')
        

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nueva Contraseña', 
                             validators=[DataRequired(), Length(min=6)],
                             render_kw={"placeholder": "Ingresa tu nueva contraseña"})
    confirm_password = PasswordField('Confirmar Nueva Contraseña', 
                                     validators=[DataRequired(), equal_to('password')],
                                     render_kw={"placeholder": "Confirma tu nueva contraseña"})
    submit = SubmitField('Restablecer Contraseña')


class EditPostForm(FlaskForm):
    titulo = StringField('Titulo', validators=[DataRequired(), Length(min=3, max=100)])
    contenido = CKEditorField('Contenido', validators=[DataRequired(), Length(min=6)])
    estado = BooleanField('Publicado', default=True)
    enviar = SubmitField('Actualizar Post')
