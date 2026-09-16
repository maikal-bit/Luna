# 🌙 LUNA — Multimodal Voice & Desktop AI Assistant

<p align="center">
  <img src="config/luna.ico" width="100" alt="LUNA Assistant Logo" />
</p>

<p align="center">
  <strong>An intelligent, charming, and hyper-responsive desktop AI companion powered by Google Gemini Live API.</strong>
</p>

<p align="center">
  <a href="#key-features">Features</a> •
  <a href="#prerequisites">Prerequisites</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#configuration">Configuration</a> •
  <a href="#tools--capabilities">Capabilities</a> •
  <a href="#mobile-dashboard">Remote Dashboard</a> •
  <a href="#architecture">Architecture</a>
</p>

---

## ✨ Overview

**LUNA** is a next-generation desktop AI companion built with **Python 3.10+**, **PyQt6**, and Google's low-latency **Gemini Live Multimodal API**. 

Unlike traditional chatbots or rigid voice assistants, Luna features:
- **Full-duplex real-time bidirectional voice conversation** with natural human intonation and emotion.
- **Deep operating system automation** for window management, settings, and file operations.
- **Direct in-app searching** across desktop apps (YouTube Desktop, Spotify, Discord, Telegram, WhatsApp, Explorer).
- **Multimodal computer vision** enabling Luna to inspect your active screen, debug code, and analyze documents.
- **Complete local privacy**: your memory and configuration stay exclusively on your local machine.

---

## 🚀 Key Features

### 🎙️ Live Bidirectional Audio Stream
- Direct WebSocket connection to Google Gemini Live API (`models/gemini-3.1-flash-live-preview` with automatic fallback to `models/gemini-2.5-flash`).
- Natural, sweet, and expressive vocal delivery (pre-configured with Google's `Kore` voice).
- Barge-in interruptibility: speak while Luna is talking to interrupt or redirect naturally.
- Local Voice Activity Detection (VAD) for instant speech turnaround.

### 🖥️ Native In-App & Desktop Control
- Direct application control: launch, focus, and search inside desktop software natively without relying on web browser tabs.
- Custom deep handlers for:
  - **YouTube Desktop** (deep binary resolution, instant `/` search hotkey)
  - **Spotify** (native `spotify:search:...` URI protocol)
  - **Discord & Telegram** (quick-switcher and chat search automation)
  - **WhatsApp & Windows File Explorer**
- Volume, display brightness, Wi-Fi control, and system power automation.

### 👁️ Screen Vision & File Processing
- On-demand screen capture and visual scene inspection via Gemini vision.
- Multi-format file processor: PDF, DOCX, CSV, XLSX, code files, audio, images, and video files.

### 🌦️ Real-Time Intelligence Tools
- **Live Weather**: Instant global weather forecasts powered by the Open-Meteo API (temperature, feels-like, wind, humidity, conditions).
- **Web Search & News**: Instant web search via DuckDuckGo and Google Gemini search grounding.
- **Developer Agent & Coding Assistant**: File creation, bug fixing, project building, and code analysis.
- **System Monitoring**: Real-time CPU, RAM, GPU, and thermal tracking with optional voice threshold alerts.

### 📱 Remote Web Dashboard
- Access Luna from your smartphone or tablet on your local network.
- Secure 6-digit PIN login with **AES-256** encrypted WebSockets.
- Stream microphone audio directly from your mobile browser (16 kHz PCM) to talk to Luna remotely.
- Wireless file upload and download to your desktop.

### 🧠 Local Long-Term Memory
- Stateful JSON memory storage for user preferences, names, languages, and contextual notes.
- Atomic writes preventing corruption and zero telemetry back to third parties.

---

## 📋 Prerequisites

1. **Operating System**:
   - Windows 10 / 11 (fully featured with OS hooks)
   - macOS (12+)
   - Linux (Ubuntu, Debian, Fedora, Arch)
2. **Python**: Python `3.10`, `3.11`, or `3.12` installed and added to `PATH`.
3. **Gemini API Key**: Free API key from [Google AI Studio](https://aistudio.google.com/).

---

## ⚡ Quick Start

### 1. Clone & Navigate into the Folder
```bash
git clone https://github.com/maikal-bit/Luna.git
cd Luna
```
> [!IMPORTANT]
> Make sure to navigate into the project directory with **`cd Luna`** before running the next commands!

### 2. Set Up Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Run Automated Setup
Run the automated installer to download Python dependencies and Playwright browser binaries:
```bash
python setup.py
```

### 4. Launch LUNA
Double-click `run_luna.bat` (on Windows) or start via terminal:
```bash
python main.py
```

On first launch, Luna's GUI will appear. Simply enter your Gemini API key in the setup dialog. Your key will be securely saved locally in `config/api_keys.json` (which is git-ignored and never shared).

---

## ⚙️ Configuration

You can configure Luna via the in-app **Settings (⚙)** tab or by copying `config/api_keys.json.example`:

```bash
cp config/api_keys.json.example config/api_keys.json
```

Edit `config/api_keys.json`:
```json
{
  "gemini_api_key": "YOUR_GEMINI_API_KEY_HERE",
  "os_system": "windows",
  "voice_name": "Kore",
  "assistant_name": "LUNA",
  "user_name": "YourName",
  "ui_color": "#d946ef"
}
```

### Available Gemini Live Voices
- `Kore` — Sweet, elegant, youthful female voice *(Default)*
- `Aoede` — Melodic, expressive female voice
- `Puck` — Playful, energetic voice
- `Charon` — Calm, deep voice
- `Fenrir` — Direct, crisp voice

---

## 🛠️ Tools & Capabilities

Luna automatically discovers all tools inside the `actions/` directory:

| Action Tool | Description |
|---|---|
| `search_in_app` | Searches directly inside YouTube Desktop, Spotify, Discord, Telegram, Explorer, etc. |
| `open_app` | Launches and switches to native desktop applications |
| `weather_report` | Live meteorological data via Open-Meteo REST API |
| `web_search` | Real-time web and news research |
| `screen_process` | Real-time visual analysis of the active screen |
| `computer_settings`| Volume, brightness, Wi-Fi, shortcuts, and power operations |
| `file_controller` | Safe cross-drive file search, organization, copy, move, and trash |
| `file_processor` | PDF, DOCX, CSV, Excel, code, and media file summaries |
| `system_status` | CPU, RAM, GPU utilization and temperature statistics |
| `dev_agent` | Multi-file code generation and software development workflows |
| `youtube_video` | YouTube video player, audio playback, and transcript summaries |
| `reminder` | Scheduled Windows toasts and notifications |

---

## 📱 Mobile Remote Dashboard

To interact with Luna from your phone:
1. Open Luna on your PC and click the **Dashboard** button on the bottom toolbar.
2. Scan the generated QR code or open `http://<your-pc-ip>:8000` on your mobile browser.
3. Enter the 6-character PIN shown on Luna's HUD.
4. Use the mobile interface to talk via phone microphone, execute commands, and transfer files!

---

## 📂 Architecture

```
Luna-Assistant/
├── actions/              # Auto-discovered tool handlers (17 actions)
│   ├── browser_control.py
│   ├── code_helper.py
│   ├── computer_control.py
│   ├── computer_settings.py
│   ├── desktop.py
│   ├── dev_agent.py
│   ├── file_controller.py
│   ├── file_processor.py
│   ├── flight_finder.py
│   ├── game_updater.py
│   ├── open_app.py
│   ├── reminder.py
│   ├── screen_processor.py
│   ├── search_in_app.py
│   ├── send_message.py
│   ├── weather_report.py
│   ├── web_search.py
│   └── youtube_video.py
├── config/               # App configuration, icons & certs
│   ├── api_keys.json.example
│   └── luna.ico
├── core/                 # Engine primitives
│   ├── action_loader.py  # Action discovery & dispatch
│   ├── audio_devices.py  # Mic & speaker routing
│   ├── llm_client.py     # Gemini client interface
│   ├── plugin_loader.py  # Plugin system
│   ├── prompt.txt        # Luna system personality & routing prompt
│   ├── stt.py & tts.py   # Speech fallbacks
│   └── wake_word.py      # Offline "Hey Luna" wake word (OpenWakeWord)
├── dashboard/            # FastAPI mobile dashboard server & static assets
│   ├── server.py
│   └── static/
├── memory/               # Local long-term memory & settings
│   ├── config_manager.py
│   └── memory_manager.py
├── plugins/              # Drop-in user plugins
├── main.py               # Application entry point & Gemini Live session loop
├── ui.py                 # Modern PyQt6 HUD & settings interface
├── requirements.txt      # Python dependencies
├── setup.py              # Automated cross-platform installer
└── run_luna.bat          # 1-click launcher for Windows
```

---

## 🛡️ Privacy & Security

- **No Remote Telemetry**: Luna does not transmit any usage data, logs, or metrics to third parties.
- **Local Credentials**: API keys and long-term memories are stored on your local disk in `.gitignore`'d files.
- **Protected File Boundaries**: The file controller prohibits destructive operations on critical operating system directories (`C:\Windows`, `Program Files`, filesystem roots).

---

## 🤝 Contributing

Contributions, bug reports, and feature requests are welcome!
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more details.
