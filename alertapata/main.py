
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

REMITENTE_GMAIL = "abyfierro88@gmail.com"
PASSWORD_APLICACION = "jakmhenthlozumof"
DESTINATARIOS = ["abygailfierro191@gmail.com", "friskpapa@gmail.com"]

class ReporteUbicacion(BaseModel):
    latitud: float
    longitud: float
    tipo_reporte: str
    detalles: str

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
            
            <img src="/static/dante.jpeg" alt="Foto de Dante" class="pet-img">
            <h1>Dante</h1>
            <span class="breed">Chihuahua • Macho • Marrón con Blanco</span>
            
            <div class="info-section">
                <p><strong>Comportamiento:</strong> Es un perro miedoso con los desconocidos. Puede llegar a ladrar para protegerse si te acercas de sorpresa, pero no es agresivo por naturaleza. Se recomienda hablarle con calma y suavidad.</p>
                <p><strong>Salud:</strong> Condición estable, gordo y sano. Está castrado (esterilizado).</p>
                <p><strong>Dirección de Casa:</strong> Anenecuilco No. 11, Col. Tierra y Libertad.</p>
                <p><strong>Contactos de Emergencia:</strong><br>• Tel Principal: 627-279-2334 (Hermana)<br>• Tel Secundario: 627-131-0481 (Aby)</p>
            </div>

            <input type="text" id="txt-detalles" class="input-detalles" placeholder="¿Alguna referencia? (Ej. va corriendo, está herido, etc.)">

            <button class="btn btn-gps-direct" onclick="enviarUbicacion('Directo (Lo tienen retenido)')">📍 ¡LO TENGO CONMIGO! (ENVIAR GPS)</button>
            
            <button class="btn btn-gps-far" onclick="enviarUbicacion('Lejano (Visto en la zona, huyó o no se deja atrapar)')">👀 LO VEO CERCA (REPORTAR ZONA)</button>
            
            <a class="btn btn-whatsapp" href="https://api.whatsapp.com/send?phone=526272792334&text=Hola!%20Escaneé%20el%20collar%20de%20Dante%20y%20tengo%20información%20sobre%20él." target="_blank">💬 CONTACTAR POR WHATSAPP</a>

            <span class="fallback-text">¿El código QR falla? Reporta directo en: alertapata.onrender.com/mascota/perro1</span>
        </div>

        <script>
        function enviarUbicacion(tipoReporte) {
            const detallesTexto = document.getElementById('txt-detalles').value || 'Sin detalles adicionales';
            
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    
                    const urlReporte = window.location.origin + '/mascota/perro1/reportar';
                    
                    fetch(urlReporte, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({latitud: lat, longitud: lon, tipo_reporte: tipoReporte, detalles: detallesTexto})
                    })
                    .then(res => res.json())
                    .then(data => {
                        alert('¡Ubicación GPS enviada con éxito a los dueños via correo!');
                        document.getElementById('txt-detalles').value = '';
                    })
                    .catch(err => {
                        alert('Error al enviar la ubicación.');
                    });
                }, function(error) {
                    alert('Por favor, activa los permisos de GPS para reportar la ubicación.');
                });
            } else {
                alert('Tu dispositivo no soporta geolocalización.');
            }
        }
        </script>
    </body>
    </html>
    """

@app.post("/mascota/perro1/reportar")
async def reportar_mascota(datos: ReporteUbicacion):
    enlace_mapa = f"https://www.google.com/maps?q={datos.latitud},{datos.longitud}"
    
    asunto = f"🚨 ALERTA PATA: ¡Dante ha sido localizado!"
    cuerpo = (
        f"El collar de Dante acaba de ser activado.\n\n"
        f"📌 Tipo de reporte: {datos.tipo_reporte}\n"
        f"📝 Notas de quien reporta: {datos.detalles}\n"
        f"📍 Ver ubicación en Google Maps para ir por él:\n{enlace_mapa}"
    )
    
    msg = MIMEText(cuerpo)
    msg['Subject'] = asunto
    msg['From'] = REMITENTE_GMAIL
    msg['To'] = ", ".join(DESTINATARIOS)
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as servidor:
            servidor.login(REMITENTE_GMAIL, PASSWORD_APLICACION)
            servidor.sendmail(REMITENTE_GMAIL, DESTINATARIOS, msg.as_string())
        print("\n[OK] ¡Alerta enviada a todos los correos con éxito!")
    except Exception as e:
        print(f"\n[ERROR] No se pudo enviar el correo: {e}")
        
    return {"status": "ok"}
