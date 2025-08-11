# app.py
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_wtf import CSRFProtect
from config import config
from forms import RegisterForm, LoginForm, EntradaForm, EditarPerfilForm, ComentForm, EditPostForm
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os 
from flask_pymongo import PyMongo
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from models.user import User
from models.post import Post
from models.coment import Coment
import datetime
from db import init_db
from flask_ckeditor import CKEditor
from flask_ckeditor.utils import cleanify
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader
import cloudinary.api


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

#configuraciones de cloudinary
app.config['CLOUDINARY_CLOUD_NAME'] = os.getenv('CLOUDINARY_CLOUD_NAME')
app.config['CLOUDINARY_API_KEY'] = os.getenv('CLOUDINARY_API_KEY')
app.config['CLOUDINARY_API_SECRET'] = os.getenv('CLOUDINARY_API_SECRET')

# Configurar Cloudinary con las credenciales
cloudinary.config(
    cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
    api_key=app.config['CLOUDINARY_API_KEY'],
    api_secret=app.config['CLOUDINARY_API_SECRET']
)

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
    posts = Post.get_all_posts()
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

# La ruta post_detail debe cargar la página completa, siempre
@app.route('/post/<string:post_id>')
def post_detail(post_id):
    post = Post.get_post(post_id) 
    form = ComentForm()
    # Pasa los comentarios a la plantilla para la carga inicial
    comments = Coment.get_coments_by_post(post_id) 
    if post is None:
        flash('La entrada del blog no se encontró.', 'danger')
        return redirect(url_for('home'))
    # Asegúrate de usar 'comments' para ser consistente con la plantilla comments_list.html
    return render_template('post_detail.html', post=post, comments=comments, form=form)


# Código corregido
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
            'fecha': datetime.datetime.utcnow()
        }
        coment_added = Coment.create_coment(coment_data)

        if coment_added:
            updated_comments = Coment.get_coments_by_post(post_id)
            form = ComentForm()

            if request.headers.get('HX-Request'):
                return render_template('userview/coments_post.html', comments=updated_comments)
            else:
                flash('Comentario agregado exitosamente!', 'success')
                return redirect(url_for('post_detail', post_id=post_id))
        else:
            if request.headers.get('HX-Request'):
                return "<div class='alert alert-danger'>Error al agregar comentario.</div>", 500
            flash('Error al agregar comentario.', 'danger')
            return redirect(url_for('post_detail', post_id=post_id))
    
    if request.headers.get('HX-Request'):
        return render_template('userview/coments_post.html', comments=Coment.get_coments_by_post(post_id))
    
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
                'fecha': datetime.datetime.utcnow(),
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


if __name__ == '__main__':
    # Usar la configuración de producción si Render asigna un puerto,
    # de lo contrario, usar la configuración de desarrollo
    if os.environ.get('PORT'):
        app.config.from_object(config['production'])
    else:
        app.config.from_object(config['develop'])
    
    # Ejecutar la aplicación
    app.run()