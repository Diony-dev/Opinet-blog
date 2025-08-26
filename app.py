# app.py
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_wtf import CSRFProtect
from config import config
from forms import RegisterForm, LoginForm, EntradaForm, EditarPerfilForm, ComentForm, EditPostForm, RequestResetForm, ResetPasswordForm
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os 
from flask_pymongo import PyMongo
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from models.user import User
from models.post import Post
from models.coment import Coment
from models.notification import Notification
import datetime
from db import init_db
from flask_ckeditor import CKEditor
from flask_ckeditor.utils import cleanify
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader
import cloudinary.api
from bson.objectid import ObjectId # Importar ObjectId para las consultas
import pytz
import locale
from flask_mail import Message, Mail

app = Flask(__name__)
load_dotenv()

ckeditor = CKEditor(app)

app.secret_key= os.getenv('SECRET_KEY')
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
UPLOAD_FOLDER = 'static/img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
crf = CSRFProtect(app)
mongo = PyMongo(app)
init_db(app) 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# configuraciones de cloudinary
app.config['CLOUDINARY_CLOUD_NAME'] = os.getenv('CLOUDINARY_CLOUD_NAME')
app.config['CLOUDINARY_API_KEY'] = os.getenv('CLOUDINARY_API_KEY')
app.config['CLOUDINARY_API_SECRET'] = os.getenv('CLOUDINARY_API_SECRET')

# Configurar Cloudinary con las credenciales
cloudinary.config(
    cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
    api_key=app.config['CLOUDINARY_API_KEY'],
    api_secret=app.config['CLOUDINARY_API_SECRET']
)
# Configurar la configuración regional a español para la traducción de fechas


#configuracione de Email
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_SENDER')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
mail = Mail(app)






@login_manager.user_loader
def load_user(user_id):
    return User.get_user(user_id)

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    loginform = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        if loginform.validate_on_submit():
            user = User.get_user_by_email(loginform.correo.data)
            if user and check_password_hash(user.password, loginform.pasw.data):
                login_user(user, remember=loginform.recordar.data)
                flash('Bienvenido de nuevo!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Credenciales incorrectas, por favor intente de nuevo.', 'danger')
    return render_template('auth/login.html', form = loginform)

@app.route('/register', methods = ['GET', 'POST'])
def register():
    registerform = RegisterForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        if registerform.validate_on_submit():
            user_data = {
                'nombre': registerform.nombre.data,
                'email': registerform.email.data,
                'pasw': generate_password_hash(registerform.pasw.data)
            }
            user = User.get_user_by_email(user_data['email'])
            if user:
                flash('Ese email ya está registrado!', 'danger')
                return redirect(url_for('register'))
            else:
                User.create_user(user_data)
                flash('Usuario registrado exitosamente, ya puedes iniciar sesión!', 'success')
                return redirect(url_for('login'))
    return render_template('auth/register.html', form=registerform)

@app.route('/home', methods=['GET'])
@login_required
def home():
    posts = Post.get_all_posts(limit=6)
    return render_template('home.html', posts=posts, user=current_user)

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('login'))

@app.route('/perfil', methods = ['GET'])
@login_required
def perfil():
    posts = Post.get_posts_by_email(current_user.email)
    return render_template('perfil.html', user=current_user, user_posts=posts)

@app.route('/my_posts', methods=['GET'])
@login_required
def my_posts():
    posts = Post.get_collection().find({'autor': current_user.nombre}).sort('fecha', -1)
    return render_template('userview/my_post.html', user=current_user, user_posts=posts)

@app.route('/post/<string:post_id>')
def post_detail(post_id):
    post = Post.get_post(post_id) 
    form = ComentForm()
    comments = Coment.get_coments_by_post(post_id) 
    if post is None:
        flash('La entrada del blog no se encontró.', 'danger')
        return redirect(url_for('home'))
    return render_template('post_detail.html', post=post, comments=comments, form=form)


@app.route('/comentar/<string:post_id>', methods=['POST'])
@login_required
def comentar(post_id):
    form = ComentForm()
    post = Post.get_post(post_id)

    if not post:
        if request.headers.get('HX-Request'):
            return "<div class='alert alert-danger'>La publicación no se encontró.</div>", 404
        flash('La entrada del blog no se encontró.', 'danger')
        return redirect(url_for('home'))

    if form.validate_on_submit():
        coment_data = {
            'contenido': form.contenido.data,
            'id_post': post_id,
            'autor': current_user.nombre,
            'fecha':  datetime.datetime.utcnow(),
            'parent_id': request.form.get('parent_id')
        }
        coment_added = Coment.create_coment(coment_data)
        updated_comments = Coment.get_coments_by_post(post_id)
        parent_id = request.form.get('parent_id')

        # Crear notificaciones (si falla, no interrumpe el flujo)
        try:
            parent_comment_doc = mongo.db.Comentarios.find_one({'_id': ObjectId(parent_id)})
            if parent_id:
                # Comentario es respuesta a otro comentario
               
                if parent_comment_doc:
                    parent_author_name = parent_comment_doc['autor']
                    parent_user_doc = mongo.db.Usuarios.find_one({'nombre': parent_author_name})
                    if parent_user_doc and str(parent_user_doc['_id']) != str(current_user.id):
                        Notification.create_notification({
                            "user_id": str(parent_user_doc['_id']),
                            "message": f"Tu comentario en la publicación '{post.titulo}' ha recibido una respuesta.",
                            "post_id": post_id
                        })
            else:
                # Comentario directo en el post
                if post.autor != current_user.nombre:
                    post_author_doc = mongo.db.Usuarios.find_one({'nombre': post.autor})
                    if post_author_doc:
                        Notification.create_notification({
                            "user_id": str(post_author_doc['_id']),
                            "message": f"Tu publicación '{post.titulo}' ha recibido un nuevo comentario.",
                            "post_id": post_id
                        })
        except Exception as e:
            print("Error creando notificación:", e)

        # Responder según si es HTMX o no
        if request.headers.get('HX-Request'):
            return render_template('userview/coments_post.html', comments=updated_comments, post=post)
        else:
            flash('Comentario agregado exitosamente!', 'success')
            return redirect(url_for('post_detail', post_id=post_id))
    
    # Formulario inválido
    if request.headers.get('HX-Request'):
        return render_template('userview/coments_post.html', comments=Coment.get_coments_by_post(post_id), post=post)
    
    flash('Error en el formulario de comentario.', 'danger')
    return redirect(url_for('post_detail', post_id=post_id))


@app.route('/crear_post', methods = ['GET', 'POST'])
@login_required
def crear_post():
    form = EntradaForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            contenido_clean = cleanify(form.contenido.data)
            post_data = {
                'titulo':form.titulo.data,
                'contenido': contenido_clean,
                'autor': current_user.nombre,
                'fecha':  datetime.datetime.utcnow(),
                'email': current_user.email
            }
            post = Post.create_post(post_data)
            if post:
                flash('Entrada de blog creada exitosamente!', 'success')
                return redirect(url_for('post_detail', post_id=post.id))
    return render_template('creat_post.html', form=form)

@app.route('/editar_perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    form = EditarPerfilForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user_data = {
                'nombre': form.nombre.data,
                'email': form.email.data
            }
            if form.foto.data:
                file = form.foto.data
                filename = secure_filename(file.filename)
                cloudinary_result = cloudinary.uploader.upload(file, folder = "user_photo", public_id = f"{current_user.id}")
                user_data['foto'] = cloudinary_result['secure_url']

            User.update_user(current_user.id, user_data)
            flash('Perfil actualizado exitosamente!', 'success')
            return redirect(url_for('perfil'))
    return render_template('editar_perfil.html', form=form)


@app.route('/cambiar_estado/<string:post_id>', methods=['POST'])
@login_required
def cambiar_estado(post_id):
    post = Post.get_post(post_id)

    if not post:
        flash('Publicación no encontrada.', 'danger')
        return redirect(url_for('my_posts'))

    if post.autor != current_user.nombre:
        flash('No tienes permiso para cambiar el estado de esta publicación.', 'danger')
        return redirect(url_for('my_posts'))

    new_estado = not post.estado
    if Post.update_post(post.id, {'estado': new_estado}):
        flash(f'Estado de la publicación "{post.titulo}" cambiado a {"publicado" if new_estado else "borrador"}.', 'success')
    else:
        flash('Error al cambiar el estado de la publicación.', 'danger')

    return redirect(url_for('my_posts'))


@app.route('/editar_post/<string:post_id>', methods = ['GET', 'POST'])
@login_required
def editar_post(post_id):
    post = Post.get_post(post_id)
    if not post:
        flash('Publicación no encontrada.', 'danger')
        return redirect(url_for('my_posts'))
    if post.autor != current_user.nombre:
        flash('No tienes permiso para editar esta publicación.', 'danger')
        return redirect(url_for('my_posts'))
    form = EditPostForm(obj=post)
    if request.method == 'POST':
        if form.validate_on_submit():
            contenido_clean = cleanify(form.contenido.data)
            post_data = {
                'titulo': form.titulo.data,
                'contenido': contenido_clean,
                'estado':form.estado.data,
                'fecha': datetime.datetime.utcnow()
            }
            if Post.update_post(post.id, post_data):
                flash('Publicación actualizada exitosamente!', 'success')
                return redirect(url_for('post_detail', post_id=post.id))
            else:
                flash('Error al actualizar la publicación.', 'danger')
    return render_template('userview/editar_post.html', form=form, post=post)


@app.route("/perfil_user/<string:user_id>", methods=['GET'])
@login_required
def perfil_user(user_id):
    user = User.get_user(user_id)
    if not user:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('home'))
    posts = Post.get_posts_by_email(user.email)
    return render_template('userview/perfil.html', usuario=user, posts=posts)

@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q')
    print(f"Búsqueda para: {query}")
    users = User.search_by_name(query)
    return render_template('userview/result.html', users=users, q=query)


@app.route('/get_reply_form/<string:post_id>/<string:parent_id>', methods=['GET'])
@login_required
def get_reply_form(post_id, parent_id):
    form = ComentForm()
    return render_template('userview/replis.html', form=form, post_id=post_id, parent_id=parent_id)


#endpoints de notificaciones
@app.route('/notificaciones', methods=['GET'])
@login_required
def notificaciones():
    user_id = current_user.id
    notificaciones = Notification.get_unread_notifications(user_id)
    print(f"Notificaciones no leídas para el usuario {user_id}: {notificaciones}")
    return render_template('userview/notifications.html', notificaciones=notificaciones)

@app.route('/marcar_leida/<string:noti_id>', methods=['POST'])
@login_required
def marcar_leida(noti_id):
    if Notification.mark_as_read(noti_id):
        flash('Notificación marcada como leída.', 'success')
    else:
        flash('Error al marcar la notificación como leída.', 'danger')
    return redirect(url_for('notificaciones'))

@app.route('/contar_notificaciones', methods=['GET'])
@login_required
def contar_notificaciones():
    user_id = current_user.id
    count = Notification.count_unread_notifications(user_id)
    return str(count)

#restablecimeinto de pasw
def send_password_reset_email(user, token):
    link = url_for('reset_token', token=token, _external=True)
    msg = Message(
        'Restablecimiento de Contraseña',
        sender='opinetsoporte@gmail.com',
        recipients=[user.email]
    )
    msg.html = f"""
<html>
  <body>
    <p>Hola <strong>{user.nombre}</strong>,</p>
    <p>Para restablecer tu contraseña, haz click en el siguiente enlace:</p>
    <p><a href="{link}">Restablecer contraseña</a></p>
    <hr>
    <p>Si no solicitaste esto, simplemente ignora este correo.</p>
  </body>
</html>
"""
    mail.send(msg)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.get_user_by_email(form.email.data)
        token = user.generate_reset_token()
        send_password_reset_email(user, token)
        flash('Se ha enviado un correo para restablecer tu contraseña.', 'info')
        return redirect(url_for('login'))
    return render_template('auth/forgot.html', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    user = User.verify_token(token)
    if user is None:
        flash('El token es inválido o ha expirado.', 'warning')
        return redirect(url_for('reset_password_request'))

    form  = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        User.update_pass(user.id, hashed_password)
        flash('Tu contraseña ha sido actualizada! Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('auth/reset.html', form=form)




if __name__ == '__main__':
    # Usar la configuración de producción si Render asigna un puerto,
    # de lo contrario, usar la configuración de desarrollo
    if os.environ.get('PORT'):
        app.config.from_object(config['production'])
    else:
        app.config.from_object(config['develop'])
    
    # Ejecutar la aplicación
    app.run()
