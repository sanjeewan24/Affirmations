"""
Affirmation Manifestation System
Complete system with auto-startup, system tray, and dashboard
"""

import sys
import json
import os
from datetime import datetime, timedelta, time
from pathlib import Path
import threading
import speech_recognition as sr
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QPushButton, QProgressBar, QHBoxLayout,
                             QMessageBox, QDialog, QTextEdit, QSystemTrayIcon,
                             QMenu, QLineEdit, QSpinBox, QTimeEdit, QTabWidget,
                             QListWidget, QListWidgetItem, QCheckBox, QGroupBox,
                             QFormLayout, QColorDialog, QComboBox, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QTime, QSettings
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QPainter, QAction

# Default affirmations - CUSTOMIZE THESE TO YOUR NEEDS
DEFAULT_AFFIRMATIONS = {
    "morning": [
        "Today, I am focused, energized, and ready to achieve my goals.",
        "I am capable of overcoming any challenge that comes my way.",
        "My mind is clear, and my actions are purposeful.",
        "I attract success and abundance into my life.",
        "Every step I take today brings me closer to my dreams."
    ],
    "night": [
        "I am grateful for all the good things that happened today.",
        "I release all stress and tension from my body and mind.",
        "I am proud of my progress and the effort I put in today.",
        "I trust in my journey and embrace tomorrow with confidence.",
        "I rest peacefully, knowing I am becoming my best self."
    ]
}

# Default keywords for voice recognition - CUSTOMIZE BASED ON YOUR AFFIRMATIONS
DEFAULT_KEYWORDS = {
    0: ["focused", "energized", "ready", "goals"],
    1: ["capable", "overcoming", "challenge"],
    2: ["mind", "clear", "actions", "purposeful"],
    3: ["attract", "success", "abundance"],
    4: ["step", "closer", "dreams"],
    5: ["grateful", "good", "things", "today"],
    6: ["release", "stress", "tension"],
    7: ["proud", "progress", "effort"],
    8: ["trust", "journey", "confidence"],
    9: ["rest", "peacefully", "best", "self"]
}


class ConfigManager:
    """Manage application configuration"""
    def __init__(self):
        self.config_file = Path.home() / ".affirmation_config.json"
        self.history_file = Path.home() / ".affirmation_history.json"
        self.config = self.load_config()
        self.history = self.load_history()
    
    def load_config(self):
        """Load configuration from file"""
        default_config = {
            "affirmations": DEFAULT_AFFIRMATIONS,
            "keywords": DEFAULT_KEYWORDS,
            "night_time": "22:30",
            "auto_startup": True,
            "morning_theme": {
                "bg_color": "#FFF8EB",
                "text_color": "#333333",
                "accent_color": "#FF8C42"
            },
            "night_theme": {
                "bg_color": "#1A2338",
                "text_color": "#E6E6FA",
                "accent_color": "#9B59B6"
            },
            "voice_sensitivity": 2,
            "last_morning_date": None,
            "last_night_date": None
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                loaded = json.load(f)
                default_config.update(loaded)
        
        return default_config
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def load_history(self):
        """Load history from file"""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_history(self):
        """Save history to file"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def add_history_entry(self, affirmation_type, completed, total):
        """Add entry to history"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": affirmation_type,
            "completed": completed,
            "total": total
        }
        self.history.append(entry)
        self.save_history()
    
    def should_show_morning(self):
        """Check if morning affirmations should be shown"""
        today = datetime.now().date().isoformat()
        last_date = self.config.get("last_morning_date")
        return last_date != today
    
    def should_show_night(self):
        """Check if night affirmations should be shown"""
        today = datetime.now().date().isoformat()
        last_date = self.config.get("last_night_date")
        return last_date != today
    
    def mark_morning_complete(self):
        """Mark morning session as complete"""
        self.config["last_morning_date"] = datetime.now().date().isoformat()
        self.save_config()
    
    def mark_night_complete(self):
        """Mark night session as complete"""
        self.config["last_night_date"] = datetime.now().date().isoformat()
        self.save_config()


class VoiceRecognitionThread(threading.Thread):
    """Thread for voice recognition with improved detection"""
    def __init__(self, callback, keywords, sensitivity, affirmation_text):
        super().__init__(daemon=True)
        self.callback = callback
        self.keywords = keywords
        self.sensitivity = sensitivity
        self.affirmation_text = affirmation_text.lower()
        self.running = True
        self.recognizer = sr.Recognizer()
        # More sensitive settings
        self.recognizer.energy_threshold = 300  # Much more sensitive
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
    
    def run(self):
        try:
            with sr.Microphone() as source:
                print("🎤 Adjusting for ambient noise... Speak normally!")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("✅ Ready! Start speaking the affirmation...")
                
                while self.running:
                    try:
                        # Listen with longer timeout
                        audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=15)
                        
                        try:
                            text = self.recognizer.recognize_google(audio).lower()
                            print(f"📝 Heard: {text}")
                            
                            # Multiple detection methods
                            detected = False
                            
                            # Method 1: Check if keywords present
                            keyword_matches = sum(1 for kw in self.keywords if kw.lower() in text)
                            if keyword_matches >= self.sensitivity:
                                detected = True
                                print(f"✅ Keyword match! ({keyword_matches} keywords found)")
                            
                            # Method 2: Check word overlap with affirmation (more lenient)
                            affirmation_words = set(self.affirmation_text.split())
                            spoken_words = set(text.split())
                            common_words = affirmation_words.intersection(spoken_words)
                            
                            # Remove common filler words
                            filler = {'the', 'a', 'an', 'is', 'are', 'am', 'my', 'i', 'me', 'and', 'or', 'to'}
                            meaningful_common = common_words - filler
                            
                            overlap_ratio = len(meaningful_common) / max(len(affirmation_words - filler), 1)
                            
                            if overlap_ratio >= 0.4:  # 40% word match is good enough
                                detected = True
                                print(f"✅ Word overlap match! ({overlap_ratio*100:.0f}% similarity)")
                            
                            # Method 3: Just detect any speech (fallback for very long affirmations)
                            if len(text.split()) >= 5:  # Spoke at least 5 words
                                # Check if at least one keyword is present
                                if keyword_matches >= 1:
                                    detected = True
                                    print(f"✅ Speech detected with keyword!")
                            
                            if detected:
                                self.callback(True, text)
                        
                        except sr.UnknownValueError:
                            print("❓ Could not understand audio, try again...")
                            self.callback(False, "Could not understand")
                        except sr.RequestError as e:
                            print(f"❌ Recognition service error: {e}")
                            self.callback(False, f"Service error: {e}")
                    
                    except sr.WaitTimeoutError:
                        # Just waiting for speech, this is normal
                        continue
                    except Exception as e:
                        print(f"⚠️ Error: {e}")
                        continue
        except Exception as e:
            print(f"❌ Microphone error: {e}")
            self.callback(False, f"Microphone error: {e}")
    
    def stop(self):
        self.running = False


class AffirmationWindow(QMainWindow):
    """Main affirmation display window"""
    voice_recognized = pyqtSignal(bool, str)
    
    def __init__(self, config_manager, affirmation_type, forced=True):
        super().__init__()
        self.config_manager = config_manager
        self.affirmation_type = affirmation_type
        self.forced = forced
        self.current_index = 0
        self.affirmations = config_manager.config["affirmations"][affirmation_type]
        self.voice_thread = None
        
        self.init_ui()
        self.update_display()
        self.start_voice_recognition()
        
        self.voice_recognized.connect(self.on_voice_recognized)
    
    def init_ui(self):
        self.setWindowTitle("Affirmation Manifestation")
        
        # Remove window frame if forced
        if self.forced:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        self.showFullScreen()
        
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(30)
        
        # Emergency exit button (top right)
        if self.forced:
            emergency_layout = QHBoxLayout()
            emergency_layout.addStretch()
            
            self.emergency_btn = QPushButton("⚠")
            self.emergency_btn.setFixedSize(40, 40)
            self.emergency_btn.setToolTip("Emergency Exit (Ctrl+Alt+Shift+Q)")
            self.emergency_btn.clicked.connect(self.emergency_exit)
            self.emergency_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(231, 76, 60, 0.7);
                    border: none;
                    border-radius: 20px;
                    color: white;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background-color: rgba(231, 76, 60, 1.0);
                }
            """)
            emergency_layout.addWidget(self.emergency_btn)
            main_layout.addLayout(emergency_layout)
        
        # Title
        self.title_label = QLabel()
        self.title_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if self.affirmation_type == "morning":
            self.title_label.setText("🌅 Morning Affirmations")
        else:
            self.title_label.setText("🌙 Night Affirmations")
        
        main_layout.addWidget(self.title_label)
        
        # Progress
        self.progress_label = QLabel()
        self.progress_label.setFont(QFont("Arial", 16))
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.progress_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(10)
        main_layout.addWidget(self.progress_bar)
        
        main_layout.addStretch()
        
        # Affirmation text
        self.affirmation_label = QLabel()
        self.affirmation_label.setFont(QFont("Arial", 32, QFont.Weight.Normal))
        self.affirmation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.affirmation_label.setWordWrap(True)
        main_layout.addWidget(self.affirmation_label)
        
        # Status label
        self.status_label = QLabel("🎤 Speak the affirmation out loud")
        self.status_label.setFont(QFont("Arial", 18))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        main_layout.addStretch()
        
        central.setLayout(main_layout)
        
        # Apply theme
        self.apply_theme()
    
    def apply_theme(self):
        """Apply color theme"""
        if self.affirmation_type == "morning":
            theme = self.config_manager.config["morning_theme"]
        else:
            theme = self.config_manager.config["night_theme"]
        
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(theme["bg_color"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(theme["text_color"]))
        self.setPalette(palette)
        
        self.title_label.setStyleSheet(f"color: {theme['accent_color']};")
        self.affirmation_label.setStyleSheet(f"color: {theme['text_color']};")
        self.status_label.setStyleSheet(f"color: {theme['text_color']};")
        
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {theme['accent_color']};
                border-radius: 5px;
                background-color: {theme['bg_color']};
            }}
            QProgressBar::chunk {{
                background-color: {theme['accent_color']};
            }}
        """)
    
    def update_display(self):
        """Update display"""
        if self.current_index < len(self.affirmations):
            self.affirmation_label.setText(self.affirmations[self.current_index])
            self.progress_label.setText(f"Affirmation {self.current_index + 1} of {len(self.affirmations)}")
            progress = int((self.current_index / len(self.affirmations)) * 100)
            self.progress_bar.setValue(progress)
        else:
            self.complete_session()
    
    def start_voice_recognition(self):
        """Start voice recognition"""
        offset = 0 if self.affirmation_type == "morning" else len(self.config_manager.config["affirmations"]["morning"])
        keywords = self.config_manager.config["keywords"].get(str(self.current_index + offset), [])
        
        if self.voice_thread and self.voice_thread.is_alive():
            self.voice_thread.stop()
            self.voice_thread.join(timeout=1)
        
        sensitivity = self.config_manager.config.get("voice_sensitivity", 2)
        current_affirmation = self.affirmations[self.current_index]
        
        self.voice_thread = VoiceRecognitionThread(
            lambda success, text: self.voice_recognized.emit(success, text),
            keywords,
            sensitivity,
            current_affirmation  # Pass the full affirmation text
        )
        self.voice_thread.start()
    
    def on_voice_recognized(self, success, text):
        """Handle voice recognition"""
        if success:
            self.status_label.setText(f"✅ Great! Moving to next...")
            self.status_label.setStyleSheet("color: #27AE60; font-weight: bold; font-size: 20px;")
            QTimer.singleShot(1500, self.next_affirmation)
        else:
            # Show what was heard
            if "error" in text.lower():
                self.status_label.setText(f"⚠️ {text}")
                self.status_label.setStyleSheet("color: #E74C3C; font-size: 16px;")
            else:
                self.status_label.setText(f"❓ Didn't catch that. Try again!")
                self.status_label.setStyleSheet("color: #F39C12; font-size: 16px;")
            
            # Reset status after 2 seconds
            QTimer.singleShot(2000, self.reset_status)
    
    def next_affirmation(self):
        """Move to next affirmation"""
        self.current_index += 1
        
        if self.current_index < len(self.affirmations):
            self.update_display()
            self.start_voice_recognition()
            self.reset_status()
        else:
            self.complete_session()
    
    def reset_status(self):
        """Reset status label to default"""
        if self.affirmation_type == "morning":
            self.status_label.setStyleSheet("color: #7F8C8D;")
        else:
            self.status_label.setStyleSheet("color: #BDC3C7;")
        self.status_label.setText("🎤 Speak the affirmation out loud (speak naturally)")
    
    def complete_session(self):
        """Complete session"""
        if self.voice_thread:
            self.voice_thread.stop()
        
        self.config_manager.add_history_entry(
            self.affirmation_type,
            len(self.affirmations),
            len(self.affirmations)
        )
        
        if self.affirmation_type == "morning":
            self.config_manager.mark_morning_complete()
        else:
            self.config_manager.mark_night_complete()
        
        QMessageBox.information(
            self,
            "Session Complete! 🎉",
            f"Congratulations! You've completed all {len(self.affirmations)} affirmations."
        )
        
        self.close()
    
    def emergency_exit(self):
        """Emergency exit"""
        reply = QMessageBox.warning(
            self,
            "Emergency Exit",
            "Are you sure you need to exit?\n\nYour progress will be saved but session will be marked incomplete.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.voice_thread:
                self.voice_thread.stop()
            
            if self.current_index > 0:
                self.config_manager.add_history_entry(
                    self.affirmation_type,
                    self.current_index,
                    len(self.affirmations)
                )
            
            self.close()
    
    def keyPressEvent(self, event):
        """Handle key press"""
        # Emergency exit combination: Ctrl+Alt+Shift+Q
        if (event.modifiers() == (Qt.KeyboardModifier.ControlModifier | 
                                   Qt.KeyboardModifier.AltModifier | 
                                   Qt.KeyboardModifier.ShiftModifier) and
            event.key() == Qt.Key.Key_Q):
            self.emergency_exit()


class DashboardWindow(QMainWindow):
    """Dashboard for configuration"""
    def __init__(self, config_manager, tray_app=None):
        super().__init__()
        self.config_manager = config_manager
        self.tray_app = tray_app
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Affirmation Dashboard")
        self.setMinimumSize(900, 700)
        
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("⚙️ Affirmation Dashboard")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Tabs
        tabs = QTabWidget()
        
        tabs.addTab(self.create_affirmations_tab(), "📝 Affirmations")
        tabs.addTab(self.create_settings_tab(), "⚙️ Settings")
        tabs.addTab(self.create_history_tab(), "📊 History")
        tabs.addTab(self.create_about_tab(), "ℹ️ About")
        
        layout.addWidget(tabs)
        
        # Bottom buttons
        btn_layout = QHBoxLayout()
        
        test_btn = QPushButton("🧪 Test Voice Recognition")
        test_btn.setFont(QFont("Arial", 12))
        test_btn.setFixedHeight(50)
        test_btn.clicked.connect(self.test_voice_recognition)
        btn_layout.addWidget(test_btn)
        
        save_btn = QPushButton("💾 Save All Changes")
        save_btn.setFont(QFont("Arial", 14))
        save_btn.setFixedHeight(50)
        save_btn.clicked.connect(self.save_all)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
        central.setLayout(layout)
    
    def test_voice_recognition(self):
        """Test voice recognition with a sample affirmation"""
        reply = QMessageBox.question(
            self,
            "Test Voice Recognition",
            "This will test the voice recognition system.\n\n"
            "Choose which affirmation set to test:",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if self.tray_app:
            if reply == QMessageBox.StandardButton.Yes:
                self.tray_app.show_affirmations("morning", False)
            else:
                self.tray_app.show_affirmations("night", False)
    
    def create_affirmations_tab(self):
        """Create affirmations editing tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Morning affirmations
        morning_group = QGroupBox("🌅 Morning Affirmations")
        morning_layout = QVBoxLayout()
        
        self.morning_list = QListWidget()
        for aff in self.config_manager.config["affirmations"]["morning"]:
            self.morning_list.addItem(aff)
        morning_layout.addWidget(self.morning_list)
        
        morning_btn_layout = QHBoxLayout()
        add_morning_btn = QPushButton("Add")
        edit_morning_btn = QPushButton("Edit")
        delete_morning_btn = QPushButton("Delete")
        
        add_morning_btn.clicked.connect(lambda: self.add_affirmation("morning"))
        edit_morning_btn.clicked.connect(lambda: self.edit_affirmation("morning"))
        delete_morning_btn.clicked.connect(lambda: self.delete_affirmation("morning"))
        
        morning_btn_layout.addWidget(add_morning_btn)
        morning_btn_layout.addWidget(edit_morning_btn)
        morning_btn_layout.addWidget(delete_morning_btn)
        morning_layout.addLayout(morning_btn_layout)
        
        morning_group.setLayout(morning_layout)
        layout.addWidget(morning_group)
        
        # Night affirmations
        night_group = QGroupBox("🌙 Night Affirmations")
        night_layout = QVBoxLayout()
        
        self.night_list = QListWidget()
        for aff in self.config_manager.config["affirmations"]["night"]:
            self.night_list.addItem(aff)
        night_layout.addWidget(self.night_list)
        
        night_btn_layout = QHBoxLayout()
        add_night_btn = QPushButton("Add")
        edit_night_btn = QPushButton("Edit")
        delete_night_btn = QPushButton("Delete")
        
        add_night_btn.clicked.connect(lambda: self.add_affirmation("night"))
        edit_night_btn.clicked.connect(lambda: self.edit_affirmation("night"))
        delete_night_btn.clicked.connect(lambda: self.delete_affirmation("night"))
        
        night_btn_layout.addWidget(add_night_btn)
        night_btn_layout.addWidget(edit_night_btn)
        night_btn_layout.addWidget(delete_night_btn)
        night_layout.addLayout(night_btn_layout)
        
        night_group.setLayout(night_layout)
        layout.addWidget(night_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_settings_tab(self):
        """Create settings tab"""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        
        layout = QVBoxLayout()
        
        # Night time setting
        time_group = QGroupBox("⏰ Schedule Settings")
        time_layout = QFormLayout()
        
        self.night_time_edit = QTimeEdit()
        time_parts = self.config_manager.config["night_time"].split(":")
        self.night_time_edit.setTime(QTime(int(time_parts[0]), int(time_parts[1])))
        time_layout.addRow("Night Session Time:", self.night_time_edit)
        
        time_group.setLayout(time_layout)
        layout.addWidget(time_group)
        
        # Voice settings
        voice_group = QGroupBox("🎤 Voice Recognition Settings")
        voice_layout = QFormLayout()
        
        self.sensitivity_spin = QSpinBox()
        self.sensitivity_spin.setMinimum(1)
        self.sensitivity_spin.setMaximum(5)
        self.sensitivity_spin.setValue(self.config_manager.config.get("voice_sensitivity", 2))
        voice_layout.addRow("Keyword Sensitivity (1-5):", self.sensitivity_spin)
        
        sensitivity_help = QLabel("Lower = easier to trigger (1 keyword match)\nHigher = stricter (more keywords needed)")
        sensitivity_help.setStyleSheet("color: gray; font-size: 11px;")
        voice_layout.addRow("", sensitivity_help)
        
        voice_group.setLayout(voice_layout)
        layout.addWidget(voice_group)
        
        # Auto-startup
        startup_group = QGroupBox("🚀 Startup Settings")
        startup_layout = QVBoxLayout()
        
        self.auto_startup_check = QCheckBox("Launch on system startup")
        self.auto_startup_check.setChecked(self.config_manager.config.get("auto_startup", True))
        startup_layout.addWidget(self.auto_startup_check)
        
        startup_group.setLayout(startup_layout)
        layout.addWidget(startup_group)
        
        # Reset buttons
        reset_group = QGroupBox("🔄 Reset Options")
        reset_layout = QVBoxLayout()
        
        reset_today_btn = QPushButton("Reset Today's Sessions")
        reset_today_btn.clicked.connect(self.reset_today_sessions)
        reset_layout.addWidget(reset_today_btn)
        
        reset_history_btn = QPushButton("Clear All History")
        reset_history_btn.clicked.connect(self.clear_history)
        reset_layout.addWidget(reset_history_btn)
        
        reset_defaults_btn = QPushButton("Restore Default Affirmations")
        reset_defaults_btn.clicked.connect(self.restore_defaults)
        reset_layout.addWidget(reset_defaults_btn)
        
        reset_group.setLayout(reset_layout)
        layout.addWidget(reset_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        
        return scroll
    
    def create_history_tab(self):
        """Create history tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Stats
        stats_label = QLabel()
        stats_label.setFont(QFont("Arial", 12))
        
        streak = self.calculate_streak()
        total_sessions = len(self.config_manager.history)
        completed_sessions = sum(1 for h in self.config_manager.history if h["completed"] == h["total"])
        
        stats_text = f"""
        📊 Statistics:
        • Current Streak: {streak} days
        • Total Sessions: {total_sessions}
        • Completed Sessions: {completed_sessions}
        • Completion Rate: {(completed_sessions/total_sessions*100 if total_sessions > 0 else 0):.1f}%
        """
        
        stats_label.setText(stats_text)
        layout.addWidget(stats_label)
        
        # History list
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setPlainText(self.format_history())
        layout.addWidget(self.history_text)
        
        widget.setLayout(layout)
        return widget
    
    def create_about_tab(self):
        """Create about tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        about_text = QLabel("""
        <h2>Affirmation Manifestation System</h2>
        <p><b>Version:</b> 2.0</p>
        <p><b>Purpose:</b> Help you manifest your goals through daily affirmations</p>
        
        <h3>How It Works:</h3>
        <ul>
            <li>Morning affirmations appear automatically when you boot your device</li>
            <li>Night affirmations appear at your scheduled time (default 10:30 PM)</li>
            <li>Speak each affirmation out loud to progress</li>
            <li>Build consistent habits and track your progress</li>
        </ul>
        
        <h3>Emergency Exit:</h3>
        <p>During forced sessions, use <b>Ctrl+Alt+Shift+Q</b> for emergency exit</p>
        
        <h3>Tips:</h3>
        <ul>
            <li>Speak clearly and with intention</li>
            <li>Find a quiet environment for best recognition</li>
            <li>Stay consistent - daily practice brings results</li>
            <li>Customize affirmations to match your personal goals</li>
        </ul>
        """)
        
        about_text.setWordWrap(True)
        about_text.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(about_text)
        
        widget.setLayout(layout)
        return widget
    
    def add_affirmation(self, aff_type):
        """Add new affirmation"""
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "Add Affirmation", "Enter new affirmation:")
        if ok and text:
            if aff_type == "morning":
                self.morning_list.addItem(text)
            else:
                self.night_list.addItem(text)
    
    def edit_affirmation(self, aff_type):
        """Edit selected affirmation"""
        from PyQt6.QtWidgets import QInputDialog
        list_widget = self.morning_list if aff_type == "morning" else self.night_list
        current_item = list_widget.currentItem()
        
        if current_item:
            text, ok = QInputDialog.getText(
                self, "Edit Affirmation", 
                "Edit affirmation:", 
                text=current_item.text()
            )
            if ok and text:
                current_item.setText(text)
    
    def delete_affirmation(self, aff_type):
        """Delete selected affirmation"""
        list_widget = self.morning_list if aff_type == "morning" else self.night_list
        current_row = list_widget.currentRow()
        
        if current_row >= 0:
            reply = QMessageBox.question(
                self, "Delete Affirmation",
                "Are you sure you want to delete this affirmation?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                list_widget.takeItem(current_row)
    
    def save_all(self):
        """Save all configuration"""
        # Save affirmations
        morning_affs = []
        for i in range(self.morning_list.count()):
            morning_affs.append(self.morning_list.item(i).text())
        
        night_affs = []
        for i in range(self.night_list.count()):
            night_affs.append(self.night_list.item(i).text())
        
        self.config_manager.config["affirmations"]["morning"] = morning_affs
        self.config_manager.config["affirmations"]["night"] = night_affs
        
        # Save time
        time = self.night_time_edit.time()
        self.config_manager.config["night_time"] = f"{time.hour():02d}:{time.minute():02d}"
        
        # Save voice sensitivity
        self.config_manager.config["voice_sensitivity"] = self.sensitivity_spin.value()
        
        # Save auto-startup
        self.config_manager.config["auto_startup"] = self.auto_startup_check.isChecked()
        
        self.config_manager.save_config()
        
        QMessageBox.information(self, "Saved", "All settings saved successfully!")
    
    def reset_today_sessions(self):
        """Reset today's sessions"""
        reply = QMessageBox.question(
            self, "Reset Sessions",
            "This will allow you to do today's affirmations again. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager.config["last_morning_date"] = None
            self.config_manager.config["last_night_date"] = None
            self.config_manager.save_config()
            QMessageBox.information(self, "Reset", "Today's sessions have been reset!")
    
    def clear_history(self):
        """Clear all history"""
        reply = QMessageBox.warning(
            self, "Clear History",
            "This will permanently delete all history. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager.history = []
            self.config_manager.save_history()
            self.history_text.setPlainText("History cleared.")
            QMessageBox.information(self, "Cleared", "History has been cleared!")
    
    def restore_defaults(self):
        """Restore default affirmations"""
        reply = QMessageBox.question(
            self, "Restore Defaults",
            "This will restore the original affirmations. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager.config["affirmations"] = DEFAULT_AFFIRMATIONS.copy()
            self.config_manager.config["keywords"] = DEFAULT_KEYWORDS.copy()
            self.config_manager.save_config()
            
            # Refresh lists
            self.morning_list.clear()
            for aff in DEFAULT_AFFIRMATIONS["morning"]:
                self.morning_list.addItem(aff)
            
            self.night_list.clear()
            for aff in DEFAULT_AFFIRMATIONS["night"]:
                self.night_list.addItem(aff)
            
            QMessageBox.information(self, "Restored", "Default affirmations restored!")
    
    def calculate_streak(self):
        """Calculate current streak"""
        if not self.config_manager.history:
            return 0
        
        dates = set()
        for entry in self.config_manager.history:
            if entry["completed"] == entry["total"]:
                dt = datetime.fromisoformat(entry["timestamp"])
                dates.add(dt.date())
        
        if not dates:
            return 0
        
        sorted_dates = sorted(dates, reverse=True)
        streak = 1
        current_date = sorted_dates[0]
        
        for date in sorted_dates[1:]:
            if current_date - date == timedelta(days=1):
                streak += 1
                current_date = date
            else:
                break
        
        return streak
    
    def format_history(self):
        """Format history for display"""
        if not self.config_manager.history:
            return "No history yet. Start your first session!"
        
        text = "=== RECENT SESSIONS ===\n\n"
        
        for entry in sorted(self.config_manager.history, key=lambda x: x['timestamp'], reverse=True)[:30]:
            dt = datetime.fromisoformat(entry['timestamp'])
            text += f"{dt.strftime('%Y-%m-%d %I:%M %p')}\n"
            text += f"  Type: {entry['type'].title()}\n"
            text += f"  Progress: {entry['completed']}/{entry['total']}\n"
            text += "-" * 50 + "\n"
        
        return text


class SystemTrayApp:
    """Main application with system tray"""
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.config_manager = ConfigManager()
        
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self.create_icon(), self.app)
        self.tray_icon.setToolTip("Affirmation Manifestation")
        
        # Create menu
        menu = QMenu()
        
        dashboard_action = QAction("Open Dashboard", menu)
        dashboard_action.triggered.connect(self.open_dashboard)
        menu.addAction(dashboard_action)
        
        menu.addSeparator()
        
        morning_action = QAction("Practice Morning Affirmations", menu)
        morning_action.triggered.connect(lambda: self.show_affirmations("morning", False))
        menu.addAction(morning_action)
        
        night_action = QAction("Practice Night Affirmations", menu)
        night_action.triggered.connect(lambda: self.show_affirmations("night", False))
        menu.addAction(night_action)
        
        menu.addSeparator()
        
        quit_action = QAction("Quit", menu)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.tray_activated)
        self.tray_icon.show()
        
        # Timer for checking night time
        self.night_timer = QTimer()
        self.night_timer.timeout.connect(self.check_night_time)
        self.night_timer.start(60000)  # Check every minute
        
        # Check if morning session needed
        if self.config_manager.should_show_morning():
            QTimer.singleShot(3000, lambda: self.show_affirmations("morning", True))
        
        self.dashboard_window = None
        self.affirmation_window = None
    
    def create_icon(self):
        """Create system tray icon"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw circle
        painter.setBrush(QColor("#FF8C42"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, 56, 56)
        
        # Draw star
        painter.setBrush(QColor("white"))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "✨")
        
        painter.end()
        
        return QIcon(pixmap)
    
    def tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.open_dashboard()
    
    def open_dashboard(self):
        """Open dashboard window"""
        if self.dashboard_window is None or not self.dashboard_window.isVisible():
            self.dashboard_window = DashboardWindow(self.config_manager, self)
            self.dashboard_window.show()
        else:
            self.dashboard_window.activateWindow()
    
    def show_affirmations(self, aff_type, forced):
        """Show affirmation window"""
        if self.affirmation_window is not None and self.affirmation_window.isVisible():
            return
        
        self.affirmation_window = AffirmationWindow(self.config_manager, aff_type, forced)
        self.affirmation_window.show()
    
    def check_night_time(self):
        """Check if it's time for night affirmations"""
        now = datetime.now().time()
        night_time_str = self.config_manager.config["night_time"]
        time_parts = night_time_str.split(":")
        night_time = time(int(time_parts[0]), int(time_parts[1]))
        
        # Check if current time matches (within 1 minute window)
        if (now.hour == night_time.hour and 
            abs(now.minute - night_time.minute) <= 1 and
            self.config_manager.should_show_night()):
            self.show_affirmations("night", True)
    
    def quit_app(self):
        """Quit application"""
        reply = QMessageBox.question(
            None,
            "Quit Application",
            "Are you sure you want to quit?\n\nThe app won't run in background.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.tray_icon.hide()
            self.app.quit()
    
    def run(self):
        """Run the application"""
        sys.exit(self.app.exec())


def main():
    app = SystemTrayApp()
    app.run()


if __name__ == "__main__":
    main()