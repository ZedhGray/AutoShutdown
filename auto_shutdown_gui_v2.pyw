#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Shutdown GUI - Google Material Design v2
Diseño moderno estilo Google con UX mejorado
"""
import sys
import json
import os
import time
import datetime
import subprocess
import threading
import winreg
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QTimeEdit, QPushButton, 
                            QCheckBox, QFrame, QSystemTrayIcon, QMenu, 
                            QMessageBox, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect,
                            QGraphicsOpacityEffect)
from PyQt6.QtCore import QTime, QTimer, Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QRectF, QSize, pyqtProperty
from PyQt6.QtGui import QFont, QIcon, QPainter, QPainterPath, QColor, QLinearGradient, QBrush, QRadialGradient, QPixmap

class ModernToggleSwitch(QWidget):
    """Toggle switch moderno estilo iOS/Material You con animaciones suaves"""
    
    toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(56, 32)
        self.is_checked = False
        self.circle_position = 4
        self.bg_color_value = 0  # 0 = gris, 100 = verde
        
        # Animación del círculo
        self.circle_animation = QPropertyAnimation(self, b"circle_pos")
        self.circle_animation.setDuration(200)
        self.circle_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        # Animación del color de fondo
        self.color_animation = QPropertyAnimation(self, b"bg_color")
        self.color_animation.setDuration(200)
        self.color_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
    def setChecked(self, checked, animate=True):
        """Establece el estado del toggle con o sin animación"""
        self.is_checked = checked
        
        # Posiciones y colores objetivo
        target_pos = 28 if checked else 4
        target_color = 100 if checked else 0
        
        if animate:
            # Animar posición del círculo
            self.circle_animation.stop()
            self.circle_animation.setStartValue(self.circle_position)
            self.circle_animation.setEndValue(target_pos)
            self.circle_animation.start()
            
            # Animar color de fondo
            self.color_animation.stop()
            self.color_animation.setStartValue(self.bg_color_value)
            self.color_animation.setEndValue(target_color)
            self.color_animation.start()
        else:
            # Sin animación (para inicialización)
            self.circle_position = target_pos
            self.bg_color_value = target_color
            self.update()
            
    def isChecked(self):
        return self.is_checked
        
    def get_circle_pos(self):
        return self.circle_position
        
    def set_circle_pos(self, pos):
        self.circle_position = pos
        self.update()
        
    def get_bg_color(self):
        return self.bg_color_value
        
    def set_bg_color(self, value):
        self.bg_color_value = value
        self.update()
        
    circle_pos = pyqtProperty(int, fget=get_circle_pos, fset=set_circle_pos)
    bg_color = pyqtProperty(int, fget=get_bg_color, fset=set_bg_color)
    
    def mousePressEvent(self, event):
        self.is_checked = not self.is_checked
        self.setChecked(self.is_checked)
        self.toggled.emit(self.is_checked)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Interpolar color de fondo basado en bg_color_value (0-100)
        # Gris: (189, 189, 189) → Verde: (52, 168, 83)
        progress = self.bg_color_value / 100.0
        
        r = int(189 + (52 - 189) * progress)
        g = int(189 + (168 - 189) * progress)
        b = int(189 + (83 - 189) * progress)
        
        bg_color = QColor(r, g, b)
            
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, 56, 32, 16, 16)
        
        # Circle con sombra
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(int(self.circle_position), 4, 24, 24)

class ModernStatusCard(QWidget):
    """Card de estado moderno estilo Google"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_active = False
        self.status_text = "Desactivado"
        self.time_text = "19:05"
        self.setFixedHeight(140)
        self.setup_ui()
        
    def setup_ui(self):
        # Sombra moderna
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)
        
    def set_status(self, active, status_text, time_text):
        self.is_active = active
        self.status_text = status_text
        self.time_text = time_text
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        
        # Gradiente de fondo según estado
        gradient = QLinearGradient(0, 0, 0, rect.height())
        
        if self.is_active:
            # Verde Google moderno
            gradient.setColorAt(0, QColor(232, 245, 233))
            gradient.setColorAt(1, QColor(200, 230, 201))
            icon_color = QColor(46, 125, 50)
            text_color = QColor(27, 94, 32)
        else:
            # Gris moderno
            gradient.setColorAt(0, QColor(250, 250, 250))
            gradient.setColorAt(1, QColor(245, 245, 245))
            icon_color = QColor(117, 117, 117)
            text_color = QColor(97, 97, 97)
        
        # Fondo con bordes redondeados
        path = QPainterPath()
        rectf = QRectF(rect)
        path.addRoundedRect(rectf, 20.0, 20.0)
        painter.fillPath(path, QBrush(gradient))
        
        # Icono grande
        if self.is_active:
            self.draw_power_icon(painter, 30, 50, icon_color)
        else:
            self.draw_power_off_icon(painter, 30, 50, icon_color)
        
        # Texto principal
        painter.setPen(text_color)
        font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(90, 55, self.status_text)
        
        # Subtexto
        if self.is_active:
            painter.setPen(QColor(97, 97, 97))
            font = QFont("Segoe UI", 13)
            painter.setFont(font)
            painter.drawText(90, 85, f"Programado a las {self.time_text}")
            
    def draw_power_icon(self, painter, x, y, color):
        """Dibuja icono de encendido"""
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))
        # Círculo
        painter.drawEllipse(x, y - 20, 40, 40)
        # Línea de power
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawRect(x + 17, y - 12, 6, 18)
        
    def draw_power_off_icon(self, painter, x, y, color):
        """Dibuja icono de apagado"""
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))
        painter.drawEllipse(x, y - 20, 40, 40)

class ModernButton(QPushButton):
    """Botón moderno estilo Google Material You"""
    
    def __init__(self, text, button_type="secondary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(48)
        self.setup_style()
        
    def setup_style(self):
        if self.button_type == "primary":
            style = """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #34A853, stop:1 #2D8F47);
                    color: white;
                    border: none;
                    border-radius: 24px;
                    font-size: 15px;
                    font-weight: 600;
                    padding: 0 32px;
                    font-family: 'Segoe UI';
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #2D8F47, stop:1 #257A3C);
                }
                QPushButton:pressed {
                    background: #1E6F31;
                }
            """
        elif self.button_type == "secondary":
            style = """
                QPushButton {
                    background: white;
                    color: #5f6368;
                    border: 1px solid #dadce0;
                    border-radius: 24px;
                    font-size: 14px;
                    font-weight: 500;
                    padding: 0 24px;
                    font-family: 'Segoe UI';
                }
                QPushButton:hover {
                    background: #f8f9fa;
                    border-color: #c6c9cc;
                }
                QPushButton:pressed {
                    background: #f1f3f4;
                }
            """
        else:  # text button
            style = """
                QPushButton {
                    background: transparent;
                    color: #1a73e8;
                    border: none;
                    border-radius: 20px;
                    font-size: 14px;
                    font-weight: 600;
                    padding: 0 20px;
                    font-family: 'Segoe UI';
                }
                QPushButton:hover {
                    background: rgba(26, 115, 232, 0.08);
                }
                QPushButton:pressed {
                    background: rgba(26, 115, 232, 0.16);
                }
            """
        self.setStyleSheet(style)

class ModernTimeSelector(QWidget):
    """Selector de tiempo moderno tipo Google Calendar"""
    
    timeChanged = pyqtSignal(QTime)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_time = QTime(19, 5)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Label
        label = QLabel("Hora de apagado")
        label.setStyleSheet("""
            color: #5f6368;
            font-size: 13px;
            font-weight: 500;
            font-family: 'Segoe UI';
        """)
        layout.addWidget(label)
        
        # Contenedor del selector
        selector_container = QFrame()
        selector_container.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #e8eaed;
                border-radius: 16px;
                padding: 4px;
            }
            QFrame:hover {
                border-color: #dadce0;
            }
        """)
        
        container_layout = QHBoxLayout(selector_container)
        container_layout.setContentsMargins(16, 8, 16, 8)
        
        # Time edit moderno
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(self.current_time)
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setButtonSymbols(QTimeEdit.ButtonSymbols.NoButtons)
        self.time_edit.timeChanged.connect(self.on_time_changed)
        
        self.time_edit.setStyleSheet("""
            QTimeEdit {
                background: transparent;
                border: none;
                color: #202124;
                font-size: 32px;
                font-weight: 400;
                font-family: 'Segoe UI', 'Google Sans';
                padding: 8px;
            }
        """)
        
        container_layout.addWidget(self.time_edit)
        container_layout.addStretch()
        
        # Botones de ajuste rápido
        quick_buttons = QWidget()
        quick_layout = QHBoxLayout(quick_buttons)
        quick_layout.setSpacing(8)
        quick_layout.setContentsMargins(0, 0, 0, 0)
        
        btn_minus = QPushButton("−15")
        btn_plus = QPushButton("+15")
        
        for btn in [btn_minus, btn_plus]:
            btn.setFixedSize(60, 36)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: #f1f3f4;
                    color: #5f6368;
                    border: none;
                    border-radius: 18px;
                    font-size: 13px;
                    font-weight: 600;
                    font-family: 'Segoe UI';
                }
                QPushButton:hover {
                    background: #e8eaed;
                }
                QPushButton:pressed {
                    background: #dadce0;
                }
            """)
        
        btn_minus.clicked.connect(lambda: self.adjust_time(-15))
        btn_plus.clicked.connect(lambda: self.adjust_time(15))
        
        quick_layout.addWidget(btn_minus)
        quick_layout.addWidget(btn_plus)
        
        container_layout.addWidget(quick_buttons)
        
        layout.addWidget(selector_container)
        
    def adjust_time(self, minutes):
        """Ajusta el tiempo en minutos"""
        new_time = self.current_time.addSecs(minutes * 60)
        self.setTime(new_time)
        
    def on_time_changed(self, time):
        self.current_time = time
        self.timeChanged.emit(time)
        
    def time(self):
        return self.current_time
        
    def setTime(self, time):
        self.current_time = time
        self.time_edit.setTime(time)

class AutoShutdownService(QThread):
    """Servicio que verifica la hora de apagado en segundo plano"""
    
    status_changed = pyqtSignal(str)
    shutdown_triggered = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.config_file = Path.home() / ".auto_shutdown_config.json"
        
    def load_config(self):
        """Carga la configuración desde archivo"""
        default_config = {
            "enabled": False,
            "shutdown_time": "19:05",
            "postpone_until": None,
            "skip_today": False
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return {**default_config, **config}
        except Exception as e:
            print(f"Error cargando config: {e}")
        
        return default_config
        
    def save_config(self, config):
        """Guarda la configuración en archivo"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error guardando config: {e}")
            
    def run(self):
        """Loop principal del servicio"""
        last_check_date = None
        
        while self.running:
            try:
                config = self.load_config()
                
                # Reset del skip_today a medianoche
                today = datetime.date.today()
                if last_check_date != today:
                    if config.get("skip_today", False):
                        config["skip_today"] = False
                        self.save_config(config)
                    last_check_date = today
                
                if not config["enabled"]:
                    self.status_changed.emit("Desactivado")
                    time.sleep(10)
                    continue
                
                # Verificar postpone
                if config.get("postpone_until"):
                    postpone_time = datetime.datetime.fromisoformat(config["postpone_until"])
                    if datetime.datetime.now() < postpone_time:
                        remaining = postpone_time - datetime.datetime.now()
                        minutes = int(remaining.total_seconds() / 60)
                        self.status_changed.emit(f"Postponido ({minutes} min)")
                        time.sleep(30)
                        continue
                    else:
                        config["postpone_until"] = None
                        self.save_config(config)
                
                # Verificar skip_today
                if config.get("skip_today", False):
                    self.status_changed.emit("Saltado por hoy")
                    time.sleep(30)
                    continue
                
                # Verificar hora de apagado
                now = datetime.datetime.now()
                shutdown_time_str = config["shutdown_time"]
                hour, minute = map(int, shutdown_time_str.split(":"))
                shutdown_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                time_diff = (shutdown_time - now).total_seconds()
                
                if -60 < time_diff <= 0:
                    self.status_changed.emit("¡Apagando!")
                    self.shutdown_triggered.emit()
                    self.execute_shutdown()
                    time.sleep(120)
                elif time_diff > 0:
                    minutes = int(time_diff / 60)
                    if minutes < 60:
                        self.status_changed.emit(f"Activo ({minutes} min)")
                    else:
                        hours = minutes // 60
                        self.status_changed.emit(f"Activo ({hours}h)")
                else:
                    self.status_changed.emit("Activo")
                
                time.sleep(30)
                
            except Exception as e:
                print(f"Error en servicio: {e}")
                time.sleep(30)
                
    def execute_shutdown(self):
        """Ejecuta el comando de apagado"""
        try:
            if os.name == 'nt':
                subprocess.Popen(['shutdown', '/s', '/t', '60'])
            else:
                subprocess.Popen(['shutdown', '-h', '+1'])
        except Exception as e:
            print(f"Error ejecutando apagado: {e}")
            
    def stop(self):
        """Detiene el servicio"""
        self.running = False
        self.wait()

class AutoShutdownGUI(QMainWindow):
    """Ventana principal con diseño moderno estilo Google"""
    
    def __init__(self):
        super().__init__()
        self.service = AutoShutdownService()
        self.setup_ui()
        self.load_settings()
        self.start_service()
        self.setup_tray_icon()
        
    def setup_ui(self):
        """Configura la interfaz"""
        self.setWindowTitle("Auto Shutdown")
        self.setFixedSize(480, 540)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        
        # Layout principal
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)
        
        # Contenedor con fondo
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 24px;
            }
        """)
        
        # Sombra del contenedor
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 60))
        container.setGraphicsEffect(shadow)
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(32, 32, 32, 32)
        container_layout.setSpacing(24)
        
        # Header
        header = self.create_header()
        container_layout.addWidget(header)
        
        # Status Card
        self.status_card = ModernStatusCard()
        container_layout.addWidget(self.status_card)
        
        # Toggle Section
        toggle_section = self.create_toggle_section()
        container_layout.addWidget(toggle_section)
        
        # Divisor
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background: #e8eaed; border: none;")
        container_layout.addWidget(divider)
        
        # Time Selector
        self.time_selector = ModernTimeSelector()
        self.time_selector.timeChanged.connect(self.on_time_changed)
        container_layout.addWidget(self.time_selector)
        
        container_layout.addStretch()
        
        main_layout.addWidget(container)
        
    def create_header(self):
        """Crea el header moderno"""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Título
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)
        
        title = QLabel("Auto Shutdown")
        title.setStyleSheet("""
            color: #202124;
            font-size: 28px;
            font-weight: 600;
            font-family: 'Segoe UI', 'Google Sans';
        """)
        
        subtitle = QLabel("Programación de apagado automático")
        subtitle.setStyleSheet("""
            color: #5f6368;
            font-size: 13px;
            font-weight: 400;
            font-family: 'Segoe UI';
        """)
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # Botones de ventana
        btn_minimize = QPushButton("−")
        btn_close = QPushButton("×")
        
        for btn in [btn_minimize, btn_close]:
            btn.setFixedSize(36, 36)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #5f6368;
                    border: none;
                    border-radius: 18px;
                    font-size: 20px;
                    font-weight: 400;
                }
                QPushButton:hover {
                    background: #f1f3f4;
                }
                QPushButton:pressed {
                    background: #e8eaed;
                }
            """)
        
        btn_minimize.clicked.connect(self.hide)
        btn_close.clicked.connect(self.hide)
        
        layout.addWidget(btn_minimize)
        layout.addWidget(btn_close)
        
        return header
        
    def create_toggle_section(self):
        """Crea la sección del toggle"""
        section = QWidget()
        layout = QHBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        label = QLabel("Activar apagado automático")
        label.setStyleSheet("""
            color: #202124;
            font-size: 15px;
            font-weight: 500;
            font-family: 'Segoe UI';
        """)
        
        # Toggle moderno
        self.toggle_switch = ModernToggleSwitch()
        self.toggle_switch.toggled.connect(self.on_enabled_changed)
        
        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(self.toggle_switch)
        
        return section
        
    def setup_tray_icon(self):
        """Configura el icono de la bandeja"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Crear icono
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Círculo de fondo
        gradient = QRadialGradient(16, 16, 16)
        gradient.setColorAt(0, QColor(66, 133, 244))
        gradient.setColorAt(1, QColor(52, 168, 83))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, 28, 28)
        
        # Texto
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(8, 20, "AS")
        painter.end()
        
        self.tray_icon.setIcon(QIcon(pixmap))
        
        # Menú del tray
        tray_menu = QMenu()
        
        self.tray_status_action = tray_menu.addAction("Estado: Cargando...")
        self.tray_status_action.setEnabled(False)
        
        tray_menu.addSeparator()
        
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
        
        # Inicializar toggle sin animación (primera vez)
        self.toggle_switch.setChecked(config["enabled"], animate=False)
        
        time_parts = config["shutdown_time"].split(":")
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        self.time_selector.setTime(QTime(hour, minute))
        
        # Asegurar que la app esté en inicio automático
        QTimer.singleShot(500, self.ensure_startup)
        
        self.update_status_display(config)
        
    def ensure_startup(self):
        """Asegura que la app esté en inicio automático de Windows"""
        if not self.is_in_startup():
            self.add_to_startup()
        
    def update_status_display(self, config=None):
        """Actualiza el display de estado"""
        if not config:
            config = self.service.load_config()
        
        is_active = config["enabled"]
        status_text = "Activo" if is_active else "Desactivado"
        time_text = config["shutdown_time"]
        
        self.status_card.set_status(is_active, status_text, time_text)
        
    def start_service(self):
        """Inicia el servicio de apagado"""
        self.service.status_changed.connect(self.update_status)
        self.service.shutdown_triggered.connect(self.on_shutdown_triggered)
        self.service.start()
        
    def update_status(self, status):
        """Actualiza el estado mostrado"""
        if hasattr(self, 'tray_status_action'):
            self.tray_status_action.setText(f"Estado: {status}")
        self.tray_icon.setToolTip(f"Auto Shutdown - {status}")
        
    def on_shutdown_triggered(self):
        """Se ejecuta cuando se va a apagar"""
        self.show()
        QMessageBox.warning(self, "Auto Shutdown", 
                          "¡La PC se apagará en 60 segundos!\n\n"
                          "Haz clic en 'Cancelar apagado' si quieres detenerlo.")
        
    def on_enabled_changed(self, state):
        """Cuando se cambia el estado del toggle"""
        config = self.service.load_config()
        config["enabled"] = state
        self.service.save_config(config)
        self.update_status_display(config)
        
    def on_time_changed(self, time):
        """Cuando se cambia la hora"""
        config = self.service.load_config()
        config["shutdown_time"] = time.toString("HH:mm")
        self.service.save_config(config)
        self.update_status_display(config)
        
    def is_in_startup(self):
        """Verifica si la app está en el inicio de Windows"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            winreg.QueryValueEx(key, "AutoShutdown")
            winreg.CloseKey(key)
            return True
        except:
            return False
            
    def add_to_startup(self):
        """Agrega la app al inicio de Windows automáticamente"""
        try:
            app_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
            
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "AutoShutdown", 0, winreg.REG_SZ, f'"{app_path}"')
            winreg.CloseKey(key)
        except Exception as e:
            print(f"No se pudo agregar a inicio automático: {e}")
        
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
            self.show_and_raise()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_and_raise()
                
    def closeEvent(self, event):
        """Maneja el cierre de la ventana"""
        self.hide()
        event.ignore()
        
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
    app.setQuitOnLastWindowClosed(False)
    
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "Auto Shutdown", 
                           "No se puede acceder a la bandeja del sistema.")
        sys.exit(1)
    
    window = AutoShutdownGUI()
    
    window.tray_icon.showMessage(
        "Auto Shutdown",
        "Aplicación iniciada. Haz clic en el icono para configurar.",
        QSystemTrayIcon.MessageIcon.Information,
        3000
    )
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
