#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Shutdown GUI - Google Material Design
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
                            QMessageBox, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect)
from PyQt6.QtCore import QTime, QTimer, Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QRectF
from PyQt6.QtGui import QFont, QIcon, QPainter, QPainterPath, QColor, QLinearGradient, QBrush, QRadialGradient

class MaterialCard(QWidget):
    """Widget tipo Material Design Card"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        
        # Agregar sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        
        # Fondo blanco con transparencia para Material Design
        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, QColor(255, 255, 255, 250))
        gradient.setColorAt(1, QColor(248, 249, 250, 245))
        
        # Crear path con bordes redondeados estilo Material
        path = QPainterPath()
        rectf = QRectF(rect)
        path.addRoundedRect(rectf, 16.0, 16.0)
        
        # Aplicar el fondo
        painter.fillPath(path, QBrush(gradient))
        
        # Borde sutil
        painter.setPen(QColor(224, 224, 224, 100))
        painter.drawPath(path)

class StatusIndicator(QWidget):
    """Indicador de estado visual estilo Google"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_active = True
        self.status_text = "Activo"
        self.time_text = "20:00"
        self.setFixedHeight(80)
        
    def set_status(self, active, status_text, time_text):
        """Actualiza el estado y redibuja"""
        self.is_active = active
        self.status_text = status_text
        self.time_text = time_text
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        
        # Color de fondo según estado
        if self.is_active:
            bg_color = QColor(76, 175, 80, 30)  # Verde Material
            border_color = QColor(76, 175, 80, 150)
            text_color = QColor(56, 142, 60)
        else:
            bg_color = QColor(158, 158, 158, 30)  # Gris Material
            border_color = QColor(158, 158, 158, 150)
            text_color = QColor(97, 97, 97)
        
        # Fondo
        path = QPainterPath()
        rectf = QRectF(rect)
        path.addRoundedRect(rectf, 12.0, 12.0)
        painter.fillPath(path, QBrush(bg_color))
        
        # Borde
        painter.setPen(border_color)
        painter.drawPath(path)
        
        # Círculo indicador
        circle_x = 20
        circle_y = rect.height() // 2
        painter.setBrush(QBrush(border_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(circle_x - 6, circle_y - 6, 12, 12)
        
        # Texto de estado
        painter.setPen(text_color)
        font = QFont("Segoe UI", 14, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(45, circle_y - 8, self.status_text)
        
        # Texto de hora (más pequeño)
        if self.is_active:
            font = QFont("Segoe UI", 11)
            painter.setFont(font)
            painter.setPen(QColor(97, 97, 97))
            painter.drawText(45, circle_y + 10, f"Apagado programado: {self.time_text}")

class MaterialTimeEdit(QWidget):
    """Selector de tiempo estilo Material Design"""
    
    timeChanged = pyqtSignal(QTime)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_time = QTime(20, 0)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Frame contenedor
        self.time_frame = QFrame()
        self.time_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                padding: 15px;
            }
            QFrame:focus-within {
                border: 2px solid #4CAF50;
            }
        """)
        
        frame_layout = QHBoxLayout(self.time_frame)
        frame_layout.setSpacing(15)
        
        # Selector de hora
        self.hour_edit = QTimeEdit()
        self.hour_edit.setTime(self.current_time)
        self.hour_edit.setDisplayFormat("hh:mm")
        self.hour_edit.setButtonSymbols(QTimeEdit.ButtonSymbols.UpDownArrows)
        self.hour_edit.timeChanged.connect(self.on_time_changed)
        
        self.hour_edit.setStyleSheet("""
            QTimeEdit {
                background: transparent;
                border: none;
                color: #2e2e2e;
                font-size: 24px;
                font-weight: 600;
                font-family: 'Segoe UI', Arial;
                padding: 5px 10px;
                min-width: 120px;
            }
            QTimeEdit::up-button {
                background: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 6px;
                width: 25px;
                margin: 2px;
            }
            QTimeEdit::down-button {
                background: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 6px;
                width: 25px;
                margin: 2px;
            }
            QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {
                background: #4CAF50;
                border-color: #4CAF50;
            }
            QTimeEdit::up-arrow {
                width: 12px;
                height: 12px;
            }
            QTimeEdit::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)
        
        frame_layout.addWidget(self.hour_edit)
        layout.addWidget(self.time_frame)
        
    def on_time_changed(self, time):
        self.current_time = time
        self.timeChanged.emit(time)
        
    def time(self):
        return self.current_time
        
    def setTime(self, time):
        self.current_time = time
        self.hour_edit.setTime(time)

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
            "skip_today": False,
            "last_updated": datetime.datetime.now().isoformat()
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
                self.save_config(default_config)
                return default_config
        except Exception as e:
            self.log(f"Error cargando configuración: {e}")
            return default_config
    
    def save_config(self, config):
        """Guarda la configuración en archivo"""
        try:
            config["last_updated"] = datetime.datetime.now().isoformat()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.log("Configuración guardada exitosamente")
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
                
                # Esperar 30 segundos antes de la siguiente verificación (más responsivo)
                for _ in range(30):
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
    """Interfaz gráfica principal con diseño Material"""
    
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
        self.setFixedSize(480, 720)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Layout principal
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Contenedor principal con Material Card
        self.card_container = MaterialCard()
        container_layout = QVBoxLayout(self.card_container)
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setSpacing(25)
        
        # Header con título y controles
        header_layout = QHBoxLayout()
        
        # Título
        title = QLabel("Auto Shutdown")
        title.setStyleSheet("""
            QLabel {
                color: #1a1a1a;
                font-size: 24px;
                font-weight: 700;
                font-family: 'Segoe UI', Arial;
                background: transparent;
            }
        """)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Botones de control
        self.minimize_btn = QPushButton("−")
        self.close_btn = QPushButton("×")
        
        control_style = """
            QPushButton {
                background: #f5f5f5;
                border: none;
                border-radius: 16px;
                color: #666;
                font-size: 16px;
                font-weight: bold;
                width: 32px;
                height: 32px;
            }
            QPushButton:hover {
                background: #e0e0e0;
                color: #333;
            }
        """
        
        self.minimize_btn.setStyleSheet(control_style)
        self.close_btn.setStyleSheet(control_style)
        self.minimize_btn.clicked.connect(self.hide)
        self.close_btn.clicked.connect(self.close)
        
        header_layout.addWidget(self.minimize_btn)
        header_layout.addWidget(self.close_btn)
        
        # Subtítulo
        subtitle = QLabel("Programación de apagado automático")
        subtitle.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 14px;
                font-family: 'Segoe UI', Arial;
                background: transparent;
                margin-bottom: 10px;
            }
        """)
        
        # Indicador de estado
        self.status_indicator = StatusIndicator()
        
        # Switch activar/desactivar estilo Material
        switch_layout = QHBoxLayout()
        switch_label = QLabel("Activar apagado automático")
        switch_label.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 16px;
                font-weight: 500;
                font-family: 'Segoe UI', Arial;
            }
        """)
        
        self.enabled_checkbox = QCheckBox()
        self.enabled_checkbox.setChecked(True)
        self.enabled_checkbox.stateChanged.connect(self.on_enabled_changed)
        self.enabled_checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 3px;
                border: 2px solid #ddd;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #4CAF50;
                border: 2px solid #4CAF50;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
            QCheckBox::indicator:hover {
                border: 2px solid #4CAF50;
            }
        """)
        
        switch_layout.addWidget(switch_label)
        switch_layout.addStretch()
        switch_layout.addWidget(self.enabled_checkbox)
        
        # Selector de hora
        time_section = QVBoxLayout()
        time_label = QLabel("Hora de apagado")
        time_label.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 16px;
                font-weight: 500;
                font-family: 'Segoe UI', Arial;
                margin-bottom: 8px;
            }
        """)
        
        self.time_edit = MaterialTimeEdit()
        self.time_edit.timeChanged.connect(self.on_time_changed)
        
        time_section.addWidget(time_label)
        time_section.addWidget(self.time_edit)
        
        # Botones de acción con estilo Material
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(12)
        
        # Botón postponer
        self.postpone_btn = QPushButton("🕐  Postponer 2 horas")
        self.postpone_btn.clicked.connect(self.postpone_shutdown)
        
        # Botón saltar hoy
        self.skip_btn = QPushButton("⏭️  Saltar hoy")
        self.skip_btn.clicked.connect(self.skip_today)
        
        # Botón cancelar apagado
        self.cancel_btn = QPushButton("❌  Cancelar apagado")
        self.cancel_btn.clicked.connect(self.cancel_shutdown)
        
        # Estilo Material para botones
        button_style = """
            QPushButton {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                color: #333;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Segoe UI', Arial;
                padding: 16px 20px;
                text-align: left;
                min-height: 20px;
            }
            QPushButton:hover {
                background: #f8f9fa;
                border: 1px solid #4CAF50;
                color: #4CAF50;
            }
            QPushButton:pressed {
                background: #e8f5e8;
            }
        """
        
        self.postpone_btn.setStyleSheet(button_style)
        self.skip_btn.setStyleSheet(button_style)
        self.cancel_btn.setStyleSheet(button_style)
        
        buttons_layout.addWidget(self.postpone_btn)
        buttons_layout.addWidget(self.skip_btn)
        buttons_layout.addWidget(self.cancel_btn)
        
        # Agregar todo al contenedor
        container_layout.addLayout(header_layout)
        container_layout.addWidget(subtitle)
        container_layout.addWidget(self.status_indicator)
        container_layout.addLayout(switch_layout)
        container_layout.addLayout(time_section)
        container_layout.addLayout(buttons_layout)
        container_layout.addStretch()
        
        layout.addWidget(self.card_container)
        
        # Fondo con gradiente Material
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(100, 181, 246, 0.1),
                    stop:0.5 rgba(129, 199, 132, 0.1),
                    stop:1 rgba(174, 213, 129, 0.1));
            }
        """)
        
    def setup_tray(self):
        """Configura el icono en la bandeja del sistema (SIN CAMBIOS)"""
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
        
        # Actualizar checkbox y estado visual INMEDIATAMENTE
        self.enabled_checkbox.setChecked(config["enabled"])
        
        time_parts = config["shutdown_time"].split(":")
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        self.time_edit.setTime(QTime(hour, minute))
        
        # Actualizar indicador visual inmediatamente
        self.update_status_display(config)
        
    def update_status_display(self, config=None):
        """Actualiza el display de estado inmediatamente"""
        if not config:
            config = self.service.load_config()
        
        is_active = config["enabled"]
        status_text = "Activo" if is_active else "Desactivado"
        time_text = config["shutdown_time"]
        
        self.status_indicator.set_status(is_active, status_text, time_text)
        
    def start_service(self):
        """Inicia el servicio de apagado"""
        self.service.status_changed.connect(self.update_status)
        self.service.shutdown_triggered.connect(self.on_shutdown_triggered)
        self.service.start()
        
    def update_status(self, status):
        """Actualiza el estado mostrado"""
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
        """Cuando se cambia el estado activado/desactivado - CAMBIO INSTANTÁNEO"""
        config = self.service.load_config()
        config["enabled"] = self.enabled_checkbox.isChecked()
        self.service.save_config(config)
        
        # ACTUALIZAR VISUAL INMEDIATAMENTE
        self.update_status_display(config)
        
    def on_time_changed(self, time):
        """Cuando se cambia la hora - ACTUALIZACIÓN INSTANTÁNEA"""
        config = self.service.load_config()
        config["shutdown_time"] = time.toString("hh:mm")
        self.service.save_config(config)
        
        # ACTUALIZAR VISUAL INMEDIATAMENTE
        self.update_status_display(config)
        
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