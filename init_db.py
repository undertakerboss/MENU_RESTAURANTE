
# init_db.py
from main import SessionLocal, Restaurante, Plato

def inicializar_datos():
    # Abrimos conexión a la base de datos
    db = SessionLocal()

    try:
        # Verificamos si ya existe el restaurante para no duplicar
        if db.query(Restaurante).first():
            print("Los datos ya fueron inicializados anteriormente.")
            return

        # 1. Creamos el Restaurante
        nuevo_restaurante = Restaurante(nombre="Restaurante Demo (MVP)")
        db.add(nuevo_restaurante)
        db.commit() # Guardamos para que se le asigne un ID (será el ID 1)
        db.refresh(nuevo_restaurante)

        # 2. Creamos los Platos vinculados al Restaurante ID 1
        plato1 = Plato(
            restaurante_id=nuevo_restaurante.id, 
            nombre="Hamburguesa Sencilla", 
            precio=20000, 
            disponible=True
        )
        plato2 = Plato(
            restaurante_id=nuevo_restaurante.id, 
            nombre="Salchipapa Especial", 
            precio=15000, 
            disponible=True
        )

        # Inyectamos los platos a la base de datos
        db.add(plato1)
        db.add(plato2)
        db.commit()

        print("Inyección de datos exitosa. Base de datos lista.")

    except Exception as e:
        print(f"Error en la inyección de datos: {e}")
        db.rollback()
    finally:
        db.close() # Siempre cerramos la conexión por seguridad

if __name__ == "__main__":
    inicializar_datos()