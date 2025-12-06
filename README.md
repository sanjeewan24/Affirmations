# 🌟 Affirmation Manifestation System

A powerful desktop application that combines **daily affirmations** with **voice recognition** to help you manifest your goals through mindful repetition and conscious speaking.

## ✨ Features

### 📱 Core Functionality
- **Morning & Night Sessions**: Separate affirmation sets optimized for different times of day
- **Voice Recognition**: Advanced speech-to-text detection with intelligent keyword matching
- **Progress Tracking**: Real-time progress indicators and completion tracking
- **Customizable Affirmations**: Easily add, edit, or delete your personal affirmations
- **History Dashboard**: Track your completion streaks and session statistics

### 🎨 User Experience
- **Immersive Full-Screen Mode**: Distraction-free environment for focused affirmation practice
- **Beautiful Themes**: Separate light theme for morning (warm tones) and dark theme for night (cool tones)
- **System Tray Integration**: Runs silently in background with quick access controls
- **Emergency Exit**: Quick escape with **Ctrl+Alt+Shift+Q** during forced sessions

### ⚙️ Advanced Settings
- **Voice Sensitivity Control**: Adjust keyword detection sensitivity (1-5 levels)
- **Customizable Schedule**: Set your preferred night session time
- **Auto-Startup**: Optionally launch on system startup
- **Persistent Configuration**: All settings saved locally in JSON format

## 🚀 Installation

### Requirements
- Python 3.8 or higher
- Windows, macOS, or Linux

### Dependencies
- `PyQt6`: Desktop GUI framework
- `SpeechRecognition`: Voice recognition library
- `pyaudio`: Audio processing for microphone input

## 📖 How to Use

### Starting a Session

1. **Launch the Dashboard**
   ```
   Click the system tray icon or run python affirmation_app.py
   ```

2. **Choose Session Type**
   - Select Morning (🌅) or Night (🌙) affirmations
   - Sessions are tracked daily to prevent duplicates

3. **Speak Your Affirmations**
   - Read each affirmation clearly and naturally
   - The system listens for keywords or word overlap
   - Move to the next affirmation once recognized

### Dashboard Controls

**📝 Affirmations Tab**
- View all current affirmations for morning and night
- Add new affirmations using the "Add" button
- Edit existing affirmations with the "Edit" button
- Delete affirmations with the "Delete" button

**⚙️ Settings Tab**
- Adjust night session time
- Control keyword sensitivity (1-5)
- Enable/disable auto-startup on system boot
- Reset today's sessions or clear history
- Restore default affirmations

**📊 History Tab**
- View your completion streak
- See total sessions and completion rate
- Browse detailed history of all sessions
- Track your manifestation journey

**ℹ️ About Tab**
- Version information
- Quick reference guide
- Emergency exit instructions

## 🎤 Voice Recognition

### How It Works

The system uses **three intelligent detection methods**:

1. **Keyword Matching**: Detects if key words from the affirmation are spoken
2. **Word Overlap**: Checks for semantic similarity (40%+ word match)
3. **Speech Detection**: Ensures meaningful speech was detected

### Sensitivity Levels

| Level | Setting | Best For |
|-------|---------|----------|
| 1 | Very Lenient | Long affirmations, flexible speaking |
| 2 | Balanced (Default) | Most users |
| 3 | Moderate | Stricter keyword matching |
| 4 | Strict | Short affirmations, precise speaking |
| 5 | Very Strict | Single keywords only |

### Tips for Best Results

- **Speak Naturally**: Don't rush or speak unnaturally
- **Clear Environment**: Minimize background noise
- **Adequate Volume**: Speak at conversational volume
- **Face Microphone**: Ensure your microphone is positioned correctly
- **One Affirmation at a Time**: Focus on one affirmation per session

## 📁 Configuration Files

The app stores data in your home directory:

- `~/.affirmation_config.json`: All settings and affirmations
- `~/.affirmation_history.json`: Session history and statistics

### Sample Config Structure

```json
{
  "affirmations": {
    "morning": [...],
    "night": [...]
  },
  "keywords": {...},
  "night_time": "22:30",
  "auto_startup": true,
  "voice_sensitivity": 2,
  "morning_theme": {...},
  "night_theme": {...}
}
```

## 🎨 Customization

### Change Affirmations

1. Open Dashboard → Affirmations tab
2. Click "Add" to create new affirmations
3. Click "Edit" to modify existing ones
4. Changes save automatically

### Customize Themes

Edit `~/.affirmation_config.json` and modify color values:

```json
"morning_theme": {
  "bg_color": "#FFF8EB",
  "text_color": "#333333",
  "accent_color": "#FF8C42"
}
```

## 🔒 Privacy

- **No Internet Required**: Voice recognition uses local processing when possible
- **Local Storage**: All data stored on your machine
- **No Tracking**: No analytics or telemetry
- **Open Source**: Review code anytime

## 🐛 Troubleshooting

### Microphone Not Working
- Check system audio settings
- Ensure PyAudio is properly installed: `pip install pyaudio`
- Try different input devices if available

### Voice Not Detected
- Increase sensitivity in settings (lower number = easier detection)
- Speak more clearly and at normal volume
- Reduce background noise
- Check microphone positioning

### Application Won't Start
- Ensure Python 3.8+ is installed
- Check that `affirmation_app.py` is in correct directory

### Settings Not Saving
- Ensure write permissions to home directory
- Check disk space availability
- Restart the application

## 📊 Statistics & Streaks

Track your manifestation journey:

- **Streak Counter**: Days of consecutive completed sessions
- **Completion Rate**: Percentage of sessions completed vs attempted
- **Session History**: Detailed log of all past sessions
- **Progress Visualization**: See your commitment to personal growth

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+Alt+Shift+Q | Emergency exit (during forced sessions) |
| Alt+Tab | Switch between windows |
| Esc | Close dashboard (not during sessions) |

## 🌟 Pro Tips

1. **Build a Habit**: Use the same time daily for better results
2. **Personalize**: Adjust affirmations to match your goals
3. **Speak Intentionally**: Really feel the words as you speak
4. **Review History**: Check your dashboard weekly for motivation
5. **Progressive Affirmations**: Update affirmations as you achieve goals

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 💡 Feedback & Support

Found a bug? Have a feature request? Open an issue on GitHub!

---

**Remember**: *This app is a tool to support your manifestation journey. Combine it with consistent action, positive thinking, and belief in your goals for maximum impact.* 🌟
