# 🖥️ Auto Shutdown - Guía de Instalación Completa

## ¿Qué hace este programa?

Este programa **apaga automáticamente tu computadora a las 8:00 PM todos los días** si no la has apagado antes. Es perfecto para no olvidarte de apagar el servidor cuando te vas.

---

## 📋 Instalación Paso a Paso

### **PASO 1: Instalar Python**

1. **Abrir navegador web** (Chrome, Firefox, Edge, etc.)
2. **Ir a**: https://python.org
3. **Hacer clic en** "Downloads"
4. **Descargar** la versión más reciente (aparecerá un botón grande amarillo)
5. **Ejecutar** el archivo descargado
6. **⚠️ MUY IMPORTANTE**: Marcar la casilla "Add Python to PATH" antes de instalar
7. **Hacer clic en** "Install Now"
8. **Esperar** a que termine la instalación
9. **Reiniciar** la computadora

### **PASO 2: Crear la carpeta del programa**

1. **Abrir** el Explorador de archivos
2. **Ir a** la unidad C: (Disco Local C)
3. **Hacer clic derecho** en un espacio vacío
4. **Seleccionar** "Nuevo" → "Carpeta"
5. **Nombrar** la carpeta: `AutoShutdown`
6. **Entrar** a la carpeta que acabas de crear

### **PASO 3: Crear el archivo del programa**

1. **Dentro de la carpeta AutoShutdown**, hacer clic derecho
2. **Seleccionar** "Nuevo" → "Documento de texto"
3. **Nombrar** el archivo: `auto_shutdown.py`
4. **⚠️ IMPORTANTE**: Asegúrate de que termine en `.py` no en `.txt`
5. **Hacer doble clic** para abrirlo con Bloc de notas
6. **Copiar todo el código** que te dieron y pegarlo en el archivo
7. **Guardar** el archivo (Ctrl + S)
8. **Cerrar** el Bloc de notas

### **PASO 4: Probar que funciona**

1. **Abrir** el símbolo del sistema:
   - Presionar `Win + R`
   - Escribir: `cmd`
   - Presionar Enter
2. **Navegar** a la carpeta:
   - Escribir: `cd C:\AutoShutdown`
   - Presionar Enter
3. **Ejecutar** el programa:
   - Escribir: `python auto_shutdown.py`
   - Presionar Enter
4. **Debe aparecer** algo como:
   ```
   === Auto Shutdown - Apagado Automático ===
   Programa que apaga automáticamente la PC a las 8:00 PM
   Presiona Ctrl+C para detener el programa
   ```
5. **Presionar** `Ctrl + C` para detenerlo por ahora

### **PASO 5: Configurar inicio automático**

1. **Ejecutar** el programa una vez para crear archivos necesarios:
   - En el símbolo del sistema, escribir: `python auto_shutdown.py`
   - Esperar 5 segundos
   - Presionar `Ctrl + C` para detenerlo
2. **Abrir** la carpeta de inicio automático:
   - Presionar `Win + R`
   - Escribir: `shell:startup`
   - Presionar Enter
3. **Ir** a la carpeta del programa:
   - Abrir otra ventana del explorador
   - Ir a `C:\AutoShutdown`
4. **ELEGIR UNA OPCIÓN** (recomendado: Opción A):

   **🔸 OPCIÓN A - Acceso directo (RECOMENDADO)**:

   - Encontrar el archivo `auto_shutdown.lnk`
   - Copiarlo a la carpeta de inicio
   - ✅ Funciona aunque muevas la carpeta AutoShutdown

   **🔸 OPCIÓN B - Archivo BAT**:

   - Encontrar el archivo `auto_shutdown.bat`
   - Copiarlo a la carpeta de inicio
   - ⚠️ Si mueves la carpeta AutoShutdown, debes copiar de nuevo el archivo

5. **Cerrar** todas las ventanas

### **PASO 6: ¡Listo!**

**Reiniciar** la computadora. El programa comenzará automáticamente y se ejecutará todos los días.

---

## 🔧 Configuración Adicional

### **Cambiar la hora de apagado**

Si quieres cambiar la hora (por ejemplo, a las 7:00 PM):

1. **Abrir** el archivo `auto_shutdown.py` con Bloc de notas
2. **Buscar** la línea que dice: `self.shutdown_time = "20:00"`
3. **Cambiar** "20:00" por la hora que quieras:
   - Para 7:00 PM: `"19:00"`
   - Para 9:00 PM: `"21:00"`
   - Para 6:30 PM: `"18:30"`
4. **Guardar** el archivo

### **Ver si está funcionando**

1. **Ir** a la carpeta de usuario (normalmente `C:\Users\[TuNombre]`)
2. **Buscar** el archivo `auto_shutdown.log`
3. **Abrirlo** con Bloc de notas para ver el historial

---

## ❗ Solución de Problemas

### **Error: "Python no se reconoce como comando"**

- **Solución**: Reinstalar Python y marcar "Add Python to PATH"

### **Error: "No se puede ejecutar el archivo"**

- **Solución**: Asegúrate de que el archivo termine en `.py` no en `.txt`

### **El programa no se inicia automáticamente**

- **Verificar**: Que el archivo `.bat` esté en la carpeta de inicio
- **Carpeta de inicio**: Win + R → escribir `shell:startup` → Enter

### **Quiero cancelar el apagado**

- **Abrir** símbolo del sistema (Win + R → cmd)
- **Escribir**: `shutdown /a`
- **Presionar** Enter

### **Quiero desinstalar el programa**

- **Eliminar** el archivo de la carpeta de inicio (`shell:startup`)
- **Eliminar** la carpeta `C:\AutoShutdown`

---

## 📞 Información Adicional

- **Hora programada**: 8:00 PM (20:00)
- **Aviso antes de apagar**: 60 segundos
- **Frecuencia de verificación**: Cada 5 minutos
- **Archivo de log**: Se guarda en tu carpeta de usuario

**⚠️ IMPORTANTE**: El programa te dará 60 segundos de aviso antes de apagar. Si estás usando la computadora, podrás cancelar el apagado ejecutando `shutdown /a` en el símbolo del sistema.

---

_¿Tienes problemas? Guarda este archivo y consulta la sección de "Solución de Problemas" arriba._
