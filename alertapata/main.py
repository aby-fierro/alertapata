from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import smtplib
from email.mime.text import MIMEText

app = FastAPI(title="API Unificada: AlertaPata + Laboratorio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


REMITENTE_GMAIL = "abygailfierro191@gmail.com"
PASSWORD_APLICACION = "ramw dszy jrgk bqbu"
DESTINATARIOS = ["abygailfierro191@gmail.com", "friskpapa@gmail.com"]

MASCOTA_INFO = {
    "nombre": "Dante",
    "raza": "Chihuahua • Macho • Marrón con Blanco",
    "comportamiento": "Es un perro miedoso con los desconocidos. Puede llegar a ladrar para protegerse si te acercas de sorpresa, pero no es agresivo por naturaleza. Se recomienda hablarle con calma y suavidad.",
    "salud": "Condición estable, gordo y sano. Está castrado (esterilizado).",
    "direccion": "Anenecuilco No. 11, Col. Tierra y Libertad.",
    "tel_principal": "627-279-2334 (Hermana)",
    "tel_secundario": "627-131-0481 (Aby)"
}


class Usuario(BaseModel):
    id: Optional[int] = None
    nombre: str
    email: str
    rol: str

class ReporteUbicacion(BaseModel):
    latitud: float
    longitud: float
    tipo_reporte: str
    detalles: str

db_usuarios = [
    {
        "id": 1,
        "nombre": "admin",
        "email": "admin@clase.com",
        "rol": "administracion"
    }
]

@app.get("/usuarios", response_model=List[Usuario])
def obtener_usuarios():
    return db_usuarios

@app.post("/usuarios", response_model=Usuario)
def crear_usuario(usuario: Usuario):
    nuevo_id = len(db_usuarios) + 1
    usuario.id = nuevo_id
    db_usuarios.append(usuario.dict())
    return usuario

@app.delete("/usuarios/{usuario_id}")
def eliminar_usuario(usuario_id: int):
    global db_usuarios
    db_usuarios = [u for u in db_usuarios if u["id"] != usuario_id]
    return {"mensaje": "Usuario borrado con exito"}

@app.get("/mascota/perro1", response_class=HTMLResponse)
async def ver_perfil():
    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AlertaPata - Perfil de TAG_NOMBRE</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background-color: #111; margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; color: #333; }
            .card { background: white; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); width: 90%; max-width: 400px; padding: 25px; text-align: center; border-top: 8px solid #ef233c; margin: 20px 0; }
            .status-badge { background-color: #d90429; color: white; padding: 8px 15px; border-radius: 30px; font-weight: bold; font-size: 14px; display: inline-block; margin-bottom: 15px; animation: parpadeo 2s infinite; }
            @keyframes parpadeo { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
            .pet-img { width: 180px; height: 180px; object-fit: cover; border-radius: 50%; border: 5px solid #ef233c; margin: 0 auto 15px auto; display: block; }
            h1 { color: #d90429; margin: 5px 0; font-size: 26px; }
            .breed { color: #666; font-style: italic; margin-bottom: 15px; display: block; }
            .info-section { text-align: left; background: #fff5f5; padding: 15px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #ef233c; }
            .info-section p { margin: 8px 0; font-size: 14px; line-height: 1.4; }
            .input-detalles { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 10px; margin-bottom: 15px; font-size: 14px; box-sizing: border-box; font-family: inherit; }
            .input-detalles:focus { border-color: #ef233c; outline: none; }
            .btn { color: white; border: none; padding: 14px; font-size: 15px; font-weight: bold; border-radius: 10px; width: 100%; cursor: pointer; transition: background 0.2s; display: flex; justify-content: center; align-items: center; gap: 10px; margin-bottom: 10px; text-decoration: none; box-sizing: border-box; }
            .btn-gps-direct { background-color: #d90429; }
            .btn-gps-direct:hover { background-color: #b30322; }
            .btn-gps-far { background-color: #f77f00; }
            .btn-gps-far:hover { background-color: #d66d00; }
            .btn-whatsapp { background-color: #25D366; }
            .btn-whatsapp:hover { background-color: #128C7E; }
            .fallback-text { font-size: 11px; color: #777; margin-top: 15px; display: block; }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="status-badge">🚨 ESTADO: ¡ME PERDÍ!</div>
            <img src="/static/dante.jpeg" alt="Foto de TAG_NOMBRE" class="pet-img">
            <h1>TAG_NOMBRE</h1>
            <span class="breed">TAG_RAZA</span>
            <div class="info-section">
                <p><strong>Comportamiento:</strong> TAG_COMPORTAMIENTO</p>
                <p><strong>Salud:</strong> TAG_SALUD</p>
                <p><strong>Dirección de Casa:</strong> TAG_DIRECCION</p>
                <p><strong>Contactos de Emergencia:</strong><br>• Tel Principal: TAG_PRINCIPAL<br>• Tel Secundario: TAG_SECUNDARIO</p>
            </div>
            <input type="text" id="txt-detalles" class="input-detalles" placeholder="¿Alguna referencia? (Ej. va corriendo, está herido, etc.)">
            <button class="btn btn-gps-direct" onclick="procesarReporte('Directo (Lo tienen retenido)')">📍 ¡LO TENGO CONMIGO! (ENVIAR GPS)</button>
            <button class="btn btn-gps-far" onclick="procesarReporte('Lejano (Visto en la zona, huyó)')">👀 LO VEO CERCA (REPORTAR ZONA)</button>
            <a class="btn btn-whatsapp" href="https://api.whatsapp.com/send?phone=526272792334&text=Hola!%20Escaneé%20el%20collar%20de%20Dante%20y%20tengo%20información%20sobre%20él." target="_blank">💬 CONTACTAR POR WHATSAPP</a>
        </div>
        <script>
        function enviarServidor(lat, lon, tipoReporte, detallesTexto) {
            return fetch('/mascota/perro1/reportar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({latitud: lat, longitud: lon, tipo_reporte: tipoReporte, detalles: detallesTexto})
            });
        }
        function procesarReporte(tipoReporte) {
            const detallesTexto = document.getElementById('txt-detalles').value || 'Sin detalles adicionales';
            alert('Enviando reporte...');
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(pos) {
                        enviarServidor(pos.coords.latitude, pos.coords.longitude, tipoReporte, detallesTexto).then(res => manejarRespuesta(res));
                    },
                    function(err) {
                        enviarServidor(0.0, 0.0, tipoReporte, detallesTexto + ' (Sin GPS)').then(res => manejarRespuesta(res));
                    },
                    { timeout: 3000 }
                );
            } else {
                enviarServidor(0.0, 0.0, tipoReporte, detallesTexto + ' (No soportado)').then(res => manejarRespuesta(res));
            }
        }
        function manejarRespuesta(res) {
            if(res.ok) { alert('¡Alerta enviada con éxito!'); document.getElementById('txt-detalles').value = ''; }
            else { alert('Error al procesar en el servidor.'); }
        }
        </script>
    </body>
    </html>
    """
    return html_template.replace("TAG_NOMBRE", MASCOTA_INFO["nombre"]).replace("TAG_RAZA", MASCOTA_INFO["raza"]).replace("TAG_COMPORTAMIENTO", MASCOTA_INFO["comportamiento"]).replace("TAG_SALUD", MASCOTA_INFO["salud"]).replace("TAG_DIRECCION", MASCOTA_INFO["direccion"]).replace("TAG_PRINCIPAL", MASCOTA_INFO["tel_principal"]).replace("TAG_SECUNDARIO", MASCOTA_INFO["tel_secundario"])

@app.post("/mascota/perro1/reportar")
async def reportar_mascota(datos: ReporteUbicacion):
    enlace_mapa = f"http://maps.google.com/?q={datos.latitud},{datos.longitud}" if datos.latitud != 0.0 else "No disponibles."
    msg = MIMEText(f"🚨 Collar Escaneado:\n\n📌 Tipo: {datos.tipo_reporte}\n📝 Notas: {datos.detalles}\n📍 Mapa: {enlace_mapa}")
    msg['Subject'] = "🚨 ALERTA PATA: ¡Dante localizado!"
    msg['From'] = REMITENTE_GMAIL
    msg['To'] = ", ".join(DESTINATARIOS)
    try:
        servidor = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        servidor.login(REMITENTE_GMAIL, PASSWORD_APLICACION)
        servidor.sendmail(REMITENTE_GMAIL, DESTINATARIOS, msg.as_string())
        servidor.quit()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "details": str(e)}
