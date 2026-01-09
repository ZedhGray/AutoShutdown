# Auto Shutdown - Apagado Automático para Windows

Aplicación moderna de apagado automático con interfaz gráfica elegante estilo Google Material Design.

## 📋 ¿Qué hace este programa?

Auto Shutdown te permite programar el apagado automático de tu PC a una hora específica cada día. La aplicación:

- Se ejecuta en segundo plano (bandeja del sistema)
- Inicia automáticamente con Windows
- Tiene una interfaz moderna y fácil de usar
- Permite postponer o cancelar apagados

## 🚀 Instalación Rápida (para usuarios)

Si solo quieres usar el programa:

1. Descarga `AutoShutdown_Setup.exe` (el instalador)
2. Ejecuta el instalador
3. Sigue las instrucciones en pantalla
4. ¡Listo! El programa se instalará automáticamente

El instalador hace todo por ti:

- Crea la carpeta del programa
- Copia los archivos necesarios
- Crea accesos directos
- Configura el inicio automático

## 🛠️ Compilación (para desarrolladores)

Si quieres compilar el programa desde el código fuente:

### Requisitos previos

- Python 3.7 o superior
- PyQt6
- PyInstaller

### Pasos para compilar

1. **Clona o descarga el proyecto**

   ```bash
   git clone [tu-repositorio]
   cd auto-shutdown
   ```

2. **Instala las dependencias**

   ```bash
   pip install PyQt6 pyinstaller
   ```

3. **Ejecuta el script de compilación**
   ```bash
   build.bat
   ```

### ¿Qué hace `build.bat`?

El script de compilación automáticamente:

1. ✅ Verifica que PyInstaller esté instalado
2. 🧹 Limpia compilaciones anteriores
3. 🔨 Compila el ejecutable (`AutoShutdown.exe`)
4. 📦 Crea el instalador (`AutoShutdown_Setup.exe`)

### Archivos generados

Después de ejecutar `build.bat`, encontrarás:

- **`dist/AutoShutdown.exe`** → El programa ejecutable (portable)
- **`installer_output/AutoShutdown_Setup.exe`** → El instalador completo

## 📁 Estructura del proyecto

```
auto-shutdown/
├── auto_shutdown_gui_v2.pyw      # Código fuente principal
├── build.bat                      # Script de compilación
├── auto_shutdown.spec             # Configuración de PyInstaller
├── installer_script.iss           # Script del instalador (Inno Setup)
├── icon.ico                       # Icono del programa (opcional)
└── README.md                      # Este archivo
```

## 🔧 Uso del programa

1. **Activar apagado automático**

   - Abre el programa desde la bandeja del sistema
   - Activa el interruptor (toggle)
   - Selecciona la hora deseada
   - ¡Listo!

2. **Opciones disponibles**
   - Postponer 2 horas
   - Saltar solo por hoy
   - Cancelar apagado inmediato
   - Desactivar completamente

## ⚠️ Notas importantes

- **Windows Defender**: La primera vez que ejecutes el programa, Windows puede mostrar una advertencia. Esto es normal para programas sin firma digital.
- **Inicio automático**: El programa se agrega automáticamente al inicio de Windows.
- **En segundo plano**: Al cerrar la ventana, el programa sigue funcionando en la bandeja del sistema.

## 💡 Consejos para compilar

- **NO ejecutes `build.bat` como Administrador** (PyInstaller no lo necesita)
- Si Windows Defender bloquea el ejecutable, agrégalo manualmente a las excepciones
- El instalador requiere [Inno Setup](https://jrsoftware.org/isdl.php) instalado

## 📝 Licencia

[Especifica tu licencia aquí]

## 🤝 Contribuciones

[Información sobre cómo contribuir]

## 📧 Contacto

[Tu información de contacto]

---

**Versión actual**: 2.0  
**Compatible con**: Windows 10/11
