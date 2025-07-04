#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Shutdown GUI - Glassmorphism Design
Programa elegante para programar apagado automático con interfaz moderna
"""

import sys
import json
import os
import time
import datetime
import subprocess
import threading
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QTimeEdit, QPushButton, 
                            QCheckBox, QFrame, QSystemTrayIcon, QMenu, 
                            QMessageBox, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import QTime, QTimer, Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QRectF
from PyQt6.QtGui import QFont, QIcon, QPainter, QPainterPath, QColor, QLinearGradient, QBrush

class GlassWidget(QWidget):
    """Widget con efecto glassmorphism"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Crear el fondo con glassmorphism NEGRO sutil
        rect = self.rect()
        
        # Fondo negro muy sutil
        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, QColor(0, 0, 0, 255))     # NEGRO TOTAL arriba
        gradient.setColorAt(1, QColor(0, 0, 0, 255))
        
        # Crear path con bordes redondeados
        path = QPainterPath()
        rectf = QRectF(rect)
        path.addRoundedRect(rectf, 20.0, 20.0)
        
        # Aplicar el fondo
        painter.fillPath(path, QBrush(gradient))
        
        # Borde blanco sutil
        painter.setPen(QColor(255, 255, 255, 40))
        painter.drawPath(path)

class AutoShutdownService(QThread):
    """Servicio que verifica la hora de apagado en segundo plano"""
    
    shutdown_triggered = pyqtSignal()
    status_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.config_file = Path.home() / "auto_shutdown_config.json"
        self.log_file = Path.home() / "auto_shutdown.log"
        self.running = True
        self.shutdown_executed_today = False
        self.last_date = datetime.datetime.now().date()
        
    def load_config(self):
        """Carga la configuración desde archivo"""
        default_config = {
            "enabled": True,
            "shutdown_time": "20:00",
            "postpone_until": None,
            "skip_today": False
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Verificar que tenga todas las claves necesarias
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key]
                return config
            else:
                return default_config
        except:
            return default_config
    
    def save_config(self, config):
        """Guarda la configuración en archivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log(f"Error guardando configuración: {e}")
    
    def log(self, message):
        """Registra mensajes en el archivo de log"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except:
            pass
    
    def should_shutdown(self, config):
        """Determina si debe apagar la PC"""
        if not config["enabled"]:
            return False
            
        now = datetime.datetime.now()
        
        # Verificar si se debe saltar hoy
        if config.get("skip_today", False):
            return False
        
        # Verificar si hay postpone activo
        if config.get("postpone_until"):
            try:
                postpone_time = datetime.datetime.fromisoformat(config["postpone_until"])
                if now < postpone_time:
                    return False
                else:
                    # Limpiar postpone vencido
                    config["postpone_until"] = None
                    self.save_config(config)
            except:
                config["postpone_until"] = None
                self.save_config(config)
        
        # Verificar hora programada - SOLO si ya pasó la hora
        shutdown_hour, shutdown_minute = map(int, config["shutdown_time"].split(":"))
        shutdown_datetime = now.replace(hour=shutdown_hour, minute=shutdown_minute, second=0, microsecond=0)
        
        return now >= shutdown_datetime
    
    def shutdown_computer(self):
        """Ejecuta el apagado de la computadora"""
        self.log("Iniciando apagado automático...")
        self.shutdown_triggered.emit()
        
        try:
            if os.name == 'nt':
                subprocess.run(['shutdown', '/s', '/t', '60', '/c', 'Auto Shutdown: Apagado programado - 60 segundos'], 
                             check=True)
                self.log("Comando de apagado ejecutado (Windows)")
            else:
                subprocess.run(['sudo', 'shutdown', '-h', '+1', 'Auto Shutdown: Apagado programado'], 
                             check=True)
                self.log("Comando de apagado ejecutado (Linux/Mac)")
        except Exception as e:
            self.log(f"Error ejecutando apagado: {e}")
    
    def run(self):
        """Hilo principal del servicio"""
        self.log("Auto Shutdown Service iniciado")
        
        while self.running:
            try:
                current_date = datetime.datetime.now().date()
                
                # Reiniciar flags si es un nuevo día
                if current_date != self.last_date:
                    self.shutdown_executed_today = False
                    self.last_date = current_date
                    # Limpiar skip_today
                    config = self.load_config()
                    if config.get("skip_today", False):
                        config["skip_today"] = False
                        self.save_config(config)
                
                # Verificar configuración
                config = self.load_config()
                
                if self.should_shutdown(config) and not self.shutdown_executed_today:
                    self.shutdown_computer()
                    self.shutdown_executed_today = True
                
                # Actualizar estado
                if config["enabled"]:
                    self.status_changed.emit(f"Activo - Apagado: {config['shutdown_time']}")
                else:
                    self.status_changed.emit("Desactivado")
                
                # Esperar 5 minutos antes de la siguiente verificación
                for _ in range(300):  # 5 minutos = 300 segundos
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.log(f"Error en servicio: {e}")
                time.sleep(60)
    
    def stop(self):
        """Detiene el servicio"""
        self.running = False
        self.quit()
        self.wait()

class AutoShutdownGUI(QMainWindow):
    """Interfaz gráfica principal con diseño glassmorphism"""
    
    def __init__(self):
        super().__init__()
        self.service = AutoShutdownService()
        self.setup_ui()
        self.setup_tray()
        self.load_settings()
        self.start_service()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setWindowTitle("Auto Shutdown")
        self.setFixedSize(550, 850)  # Aún más grande
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Layout principal
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(25)
        
        # Contenedor principal con glassmorphism
        self.glass_container = GlassWidget()
        container_layout = QVBoxLayout(self.glass_container)
        container_layout.setContentsMargins(35, 35, 35, 35)
        container_layout.setSpacing(30)
        
        # Título
        title = QLabel("Auto Shutdown")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
                background: transparent;
                margin-bottom: 10px;
            }
        """)
        
        # Subtítulo
        subtitle = QLabel("Control de apagado automático")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 13px;
                background: transparent;
                margin-bottom: 15px;
            }
        """)
        
        # Estado actual
        self.status_label = QLabel("Cargando...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: rgba(0, 255, 150, 0.9);
                font-size: 14px;
                font-weight: bold;
                background: rgba(0, 255, 150, 0.1);
                border: 1px solid rgba(0, 255, 150, 0.3);
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        # Checkbox activar/desactivar
        self.enabled_checkbox = QCheckBox("Activar apagado automático")
        self.enabled_checkbox.setChecked(True)
        self.enabled_checkbox.stateChanged.connect(self.on_enabled_changed)
        self.enabled_checkbox.setStyleSheet("""
            QCheckBox {
                color: white;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid rgba(255, 255, 255, 0.5);
                background: rgba(255, 255, 255, 0.1);
            }
            QCheckBox::indicator:checked {
                background: rgba(0, 255, 150, 0.8);
                border: 2px solid rgba(0, 255, 150, 1);
            }
        """)
        
        # Selector de hora
        time_frame = QFrame()
        time_frame.setStyleSheet("background: transparent;")
        time_layout = QVBoxLayout(time_frame)
        
        time_label = QLabel("Hora de apagado:")
        time_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime(20, 0))  # 8:00 PM por defecto
        self.time_edit.setDisplayFormat("hh:mm")
        self.time_edit.timeChanged.connect(self.on_time_changed)
        # Hacer el QTimeEdit editable con teclado y mouse
        self.time_edit.setReadOnly(False)
        self.time_edit.setButtonSymbols(QTimeEdit.ButtonSymbols.UpDownArrows)
        self.time_edit.setStyleSheet("""
            QTimeEdit {
                background: rgba(255, 255, 255, 0.15);
                border: 2px solid rgba(255, 255, 255, 0.4);
                border-radius: 12px;
                color: white;
                font-size: 20px;
                font-weight: bold;
                padding: 15px;
                text-align: center;
                selection-background-color: rgba(0, 255, 150, 0.3);
            }
            QTimeEdit:focus {
                border: 2px solid rgba(0, 255, 150, 0.8);
                background: rgba(255, 255, 255, 0.2);
            }
            QTimeEdit::up-button {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                width: 20px;
                margin-right: 5px;
            }
            QTimeEdit::down-button {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                width: 20px;
                margin-right: 5px;
            }
            QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {
                background: rgba(255, 255, 255, 0.3);
            }
        """)
        
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_edit)
        
        # Botones de acción
        buttons_frame = QFrame()
        buttons_frame.setStyleSheet("background: transparent;")
        buttons_layout = QVBoxLayout(buttons_frame)
        buttons_layout.setSpacing(15)
        
        # Botón postponer
        self.postpone_btn = QPushButton("🕐 Postponer 2 horas")
        self.postpone_btn.clicked.connect(self.postpone_shutdown)
        
        # Botón saltar hoy
        self.skip_btn = QPushButton("⏭️ Saltar hoy")
        self.skip_btn.clicked.connect(self.skip_today)
        
        # Botón cancelar apagado
        self.cancel_btn = QPushButton("❌ Cancelar apagado")
        self.cancel_btn.clicked.connect(self.cancel_shutdown)
        
        # Estilo para botones - MÁS GRANDES
        button_style = """
            QPushButton {
                background: rgba(255, 255, 255, 0.15);
                border: 2px solid rgba(255, 255, 255, 0.4);
                border-radius: 15px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 20px 25px;
                text-align: left;
                min-height: 30px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.25);
                border: 2px solid rgba(255, 255, 255, 0.6);
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.35);
                transform: translateY(1px);
            }
        """
        
        self.postpone_btn.setStyleSheet(button_style)
        self.skip_btn.setStyleSheet(button_style)
        self.cancel_btn.setStyleSheet(button_style)
        
        buttons_layout.addWidget(self.postpone_btn)
        buttons_layout.addWidget(self.skip_btn)
        buttons_layout.addWidget(self.cancel_btn)
        
        # Botón minimizar/cerrar
        controls_frame = QFrame()
        controls_frame.setStyleSheet("background: transparent;")
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.addStretch()
        
        self.minimize_btn = QPushButton("🗕")
        self.close_btn = QPushButton("✕")
        
        control_style = """
            QPushButton {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 15px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                width: 30px;
                height: 30px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.2);
            }
        """
        
        self.minimize_btn.setStyleSheet(control_style)
        self.close_btn.setStyleSheet(control_style)
        self.minimize_btn.clicked.connect(self.hide)
        self.close_btn.clicked.connect(self.close)
        
        controls_layout.addWidget(self.minimize_btn)
        controls_layout.addWidget(self.close_btn)
        
        # Agregar todo al contenedor
        container_layout.addWidget(title)
        container_layout.addWidget(subtitle)
        container_layout.addWidget(self.status_label)
        container_layout.addWidget(self.enabled_checkbox)
        container_layout.addWidget(time_frame)
        container_layout.addWidget(buttons_frame)
        container_layout.addStretch()
        container_layout.addWidget(controls_frame)
        
        layout.addWidget(self.glass_container)
        
        # Fondo con gradiente
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(30, 60, 114, 0.8),
                    stop:0.5 rgba(42, 82, 152, 0.8),
                    stop:1 rgba(20, 40, 80, 0.8));
            }
        """)
        
    def setup_tray(self):
        """Configura el icono en la bandeja del sistema"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Crear un icono simple usando texto
        from PyQt6.QtGui import QPixmap, QPainter, QFont
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparente
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fondo circular
        painter.setBrush(QBrush(QColor(42, 82, 152)))
        painter.setPen(QColor(255, 255, 255))
        painter.drawEllipse(2, 2, 28, 28)
        
        # Texto "AS" (Auto Shutdown)
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(8, 20, "AS")
        painter.end()
        
        self.tray_icon.setIcon(QIcon(pixmap))
        
        # Menú del tray
        tray_menu = QMenu()
        
        # Estado actual
        self.tray_status_action = tray_menu.addAction("Estado: Cargando...")
        self.tray_status_action.setEnabled(False)
        
        tray_menu.addSeparator()
        
        # Acciones principales
        show_action = tray_menu.addAction("🔧 Configurar")
        show_action.triggered.connect(self.show_and_raise)
        
        postpone_action = tray_menu.addAction("🕐 Postponer 2 horas")
        postpone_action.triggered.connect(self.postpone_shutdown)
        
        skip_action = tray_menu.addAction("⏭️ Saltar hoy")
        skip_action.triggered.connect(self.skip_today)
        
        tray_menu.addSeparator()
        
        cancel_action = tray_menu.addAction("❌ Cancelar apagado")
        cancel_action.triggered.connect(self.cancel_shutdown)
        
        tray_menu.addSeparator()
        
        exit_action = tray_menu.addAction("🚪 Salir")
        exit_action.triggered.connect(self.quit_app)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # Tooltip
        self.tray_icon.setToolTip("Auto Shutdown - Apagado automático")
        self.tray_icon.show()
        
    def show_and_raise(self):
        """Muestra y enfoca la ventana"""
        self.show()
        self.raise_()
        self.activateWindow()
        
    def load_settings(self):
        """Carga la configuración guardada"""
        config = self.service.load_config()
        
        self.enabled_checkbox.setChecked(config["enabled"])
        
        time_parts = config["shutdown_time"].split(":")
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        self.time_edit.setTime(QTime(hour, minute))
        
    def start_service(self):
        """Inicia el servicio de apagado"""
        self.service.status_changed.connect(self.update_status)
        self.service.shutdown_triggered.connect(self.on_shutdown_triggered)
        self.service.start()
        
    def update_status(self, status):
        """Actualiza el estado mostrado"""
        self.status_label.setText(status)
        
        # Actualizar también el menú del tray
        if hasattr(self, 'tray_status_action'):
            self.tray_status_action.setText(f"Estado: {status}")
        
        # Actualizar tooltip
        self.tray_icon.setToolTip(f"Auto Shutdown - {status}")
        
    def on_shutdown_triggered(self):
        """Se ejecuta cuando se va a apagar"""
        self.show()
        QMessageBox.warning(self, "Auto Shutdown", 
                          "¡La PC se apagará en 60 segundos!\n\n"
                          "Haz clic en 'Cancelar apagado' si quieres detenerlo.")
        
    def on_enabled_changed(self, state):
        """Cuando se cambia el estado activado/desactivado"""
        config = self.service.load_config()
        config["enabled"] = self.enabled_checkbox.isChecked()
        self.service.save_config(config)
        
    def on_time_changed(self, time):
        """Cuando se cambia la hora"""
        config = self.service.load_config()
        config["shutdown_time"] = time.toString("hh:mm")
        self.service.save_config(config)
        
    def postpone_shutdown(self):
        """Postpone el apagado 2 horas"""
        config = self.service.load_config()
        postpone_until = datetime.datetime.now() + datetime.timedelta(hours=2)
        config["postpone_until"] = postpone_until.isoformat()
        self.service.save_config(config)
        
        QMessageBox.information(self, "Postponer", 
                              f"Apagado postponido hasta las {postpone_until.strftime('%H:%M')}")
        
    def skip_today(self):
        """Salta el apagado solo por hoy"""
        config = self.service.load_config()
        config["skip_today"] = True
        self.service.save_config(config)
        
        QMessageBox.information(self, "Saltar hoy", 
                              "El apagado automático está desactivado solo por hoy")
        
    def cancel_shutdown(self):
        """Cancela un apagado en progreso"""
        try:
            if os.name == 'nt':
                subprocess.run(['shutdown', '/a'], check=True)
                QMessageBox.information(self, "Cancelado", "Apagado cancelado exitosamente")
            else:
                QMessageBox.information(self, "Cancelar", 
                                      "Ejecuta: sudo shutdown -c\nen la terminal para cancelar")
        except subprocess.CalledProcessError:
            QMessageBox.warning(self, "Advertencia", "No hay ningún apagado programado para cancelar")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cancelando apagado: {e}")
            
    def tray_icon_activated(self, reason):
        """Maneja clics en el icono de la bandeja"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Un solo clic muestra la ventana
            self.show_and_raise()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Doble clic también muestra la ventana
            self.show_and_raise()
                
    def closeEvent(self, event):
        """Maneja el cierre de la ventana - siempre minimiza al tray"""
        self.hide()
        event.ignore()
        
        # Mostrar mensaje solo la primera vez
        if not hasattr(self, '_hide_message_shown'):
            self.tray_icon.showMessage(
                "Auto Shutdown",
                "La aplicación sigue ejecutándose en segundo plano.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
            self._hide_message_shown = True
            
    def quit_app(self):
        """Cierra completamente la aplicación"""
        self.service.stop()
        self.tray_icon.hide()
        QApplication.quit()
        
    def mousePressEvent(self, event):
        """Permite arrastrar la ventana"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.globalPosition().toPoint()
            
    def mouseMoveEvent(self, event):
        """Arrastra la ventana"""
        if hasattr(self, 'drag_start_position'):
            if event.buttons() == Qt.MouseButton.LeftButton:
                self.move(self.pos() + event.globalPosition().toPoint() - self.drag_start_position)
                self.drag_start_position = event.globalPosition().toPoint()

def main():
    """Función principal"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # No cerrar cuando se oculta la ventana
    
    # Verificar si ya hay una instancia corriendo
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "Auto Shutdown", 
                           "No se puede acceder a la bandeja del sistema.")
        sys.exit(1)
    
    window = AutoShutdownGUI()
    
    # INICIO MINIMIZADO - No mostrar la ventana al abrir
    # Solo mostrar mensaje en tray la primera vez
    window.tray_icon.showMessage(
        "Auto Shutdown",
        "Aplicación iniciada. Haz clic en el icono para configurar.",
        QSystemTrayIcon.MessageIcon.Information,
        3000  # 3 segundos
    )
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()