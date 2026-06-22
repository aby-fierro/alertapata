
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
import sqlite3

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

REMITENTE_GMAIL = "abygailfierro191@gmail.com"
PASSWORD_APLICACION = "ramw dszy jrgk bqbu"
DESTINATARIOS = ["abygailfierro191@gmail.com", "friskpapa@gmail.com"]

# --- CONFIGURACIÓN E INICIALIZACIÓN DE LA BASE DE DATOS ---
def inicializar_bd():
    conexion = sqlite3.connect("alertapata.db")
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mascotas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            raza TEXT,
            comportamiento TEXT,
            salud TEXT,
            direccion TEXT,
            tel_principal TEXT,
            tel_secundario TEXT
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM mascotas")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO mascotas (nombre, raza, comportamiento, salud, direccion, tel_principal, tel_secundario)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "Dante", 
            "Chihuahua • Macho • Marrón con Blanco",
            "Es un perro miedoso con los desconocidos. Puede llegar a ladrar para protegerse si te acercas de sorpresa, pero no es agresivo por naturaleza. Se recomienda hablarle con calma y suavidad.",
            "Condición estable, gordo y sano. Está castrado (esterilizado).",
            "Anenecuilco No. 11, Col. Tierra y Libertad.",
            "627-279-2334 (Hermana)",
            "627-131-0481 (Aby)"
        ))
        conexion.commit()
    conexion.close()

inicializar_bd()

class ReporteUbicacion(BaseModel):
    latitud: float
    longitud: float
    tipo_reporte: str
    detalles: str

@app.get("/mascota/perro1", response_class=HTMLResponse)
async def ver_perfil():
    conexion = sqlite3.connect("alertapata.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT nombre, raza, comportamiento, salud, direccion, tel_principal, tel_secundario FROM mascotas WHERE id = 1")
    mascota = cursor.fetchone()
    conexion.close()
    
    nombre_db, raza_db, comportamiento_db, salud_db, direccion_db, tel_principal_db, tel_secundario_db = mascota

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

            <button id="btn-directo" class="btn btn-gps-direct" onclick="enviarUbicacion('Directo (Lo tienen retenido)')">📍 ¡LO TENGO CONMIGO! (ENVIAR GPS)</button>
            
            <button id="btn-lejano" class="btn btn-gps-far" onclick="enviarUbicacion('Lejano (Visto en la zona, huyó o no se deja atrapar)')">👀 LO VEO CERCA (REPORTAR ZONA)</button>
            
            <a class="btn btn-whatsapp" href="https://api.whatsapp.com/send?phone=526272792334&text=Hola!%20Escaneé%20el%20collar%20de%20Dante%20y%20tengo%20información%20sobre%20él." target="_blank">💬 CONTACTAR POR WHATSAPP</a>

            <span class="fallback-text">¿El código QR falla? Reporta directo en: alertapata.onrender.com/mascota/perro1</span>
        </div>

        <script>
        function enviarServidor(lat, lon, tipoReporte, detallesTexto) {
            fetch('/mascota/perro1/reportar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({latitud: lat, longitud: lon, tipo_reporte: tipoReporte, detalles: detallesTexto})
            })
            .then(res => res.json())
            .then(data => {
                alert('¡Reporte enviado con éxito a los dueños!');
                document.getElementById('txt-detalles').value = '';
            })
            .catch(err => {
                alert('Reporte enviado.');
            });
        }

        function enviarUbicacion(tipoReporte) {
            const detallesTexto = document.getElementById('txt-detalles').value || 'Sin detalles adicionales';
            
            if (navigator.geolocation) {
                // Configuramos opciones con un tiempo límite estricto de 6 segundos
                const opcionesGps = {
                    enableHighAccuracy: true,
                    timeout: 6000,
                    maximumAge: 0
                };

                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        // Si encuentra el GPS rápido, manda la ubicación exacta
                        enviarServidor(position.coords.latitude, position.coords.longitude, tipoReporte, detallesTexto);
                    }, 
                    function(error) {
                        // Si el celular bloquea el GPS o tarda demasiado, manda el reporte con 0.0 pero NO se congela
                        console.log("Error o timeout en GPS, enviando reporte básico");
                        enviarServidor(0.0, 0.0, tipoReporte, detallesTexto + ' (Nota: El celular del informante no compartió coordenadas GPS exactas).');
                    }, 
                    opcionesGps
                );
            } else {
                // Si el dispositivo viejito no tiene geolocalización, envía el texto de todas formas
                enviarServidor(0.0, 0.0, tipoReporte, detallesTexto);
            }
        }
        </script>
    </body>
    </html>
    """
    
    response_html = html_template.replace("TAG_NOMBRE", nombre_db)
    response_html = response_html.replace("TAG_RAZA", raza_db)
    response_html = response_html.replace("TAG_COMPORTAMIENTO", comportamiento_db)
    response_html = response_html.replace("TAG_SALUD", salud_db)
    response_html = response_html.replace("TAG_DIRECCION", direccion_db)
    response_html = response_html.replace("TAG_PRINCIPAL", tel_principal_db)
    response_html = response_html.replace("TAG_SECUNDARIO", tel_secundario_db)
    
    return response_html

@app.post("/mascota/perro1/reportar")
async def reportar_mascota(datos: ReporteUbicacion):
    if datos.latitud == 0.0 and datos.longitud == 0.0:
        enlace_mapa = "No disponible (El informante rechazó los permisos de ubicación o su GPS tardó demasiado)."
    else:
        enlace_mapa = f"http://maps.google.com/?q={datos.latitud},{datos.longitud}"
    
    asunto = f"🚨 ALERTA PATA: ¡Dante ha sido localizado!"
    cuerpo = (
        f"El collar de Dante acaba de ser activado.\n\n"
        f"📌 Tipo de reporte: {datos.tipo_reporte}\n"
        f"📝 Notas de quien reporta: {datos.detalles}\n"
        f"📍 Ubicación:\n{enlace_mapa}"
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
        print("\n[OK] Correo enviado con éxito.")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        
    return {"status": "ok"}
