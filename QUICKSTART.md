# 🚀 Quick Start Guide

## Overview
Software-AI (Persian Version) is an AI-powered Windows automation system that can control your computer using natural language commands.

## 🎯 What You Can Do

- **Open applications**: "Open Notepad and type Hello"
- **Control browser**: "Open Chrome and go to google.com"
- **System information**: "What's my RAM usage?"
- **Window management**: "Minimize all windows"
- **File operations**: "Create a file named test.txt"
- **Complex tasks**: "Take a screenshot and save it"

## 📋 Prerequisites

- Python 3.13
- Windows 10/11
- API Keys for AI models (Google Gemini, OpenAI, or Groq)

## ⚡ Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/shahincodev/Software-AI-Persian.git
cd Software-AI-Persian
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
Create `.env` file in project root:
```env
# Choose one or more AI providers:

# Google Gemini (recommended)
GEMINI_API_KEY=your_gemini_api_key_here

# OpenAI GPT-4
OPENAI_API_KEY=your_openai_api_key_here

# Groq
GROQ_API_KEY=your_groq_api_key_here
```

**Get API Keys:**
- Gemini: https://makersuite.google.com/app/apikey
- OpenAI: https://platform.openai.com/api-keys
- Groq: https://console.groq.com/keys

### 4. Test System
```bash
python test_system.py
```

You should see:
```
✅ ALL TESTS PASSED (5/5)
🚀 System is ready to use!
```

### 5. Run Application
```bash
# Text mode (type commands)
python main.py --input-mode text

# Voice mode (speak commands)
python main.py --input-mode voice

# Auto mode (AI decides)
python main.py --input-mode auto
```

## 🎮 Usage Examples

### Text Mode
```
Software-AI> Open Notepad and type "Hello from AI!"
✅ Opening Notepad...
✅ Typing text...
Done!

Software-AI> What's my CPU usage?
🖥️ CPU: 45%

Software-AI> Close all Chrome tabs
✅ Terminated 33 Chrome processes
```

### Voice Mode
Just speak naturally:
- "Open calculator"
- "Search Google for Python tutorials"
- "What time is it?"

## 📊 Logging System

All actions are automatically logged for debugging:

```bash
# View recent logs
python tools/log_analyzer.py recent -n 20

# Show only errors
python tools/log_analyzer.py errors

# Search logs
python tools/log_analyzer.py search "notepad"

# View statistics
python tools/log_analyzer.py stats
```

**Log Files Location:** `data/logs/`
- `app.log` - Main application log
- `errors.log` - Errors only
- `user_actions.jsonl` - All user actions
- `ai_interactions.jsonl` - AI requests/responses
- `full_trace.jsonl` - Everything in JSON format
- `session_YYYYMMDD_HHMMSS.jsonl` - Current session
- `error_report_*.txt` - Error summaries

## 🛠️ Troubleshooting

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### API Key Issues
```bash
# Verify .env file exists
ls .env

# Check environment variables
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('GEMINI_API_KEY:', 'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET')"
```

### Permission Errors
Run PowerShell as Administrator:
```powershell
# Allow script execution
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### OCR Not Working
Install Tesseract OCR:
1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to: `C:\Program Files\Tesseract-OCR\`
3. Add to PATH

## 📚 Documentation

- **Main Docs**: `docs/` folder
- **Action Layer**: `docs/WEEK2_QUICK_REFERENCE.md`
- **Desktop Vision**: `docs/DESKTOP_VISION.md`
- **Logging**: `docs/ADVANCED_LOGGING.md`
- **Integration**: `docs/INTEGRATION_GUIDE.md`

## 🎓 Examples

Run example scripts:
```bash
# Keyboard control demo
python examples/keyboard_demo.py

# Mouse control demo
python examples/mouse_demo.py

# Windows automation demo
python examples/windows_automation_demo.py

# Logging system demo
python examples/logging_demo.py
```

## 🔒 Safety Features

- **Action Safety**: Prevents dangerous operations
- **Smart Wait**: Ensures UI readiness
- **Action Recovery**: Automatic retry on failure
- **Logging**: Complete audit trail

## 📈 Performance Tips

1. **Use specific commands**: "Open Chrome" instead of "Open browser"
2. **Wait for completion**: Let actions finish before next command
3. **Check logs**: Review `data/logs/` if issues occur
4. **Use voice mode**: More natural for complex tasks

## 🆘 Getting Help

1. **Check Logs**: `python tools/log_analyzer.py errors`
2. **Run Tests**: `python test_system.py`
3. **Read Docs**: See `docs/` folder
4. **GitHub Issues**: https://github.com/shahincodev/Software-AI-Persian/issues

## 📝 Common Commands

| Command | Description |
|---------|-------------|
| `Open [app]` | Launch application |
| `Close [app]` | Terminate application |
| `Type [text]` | Type text |
| `Click [target]` | Click on screen element |
| `Search [query]` | Web search |
| `System info` | Show system stats |
| `Screenshot` | Take screenshot |
| `Exit` / `Quit` | Close program |

## 🎯 Next Steps

1. Try basic commands in text mode
2. Experiment with voice mode
3. Review logs to understand system behavior
4. Read documentation for advanced features
5. Create custom automation scripts

## 📖 Advanced Features

- **Context Awareness**: Understands current state
- **Multi-Monitor**: Handles multiple displays
- **Action Recovery**: Automatic retry logic
- **Memory System**: Remembers past actions
- **Smart Wait**: Waits for UI elements

## 🔧 Development

Run tests:
```bash
# Unit tests
pytest tests/

# Integration tests
python tests/integration_tests.py

# System validation
python test_system.py
```

## 📜 License

See LICENSE file for details.

---

**Ready to go?** Run: `python main.py --input-mode text` 🚀
