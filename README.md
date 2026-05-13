# Modern-Text-Tool-Dashboard

![Python](https://img.shields.io/badge/Power%20BI-F2C811?style=for-the-badge&logo=python&logoColor=black)
![DAX](https://img.shields.io/badge/DAX-Advanced-blue?style=for-the-badge)

# 📝 Text Tool Pro v3.0 — Ultimate Edition

A powerful, all-in-one desktop text processing dashboard built with Python and Tkinter.  
Speak, listen, translate, analyze, summarize, and export — all in one beautiful offline-first app.

---

## 🖥️ Screenshot Preview

```
╔══════════════════════════════════════════════════════════════════════════════╗
║              TEXT TOOL PRO  v3.0  —  Ultimate Edition                       ║
║  Features: TTS · STT · PDF · Translation · Speed/Volume Control             ║
║  Dark/Light Themes · Word Count · Session History · Export · Find & Replace ║
║  AI Summarize · Char Analysis · Live Status · Animated Sidebar              ║
║  Spell Check · Word Wrap · Line Numbers · Font Control · Drag & Drop        ║
║  Auto-Save · Pinned Notes · Sentence Highlighter · Readability Score        ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## 🚀 Features

### 🔊 Text-to-Speech (TTS)
- Speaks English text using **pyttsx3** (offline, fast)
- Speaks **100+ languages** using **Edge TTS** (Microsoft Neural voices)
- **Male & Female voice selection** for every language
- Speed and volume control sliders
- Auto-detects language from input text using **langdetect**

### 🎙️ Speech-to-Text (STT)
- Record your voice and convert it to text instantly
- Powered by **SpeechRecognition** + **PyAudio**
- Works with your system microphone

### 🌐 Translation
- Translate between **100+ languages**
- Auto-detect source language
- Powered by **deep-translator** (Google Translate backend)
- Swap source and target languages with one click
- Speak translated output directly

### 📄 PDF Support
- Open and extract text from PDF files
- Powered by **PyPDF2**
- Extracted text loads directly into the editor

### 📊 Text Analysis
- Word count, character count, line count
- Sentence count and reading time estimate
- **Flesch Reading Ease score** (readability)
- Word frequency analysis (top 15 words)
- Live stats in the status bar

### 📝 AI Summarize
- Summarize long text into key points
- Useful for articles, documents, and reports

### 💾 Export Options
- Save text as `.txt` file
- Export translation/output as text
- Save audio as `.mp3` using gTTS

### 🎨 Themes (7 Built-in)
| Theme | Style |
|---|---|
| Obsidian | Dark blue (default) |
| Neon Forge | Cyberpunk dark |
| Crimson | Dark red |
| Arctic | Clean light |
| Sakura | Pink light |
| Midnight Blue | Deep navy |
| Forest | Dark green |

### ✏️ Editor Features
- Line numbers
- Word wrap toggle
- Find & Replace (`Ctrl+F`)
- Undo / Redo (`Ctrl+Z` / `Ctrl+Y`)
- Font family and size control
- Sentence highlighting
- Drag & drop paste
- Live readability score

### 💡 Other Features
- **Auto-save** every 30 seconds — restores on next launch
- **Session history** — browse all previous inputs
- **Pinned Notes** panel
- Animated sidebar
- Live status bar with TTS / STT / PDF / GT indicators
- Keyboard shortcuts for all major actions

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl + Enter` | Speak text |
| `Ctrl + F` | Find & Replace |
| `Ctrl + S` | Save text |
| `Ctrl + O` | Open PDF |
| `Ctrl + Z` | Undo |
| `Ctrl + Y` | Redo |

---

## 🛠️ Requirements

**Python version:** `3.11` (recommended)

### Install all dependencies:
```bash
py -3.11 -m pip install -r requirement.txt
```

### requirement.txt
```
certifi==2024.8.30
chardet==3.0.4
charset-normalizer==3.3.2
click==8.1.7
colorama==0.4.6
comtypes==1.4.7
deep-translator
gTTS==2.5.3
h11==0.9.0
h2==3.2.0
hpack==3.0.0
hstspreload==2024.10.1
httpcore==0.9.1
httpx>=0.25.0
hyperframe==5.2.0
idna==2.10
playsound3==3.0.0
PyAudio==0.2.14
PyPDF2==2.11.2
pypiwin32==223
pyttsx3==2.98
pywin32==307
requests==2.32.3
rfc3986==1.5.0
sniffio==1.3.1
SpeechRecognition==3.10.4
typing_extensions>=4.14.1
urllib3==2.2.3
langdetect
edge-tts
```

---

## ▶️ How to Run

```bash
py -3.11 main.py
```

### Verify all packages installed correctly:
```bash
py -3.11 -c "import speech_recognition, PyPDF2, pyttsx3, gtts, playsound3, pyaudio, deep_translator, langdetect, edge_tts; print('All OK!')"
```

---

## 📁 Project Structure

```
Modern Text Tool Dashboard/
│
├── main.py              # Main application (single file)
├── requirement.txt      # All dependencies
├── README.md            # This file
└── autosave.json        # Auto-generated — stores last session text
```

---

## 🔧 Troubleshooting

| Problem | Fix |
|---|---|
| PyAudio fails to install | Already installed on Python 3.11 — use `py -3.11` |
| `pipwin` SSL error | pipwin is dead — use `py -3.11 -m pip install PyAudio` directly |
| googletrans conflict | Use `deep-translator` instead (already in requirement.txt) |
| No voice for other languages | Install `edge-tts`: `py -3.11 -m pip install edge-tts` |
| Network error during install | Retry: `py -3.11 -m pip install <package> --retries 10` |
| App doesn't remember last text | Check `autosave.json` exists in project folder |

---

## 🏭 Why This Tool Matters — Industry & Market Importance

### The Problem It Solves

In today's world, content is created and consumed across dozens of languages, formats, and accessibility needs. Most people rely on 4–5 separate tools just to do what Text Tool Pro does in one window — a text editor, a translator, a TTS reader, a voice recorder, a PDF extractor, and a text analyzer.

### Who Needs This

**Education sector** — Teachers and students working with multilingual content need to read, translate, and speak text in different languages. This tool eliminates the need for switching between browser tabs, online converters, and separate apps.

**Accessibility** — People with visual impairments or reading difficulties (dyslexia, low literacy) rely on text-to-speech tools daily. Having male/female neural voices in 100+ languages makes content accessible to a global audience — not just English speakers.

**Content creators and writers** — Bloggers, journalists, and copywriters use readability scores (Flesch score), word frequency analysis, and summarization to polish their work. This tool gives them a professional writing assistant without a subscription fee.

**Business and enterprises** — Companies operating across multiple countries need fast document translation and text processing. A lightweight desktop tool that works offline (no data leaving the machine) is valuable for privacy-sensitive industries like legal, finance, and healthcare.

**Developers and researchers** — The app's ability to extract text from PDFs, analyze word frequency, estimate reading time, and export results makes it a useful research assistant for anyone processing large volumes of text.

### Market Relevance

The global **Text-to-Speech market** was valued at over $3 billion in 2023 and is projected to exceed $8 billion by 2030 (CAGR ~14%). The **machine translation market** is similarly growing rapidly, driven by globalization and multilingual digital content needs.

Most commercial alternatives — like Natural Reader, Speechify, or DeepL — are cloud-based subscription tools. Text Tool Pro offers a **free, offline-first, open alternative** that runs entirely on your machine with no API costs, no data privacy concerns, and no internet requirement for core features.

### Why It Stands Out

- **Single file, zero cloud dependency** for core features — works even without internet
- **Neural voices via Edge TTS** — same quality as paid apps like Speechify
- **100+ language support** — covers virtually every major language on Earth
- **All-in-one** — replaces Notepad++, Google Translate, Natural Reader, Adobe Acrobat reader, and a voice recorder simultaneously
- **Completely free and open** — no subscription, no account, no tracking

In short, Text Tool Pro is not just a student project — it is a genuinely useful productivity tool that addresses real accessibility, localization, and content processing needs across education, business, and personal use worldwide.

---

## 👨‍💻 Built With

- **Python 3.11**
- **Tkinter** — GUI framework
- **pyttsx3** — Offline English TTS
- **edge-tts** — Microsoft Neural TTS (multilingual)
- **SpeechRecognition + PyAudio** — Voice input
- **deep-translator** — 100+ language translation
- **gTTS** — Google Text-to-Speech
- **PyPDF2** — PDF text extraction
- **langdetect** — Automatic language detection
- **playsound3** — Audio playback
