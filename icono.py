from PIL import Image, ImageDraw

def generar_icono_profesional():
    # 1. Crear lienzo en 512x512 para definición perfecta
    size = (512, 512)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # PALETA DE COLORES CORPORATIVA
    COLOR_PANTONE_349C = (4, 106, 56, 255)   # #046a38 (Verde Principal)
    COLOR_PANTONE_DARK = (2, 65, 34, 255)    # Verde Oscuro (Cuerpo trasero)
    COLOR_GOLD = (212, 175, 55, 255)         # #d4af37 (Dorado Metálico)
    COLOR_WHITE = (255, 255, 255, 255)       # Blanco puro para visibilidad

    # --- 1. Pestaña de la carpeta (Atrás) ---
    draw.rounded_rectangle([60, 100, 240, 180], radius=20, fill=COLOR_PANTONE_DARK)

    # --- 2. Cuerpo trasero de la carpeta ---
    draw.rounded_rectangle([60, 140, 452, 430], radius=30, fill=COLOR_PANTONE_DARK)

    # --- 3. Hoja de Datos / Servidor (Emerge del centro) ---
    # Una hoja limpia blanca con líneas doradas muy visibles
    draw.rounded_rectangle([130, 80, 382, 300], radius=20, fill=COLOR_WHITE)
    # Trazos de datos (Líneas horizontales gruesas)
    draw.rounded_rectangle([170, 130, 342, 150], radius=5, fill=COLOR_GOLD)
    draw.rounded_rectangle([170, 175, 342, 195], radius=5, fill=COLOR_PANTONE_349C)
    draw.rounded_rectangle([170, 220, 280, 240], radius=5, fill=COLOR_GOLD)

    # --- 4. Solapa Frontal de la Carpeta (Adelante) ---
    draw.rounded_rectangle([60, 210, 452, 430], radius=30, fill=COLOR_PANTONE_349C)

    # --- 5. Borde / Acento Dorado Superior en la Solapa ---
    draw.rounded_rectangle([60, 210, 452, 235], radius=10, fill=COLOR_GOLD)

    # --- 6. Símbolo de Backup / Flechas Circulares Centradas (Ultra Nítidas) ---
    cx, cy = 256, 330  # Centro exacto de la solapa frontal
    
    # Flecha 1 (Arco superior)
    draw.arc([cx - 55, cy - 55, cx + 55, cy + 55], start=210, end=30, fill=COLOR_WHITE, width=16)
    # Cabeza de la flecha
    draw.polygon([(cx + 55, cy - 10), (cx + 75, cy + 20), (cx + 35, cy + 20)], fill=COLOR_WHITE)

    # Flecha 2 (Arco inferior)
    draw.arc([cx - 55, cy - 55, cx + 55, cy + 55], start=30, end=210, fill=COLOR_WHITE, width=16)
    # Cabeza de la flecha
    draw.polygon([(cx - 55, cy + 10), (cx - 75, cy - 20), (cx - 35, cy - 20)], fill=COLOR_WHITE)

    # --- 7. GUARDAR PNG Y .ICO MULTITAMAÑO ---
    # Guardar PNG
    img.save("icono.png", "PNG")

    # Guardar .ICO con todas las capas de resolución requeridas por Windows
    # (Desde 16x16 hasta 256x256 en un solo archivo)
    img.save(
        "icono.ico", 
        format="ICO", 
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    )
    print("✨ 'icono.png' e 'icono.ico' generados exitosamente en alta definición y multitamaño.")

if __name__ == "__main__":
    generar_icono_profesional()