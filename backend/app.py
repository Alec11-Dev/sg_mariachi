
# Fichero el cual creara la instancia de flask # 
import os
from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

#Importaciones de todos los blueprinbts
from src.routes.people_route import people_route
from src.routes.reservation_route import reservation_route
from src.routes.fact_revenues_route import fact_revenues_route
from src.routes.auth_route import auth_route

# --- CORRECCIÓN 1: Cargar el .env PRIMERO ---
# Esta línea DEBE estar al principio, antes de acceder a cualquier variable de entorno.
load_dotenv()
#Por el moemento no se utilizaran variables de entonro


app = Flask(__name__)

# """
# ESTAS CONFIGURACIONES ESTABAN DESDE UN PRINCIPIO
# secret_key = os.environ.get('SECRET_KEY')
# if not secret_key:
#     raise ValueError("No se encontró la SECRET_KEY en el entorno. La aplicación no puede iniciar de forma segura.")
# app.config['JWT_SECRET_KEY'] = secret_key

# Configuración de los tiempos de expiración
# app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
# app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=1)

# jwt = JWTManager(app)
# NOTA: Si usas sesiones estándar, no necesitas JWTManager por ahora.
# jwt = JWTManager(app)
# AQUI TERMINA EL BLOQUE DE CONFIGURACIÓN DE JWT, SI USAMOS SÓLO SESIONES, PODEMOS OMITIRLO O DEJARLO PARA FUTURA EXPANSIÓN.

# --- CONFIGURACIÓN DE SESIONES (Nueva config, sialgo falla tratamos de solucionarlo desde aqui) ---
# 1. SECRET_KEY: Necesaria para firmar las cookies de sesión.
# En producción, esto debe venir de una variable de entorno y ser muy seguro.
app.secret_key = os.environ.get('SECRET_KEY') or 'clave_super_secreta_para_desarrollo_123'

# 2. TIEMPO DE VIDA: Cuánto tiempo dura la sesión antes de "romperse" sola (expirar).
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# --- CONFIGURACIÓN DE COOKIES ---
if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('URL_FRONTEND'):
    # Si estamos en Railway, asumimos que el frontend y backend están en dominios diferentes (deploy separados)
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Permitir cookies entre sitios
    app.config['SESSION_COOKIE_SECURE'] = True  # Solo enviar cookies por HTTPS
else:
    # En desarrollo local, podemos usar la configuración más permisiva
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Permitir cookies en el mismo sitio y en algunos casos entre sitios
    app.config['SESSION_COOKIE_SECURE'] = False  # Permitir cookies por HTTP para desarrollo

# 3. HACER LA SESIÓN PERMANENTE: Para que se respete el tiempo de vida de arriba.
@app.before_request
def make_session_permanent():
    from flask import session
    session.permanent = True

#Blueprints van aqui ...
app.register_blueprint(people_route)
app.register_blueprint(reservation_route)
app.register_blueprint(fact_revenues_route)
app.register_blueprint(auth_route)


frontend_urls = os.environ.get("URL_FRONTEND", "http://localhost:5173")
#frontend_urls = "http://localhost:5173,http://localhost:5173"
# Convertir a lista si hay múltiples URLs separadas por coma
origins_list = [url.strip() for url in frontend_urls.split(",")]

#print(origins_list) 
CORS(app, resources={
    r"/*": {
        "origins": origins_list,  # Usar lista en lugar de string
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": [
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Accept",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers"
        ],
        "expose_headers": ["Content-Disposition"],
        "supports_credentials": True,
        "max_age": 86400,
        "send_wildcard": False,  # IMPORTANTE: Edge requiere esto en False
        "always_send": True  # Enviar headers CORS siempre, incluso en OPTIONS
    }
})

if __name__ == '__main__':
    app.run(debug=True)