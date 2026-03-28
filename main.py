# main.py
import uvicorn
import qrcode
import io
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# --- 1. ARQUITECTURA DE DATOS (Escalable) ---
# Usamos SQLite para desarrollo ágil, preparado para migrar a PostgreSQL en AMS 1.0.
SQLALCHEMY_DATABASE_URL = "sqlite:///./restaurantes.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 2. MODELOS DE ENTIDAD-RELACIÓN ---
class Restaurante(Base):
    __tablename__ = "restaurantes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)

class Plato(Base):
    __tablename__ = "platos"
    id = Column(Integer, primary_key=True, index=True)
    restaurante_id = Column(Integer, ForeignKey("restaurantes.id"))
    nombre = Column(String, index=True)
    precio = Column(Float)
    disponible = Column(Boolean, default=True) # Interruptor lógico de stock

# Generación automática de las tablas en el disco
Base.metadata.create_all(bind=engine)

# --- 3. MOTOR DEL SERVIDOR ---
app = FastAPI(title="Motor Menú QR")
templates = Jinja2Templates(directory="templates")

# Inyección de dependencias para seguridad en las conexiones a la BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 4. ENRUTAMIENTO (Endpoints) ---

# A. Vista Cliente (El QR apunta aquí)
@app.get("/menu/{restaurante_id}", response_class=HTMLResponse)
def ver_menu(request: Request, restaurante_id: int, db: Session = Depends(get_db)):
    restaurante = db.query(Restaurante).filter(Restaurante.id == restaurante_id).first()
    # Filtro lógico: Solo extraemos platos donde disponible == True
    platos = db.query(Plato).filter(Plato.restaurante_id == restaurante_id, Plato.disponible == True).all()
    
    return templates.TemplateResponse("menu.html", {"request": request, "restaurante": restaurante, "platos": platos})

# B. Vista Administrador (Enlace privado para el dueño)
@app.get("/admin/{restaurante_id}", response_class=HTMLResponse)
def panel_admin(request: Request, restaurante_id: int, db: Session = Depends(get_db)):
    restaurante = db.query(Restaurante).filter(Restaurante.id == restaurante_id).first()
    # El dueño ve TODOS los datos, sin filtros lógicos
    platos = db.query(Plato).filter(Plato.restaurante_id == restaurante_id).all()
    
    return templates.TemplateResponse("admin.html", {"request": request, "restaurante": restaurante, "platos": platos})

# C. Lógica Binaria (Cambiar estado Disponible <-> Agotado)
@app.post("/admin/toggle/{plato_id}")
def toggle_plato(plato_id: int, db: Session = Depends(get_db)):
    plato = db.query(Plato).filter(Plato.id == plato_id).first()
    if plato:
        plato.disponible = not plato.disponible # Invierte el valor booleano
        db.commit()
    return RedirectResponse(url=f"/admin/{plato.restaurante_id}", status_code=303)

# D. Agregar nuevo plato dinámicamente (Autoservicio)
@app.post("/admin/{restaurante_id}/agregar")
def agregar_plato(restaurante_id: int, nombre: str = Form(...), precio: float = Form(...), db: Session = Depends(get_db)):
    nuevo_plato = Plato(restaurante_id=restaurante_id, nombre=nombre, precio=precio, disponible=True)
    db.add(nuevo_plato)
    db.commit()
    return RedirectResponse(url=f"/admin/{restaurante_id}", status_code=303)

# E. Generador automático de QR en RAM (Stateless)
@app.get("/admin/{restaurante_id}/qr")
def descargar_qr(request: Request, restaurante_id: int):
    # Construimos la URL dinámica
    url_destino = str(request.base_url) + f"menu/{restaurante_id}"
    
    # Lógica de encriptación 2D y corrección de errores H (30%)
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=15, border=4)
    qr.add_data(url_destino)
    qr.make(fit=True)
    
    # Generamos la imagen en la memoria RAM
    img = qr.make_image(fill_color="#2f3542", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    
    # Descarga directa sin tocar el disco duro
    return StreamingResponse(buf, media_type="image/png", headers={"Content-Disposition": "attachment; filename=QR_Menu.png"})

# Bloque de ejecución directa de Uvicorn
if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)