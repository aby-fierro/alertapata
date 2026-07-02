import os
import smtplib
from email.mime.text import MIMEText
from typing import List, Optional
from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- REQUISITOS DE SQLALCHEMY EN UN SOLO ARCHIVO PARA TU COMODIDAD ---
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

# Configuración de la Base de Datos (Se crea en el directorio actual)
DATABASE_URL = "sqlite:///./mascotas.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- MODELOS DE LA BASE DE DATOS (DATABASE MODELS) ---
class Mascota(Base):
    __tablename__ = "mascotas"
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True) # Ej: "perro1"
    nombre = Column(String, nullable=False)
    raza = Column(String)
    comportamiento = Column(String)
    salud = Column(String)
    direccion = Column(String)
    tel_principal = Column(String)
    tel_secundario = Column(String)

class Reporte(Base):
    __tablename__ = "reportes"
    id = Column(Integer, primary_key=True, index=True)
    mascota_id = Column(Integer, ForeignKey("mascotas.id"))
    fecha = Column(DateTime, default=datetime.utcnow)
    latitud = Column(Float)
    longitud = Column(Float)
    tipo_reporte = Column(String)
    detalles = Column(String)

# Crear las tablas automáticamente si no existen
Base.metadata.create_all(bind=engine)

# --- SCHEMAS DE PYDANTIC ---
class ReporteUbicacion(BaseModel):
    latitud: float
    longitud: float
    tipo_reporte: str
    detalles: str

# --- INICIALIZACIÓN DE FASTAPI ---
app = FastAPI(title="AlertaPata - API Profesional")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos de forma segura
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Variables de entorno seguras para producción
REMITENTE_GMAIL = os.getenv("REMITENTE_GMAIL", "abygailfierro191@gmail.com")
PASSWORD_APLICACION = os.getenv("PASSWORD_APLICACION", "ramw dszy jrgk bqbu")
DESTINATARIOS = os.getenv("DESTINATARIOS", "abygailfierro191@gmail.com,friskpapa@gmail.com").split(",")

# Dependencia para la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Semilla de datos: Insertar a Dante automáticamente si la base está en ceros
def poblar_base_datos():
    db = SessionLocal()
    if db.query(Mascota).count() == 0:
        dante = Mascota(
            slug="perro1",
            nombre="Dante",
            raza="Chihuahua • Macho • Marrón con Blanco",
            comportamiento="Es un perro miedoso con los desconocidos. Puede llegar a ladrar para protegerse si te acercas de sorpresa, pero no es agresivo por naturaleza. Se recomienda hablarle con calma y suavidad.",
            salud="Condición estable, gordo y sano. Está castrado (esterilizado).",
            direccion="Anenecuilco No. 11, Col. Tierra y Libertad.",
            tel_principal="627-279-2334 (Hermana)",
            tel_secundario="627-131-0481 (Aby)"
        )
        db.add(dante)
        db.commit()
    db.close()

poblar_base_datos()

# --- RUTAS PRINCIPALES (ENDPOINTS) ---

@app.get("/", response_class=HTMLResponse)
async def inicio():
    return "<h1>AlertaPata API está en línea. Accede a /mascota/perro1 para ver el perfil.</h1>"

@app.get("/mascota/{mascota_slug}", response_class=HTMLResponse)
async def ver_perfil(mascota_slug: str, db: Session = Depends(get_db)):
    mascota = db.query(Mascota).filter(Mascota.slug == mascota_slug).first()
    
    if not mascota:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
        
    foto_perro = "/static/dante.jpeg" if os.path.exists("static/dante.jpeg") else "https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=500"

    # HTML profesional renderizado dinámicamente con los datos de SQLAlchemy
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AlertaPata - Perfil de {mascota.nombre}</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background-color: #111; margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; color: #333; }}
            .card {{ background: white; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); width: 90%; max-width: 400px; padding: 25px; text-align: center; border-top: 8px solid #ef233c; margin: 20px 0; }}
            .status-badge {{ background-color: #d90429; color: white; padding: 8px 15px; border-radius: 30px; font-weight: bold; font-size: 14px; display: inline-block; margin-bottom: 15px; animation: parpadeo 2s infinite; }}
            @keyframes parpadeo {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} 100% {{ opacity: 1; }} }}
            .pet-img {{ width: 180px; height: 180px; object-fit: cover; border-radius: 50%; border: 5px solid #ef233c; margin: 0 auto 15px auto; display: block; }}
            h1 {{ color: #ef233c; margin: 5px 0; font-size: 26px; }}
            .breed {{ color: #666; font-style: italic; margin-bottom: 15px; display: block; }}
            .info-section {{ text-align: left; background: #fff5f5; padding: 15px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #ef233c; }}
            .info-section p {{ margin: 8px 0; font-size: 14px; line-height: 1.4; }}
            .input-detalles {{ width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 10px; margin-bottom: 15px; font-size: 14px; box-sizing: border-box; font-family: inherit; }}
            .input-detalles:focus {{ border-color: #ef233c; outline: none; }}
            .btn {{ color: white; border: none; padding: 14px; font-size: 15px; font-weight: bold; border-radius: 10px; width: 100%; cursor: pointer; transition: background 0.2s; display: flex; justify-content: center; align-items: center; gap: 10px; margin-bottom: 10px; text-decoration: none; box-sizing: border-box; }}
            .btn-gps-direct {{ background-color: #d90429; }}
            .btn-gps-direct:hover {{ background-color: #b30322; }}
            .btn-gps-far {{ background-color: #f77f00; }}
            .btn-gps-far:hover {{ background-color: #d66d00; }}
            .btn-whatsapp {{ background-color: #25D366; }}
            .btn-whatsapp:hover {{ background-color: #128C7E; }}
            .fallback-text {{ font-size: 11px; color: #777; margin-top: 15px; display: block; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="status-badge">🚨 ESTADO: ¡ME PERDÍ!</div>
            
            <img src="{foto_perro}" alt="Foto de {mascota.nombre}" class="pet-img">
            <h1>{mascota.nombre}</h1>
            <span class="breed">{mascota.raza}</span>
            
            <div class="info-section">
                <p><strong>Comportamiento:</strong> {mascota.comportamiento}</p>
                <p><strong>Salud:</strong> {mascota.salud}</p>
                <p><strong>Dirección de Casa:</strong> {mascota.direccion}</p>
                <p><strong>Contactos de Emergencia:</strong><br>• Tel Principal: {mascota.tel_principal}<br>• Tel Secundario: {mascota.tel_secundario}</p>
            </div>

            <input type="text" id="txt-detalles" class="input-detalles" placeholder="¿Alguna referencia? (Ej. va corriendo, está herido, etc.)">

            <button class="btn btn-gps-direct" onclick="enviarUbicacion('Directo (Lo tienen retenido)')">📍 ¡LO TENGO CONMIGO! (ENVIAR GPS)</button>
            
            <button class="btn btn-gps-far" onclick="enviarUbicacion('Lejano (Visto en la zona, huyó o no se deja atrapar)')">👀 LO VEO CERCA (REPORTAR ZONA)</button>
            
            <a class="btn btn-whatsapp" href="https://api.whatsapp.com/send?phone=526272792334&text=Hola!%20Escaneé%20el%20collar%20de%20Dante%20y%20tengo%20información%20sobre%20él." target="_blank">💬 CONTACTAR POR WHATSAPP</a>

            <span class="fallback-text">¿El código QR falla? Reporta directo en: alertapata.onrender.com/mascota/{mascota_slug}</span>
        </div>

        <script>
        function enviarServidor(lat, lon, tipoReporte, detallesTexto) {{
            return fetch('/mascota/{mascota_slug}/reportar', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{latitud: lat, longitud: lon, tipo_reporte: tipoReporte, detalles: detallesTexto}})
            }});
        }}

        function enviarUbicacion(tipoReporte) {{
            const detallesTexto = document.getElementById('txt-detalles').value || 'Sin detalles adicionales';
            alert('Enviando reporte de alerta a los dueños...');
            
            if (navigator.geolocation) {{
                navigator.geolocation.getCurrentPosition(
                    function(position) {{
                        enviarServidor(position.coords.latitude, position.coords.longitude, tipoReporte, detallesTexto)
                        .then(res => manejarRespuesta(res));
                    }},
                    function(e) {{
                        enviarServidor(0.0, 0.0, tipoReporte, detallesTexto + ' (GPS Bloqueado)')
                        .then(res => manejarRespuesta(res));
                    }},
                    {{ enableHighAccuracy: true, timeout: 5000 }}
                );
            } else {{
                enviarServidor(0.0, 0.0, tipoReporte, detallesTexto + ' (Navegador sin GPS)')
                .then(res => manejarRespuesta(res));
            }}
        }}

        function manejarRespuesta(res) {{
            if(res.ok) {{
                alert('¡Alerta enviada con éxito!');
                document.getElementById('txt-detalles').value = '';
            }} else {{
                alert('Hubo un problema al procesar el reporte.');
            }}
        }}
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/mascota/{mascota_slug}/reportar")
async def reportar_mascota(mascota_slug: str, datos: ReporteUbicacion, db: Session = Depends(get_db)):
    mascota = db.query(Mascota).filter(Mascota.slug == mascota_slug).first()
    if not mascota:
        raise HTTPException(status_code=404, detail="Mascota no registrada")
    
    # 1. Guardar el reporte de forma permanente en la base de datos local de SQLite
    nuevo_reporte = Reporte(
        mascota_id=mascota.id,
        latitud=datos.latitud,
        longitud=datos.longitud,
        tipo_reporte=datos.tipo_reporte,
        detalles=datos.detalles
    )
    db.add(nuevo_reporte)
    db.commit()
    
    # 2. Generar enlace de Google Maps
    if datos.latitud == 0.0 and datos.longitud == 0.0:
        enlace_mapa = "Coordenadas no adjuntas (Permisos denegados o señal buscando)."
    else:
        enlace_mapa = f"https://www.google.com/maps?q={datos.latitud},{datos.longitud}"
    
    # 3. Estructurar y enviar correo electrónico de emergencia
    asunto = f"🚨 ALERTA PATA: ¡{mascota.nombre} ha sido localizado!"
    cuerpo = (
        f"El collar de {mascota.nombre} acaba de ser escaneado e interactuado.\n\n"
        f"📌 Tipo de reporte: {datos.tipo_reporte}\n"
        f"📝 Notas de quien reporta: {datos.detalles}\n"
        f"📍 Enlace de Ubicación en vivo:\n{enlace_mapa}\n\n"
        f"El reporte ha quedado registrado permanentemente en el historial de la base de datos."
    )
    
    msg = MIMEText(cuerpo)
    msg['Subject'] = asunto
    msg['From'] = REMITENTE_GMAIL
    msg['To'] = ", ".join(DESTINATARIOS)
    
    try:
        servidor = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        servidor.login(REMITENTE_GMAIL, PASSWORD_APLICACION)
        servidor.sendmail(REMITENTE_GMAIL, DESTINATARIOS, msg.as_string())
        servidor.quit()
        return {"status": "ok", "message": "Reporte guardado y correo enviado con éxito"}
    except Exception as e:
        return {"status": "saved_locally_error_email", "details": str(e)}
