from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3

app = FastAPI(title="Menú QR La Parrilla")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Función auxiliar para conectar a la BD
def obtener_conexion():
    conn = sqlite3.connect('restaurantes.db')
    conn.row_factory = sqlite3.Row # Para poder acceder a las columnas por nombre
    return conn

# 1. RUTA DEL CLIENTE (EL MENÚ)
@app.get("/", response_class=HTMLResponse)
async def ver_menu(request: Request, mesa: str = None):
    conn = obtener_conexion()
    # Solo traemos los platos que están disponibles (disponible = 1)
    platos = conn.execute('SELECT * FROM platos WHERE disponible = 1').fetchall()
    conn.close()
    return templates.TemplateResponse("index.html", {"request": request, "mesa_id": mesa, "platos": platos})

# 2. RUTA DEL DUEÑO (PANEL ADMIN)
@app.get("/admin", response_class=HTMLResponse)
async def ver_admin(request: Request):
    conn = obtener_conexion()
    platos = conn.execute('SELECT * FROM platos').fetchall()
    conn.close()
    return templates.TemplateResponse("admin.html", {"request": request, "platos": platos})

# 3. RUTA DEL BOTÓN DE PÁNICO (APAGAR/PRENDER PLATO)
@app.post("/admin/toggle/{plato_id}")
async def toggle_plato(plato_id: int):
    conn = obtener_conexion()
    plato = conn.execute('SELECT disponible FROM platos WHERE id = ?', (plato_id,)).fetchone()
    # Invertimos el estado (Si es 1 pasa a 0, si es 0 pasa a 1)
    nuevo_estado = 0 if plato['disponible'] else 1
    conn.execute('UPDATE platos SET disponible = ? WHERE id = ?', (nuevo_estado, plato_id))
    conn.commit()
    conn.close()
    # Recargamos la página del admin
    return RedirectResponse(url="/admin", status_code=303)