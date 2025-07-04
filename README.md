# 🖥️ Auto Shutdown GUI - Guía de Instalación

## ¿Qué hace este programa?

Este programa **apaga automáticamente tu computadora** a la hora que configures todos los días. Tiene una interfaz gráfica moderna con glassmorphism y se ejecuta desde la bandeja del sistema.

---

## 📋 Instalación Paso a Paso

### **PASO 1: Instalar Python**

1. **Ir a**: https://python.org
2. **Descargar** la versión más reciente
3. **⚠️ MUY IMPORTANTE**: Marcar "Add Python to PATH" al instalar
4. **Instalar** y **reiniciar** la computadora

### **PASO 2: Crear la carpeta del programa**

1. **Crear carpeta**: `C:\AutoShutdown`
2. **Guardar** los archivos del programa ahí:
   - `auto_shutdown_gui.pyw`
   - `requirements.txt`

### **PASO 3: Instalar dependencias**

1. **Abrir** símbolo del sistema (cmd)
2. **Navegar** a la carpeta: `cd C:\AutoShutdown`
3. **Instalar PyQt6**: `pip install -r requirements.txt`

### **PASO 4: Probar que funciona**

1. **Ejecutar**: `python auto_shutdown_gui.pyw`
2. **Debe aparecer**: Icono en la bandeja del sistema (junto al WiFi/sonido)
3. **Hacer clic** en el icono para abrir la interfaz

### **PASO 5: Configurar inicio automático**

1. **Crear acceso directo**:

   - Clic derecho en `auto_shutdown_gui.pyw`
   - "Crear acceso directo"
   - Renombrar a: `Auto Shutdown`

2. **Agregar al inicio**:
   - Presionar `Win + R`
   - Escribir: `shell:startup`
   - Presionar Enter
   - **Copiar** el acceso directo a esa carpeta

### **PASO 6: ¡Listo!**

**Reiniciar** la computadora. El programa se ejecutará automáticamente y aparecerá en la bandeja del sistema.

---

## 🎛️ Cómo usar la interfaz

### **Desde la bandeja del sistema:**

- **Clic** en el icono "AS" para abrir configuración
- **Clic derecho** para menú rápido con opciones

### **Controles principales:**

- **✅ Activar/Desactivar** - Checkbox principal
- **🕐 Hora de apagado** - Selector con flechitas o escribir directamente
- **🕐 Postponer 2 horas** - Para casos especiales
- **⏭️ Saltar hoy** - Desactiva solo por hoy
- **❌ Cancelar apagado** - Si ya está en progreso

### **Configuración de hora:**

- **Usar flechitas** ↑↓ para cambiar
- **Escribir directamente** la hora (ej: 1900 para 7:00 PM)
- **Formato 24 horas**: 20:00 = 8:00 PM

---

## ❗ Solución de Problemas

### **Error: "PyQt6 no encontrado"**

- **Solución**: `pip install PyQt6`

### **Error: "Python no reconocido"**

- **Solución**: Reinstalar Python con "Add to PATH" marcado

### **El programa no aparece en la bandeja**

- **Verificar**: Que el archivo termine en `.pyw` no `.py`
- **Probar**: Ejecutar desde cmd para ver errores

### **No se inicia automáticamente**

- **Verificar**: Que el acceso directo esté en `shell:startup`
- **Probar**: Ejecutar el acceso directo manualmente

### **Quiero cancelar un apagado**

- **Opción 1**: Clic en "Cancelar apagado" en la interfaz
- **Opción 2**: Cmd → `shutdown /a`

### **Quiero desinstalar**

- **Eliminar**: Acceso directo de la carpeta startup
- **Eliminar**: Carpeta `C:\AutoShutdown`

---

## 📄 Archivos del programa

- **auto_shutdown_gui.pyw** - Programa principal
- **requirements.txt** - Dependencias de Python
- **auto_shutdown_config.json** - Configuración (se crea automáticamente)
- **auto_shutdown.log** - Historial de actividad

---

## 🔧 Configuración por defecto

- **Hora programada**: 8:00 PM (20:00)
- **Aviso antes de apagar**: 60 segundos
- **Verificación**: Cada 5 minutos
- **Estado inicial**: Activado

---

_El programa se ejecuta silenciosamente en segundo plano y solo aparece cuando necesitas configurarlo o cuando va a apagar la PC._
