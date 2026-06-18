from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuración de tu correo con tus datos reales
REMITENTE_GMAIL = "abyfierro88@gmail.com"
PASSWORD_APLICACION = "jakmhenthlozumof"
DESTINATARIO_ALERTA = "abygailfierro191@gmail.com"

class ReporteUbicacion(BaseModel):
    latitud: float
    longitud: float

@app.get("/mascota/perro1", response_class=HTMLResponse)
async def ver_perfil():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AlertaPata - Perfil de Dante</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background-color: #f8f9fa; margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
            .card { background: white; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); width: 90%; max-width: 400px; padding: 30px; text-align: center; border-top: 8px solid #d90429; }
            .pet-img { width: 100%; max-width: 250px; height: 250px; object-fit: cover; border-radius: 50%; border: 5px solid #ef233c; margin: 0 auto 15px auto; display: block; }
            h1 { color: #d90429; margin: 10px 0 5px 0; font-size: 28px; }
            .badge { background-color: #ef233c; color: white; padding: 5px 15px; border-radius: 20px; font-size: 14px; display: inline-block; margin-bottom: 20px; }
            .info-section { text-align: left; background: #fff5f5; padding: 15px; border-radius: 12px; margin-bottom: 25px; border-left: 4px solid #ef233c; }
            .info-section p { margin: 8px 0; font-size: 15px; line-height: 1.4; }
            .btn-gps { background-color: #d90429; color: white; border: none; padding: 15px 20px; font-size: 16px; font-weight: bold; border-radius: 10px; width: 100%; cursor: pointer; transition: background 0.2s; display: flex; justify-content: center; align-items: center; gap: 10px; }
            .btn-gps:hover { background-color: #b30322; }
        </style>
    </head>
    <body>
        <div class="card">
            <img src="/static/dante.jpeg" alt="Foto de Dante" class="pet-img">
            <h1>Dante</h1>
            <span class="badge">Chihuahua, Marron Con Blanco</span>
            <div class="info-section">
                <p><strong>Comportamiento:</strong> Es Amigable pero Ladra si te acercas de la nada. No es Agresivo Pero No Hay Que Fiarse. No recomendable agarrarlo bruscamente.</p>
                <p><strong>Salud:</strong> Tiene todas sus vacunas al dia. Esta Castrado.</p>
                <p><strong>Contacto:</strong> 627-XXX-XXXX (Familia Fierro)</p>
            </div>
            <button class="btn-gps" onclick="enviarUbicacion()">📍 REPORTAR AVISTAMIENTO (ENVIAR GPS)</button>
        </div>

        <script>
        function enviarUbicacion() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    
                    fetch('/mascota/perro1/reportar', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({latitud: lat, longitud: lon})
                    })
                    .then(res => res.json())
                    .then(data => {
                        alert('¡Ubicacion GPS enviada con exito al dueno!');
                    })
                    .catch(err => {
                        alert('Error al enviar la ubicacion.');
                    });
                }, function(error) {
                    alert('Por favor, activa los permisos de GPS para reportar.');
                });
            } else {
                alert('Tu dispositivo no soporta geolocalizacion.');
            }
        }
        </script>
    </body>
    </html>
    """

@app.post("/mascota/{mascota_id}/reportar")
async def reportar_mascota(mascota_id: str, datos: ReporteUbicacion):
    enlace_mapa = f"https://www.google.com/maps?q={datos.latitud},{datos.longitud}"
    
    asunto = f"🚨 ALERTA: ¡{mascota_id.upper()} (Dante) ha sido escaneado!"
    cuerpo = f"El collar de Dante acaba de ser escaneado.\n\n📍 Ver ubicacion en tiempo real en Google Maps:\n{enlace_mapa}"
    
    msg = MIMEText(cuerpo)
    msg['Subject'] = asunto
    msg['From'] = REMITENTE_GMAIL
    msg['To'] = DESTINATARIO_ALERTA
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as servidor:
            servidor.login(REMITENTE_GMAIL, PASSWORD_APLICACION)
            servidor.sendmail(REMITENTE_GMAIL, [DESTINATARIO_ALERTA], msg.as_string())
        print("\n[OK] ¡Alerta enviada por correo electrónico con éxito!")
    except Exception as e:
        print(f"\n[ERROR] No se pudo enviar el correo: {e}")
        
    return {"status": "ok"}
