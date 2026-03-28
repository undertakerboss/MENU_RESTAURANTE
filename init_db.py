import sqlite3

def crear_base_datos():
    # Conectamos (o creamos) la base de datos
    conexion = sqlite3.connect('restaurantes.db')
    cursor = conexion.cursor()

    # Creamos la tabla desde cero
    cursor.execute('DROP TABLE IF EXISTS platos')
    cursor.execute('''
        CREATE TABLE platos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio INTEGER NOT NULL,
            imagen TEXT,
            disponible BOOLEAN NOT NULL CHECK (disponible IN (0, 1))
        )
    ''')

    # Insertamos nuestros 4 platos iniciales (disponible = 1)
    platos_iniciales = [
        ('Hamburguesa Clásica', 'Carne angus 150g, queso cheddar, vegetales y salsa.', 22000, 'https://upload.wikimedia.org/wikipedia/commons/1/11/Cheeseburger.png', 1),
        ('Perro Suizo', 'Salchicha premium, full queso mozzarella, papita ripio y salsas.', 18000, 'https://upload.wikimedia.org/wikipedia/commons/b/b1/Hot_dog_with_mustard.png', 1),
        ('Pizza Slice', 'Porción gigante de pepperoni con mozzarella fundida.', 15000, 'https://upload.wikimedia.org/wikipedia/commons/6/67/Transparent_Pizza.png', 1),
        ('Arepa Parrillera', 'Arepa artesanal rellena de chorizo santarrosano asado.', 19000, 'https://upload.wikimedia.org/wikipedia/commons/1/11/Cheeseburger.png', 1)
    ]

    cursor.executemany('INSERT INTO platos (nombre, descripcion, precio, imagen, disponible) VALUES (?, ?, ?, ?, ?)', platos_iniciales)
    
    conexion.commit()
    conexion.close()
    print("✅ Base de datos 'restaurantes.db' inicializada con éxito. Platos cargados.")

if __name__ == '__main__':
    crear_base_datos()