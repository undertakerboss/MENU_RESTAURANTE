import qrcode

def crear_qr_comercial(url_destino, nombre_archivo):
    # Configuración de grado industrial (soporta hasta 30% de daño o suciedad)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H, 
        box_size=15, # Tamaño de alta resolución
        border=2,    # Borde optimizado para impresión
    )
    
    qr.add_data(url_destino)
    qr.make(fit=True)

    # Generamos la imagen con colores institucionales (Negro sobre blanco)
    img = qr.make_image(fill_color="#111111", back_color="#ffffff")
    img.save(nombre_archivo)
    print(f"Éxito total: Código QR guardado como '{nombre_archivo}'.")
    print(f"Apunta directamente a tu servidor en la nube: {url_destino}")

if __name__ == "__main__":
    # ESTA ES TU URL REAL EN INTERNET
    url_del_menu = "https://undertakerboss.github.io/MENU_RESTAURANTE/"
    
    # Genera la imagen para la mesa del restaurante
    crear_qr_comercial(url_del_menu, "QR_Mesa_1.png")