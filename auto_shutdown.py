#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Shutdown - Apagado Automático Diario
Programa que apaga automáticamente la PC a las 8:00 PM todos los días
"""

import os
import time
import datetime
import sys
import subprocess
from pathlib import Path

class AutoShutdown:
    def __init__(self):
        self.shutdown_time = "20:00"  # 8:00 PM en formato 24h
        self.check_interval = 300  # Verificar cada 5 minutos (300 segundos)
        self.log_file = Path.home() / "auto_shutdown.log"
        
    def log(self, message):
        """Registra mensajes en el archivo de log"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error escribiendo log: {e}")
    
    def is_shutdown_time(self):
        """Verifica si es hora de apagar"""
        now = datetime.datetime.now()
        shutdown_hour, shutdown_minute = map(int, self.shutdown_time.split(":"))
        shutdown_datetime = now.replace(hour=shutdown_hour, minute=shutdown_minute, second=0, microsecond=0)
        
        # Si ya pasó la hora programada hoy, apagar
        if now >= shutdown_datetime:
            return True
            
        return False
    
    def shutdown_computer(self):
        """Apaga la computadora"""
        self.log("Iniciando apagado automático...")
        
        try:
            # Comando para Windows
            if os.name == 'nt':
                # Dar 60 segundos de aviso antes de apagar
                subprocess.run(['shutdown', '/s', '/t', '60', '/c', 'Apagado automático programado - 60 segundos'], 
                             check=True)
                self.log("Comando de apagado ejecutado (Windows) - 60 segundos de aviso")
            
            # Comando para Linux/Mac
            else:
                # Programar apagado en 1 minuto
                subprocess.run(['sudo', 'shutdown', '-h', '+1', 'Apagado automático programado'], 
                             check=True)
                self.log("Comando de apagado ejecutado (Linux/Mac) - 1 minuto de aviso")
                
        except subprocess.CalledProcessError as e:
            self.log(f"Error ejecutando comando de apagado: {e}")
            # Método alternativo para Windows
            if os.name == 'nt':
                try:
                    os.system('shutdown /s /t 60')
                    self.log("Comando de apagado alternativo ejecutado")
                except Exception as e2:
                    self.log(f"Error con comando alternativo: {e2}")
        
        except Exception as e:
            self.log(f"Error inesperado: {e}")
    
    def run(self):
        """Función principal que mantiene el programa corriendo"""
        self.log("Auto Shutdown iniciado - Hora programada: " + self.shutdown_time)
        
        shutdown_executed_today = False
        last_date = datetime.datetime.now().date()
        
        while True:
            try:
                current_date = datetime.datetime.now().date()
                
                # Reiniciar el flag si es un nuevo día
                if current_date != last_date:
                    shutdown_executed_today = False
                    last_date = current_date
                    self.log(f"Nuevo día: {current_date}")
                
                # Verificar si es hora de apagar y no se ha ejecutado hoy
                if self.is_shutdown_time() and not shutdown_executed_today:
                    self.log("Hora de apagado detectada")
                    self.shutdown_computer()
                    shutdown_executed_today = True
                
                # Esperar antes de la siguiente verificación
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                self.log("Programa terminado por el usuario")
                break
            except Exception as e:
                self.log(f"Error en el bucle principal: {e}")
                time.sleep(self.check_interval)

def create_startup_script():
    """Crea un script .bat para agregar al inicio de Windows"""
    script_dir = Path(__file__).parent
    
    # BAT que se ejecuta invisible (sin ventana)
    bat_content = f'''@echo off
REM Auto Shutdown - Apagado Automático
cd /d "%~dp0"
pythonw auto_shutdown.py
'''
    
    bat_file = script_dir / "auto_shutdown.bat"
    with open(bat_file, "w", encoding="utf-8") as f:
        f.write(bat_content)
    
    # Crear acceso directo también
    create_shortcut(script_dir, bat_file)
    
    print(f"Script .bat creado: {bat_file}")
    print(f"Acceso directo creado: auto_shutdown.lnk")
    print("\nPara agregarlo al inicio:")
    print("1. Presiona Win + R, escribe 'shell:startup' y presiona Enter")
    print("2. Copia el archivo 'auto_shutdown.lnk' a esa carpeta")
    print("3. ¡Listo! Se ejecutará invisible al iniciar Windows")
    print("\n✅ El programa se ejecutará en segundo plano SIN ventana")
    print("📄 Para verificar que funciona, revisa: auto_shutdown.log")

def create_shortcut(script_dir, bat_file):
    """Crea un acceso directo al archivo .bat"""
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(str(script_dir / "auto_shutdown.lnk"))
        shortcut.TargetPath = str(bat_file)
        shortcut.WorkingDirectory = str(script_dir)
        shortcut.Description = "Auto Shutdown - Apagado Automático"
        shortcut.save()
    except ImportError:
        # Si no tiene win32com, crear un script VBS para crear el acceso directo
        vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
Set Shortcut = WshShell.CreateShortcut("{script_dir}\\auto_shutdown.lnk")
Shortcut.TargetPath = "{bat_file}"
Shortcut.WorkingDirectory = "{script_dir}"
Shortcut.Description = "Auto Shutdown - Apagado Automático"
Shortcut.Save
'''
        vbs_file = script_dir / "create_shortcut.vbs"
        with open(vbs_file, "w", encoding="utf-8") as f:
            f.write(vbs_content)
        
        try:
            import subprocess
            subprocess.run(['cscript', str(vbs_file), '//nologo'], check=True)
            vbs_file.unlink()  # Eliminar el archivo VBS temporal
        except:
            pass  # Si falla, no importa

if __name__ == "__main__":
    # Programa se ejecuta en segundo plano sin interfaz
    auto_shutdown = AutoShutdown()
    auto_shutdown.run()