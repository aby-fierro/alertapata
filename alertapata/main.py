from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
import sqlite3

app = FastAPI(title="AlertaPata - Sistema de Recuperación de Mascotas")

# --- CONFIGURACIÓN DE SEGURIDAD CORS PARA CELULARES ---
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
            <div class="status-badge">🚨 ESTADO: ¡
