"""
Script para crear un icono simple para Auto Shutdown
Requiere: pip install pillow
"""
from PIL import Image, ImageDraw, ImageFont

def create_icon():
    """Crea un icono simple de 256x256"""
    # Crear imagen de 256x256
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Círculo de fondo con gradiente simulado
    # Verde Google
    for i in range(size//2):
        alpha = int(255 * (1 - i/(size//2)))
        color = (52, 168, 83, alpha)
        draw.ellipse([i, i, size-i, size-i], fill=color)
    
    # Círculo principal
    margin = 30
    draw.ellipse([margin, margin, size-margin, size-margin], 
                 fill=(52, 168, 83), outline=(34, 139, 34), width=8)
    
    # Símbolo de power (círculo + línea)
    center = size // 2
    
    # Círculo interior blanco
    inner_margin = 70
    draw.ellipse([inner_margin, inner_margin, size-inner_margin, size-inner_margin],
                 outline=(255, 255, 255), width=15, fill=None)
    
    # Línea vertical de power
    line_width = 15
    line_top = 60
    line_bottom = center
    draw.rectangle([center - line_width//2, line_top, 
                   center + line_width//2, line_bottom],
                  fill=(255, 255, 255))
    
    # Guardar en diferentes tamaños para el .ico
    img.save('icon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (256,256)])
    print("✅ Icono creado: icon.ico")
    print("   Contiene tamaños: 16x16, 32x32, 48x48, 256x256")

if __name__ == "__main__":
    try:
        create_icon()
    except ImportError:
        print("❌ Error: Pillow no está instalado")
        print("   Instala con: pip install pillow")
        print("   O continúa sin icono (no es obligatorio)")
