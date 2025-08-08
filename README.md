
# 🌐 Opinet Blog - Plataforma de Publicaciones

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0-lightgreen.svg)](https://flask.palletsprojects.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Plataforma de blogging desarrollada con Flask que permite a los usuarios compartir sus conocimientos sobre tecnología, programación y más.

## ✨ Características principales

- **🔐 Autenticación segura** con hash de contraseñas
- **📝 CRUD completo** para publicaciones
- **👤 Perfiles de usuario** con avatares personalizables
- **💬 Sistema de comentarios** en publicaciones
- **🎨 Interfaz moderna** con Bootstrap 5
- **📱 Diseño responsive** para todos los dispositivos
- **🔍 Búsqueda y filtrado** de contenido

## 🛠 Stack tecnológico

| Capa         | Tecnologías                     |
|--------------|---------------------------------|
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap 5 |
| **Backend**  | Python, Flask                   |
| **Database** | SQLite (PostgreSQL ready)       |
| **Auth**     | Flask-Login                     |
| **Templates**| Jinja2                          |

## 🚀 Instalación local

1. Clona el repositorio:
```bash
git clone https://github.com/Diony-dev/Opinet-blog.git
cd Opinet-blog
```

2. Configura el entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. Instala dependencias:
```bash
pip install -r requirements.txt
```

4. Configura las variables de entorno:
```bash
cp .env.example .env
# Edita el .env con tus credenciales
```

5. Inicia la aplicación:
```bash
flask run
```

## 🏗 Estructura del proyecto

```
Opinet-blog/
├── app/
│   ├── templates/       # Plantillas HTML
│   ├── static/          # CSS, JS, imágenes
│   ├── models.py        # Modelos de base de datos
│   ├── routes.py        # Rutas principales
│   └── ...
├── migrations/          # Migraciones de la DB
├── config.py            # Configuración Flask
└── requirements.txt     # Dependencias
```

## 🌍 Despliegue en Render

1. Crea una nueva instancia de **Web Service** en Render
2. Conecta tu repositorio de GitHub
3. Configura las variables de entorno:
   - `FLASK_APP=run.py`
   - `DATABASE_URL` (proporcionada por Render)
4. Usa el siguiente comando de build:
```bash
pip install -r requirements.txt && flask db upgrade
```

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## 📸 Demo

![Página principal](https://raw.githubusercontent.com/Diony-dev/Opinet-blog/main/screenshots/home.png)
*Interfaz principal del blog*

## 🤝 Cómo contribuir

1. Haz un fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/awesome-feature`)
3. Haz commit de tus cambios (`git commit -m 'Add awesome feature'`)
4. Haz push a la rama (`git push origin feature/awesome-feature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

✒️ **Autor**: [Diony Dev](https://github.com/Diony-dev)  
📧 **Contacto**: [Tu email o redes sociales]  
🔗 **Live Demo**: [Enlace a demo en vivo si está disponible]
```

### Características destacables que he incluido:
1. **Badges actualizados** con las tecnologías clave
2. **Instrucciones claras** para instalación local
3. **Guía visual** de la estructura del proyecto
4. **Configuración específica** para despliegue en Render
5. **Sección de demo** con imagen (deberás subir screenshots a tu repo)

¿Qué más te gustaría añadir o modificar? Podría incluir también:
- Diagrama de la arquitectura
- Roadmap de futuras features
- Instrucciones para usar PostgreSQL en producción
- Sistema de testing (si lo implementas)
