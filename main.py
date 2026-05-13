"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              TEXT TOOL PRO  v3.0  —  Ultimate Edition                       ║
║  Features: TTS · STT · PDF · Translation · Speed/Volume Control             ║
║  Dark/Light Themes · Word Count · Session History · Export · Find & Replace ║
║  AI Summarize · Char Analysis · Live Status · Animated Sidebar              ║
║  Spell Check · Word Wrap · Line Numbers · Font Control · Drag & Drop        ║
║  Auto-Save · Pinned Notes · Sentence Highlighter · Readability Score        ║
╚══════════════════════════════════════════════════════════════════════════════╝

INSTALL (one-time):
    pip install SpeechRecognition PyPDF2 pyttsx3
    pip install gtts playsound3 pyaudio googletrans==3.1.0a0

Run:  python main.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font as tkfont
import threading
import os
import datetime
import json
import re
import sys
import time
import math

# ── Optional heavy libs (graceful fallback) ─────────────────────────────────
try:
    import speech_recognition as sr
    SR_OK = True
except ImportError:
    SR_OK = False

try:
    import PyPDF2
    PDF_OK = True
except ImportError:
    PDF_OK = False

try:
    import pyttsx3
    TTS_OK = True
except ImportError:
    TTS_OK = False

# ── Translation backends ────────────────────────────────────────────────────
_TRANSLATE_BACKEND = None
GT_OK = False

try:
    from deep_translator import GoogleTranslator as _DeepGT
    _TRANSLATE_BACKEND = "deep"
    GT_OK = True
except ImportError:
    _DeepGT = None

if _TRANSLATE_BACKEND is None:
    try:
        from googletrans import Translator as _GTrans
        _TRANSLATE_BACKEND = "googletrans"
        GT_OK = True
    except ImportError:
        _GTrans = None

def _do_translate(text: str, src: str, tgt: str) -> str:
    if _TRANSLATE_BACKEND == "deep":
        src_arg = "auto" if src in ("auto", "") else src
        MAX = 4800
        if len(text) <= MAX:
            return _DeepGT(source=src_arg, target=tgt).translate(text)
        chunks, cur = [], ""
        for line in text.splitlines(keepends=True):
            if len(cur) + len(line) > MAX:
                if cur:
                    chunks.append(_DeepGT(source=src_arg, target=tgt).translate(cur))
                cur = line
            else:
                cur += line
        if cur:
            chunks.append(_DeepGT(source=src_arg, target=tgt).translate(cur))
        return "".join(chunks)
    elif _TRANSLATE_BACKEND == "googletrans":
        t = _GTrans()
        result = t.translate(text, src=src if src != "auto" else "auto", dest=tgt)
        return result.text
    else:
        raise RuntimeError("No translation library installed.\nRun:  pip install deep-translator")

try:
    from gtts import gTTS
    GTTS_OK = True
except ImportError:
    GTTS_OK = False

try:
    from playsound3 import playsound
    PS_OK = True
except ImportError:
    PS_OK = False

# ── Full language map ────────────────────────────────────────────────────────
LANG_MAP = {
    "auto":"auto-detect (source only)",
    "af":"afrikaans","sq":"albanian","am":"amharic","ar":"arabic",
    "hy":"armenian","az":"azerbaijani","eu":"basque","be":"belarusian",
    "bn":"bengali","bs":"bosnian","bg":"bulgarian","ca":"catalan",
    "ceb":"cebuano","zh-cn":"chinese (simplified)","zh-tw":"chinese (traditional)",
    "co":"corsican","hr":"croatian","cs":"czech","da":"danish",
    "nl":"dutch","en":"english","eo":"esperanto","et":"estonian",
    "fi":"finnish","fr":"french","fy":"frisian","gl":"galician",
    "ka":"georgian","de":"german","el":"greek","gu":"gujarati",
    "ht":"haitian creole","ha":"hausa","haw":"hawaiian","he":"hebrew",
    "hi":"hindi","hmn":"hmong","hu":"hungarian","is":"icelandic",
    "ig":"igbo","id":"indonesian","ga":"irish","it":"italian",
    "ja":"japanese","jw":"javanese","kn":"kannada","kk":"kazakh",
    "km":"khmer","ko":"korean","ku":"kurdish","ky":"kyrgyz",
    "lo":"lao","la":"latin","lv":"latvian","lt":"lithuanian",
    "lb":"luxembourgish","mk":"macedonian","mg":"malagasy","ms":"malay",
    "ml":"malayalam","mt":"maltese","mi":"maori","mr":"marathi",
    "mn":"mongolian","my":"myanmar","ne":"nepali","no":"norwegian",
    "ny":"nyanja","or":"odia","ps":"pashto","fa":"persian",
    "pl":"polish","pt":"portuguese","pa":"punjabi","ro":"romanian",
    "ru":"russian","sm":"samoan","gd":"scots gaelic","sr":"serbian",
    "st":"sesotho","sn":"shona","sd":"sindhi","si":"sinhala",
    "sk":"slovak","sl":"slovenian","so":"somali","es":"spanish",
    "su":"sundanese","sw":"swahili","sv":"swedish","tl":"filipino",
    "tg":"tajik","ta":"tamil","tt":"tatar","te":"telugu",
    "th":"thai","tr":"turkish","tk":"turkmen","uk":"ukrainian",
    "ur":"urdu","ug":"uyghur","uz":"uzbek","vi":"vietnamese",
    "cy":"welsh","xh":"xhosa","yi":"yiddish","yo":"yoruba","zu":"zulu",
}
LANG_NAMES = list(LANG_MAP.values())
LANG_CODES = list(LANG_MAP.keys())

# ═══════════════════════════════════════════════════════════════════════════════
#  THEMES
# ═══════════════════════════════════════════════════════════════════════════════
THEMES = {
    "Obsidian": {
        "bg": "#0a0e1a", "sidebar": "#0f1525", "panel": "#141e35",
        "card": "#111827", "accent": "#4f8ef7", "accent2": "#10d9a0",
        "danger": "#f05068", "warning": "#f5a623", "text": "#e8edf8",
        "subtext": "#6b7ea0", "border": "#1e2d50", "input_bg": "#0d1220",
        "btn_bg": "#19243d", "btn_hover": "#223060", "highlight": "#2563eb",
        "tag_bg": "#1a2540", "scrollbar": "#1e2d50", "sep": "#1a2540",
        "line_num_bg": "#0d1628", "line_num_fg": "#3a4e6e",
    },
    "Neon Forge": {
        "bg": "#070b0f", "sidebar": "#0b1018", "panel": "#0f1820",
        "card": "#0d1620", "accent": "#00f5d4", "accent2": "#f72585",
        "danger": "#ff2d55", "warning": "#ff9f0a", "text": "#caf0f8",
        "subtext": "#4a6d7c", "border": "#163040", "input_bg": "#070b0f",
        "btn_bg": "#0f1820", "btn_hover": "#163040", "highlight": "#007b6e",
        "tag_bg": "#0b1820", "scrollbar": "#163040", "sep": "#0d1e28",
        "line_num_bg": "#090e14", "line_num_fg": "#1e4050",
    },
    "Crimson": {
        "bg": "#0c0608", "sidebar": "#130809", "panel": "#1c0d0f",
        "card": "#160b0c", "accent": "#e84855", "accent2": "#f7b731",
        "danger": "#ff3333", "warning": "#f39c12", "text": "#f5e6e8",
        "subtext": "#8a5562", "border": "#3a1520", "input_bg": "#0c0608",
        "btn_bg": "#1c0d0f", "btn_hover": "#2e1218", "highlight": "#9b1c28",
        "tag_bg": "#1a0c10", "scrollbar": "#2e1218", "sep": "#2a1018",
        "line_num_bg": "#100608", "line_num_fg": "#3a1520",
    },
    "Arctic": {
        "bg": "#f0f4f8", "sidebar": "#e2eaf3", "panel": "#d8e4f0",
        "card": "#eaf0f8", "accent": "#1a6fff", "accent2": "#00c78c",
        "danger": "#e8334a", "warning": "#e67e22", "text": "#1a2540",
        "subtext": "#5a7090", "border": "#b8cce0", "input_bg": "#ffffff",
        "btn_bg": "#d0dcea", "btn_hover": "#b8cce0", "highlight": "#2563eb",
        "tag_bg": "#e0ecf8", "scrollbar": "#b8cce0", "sep": "#c8d8e8",
        "line_num_bg": "#e8f0f8", "line_num_fg": "#90a8c0",
    },
    "Sakura": {
        "bg": "#fdf0f5", "sidebar": "#f8e8f0", "panel": "#f0d8e8",
        "card": "#fdf5f8", "accent": "#c2185b", "accent2": "#2e7d32",
        "danger": "#c62828", "warning": "#ef6c00", "text": "#2d1525",
        "subtext": "#9e6080", "border": "#e8b8cc", "input_bg": "#fff8fb",
        "btn_bg": "#f0d0e0", "btn_hover": "#e8b8cc", "highlight": "#880e4f",
        "tag_bg": "#f8e4ee", "scrollbar": "#e8b8cc", "sep": "#f0c8d8",
        "line_num_bg": "#fce4ee", "line_num_fg": "#d4a0b8",
    },
    "Midnight Blue": {
        "bg": "#0d1b2a", "sidebar": "#112236", "panel": "#162b42",
        "card": "#102030", "accent": "#4cc9f0", "accent2": "#7bed9f",
        "danger": "#ff6b81", "warning": "#ffa502", "text": "#dfe6ed",
        "subtext": "#5d7a8a", "border": "#1e3a52", "input_bg": "#0a1520",
        "btn_bg": "#162030", "btn_hover": "#1e3050", "highlight": "#0080bb",
        "tag_bg": "#12243a", "scrollbar": "#1e3a52", "sep": "#162540",
        "line_num_bg": "#0c1a28", "line_num_fg": "#284060",
    },
    "Forest": {
        "bg": "#0d1a0f", "sidebar": "#102214", "panel": "#152c18",
        "card": "#112015", "accent": "#4ade80", "accent2": "#60a5fa",
        "danger": "#f87171", "warning": "#fbbf24", "text": "#d4edda",
        "subtext": "#5a7a62", "border": "#1e3d24", "input_bg": "#0a150c",
        "btn_bg": "#152218", "btn_hover": "#1e3424", "highlight": "#166534",
        "tag_bg": "#122018", "scrollbar": "#1e3424", "sep": "#182a1c",
        "line_num_bg": "#0c1a10", "line_num_fg": "#284030",
    },
}

_ACTIVE_THEME = "Obsidian"

# ═══════════════════════════════════════════════════════════════════════════════
#  UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════
def _name_to_code(name: str) -> str:
    if "auto" in name.lower():
        return "auto"
    name_l = name.lower()
    for code, lname in LANG_MAP.items():
        if lname.lower() == name_l:
            return code
    return "en"

def word_frequency(text: str) -> dict:
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    return dict(sorted(freq.items(), key=lambda x: -x[1])[:15])

def reading_time(text: str) -> str:
    words = len(text.split())
    minutes = max(1, round(words / 200))
    return f"{minutes} min read"

def count_sentences(text: str) -> int:
    return len(re.findall(r'[.!?]+', text))

def flesch_reading_ease(text: str) -> float:
    """Flesch Reading Ease score (0–100, higher = easier)."""
    words_l = text.split()
    n_words = len(words_l)
    n_sents = max(1, count_sentences(text))
    n_sylls = sum(_count_syllables(w) for w in words_l)
    if n_words == 0:
        return 0.0
    score = 206.835 - 1.015 * (n_words / n_sents) - 84.6 * (n_sylls / n_words)
    return round(max(0.0, min(100.0, score)), 1)

def _count_syllables(word: str) -> int:
    word = word.lower().strip(".,!?;:'\"")
    if not word:
        return 0
    count = len(re.findall(r'[aeiou]+', word))
    if word.endswith('e') and count > 1:
        count -= 1
    return max(1, count)

def readability_label(score: float) -> str:
    if score >= 90: return "Very Easy"
    if score >= 70: return "Easy"
    if score >= 60: return "Standard"
    if score >= 50: return "Fairly Difficult"
    if score >= 30: return "Difficult"
    return "Very Difficult"

# ═══════════════════════════════════════════════════════════════════════════════
#  AUTO-SAVE MANAGER
# ═══════════════════════════════════════════════════════════════════════════════
AUTOSAVE_PATH = os.path.join(os.path.expanduser("~"), ".texttoolpro_autosave.json")

def autosave_write(text: str):
    try:
        with open(AUTOSAVE_PATH, "w", encoding="utf-8") as f:
            json.dump({"ts": datetime.datetime.now().isoformat(), "text": text}, f)
    except Exception:
        pass

def autosave_read() -> str:
    try:
        with open(AUTOSAVE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("text", "")
    except Exception:
        return ""

# ═══════════════════════════════════════════════════════════════════════════════
#  CUSTOM WIDGETS
# ═══════════════════════════════════════════════════════════════════════════════
class ModernButton(tk.Button):
    def __init__(self, parent, text, command, T,
                 style="normal", size="md", icon="", **kw):
        font_sizes = {"sm": 8, "md": 10, "lg": 12}
        padx_map   = {"sm": 8, "md": 14, "lg": 20}
        pady_map   = {"sm": 4, "md": 7,  "lg": 10}

        if style == "accent":
            bg, fg, hover = T["accent"], T["bg"], T["highlight"]
        elif style == "danger":
            bg, fg, hover = T["danger"], "#ffffff", "#b71c1c"
        elif style == "success":
            bg, fg, hover = T["accent2"], T["bg"], "#007a5e"
        else:
            bg, fg, hover = T["btn_bg"], T["text"], T["btn_hover"]

        label = f"{icon}  {text}" if icon else text
        super().__init__(parent, text=label, command=command,
                         bg=bg, fg=fg,
                         font=("Segoe UI Semibold", font_sizes[size]),
                         relief="flat", bd=0, cursor="hand2",
                         activebackground=hover, activeforeground=fg,
                         padx=padx_map[size], pady=pady_map[size], **kw)
        self._bg, self._hover = bg, hover
        self.bind("<Enter>",           lambda e: self.config(bg=self._hover))
        self.bind("<Leave>",           lambda e: self.config(bg=self._bg))
        self.bind("<Button-1>",        lambda e: self.config(relief="sunken"))
        self.bind("<ButtonRelease-1>", lambda e: self.config(relief="flat"))

    def recolor(self, T, style="normal"):
        if style == "accent":
            self._bg, self._hover = T["accent"], T["highlight"]
            fg = T["bg"]
        elif style == "danger":
            self._bg, self._hover = T["danger"], "#b71c1c"
            fg = "#ffffff"
        elif style == "success":
            self._bg, self._hover = T["accent2"], "#007a5e"
            fg = T["bg"]
        else:
            self._bg, self._hover = T["btn_bg"], T["btn_hover"]
            fg = T["text"]
        self.config(bg=self._bg, fg=fg,
                    activebackground=self._hover, activeforeground=fg)


class StatusDot(tk.Canvas):
    def __init__(self, parent, T, size=10, **kw):
        super().__init__(parent, width=size, height=size,
                         bg=T["sidebar"], highlightthickness=0, **kw)
        self._size  = size
        self._T     = T
        self._dot   = self.create_oval(1, 1, size-1, size-1,
                                       fill=T["subtext"], outline="")
        self._state = "idle"
        self._pulse_job = None

    def set_state(self, state):
        self._state = state
        colors = {
            "idle":    self._T["subtext"],
            "active":  self._T["accent2"],
            "error":   self._T["danger"],
            "warning": self._T["warning"],
        }
        self.itemconfig(self._dot, fill=colors.get(state, self._T["subtext"]))
        if state == "active":
            self._start_pulse()
        else:
            self._stop_pulse()

    def _start_pulse(self):
        self._stop_pulse()
        self._pulse_phase = 0.0
        self._do_pulse()

    def _stop_pulse(self):
        if self._pulse_job:
            try:
                self.after_cancel(self._pulse_job)
            except Exception:
                pass
            self._pulse_job = None

    def _do_pulse(self):
        if self._state != "active":
            return
        self._pulse_phase = (self._pulse_phase + 0.15) % (2 * math.pi)
        alpha = (math.sin(self._pulse_phase) + 1) / 2  # 0–1
        # interpolate between subtext and accent2
        s = int(alpha * 255)
        fill = f"#{s:02x}{min(255, s+80):02x}{min(255, s+40):02x}"
        try:
            self.itemconfig(self._dot, fill=self._T["accent2"])
        except Exception:
            pass
        self._pulse_job = self.after(80, self._do_pulse)


class LineNumberCanvas(tk.Canvas):
    """Draws line numbers alongside a Text widget."""
    def __init__(self, parent, text_widget, T, **kw):
        super().__init__(parent, width=42, highlightthickness=0,
                         bg=T.get("line_num_bg", T["sidebar"]), **kw)
        self._text  = text_widget
        self._T     = T
        self._font  = ("Consolas", 11)
        if text_widget is not None:
            self.attach_text(text_widget)

    def attach_text(self, text_widget):
        """Bind events to the real Text widget. Call this after __init__ if
        the widget was not available at construction time (passed as None)."""
        self._text = text_widget
        self._text.bind("<KeyRelease>", self.redraw)
        self._text.bind("<ButtonRelease>", self.redraw)
        self._text.bind("<MouseWheel>", lambda e: self.after(10, self.redraw))
        self._text.bind("<Configure>", lambda e: self.after(10, self.redraw))

    def redraw(self, event=None):
        self.delete("all")
        i  = self._text.index("@0,0")
        fg = self._T.get("line_num_fg", self._T["subtext"])
        while True:
            dline = self._text.dlineinfo(i)
            if dline is None:
                break
            y   = dline[1]
            lno = int(str(i).split(".")[0])
            self.create_text(38, y + 8, anchor="ne", text=str(lno),
                             fill=fg, font=self._font)
            i = self._text.index(f"{i}+1line")
            if self._text.compare(i, ">=", "end"):
                break

    def recolor(self, T):
        self._T = T
        self.config(bg=T.get("line_num_bg", T["sidebar"]))
        self.redraw()


# ═══════════════════════════════════════════════════════════════════════════════
#  FIND & REPLACE DIALOG
# ═══════════════════════════════════════════════════════════════════════════════
class FindReplaceDialog(tk.Toplevel):
    def __init__(self, parent, text_widget, T):
        super().__init__(parent)
        self.title("Find & Replace")
        self.resizable(False, False)
        self.config(bg=T["panel"])
        self.transient(parent)
        self.grab_set()
        self._widget = text_widget
        self._T = T
        self._last = "1.0"
        self._match_count = 0

        pad = dict(padx=16, pady=6)

        tk.Label(self, text="🔍  FIND & REPLACE", bg=T["panel"], fg=T["accent"],
                 font=("Segoe UI", 11, "bold")).grid(
                 row=0, column=0, columnspan=2, **pad, pady=(14, 4), sticky="w")

        for row_i, (label, attr) in enumerate(
                [("Find:", "find_var"), ("Replace:", "repl_var")], start=1):
            tk.Label(self, text=label, bg=T["panel"], fg=T["subtext"],
                     font=("Segoe UI", 9)).grid(row=row_i, column=0, **pad, sticky="e")
            setattr(self, attr, tk.StringVar())
            e = tk.Entry(self, textvariable=getattr(self, attr), width=30,
                         bg=T["input_bg"], fg=T["text"], relief="flat",
                         insertbackground=T["accent"],
                         font=("Segoe UI", 9))
            e.grid(row=row_i, column=1, **pad, sticky="ew")

        self.case_var = tk.BooleanVar(value=False)
        tk.Checkbutton(self, text="Case Sensitive", variable=self.case_var,
                       bg=T["panel"], fg=T["subtext"],
                       selectcolor=T["card"],
                       activebackground=T["panel"],
                       font=("Segoe UI", 8)).grid(
                       row=3, column=1, sticky="w", padx=16, pady=2)

        self._match_lbl = tk.Label(self, text="", bg=T["panel"],
                                   fg=T["accent2"], font=("Segoe UI", 8))
        self._match_lbl.grid(row=4, column=0, columnspan=2, padx=16, sticky="w")

        btn_frame = tk.Frame(self, bg=T["panel"])
        btn_frame.grid(row=5, column=0, columnspan=2, pady=(8, 14), padx=16, sticky="ew")

        for txt, cmd, sty in [
            ("Find Next",    self._find_next,   "accent"),
            ("Replace",      self._replace_one, "normal"),
            ("Replace All",  self._replace_all, "normal"),
            ("Close",        self.destroy,      "danger"),
        ]:
            ModernButton(btn_frame, txt, cmd, T, style=sty, size="sm").pack(
                side="left", padx=3)

        self._last = "1.0"
        # Bind Enter key in find field
        self.bind("<Return>", lambda e: self._find_next())
        self.bind("<Escape>", lambda e: self.destroy())
        self.focus()

    def _find_next(self):
        q = self.find_var.get()
        if not q:
            return
        self._widget.tag_remove("found", "1.0", "end")
        nocase = not self.case_var.get()
        pos = self._widget.search(q, self._last, stopindex="end", nocase=nocase)
        if not pos:
            pos = self._widget.search(q, "1.0", stopindex="end", nocase=nocase)
            self._last = "1.0"
        if pos:
            end_p = f"{pos}+{len(q)}c"
            self._widget.tag_add("found", pos, end_p)
            self._widget.tag_config("found", background=self._T["warning"],
                                    foreground=self._T["bg"])
            self._widget.see(pos)
            self._last = end_p
            # Count total occurrences
            content = self._widget.get("1.0", "end-1c")
            flags = 0 if self.case_var.get() else re.IGNORECASE
            total = len(re.findall(re.escape(q), content, flags))
            self._match_lbl.config(text=f"{total} match(es) found")
        else:
            self._match_lbl.config(text="Not found")
            messagebox.showinfo("Not Found", f'"{q}" was not found.', parent=self)

    def _replace_one(self):
        q, r = self.find_var.get(), self.repl_var.get()
        if not q:
            return
        content = self._widget.get("1.0", "end-1c")
        idx = content.lower().find(q.lower()) if not self.case_var.get() else content.find(q)
        if idx == -1:
            messagebox.showinfo("Not Found", f'"{q}" was not found.', parent=self)
            return
        self._widget.delete("1.0", "end")
        self._widget.insert("1.0", content[:idx] + r + content[idx + len(q):])

    def _replace_all(self):
        q, r = self.find_var.get(), self.repl_var.get()
        if not q:
            return
        content = self._widget.get("1.0", "end-1c")
        if self.case_var.get():
            count   = content.count(q)
            new_c   = content.replace(q, r)
        else:
            count   = len(re.findall(re.escape(q), content, re.IGNORECASE))
            new_c   = re.sub(re.escape(q), r, content, flags=re.IGNORECASE)
        self._widget.delete("1.0", "end")
        self._widget.insert("1.0", new_c)
        self._match_lbl.config(text=f"Replaced {count} occurrence(s)")
        messagebox.showinfo("Done", f"Replaced {count} occurrence(s).", parent=self)


# ═══════════════════════════════════════════════════════════════════════════════
#  ANALYSIS WINDOW
# ═══════════════════════════════════════════════════════════════════════════════
class AnalysisWindow(tk.Toplevel):
    def __init__(self, parent, text, T):
        super().__init__(parent)
        self.title("Text Analysis")
        self.config(bg=T["bg"])
        self.geometry("480x560")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, True)

        tk.Label(self, text="📊  TEXT ANALYSIS", bg=T["bg"], fg=T["accent"],
                 font=("Segoe UI", 13, "bold")).pack(padx=20, pady=(18, 6), anchor="w")
        tk.Frame(self, height=1, bg=T["border"]).pack(fill="x", padx=20, pady=4)

        words      = text.split()
        chars      = len(text)
        chars_ns   = len(text.replace(" ", ""))
        sentences  = count_sentences(text)
        paragraphs = len([p for p in text.split("\n\n") if p.strip()])
        avg_word   = round(sum(len(w) for w in words) / max(1, len(words)), 1)
        rt         = reading_time(text)
        flesch     = flesch_reading_ease(text)
        r_label    = readability_label(flesch)
        unique_wds = len(set(w.lower() for w in words if w.isalpha()))
        vocab_rich = round(unique_wds / max(1, len(words)) * 100, 1)

        stats = [
            ("📝 Words",               len(words)),
            ("🔤 Characters",          chars),
            ("🔡 Chars (no spaces)",   chars_ns),
            ("📜 Sentences",           sentences),
            ("📋 Paragraphs",          paragraphs),
            ("🔠 Unique Words",        unique_wds),
            ("💎 Vocabulary Richness", f"{vocab_rich}%"),
            ("📏 Avg word length",     f"{avg_word} chars"),
            ("⏱️ Reading time",        rt),
            ("📖 Readability Score",   f"{flesch}  ({r_label})"),
        ]

        for label, value in stats:
            row = tk.Frame(self, bg=T["card"])
            row.pack(fill="x", padx=20, pady=2)
            tk.Label(row, text=label, bg=T["card"], fg=T["subtext"],
                     font=("Segoe UI", 9), anchor="w").pack(side="left", padx=12, pady=6)
            tk.Label(row, text=str(value), bg=T["card"], fg=T["accent"],
                     font=("Segoe UI", 9, "bold"), anchor="e").pack(side="right", padx=12, pady=6)

        # Readability bar
        tk.Label(self, text=f"Readability: {flesch}/100", bg=T["bg"],
                 fg=T["subtext"], font=("Segoe UI", 8)).pack(padx=20, pady=(10, 2), anchor="w")
        bar_outer = tk.Frame(self, bg=T["border"], height=8)
        bar_outer.pack(fill="x", padx=20)
        bar_inner = tk.Frame(bar_outer, height=8,
                             bg=T["accent2"] if flesch >= 60 else T["warning"] if flesch >= 40 else T["danger"])
        bar_inner.place(relwidth=min(1.0, flesch / 100), relheight=1.0)

        tk.Label(self, text="🔁  Top Words", bg=T["bg"], fg=T["subtext"],
                 font=("Segoe UI", 9, "bold")).pack(padx=20, pady=(14, 4), anchor="w")

        freq = word_frequency(text)
        if freq:
            freq_frame = tk.Frame(self, bg=T["panel"])
            freq_frame.pack(fill="x", padx=20)
            for word, cnt in freq.items():
                row = tk.Frame(freq_frame, bg=T["panel"])
                row.pack(fill="x", padx=8, pady=1)
                tk.Label(row, text=word, bg=T["panel"], fg=T["text"],
                         font=("Consolas", 9), width=18, anchor="w").pack(side="left")
                max_cnt = list(freq.values())[0]
                bar_w   = max(4, int(120 * cnt / max_cnt))
                bar_c   = tk.Canvas(row, height=14, width=130, bg=T["panel"],
                                    highlightthickness=0)
                bar_c.pack(side="left", padx=4)
                bar_c.create_rectangle(0, 2, bar_w, 12, fill=T["accent"], outline="")
                tk.Label(row, text=str(cnt), bg=T["panel"], fg=T["subtext"],
                         font=("Segoe UI", 8)).pack(side="left", padx=4)

        ModernButton(self, "Close", self.destroy, T, style="danger",
                     size="sm").pack(pady=16)


# ═══════════════════════════════════════════════════════════════════════════════
#  PINNED NOTES WINDOW
# ═══════════════════════════════════════════════════════════════════════════════
NOTES_PATH = os.path.join(os.path.expanduser("~"), ".texttoolpro_notes.json")

class PinnedNotesWindow(tk.Toplevel):
    def __init__(self, parent, T):
        super().__init__(parent)
        self.title("📌 Pinned Notes")
        self.geometry("420x500")
        self.config(bg=T["bg"])
        self.transient(parent)
        self._T = T
        self._notes = self._load()
        self._build(T)

    def _load(self):
        try:
            with open(NOTES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save(self):
        try:
            with open(NOTES_PATH, "w", encoding="utf-8") as f:
                json.dump(self._notes, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _build(self, T):
        tk.Label(self, text="📌  PINNED NOTES", bg=T["bg"], fg=T["accent"],
                 font=("Segoe UI", 12, "bold")).pack(padx=16, pady=(14, 6), anchor="w")
        tk.Frame(self, height=1, bg=T["border"]).pack(fill="x", padx=16)

        self._listbox = tk.Listbox(self, bg=T["panel"], fg=T["text"],
                                   font=("Segoe UI", 9), relief="flat",
                                   selectbackground=T["highlight"],
                                   activestyle="none", bd=0)
        self._listbox.pack(fill="both", expand=True, padx=16, pady=(8, 4))
        for note in self._notes:
            self._listbox.insert("end", note[:80])

        self._entry = tk.Text(self, height=3, bg=T["input_bg"], fg=T["text"],
                              relief="flat", font=("Segoe UI", 9),
                              insertbackground=T["accent"], padx=8, pady=6)
        self._entry.pack(fill="x", padx=16, pady=(4, 0))
        tk.Label(self, text="Type a note above ↑", bg=T["bg"],
                 fg=T["subtext"], font=("Segoe UI", 7)).pack(anchor="w", padx=18)

        btn_row = tk.Frame(self, bg=T["bg"])
        btn_row.pack(fill="x", padx=16, pady=8)
        ModernButton(btn_row, "Add Note",    self._add,    T, style="accent", size="sm").pack(side="left", padx=2)
        ModernButton(btn_row, "Delete",      self._delete, T, style="danger",  size="sm").pack(side="left", padx=2)
        ModernButton(btn_row, "Copy Note",   self._copy,   T, style="normal",  size="sm").pack(side="left", padx=2)

    def _add(self):
        text = self._entry.get("1.0", "end-1c").strip()
        if not text:
            return
        self._notes.append(text)
        self._listbox.insert("end", text[:80])
        self._entry.delete("1.0", "end")
        self._save()

    def _delete(self):
        sel = self._listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        self._notes.pop(idx)
        self._listbox.delete(idx)
        self._save()

    def _copy(self):
        sel = self._listbox.curselection()
        if not sel:
            return
        self.clipboard_clear()
        self.clipboard_append(self._notes[sel[0]])


# ═══════════════════════════════════════════════════════════════════════════════
#  FONT PICKER DIALOG
# ═══════════════════════════════════════════════════════════════════════════════
class FontPickerDialog(tk.Toplevel):
    def __init__(self, parent, T, current_font, current_size, callback):
        super().__init__(parent)
        self.title("Font Settings")
        self.resizable(False, False)
        self.config(bg=T["panel"])
        self.transient(parent)
        self.grab_set()
        self._callback = callback

        all_fonts = sorted(set(tkfont.families()))
        mono_fonts = [f for f in all_fonts if any(k in f.lower()
                      for k in ["mono", "consol", "courier", "fixed", "code",
                                 "typewriter", "lucida console", "cascadia"])]
        display_fonts = mono_fonts + [f for f in all_fonts if f not in mono_fonts]

        self._font_var = tk.StringVar(value=current_font)
        self._size_var = tk.IntVar(value=current_size)

        tk.Label(self, text="🖋  FONT SETTINGS", bg=T["panel"], fg=T["accent"],
                 font=("Segoe UI", 11, "bold")).pack(padx=20, pady=(14, 8), anchor="w")

        row1 = tk.Frame(self, bg=T["panel"])
        row1.pack(fill="x", padx=20, pady=4)
        tk.Label(row1, text="Family:", bg=T["panel"], fg=T["subtext"],
                 font=("Segoe UI", 9), width=8, anchor="w").pack(side="left")
        self._font_cb = ttk.Combobox(row1, textvariable=self._font_var,
                                     values=display_fonts, width=26,
                                     font=("Segoe UI", 9), state="readonly")
        self._font_cb.pack(side="left")
        self._font_cb.bind("<<ComboboxSelected>>", self._preview)

        row2 = tk.Frame(self, bg=T["panel"])
        row2.pack(fill="x", padx=20, pady=4)
        tk.Label(row2, text="Size:", bg=T["panel"], fg=T["subtext"],
                 font=("Segoe UI", 9), width=8, anchor="w").pack(side="left")
        ttk.Spinbox(row2, from_=8, to=32, textvariable=self._size_var,
                    width=5, font=("Segoe UI", 9),
                    command=self._preview).pack(side="left")

        self._prev_lbl = tk.Label(self, text="The quick brown fox jumps",
                                  bg=T["input_bg"], fg=T["text"],
                                  padx=12, pady=10, relief="flat")
        self._prev_lbl.pack(fill="x", padx=20, pady=8)
        self._preview()

        btn_row = tk.Frame(self, bg=T["panel"])
        btn_row.pack(pady=(0, 14))
        ModernButton(btn_row, "Apply", self._apply, T, style="accent", size="sm").pack(side="left", padx=6)
        ModernButton(btn_row, "Cancel", self.destroy, T, style="danger", size="sm").pack(side="left", padx=6)

    def _preview(self, *_):
        try:
            f = (self._font_var.get(), self._size_var.get())
            self._prev_lbl.config(font=f)
        except Exception:
            pass

    def _apply(self):
        self._callback(self._font_var.get(), self._size_var.get())
        self.destroy()


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════
class TextToolPro(tk.Tk):
    _sidebar_frames = []
    _toolbar_btns   = []
    _action_btns    = []
    _voice_radios   = []
    _trans_combos   = []

    def __init__(self):
        super().__init__()
        self.title("Text Tool Pro  ·  v3.0 Ultimate")
        self.geometry("1360x820+60+40")
        self.minsize(1000, 640)
        self.resizable(True, True)

        # State vars
        self.T             = THEMES[_ACTIVE_THEME]
        self.theme_var     = tk.StringVar(value=_ACTIVE_THEME)
        self.voice_gender  = tk.StringVar(value="Male")
        self.speed_var     = tk.DoubleVar(value=165)
        self.volume_var    = tk.DoubleVar(value=1.0)
        self.src_lang_var  = tk.StringVar(value="english")
        self.tgt_lang_var  = tk.StringVar(value="french")
        self.status_var    = tk.StringVar(value="●  Ready")
        self.stats_var     = tk.StringVar(value="Words: 0  |  Chars: 0  |  Lines: 1")
        self.wrap_var      = tk.BooleanVar(value=True)
        self.linenum_var   = tk.BooleanVar(value=True)
        self.font_family   = "Consolas"
        self.font_size     = 11
        self.is_speaking   = False
        self.is_recording  = False
        self.history       = []
        self._autosave_job = None

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build_ui()
        self.apply_theme(_ACTIVE_THEME)
        self._animate_startup()
        self._start_autosave()
        self._restore_autosave()

    # ══════════════════════════════════════════════════════════════════════════
    #  AUTO-SAVE
    # ══════════════════════════════════════════════════════════════════════════
    def _start_autosave(self):
        self._do_autosave()

    def _do_autosave(self):
        try:
            text = self.input_text.get("1.0", "end-1c")
            if text.strip():
                autosave_write(text)
        except Exception:
            pass
        self._autosave_job = self.after(30_000, self._do_autosave)  # every 30 s

    def _restore_autosave(self):
        text = autosave_read()
        if text and text.strip():
            if messagebox.askyesno("Restore",
                                   "Auto-saved text found from your last session.\n"
                                   "Restore it to the editor?"):
                self.input_text.insert("1.0", text)
                self._on_text_change()
                self._set_status("Auto-save restored ✔", "active")

    # ══════════════════════════════════════════════════════════════════════════
    #  UI CONSTRUCTION
    # ══════════════════════════════════════════════════════════════════════════
    def _build_ui(self):
        self.columnconfigure(0, weight=0, minsize=230)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0)

        self._build_header()
        self._build_sidebar()
        self._build_main()
        self._build_statusbar()

    # ── HEADER ────────────────────────────────────────────────────────────────
    def _build_header(self):
        T = self.T
        self.header = tk.Frame(self, height=60)
        self.header.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.header.columnconfigure(1, weight=1)

        # Logo
        logo_frame = tk.Frame(self.header)
        logo_frame.grid(row=0, column=0, padx=(20, 0), pady=10, sticky="w")

        self.lbl_dot = tk.Label(logo_frame, text="⬡", font=("Segoe UI", 18, "bold"))
        self.lbl_dot.pack(side="left", padx=(0, 6))

        logo_right = tk.Frame(logo_frame)
        logo_right.pack(side="left")
        self.lbl_logo = tk.Label(logo_right, text="TEXT TOOL PRO",
                                 font=("Segoe UI", 13, "bold"))
        self.lbl_logo.pack(anchor="w")
        self.lbl_sub = tk.Label(logo_right, text="Ultimate Edition  v3.0",
                                font=("Segoe UI", 7))
        self.lbl_sub.pack(anchor="w")

        # Tab pills
        tab_frame = tk.Frame(self.header)
        tab_frame.grid(row=0, column=1, padx=20, sticky="w")
        self._tab_btns = {}
        for tab in ["Editor", "Translate", "History"]:
            b = tk.Button(tab_frame, text=tab,
                          font=("Segoe UI", 9, "bold"),
                          relief="flat", bd=0, cursor="hand2",
                          padx=14, pady=5,
                          command=lambda t=tab: self._switch_tab(t))
            b.pack(side="left", padx=2)
            self._tab_btns[tab] = b
        self._current_tab = "Editor"

        # Right controls
        right = tk.Frame(self.header)
        right.grid(row=0, column=2, padx=20, pady=10, sticky="e")

        # Font button
        self.font_btn = tk.Button(right, text="🖋 Font", font=("Segoe UI", 8, "bold"),
                                  relief="flat", bd=0, cursor="hand2",
                                  padx=8, pady=4, command=self._open_font_picker)
        self.font_btn.pack(side="left", padx=4)

        # Wrap toggle
        self.wrap_chk = tk.Checkbutton(right, text="Wrap", variable=self.wrap_var,
                                       font=("Segoe UI", 8), cursor="hand2",
                                       command=self._toggle_wrap)
        self.wrap_chk.pack(side="left", padx=4)

        # Line numbers toggle
        self.linenum_chk = tk.Checkbutton(right, text="Lines", variable=self.linenum_var,
                                          font=("Segoe UI", 8), cursor="hand2",
                                          command=self._toggle_line_numbers)
        self.linenum_chk.pack(side="left", padx=4)

        # Theme selector
        tk.Label(right, text="THEME", font=("Segoe UI", 7, "bold")).pack(
            side="left", padx=(8, 4))
        self.theme_cb = ttk.Combobox(right, textvariable=self.theme_var,
                                     values=list(THEMES.keys()), width=13,
                                     state="readonly", font=("Segoe UI", 9))
        self.theme_cb.pack(side="left", padx=(0, 8))
        self.theme_cb.bind("<<ComboboxSelected>>",
                           lambda e: self.apply_theme(self.theme_var.get()))

        # Notes & mode
        self.notes_btn = tk.Button(right, text="📌 Notes",
                                   font=("Segoe UI", 8, "bold"), relief="flat", bd=0,
                                   cursor="hand2", padx=8, pady=4,
                                   command=self._open_notes)
        self.notes_btn.pack(side="left", padx=4)

        self.mode_btn = tk.Button(right, text="📄  Text Mode",
                                  font=("Segoe UI", 9, "bold"), relief="flat", bd=0,
                                  cursor="hand2", padx=10, pady=5,
                                  command=self._toggle_mode)
        self.mode_btn.pack(side="left", padx=4)

    # ── SIDEBAR ───────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        self.sidebar = tk.Frame(self, width=230)
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        self.sidebar.pack_propagate(False)
        self.sidebar.columnconfigure(0, weight=1)

        self._sb_canvas    = tk.Canvas(self.sidebar, highlightthickness=0)
        self._sb_scrollbar = ttk.Scrollbar(self.sidebar, orient="vertical",
                                           command=self._sb_canvas.yview)
        self._sb_canvas.configure(yscrollcommand=self._sb_scrollbar.set)
        self._sb_scrollbar.pack(side="right", fill="y")
        self._sb_canvas.pack(side="left", fill="both", expand=True)

        self._sb_inner  = tk.Frame(self._sb_canvas)
        self._sb_window = self._sb_canvas.create_window((0, 0), window=self._sb_inner,
                                                         anchor="nw")
        self._sb_inner.bind("<Configure>", self._on_sb_configure)
        self._sb_canvas.bind("<Configure>", self._on_sb_resize)

        # Mouse-wheel scrolling on sidebar
        self._sb_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self._build_sb_voice()
        self._sb_sep()
        self._build_sb_translate()
        self._sb_sep()
        self._build_sb_files()
        self._sb_sep()
        self._build_sb_tools()

    def _on_mousewheel(self, event):
        try:
            self._sb_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass

    def _sb_sep(self):
        tk.Frame(self._sb_inner, height=1).pack(fill="x", padx=14, pady=6)

    def _sb_section(self, title):
        tk.Label(self._sb_inner, text=title,
                 font=("Segoe UI", 8, "bold"), anchor="w").pack(
                 fill="x", padx=14, pady=(10, 4))

    def _build_sb_voice(self):
        T = self.T
        self._sb_section("🔊  VOICE  &  SPEECH")
        frm = tk.Frame(self._sb_inner)
        frm.pack(fill="x", padx=10, pady=2)

        g_row = tk.Frame(frm)
        g_row.pack(fill="x", pady=3)
        tk.Label(g_row, text="Gender", font=("Segoe UI", 8),
                 width=8, anchor="w").pack(side="left", padx=(4, 0))
        self._voice_radios = []
        for gender in ("Male", "Female"):
            rb = tk.Radiobutton(g_row, text=gender, variable=self.voice_gender,
                                value=gender, font=("Segoe UI", 8),
                                relief="flat", cursor="hand2")
            rb.pack(side="left", padx=3)
            self._voice_radios.append(rb)

        self._make_slider(frm, "Speed",  self.speed_var,  50, 350, "spd_lbl", "%d wpm", int)
        self._make_slider(frm, "Volume", self.volume_var, 0.0, 1.0, "vol_lbl",
                          "%.0f%%", lambda v: float(v) * 100)

        v_row = tk.Frame(frm)
        v_row.pack(fill="x", pady=3)
        tk.Label(v_row, text="Voice", font=("Segoe UI", 8),
                 width=8, anchor="w").pack(side="left", padx=(4, 0))
        self.voice_name_var = tk.StringVar(value="Auto (by gender)")
        self.voice_cb = ttk.Combobox(v_row, textvariable=self.voice_name_var,
                                     font=("Segoe UI", 8), state="readonly", width=14)
        self.voice_cb.pack(side="right", padx=2)
        self._populate_voice_dropdown()

        sb_btn_frame = tk.Frame(frm)
        sb_btn_frame.pack(fill="x", pady=(6, 2))

        self.speak_btn = ModernButton(sb_btn_frame, "▶  Speak", self._speak,
                                     T, style="accent", size="sm")
        self.speak_btn.pack(side="left", padx=2, fill="x", expand=True)

        self.stop_btn = ModernButton(sb_btn_frame, "■  Stop", self._stop_speak,
                                    T, style="danger", size="sm")
        self.stop_btn.pack(side="left", padx=2, fill="x", expand=True)

        self.rec_btn = ModernButton(frm, "🎙  Record Microphone", self._record,
                                   T, style="normal", size="sm")
        self.rec_btn.pack(fill="x", padx=2, pady=(3, 0))

    def _make_slider(self, parent, label, var, from_, to, lbl_attr, fmt, val_fn=None):
        row = tk.Frame(parent)
        row.pack(fill="x", pady=3)
        tk.Label(row, text=label, font=("Segoe UI", 8),
                 width=8, anchor="w").pack(side="left", padx=(4, 0))
        lbl = tk.Label(row, font=("Segoe UI", 8, "bold"), width=7, anchor="e")
        lbl.pack(side="right", padx=(0, 4))
        setattr(self, lbl_attr, lbl)

        def _update(v):
            val = val_fn(float(v)) if val_fn else float(v)
            lbl.config(text=fmt % val)

        sc = ttk.Scale(parent, from_=from_, to=to, orient="horizontal",
                       variable=var, command=_update)
        sc.pack(fill="x", padx=6, pady=2)
        _update(var.get())
        return sc

    def _build_sb_translate(self):
        T = self.T
        self._sb_section("🌐  TRANSLATION")
        frm = tk.Frame(self._sb_inner)
        frm.pack(fill="x", padx=10, pady=2)

        self._trans_combos = []

        src_row = tk.Frame(frm)
        src_row.pack(fill="x", pady=2)
        tk.Label(src_row, text="From", font=("Segoe UI", 8),
                 width=5, anchor="w").pack(side="left", padx=(4, 0))
        src_langs = ["auto-detect (source only)"] + [v for k, v in LANG_MAP.items() if k != "auto"]
        src_cb = ttk.Combobox(src_row, textvariable=self.src_lang_var,
                              values=src_langs, font=("Segoe UI", 8),
                              state="readonly", width=15)
        src_cb.pack(side="right", padx=2)
        self._trans_combos.append(src_cb)

        swap_row = tk.Frame(frm)
        swap_row.pack(fill="x", pady=1)
        swap_btn = tk.Button(swap_row, text="⇅  Swap Languages",
                             command=self._swap_languages,
                             font=("Segoe UI", 8), relief="flat", bd=0,
                             cursor="hand2", padx=6, pady=2)
        swap_btn.pack(side="right", padx=2)
        self._swap_btn = swap_btn

        tgt_row = tk.Frame(frm)
        tgt_row.pack(fill="x", pady=2)
        tk.Label(tgt_row, text="To", font=("Segoe UI", 8),
                 width=5, anchor="w").pack(side="left", padx=(4, 0))
        tgt_langs = [v for k, v in LANG_MAP.items() if k != "auto"]
        tgt_cb = ttk.Combobox(tgt_row, textvariable=self.tgt_lang_var,
                              values=tgt_langs, font=("Segoe UI", 8),
                              state="readonly", width=15)
        tgt_cb.pack(side="right", padx=2)
        self._trans_combos.append(tgt_cb)

        self._trans_btn_holder = tk.Frame(frm)
        self._trans_btn_holder.pack(fill="x", pady=(6, 2))

    def _build_sb_files(self):
        self._sb_section("📁  FILES")
        self._file_frame = tk.Frame(self._sb_inner)
        self._file_frame.pack(fill="x", padx=10, pady=2)

    def _build_sb_tools(self):
        self._sb_section("🛠️  TEXT TOOLS")
        frm = tk.Frame(self._sb_inner)
        frm.pack(fill="x", padx=10, pady=2)
        self._tools_frame = frm

    def _on_sb_configure(self, event=None):
        self._sb_canvas.configure(scrollregion=self._sb_canvas.bbox("all"))

    def _on_sb_resize(self, event):
        self._sb_canvas.itemconfig(self._sb_window, width=event.width)

    # ── MAIN PANEL ────────────────────────────────────────────────────────────
    def _build_main(self):
        self.main_frame = tk.Frame(self)
        self.main_frame.grid(row=1, column=1, sticky="nsew")
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        self.tab_container = tk.Frame(self.main_frame)
        self.tab_container.grid(row=0, column=0, rowspan=10, sticky="nsew")
        self.tab_container.columnconfigure(0, weight=1)
        self.tab_container.rowconfigure(0, weight=1)

        self._build_editor_tab()
        self._build_translate_tab()
        self._build_history_tab()
        self._switch_tab("Editor")

    def _build_editor_tab(self):
        T = self.T
        self.editor_tab = tk.Frame(self.tab_container)
        self.editor_tab.columnconfigure(0, weight=1)
        self.editor_tab.rowconfigure(1, weight=3)
        self.editor_tab.rowconfigure(4, weight=2)

        # Toolbar
        self.toolbar = tk.Frame(self.editor_tab)
        self.toolbar.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 4))
        self._build_toolbar()

        # Input area
        in_wrapper = tk.Frame(self.editor_tab)
        in_wrapper.grid(row=1, column=0, sticky="nsew", padx=14, pady=(4, 0))
        in_wrapper.columnconfigure(1, weight=1)
        in_wrapper.rowconfigure(1, weight=1)

        in_hdr = tk.Frame(in_wrapper)
        in_hdr.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 4))
        tk.Label(in_hdr, text="INPUT", font=("Segoe UI", 8, "bold")).pack(side="left")
        self.input_info = tk.Label(in_hdr, text="", font=("Segoe UI", 8))
        self.input_info.pack(side="right")
        # Readability live label
        self.readability_lbl = tk.Label(in_hdr, text="", font=("Segoe UI", 7))
        self.readability_lbl.pack(side="right", padx=8)

        # Line number canvas
        self.line_num_canvas = LineNumberCanvas(in_wrapper, None, T)  # placeholder, set below

        self.input_text = tk.Text(in_wrapper, wrap="word", relief="flat",
                                  font=(self.font_family, self.font_size),
                                  bd=0, undo=True,
                                  insertwidth=2, spacing1=2, spacing3=2,
                                  padx=12, pady=10)

        # Now connect line num canvas to the real text widget
        self.line_num_canvas.attach_text(self.input_text)
        self.line_num_canvas.grid(row=1, column=0, sticky="ns")

        self.input_text.grid(row=1, column=1, sticky="nsew")
        in_sb = ttk.Scrollbar(in_wrapper, orient="vertical",
                               command=self._sync_scroll)
        in_sb.grid(row=1, column=2, sticky="ns")
        self.input_text.config(yscrollcommand=lambda f, l: (in_sb.set(f, l),
                                                              self.line_num_canvas.redraw()))
        self.input_text.bind("<KeyRelease>",    self._on_text_change)
        self.input_text.bind("<ButtonRelease>", self._on_text_change)

        # Drag & Drop paste on input area
        self.input_text.bind("<Control-v>", lambda e: self._on_text_change())

        # Action bar
        self.action_bar = tk.Frame(self.editor_tab)
        self.action_bar.grid(row=2, column=0, sticky="ew", padx=14, pady=8)
        self._build_action_bar()

        # Separator
        tk.Frame(self.editor_tab, height=1).grid(row=3, column=0, sticky="ew", padx=14)

        # Output area
        out_wrapper = tk.Frame(self.editor_tab)
        out_wrapper.grid(row=4, column=0, sticky="nsew", padx=14, pady=(6, 14))
        out_wrapper.columnconfigure(0, weight=1)
        out_wrapper.rowconfigure(1, weight=1)

        out_hdr = tk.Frame(out_wrapper)
        out_hdr.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 4))
        tk.Label(out_hdr, text="OUTPUT  ·  Translation / Summary / Result",
                 font=("Segoe UI", 8, "bold")).pack(side="left")

        # Output buttons
        for txt, cmd in [("📋 Copy", self._copy_output),
                          ("📤 Export Output", self._export_output)]:
            tk.Button(out_hdr, text=txt,
                      font=("Segoe UI", 7), relief="flat",
                      bd=0, cursor="hand2", padx=6, pady=2,
                      command=cmd).pack(side="right", padx=4)
        self.copy_output_btn = out_hdr.winfo_children()[-1]  # for theming

        self.output_text = tk.Text(out_wrapper, wrap="word", relief="flat",
                                   font=(self.font_family, self.font_size),
                                   bd=0, state="disabled",
                                   padx=12, pady=10, spacing1=2, spacing3=2)
        self.output_text.grid(row=1, column=0, sticky="nsew")
        out_sb = ttk.Scrollbar(out_wrapper, orient="vertical",
                               command=self.output_text.yview)
        out_sb.grid(row=1, column=1, sticky="ns")
        self.output_text.config(yscrollcommand=out_sb.set)

        # Keyboard shortcuts
        self.bind_all("<Control-z>",     lambda e: self.input_text.edit_undo())
        self.bind_all("<Control-y>",     lambda e: self.input_text.edit_redo())
        self.bind_all("<Control-f>",     lambda e: self._open_find())
        self.bind_all("<Control-s>",     lambda e: self._save_text())
        self.bind_all("<Control-o>",     lambda e: self._open_pdf())
        self.bind_all("<Control-Return>",lambda e: self._speak())

    def _sync_scroll(self, *args):
        self.input_text.yview(*args)
        self.line_num_canvas.redraw()

    def _build_translate_tab(self):
        T = self.T
        self.translate_tab = tk.Frame(self.tab_container)
        self.translate_tab.columnconfigure(0, weight=1)
        self.translate_tab.columnconfigure(2, weight=1)
        self.translate_tab.rowconfigure(1, weight=1)

        hdr = tk.Frame(self.translate_tab)
        hdr.grid(row=0, column=0, columnspan=3, sticky="ew", padx=16, pady=(14, 6))
        tk.Label(hdr, text="🌐  TRANSLATE",
                 font=("Segoe UI", 13, "bold")).pack(side="left")
        tk.Label(hdr, text="  ·  supports 100+ languages  ·  auto-detect source",
                 font=("Segoe UI", 9)).pack(side="left", padx=6)

        lang_bar = tk.Frame(self.translate_tab)
        lang_bar.grid(row=0, column=0, columnspan=3, sticky="ew", padx=16, pady=(48, 0))
        lang_bar.columnconfigure(0, weight=1)
        lang_bar.columnconfigure(2, weight=1)

        src_frame = tk.Frame(lang_bar)
        src_frame.grid(row=0, column=0, sticky="ew")
        tk.Label(src_frame, text="SOURCE LANGUAGE", font=("Segoe UI", 7, "bold")).pack(anchor="w")
        src_langs = ["auto-detect (source only)"] + [v for k, v in LANG_MAP.items() if k != "auto"]
        self.tr_src_cb = ttk.Combobox(src_frame, textvariable=self.src_lang_var,
                                      values=src_langs, font=("Segoe UI", 10),
                                      state="readonly", width=22)
        self.tr_src_cb.pack(fill="x", pady=(2, 0))

        mid_frame = tk.Frame(lang_bar)
        mid_frame.grid(row=0, column=1, padx=10)
        tk.Button(mid_frame, text="⇄", font=("Segoe UI", 16, "bold"),
                  relief="flat", bd=0, cursor="hand2",
                  command=self._swap_languages).pack(pady=14)

        tgt_frame = tk.Frame(lang_bar)
        tgt_frame.grid(row=0, column=2, sticky="ew")
        tk.Label(tgt_frame, text="TARGET LANGUAGE", font=("Segoe UI", 7, "bold")).pack(anchor="w")
        tgt_langs = [v for k, v in LANG_MAP.items() if k != "auto"]
        self.tr_tgt_cb = ttk.Combobox(tgt_frame, textvariable=self.tgt_lang_var,
                                      values=tgt_langs, font=("Segoe UI", 10),
                                      state="readonly", width=22)
        self.tr_tgt_cb.pack(fill="x", pady=(2, 0))

        # Left = input
        left = tk.Frame(self.translate_tab)
        left.grid(row=1, column=0, sticky="nsew", padx=(14, 4), pady=10)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)
        tk.Label(left, text="INPUT TEXT", font=("Segoe UI", 8, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 4))
        self.tr_input = tk.Text(left, wrap="word", relief="flat",
                                font=("Consolas", 11), bd=0, undo=True,
                                insertwidth=2, spacing1=2, spacing3=2,
                                padx=12, pady=10)
        self.tr_input.grid(row=1, column=0, sticky="nsew")
        tr_in_sb = ttk.Scrollbar(left, orient="vertical", command=self.tr_input.yview)
        tr_in_sb.grid(row=1, column=1, sticky="ns")
        self.tr_input.config(yscrollcommand=tr_in_sb.set)

        tr_btn_left = tk.Frame(left)
        tr_btn_left.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(4, 0))
        tk.Button(tr_btn_left, text="📋 Paste", relief="flat", bd=0,
                  font=("Segoe UI", 8), cursor="hand2",
                  command=lambda: (self.tr_input.insert("insert",
                                   self.clipboard_get()),)).pack(side="left", padx=2)
        tk.Button(tr_btn_left, text="🗑 Clear", relief="flat", bd=0,
                  font=("Segoe UI", 8), cursor="hand2",
                  command=lambda: self.tr_input.delete("1.0", "end")).pack(side="left")
        tk.Button(tr_btn_left, text="← Use Editor Text", relief="flat", bd=0,
                  font=("Segoe UI", 8), cursor="hand2",
                  command=self._tr_pull_from_editor).pack(side="right", padx=4)

        # Center translate button
        center = tk.Frame(self.translate_tab)
        center.grid(row=1, column=1, sticky="ns", padx=4, pady=10)
        tk.Button(center, text="▶\nT\nR\nA\nN\nS\nL\nA\nT\nE",
                  font=("Segoe UI", 9, "bold"),
                  relief="flat", bd=0, cursor="hand2",
                  width=3, padx=6, pady=10,
                  command=self._tr_panel_translate).pack(expand=True)
        self._tr_go_btn = center.winfo_children()[0]

        # Right = output
        right = tk.Frame(self.translate_tab)
        right.grid(row=1, column=2, sticky="nsew", padx=(4, 14), pady=10)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        out_hdr = tk.Frame(right)
        out_hdr.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 4))
        tk.Label(out_hdr, text="TRANSLATED TEXT",
                 font=("Segoe UI", 8, "bold")).pack(side="left")
        tk.Button(out_hdr, text="📋 Copy", relief="flat", bd=0,
                  font=("Segoe UI", 7), cursor="hand2",
                  command=self._tr_copy_output).pack(side="right")
        tk.Button(out_hdr, text="→ Send to Editor", relief="flat", bd=0,
                  font=("Segoe UI", 7), cursor="hand2",
                  command=self._tr_send_to_editor).pack(side="right", padx=4)
        # Speak translation button
        tk.Button(out_hdr, text="🔊 Speak", relief="flat", bd=0,
                  font=("Segoe UI", 7), cursor="hand2",
                  command=self._tr_speak_output).pack(side="right", padx=4)

        self.tr_output = tk.Text(right, wrap="word", relief="flat",
                                 font=("Consolas", 11), bd=0, state="disabled",
                                 padx=12, pady=10, spacing1=2, spacing3=2)
        self.tr_output.grid(row=1, column=0, sticky="nsew")
        tr_out_sb = ttk.Scrollbar(right, orient="vertical",
                                  command=self.tr_output.yview)
        tr_out_sb.grid(row=1, column=1, sticky="ns")
        self.tr_output.config(yscrollcommand=tr_out_sb.set)

    def _build_history_tab(self):
        T = self.T
        self.history_tab = tk.Frame(self.tab_container)
        self.history_tab.columnconfigure(0, weight=1)
        self.history_tab.rowconfigure(1, weight=1)

        hdr_row = tk.Frame(self.history_tab)
        hdr_row.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 8))
        tk.Label(hdr_row, text="📝  SESSION HISTORY",
                 font=("Segoe UI", 12, "bold"), anchor="w").pack(side="left")
        # Search bar for history
        tk.Label(hdr_row, text="Search:", font=("Segoe UI", 8)).pack(side="left", padx=(16, 4))
        self._hist_search_var = tk.StringVar()
        self._hist_search_var.trace_add("write", self._filter_history)
        tk.Entry(hdr_row, textvariable=self._hist_search_var,
                 font=("Segoe UI", 9), width=20,
                 relief="flat").pack(side="left")

        pane = tk.Frame(self.history_tab)
        pane.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        pane.columnconfigure(0, weight=1)
        pane.columnconfigure(1, weight=2)
        pane.rowconfigure(0, weight=1)

        list_frame = tk.Frame(pane)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        self.history_lb = tk.Listbox(list_frame, font=("Segoe UI", 9),
                                     relief="flat", bd=0, selectmode="single",
                                     activestyle="none")
        h_sb = ttk.Scrollbar(list_frame, orient="vertical",
                              command=self.history_lb.yview)
        self.history_lb.config(yscrollcommand=h_sb.set)
        self.history_lb.grid(row=0, column=0, sticky="nsew")
        h_sb.grid(row=0, column=1, sticky="ns")
        self.history_lb.bind("<<ListboxSelect>>", self._preview_history)

        detail_frame = tk.Frame(pane)
        detail_frame.grid(row=0, column=1, sticky="nsew")
        detail_frame.rowconfigure(1, weight=1)
        detail_frame.columnconfigure(0, weight=1)

        tk.Label(detail_frame, text="Preview", font=("Segoe UI", 9, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 4))
        self.hist_preview = tk.Text(detail_frame, wrap="word", font=("Consolas", 10),
                                    relief="flat", bd=0, state="disabled",
                                    padx=10, pady=8)
        self.hist_preview.grid(row=1, column=0, sticky="nsew")
        hp_sb = ttk.Scrollbar(detail_frame, orient="vertical",
                               command=self.hist_preview.yview)
        hp_sb.grid(row=1, column=1, sticky="ns")
        self.hist_preview.config(yscrollcommand=hp_sb.set)

        btn_row = tk.Frame(pane)
        btn_row.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ModernButton(btn_row, "Load to Editor",  self._load_from_history, T,
                     style="accent", size="sm").pack(side="left", padx=4)
        ModernButton(btn_row, "Delete Entry",    self._delete_history_entry, T,
                     style="normal", size="sm").pack(side="left", padx=4)
        ModernButton(btn_row, "Export History",  self._export_history, T,
                     style="normal", size="sm").pack(side="left", padx=4)
        ModernButton(btn_row, "Clear History",   self._clear_history, T,
                     style="danger", size="sm").pack(side="left", padx=4)

    # ── TOOLBAR ───────────────────────────────────────────────────────────────
    def _build_toolbar(self):
        tb = self.toolbar
        self._toolbar_btns = []

        groups = [
            [("📋", "Copy",  self._copy_input),
             ("📌", "Paste", self._paste_input),
             ("🗑️", "Clear", self._clear_all)],
            [("↩", "Undo", lambda: self.input_text.edit_undo()),
             ("↪", "Redo", lambda: self.input_text.edit_redo())],
            [("🔍", "Find",  self._open_find)],
            [("AA", "UPPER", lambda: self._transform("upper")),
             ("aa", "lower", lambda: self._transform("lower")),
             ("Aa", "Title", lambda: self._transform("title")),
             ("↔", "Trim",  self._trim_whitespace)],
            [("¶",  "Count Sentences", self._count_sentences_action),
             ("#",  "Word Freq",       lambda: self._analyze())],
        ]

        for i, group in enumerate(groups):
            if i > 0:
                tk.Frame(tb, width=1, height=22).pack(side="left", padx=6)
            for icon, label, cmd in group:
                b = tk.Button(tb, text=f"{icon}", command=cmd,
                              font=("Segoe UI", 9), relief="flat", bd=0,
                              cursor="hand2", padx=8, pady=4)
                b.pack(side="left", padx=1)
                b._style = "normal"
                # Tooltip
                self._add_tooltip(b, label)
                self._toolbar_btns.append(b)

    def _add_tooltip(self, widget, text):
        tip = None
        def show(e):
            nonlocal tip
            x = widget.winfo_rootx() + 4
            y = widget.winfo_rooty() + widget.winfo_height() + 4
            tip = tk.Toplevel(widget)
            tip.wm_overrideredirect(True)
            tip.wm_geometry(f"+{x}+{y}")
            tk.Label(tip, text=text, font=("Segoe UI", 8),
                     bg=self.T["card"], fg=self.T["text"],
                     padx=6, pady=3, relief="flat").pack()
        def hide(e):
            nonlocal tip
            if tip:
                try: tip.destroy()
                except Exception: pass
                tip = None
        widget.bind("<Enter>", show)
        widget.bind("<Leave>", hide)

    # ── ACTION BAR ────────────────────────────────────────────────────────────
    def _build_action_bar(self):
        ab = self.action_bar
        T  = self.T
        self._action_btns = []

        actions = [
            ("▶  Speak",      self._speak,      "accent"),
            ("■  Stop",       self._stop_speak, "danger"),
            ("🌐  Translate", self._translate,  "accent"),
            ("📊  Analyze",   self._analyze,    "normal"),
            ("📝  Summarize", self._summarize,  "normal"),
            ("💾  Save Text", self._save_text,  "normal"),
            ("🎵  Save MP3",  self._save_audio, "normal"),
        ]
        for lbl, cmd, sty in actions:
            b = ModernButton(ab, lbl, cmd, T, style=sty, size="md")
            b.pack(side="left", padx=3)
            self._action_btns.append((b, sty))

    # ── STATUS BAR ────────────────────────────────────────────────────────────
    def _build_statusbar(self):
        self.statusbar = tk.Frame(self, height=26)
        self.statusbar.grid(row=2, column=0, columnspan=2, sticky="ew")

        self._status_dot = StatusDot(self.statusbar, self.T)
        self._status_dot.pack(side="left", padx=(14, 4), pady=4)

        tk.Label(self.statusbar, textvariable=self.status_var,
                 font=("Segoe UI", 8)).pack(side="left")

        tk.Label(self.statusbar, textvariable=self.stats_var,
                 font=("Segoe UI", 8)).pack(side="right", padx=14)

        lib_frame = tk.Frame(self.statusbar)
        lib_frame.pack(side="right", padx=8)
        for lib, ok, color in [("TTS", TTS_OK, "accent2"),
                                ("STT", SR_OK,  "accent"),
                                ("PDF", PDF_OK, "warning"),
                                ("GT",  GT_OK,  "accent2")]:
            bg = self.T[color] if ok else self.T["subtext"]
            tk.Label(lib_frame, text=lib, bg=bg, fg=self.T["bg"],
                     font=("Segoe UI", 6, "bold"),
                     padx=4, pady=1).pack(side="left", padx=1)

    # ══════════════════════════════════════════════════════════════════════════
    #  THEME ENGINE
    # ══════════════════════════════════════════════════════════════════════════
    def apply_theme(self, name: str = None):
        global _ACTIVE_THEME
        if name:
            _ACTIVE_THEME = name
        self.T = THEMES[_ACTIVE_THEME]
        T = self.T

        self.config(bg=T["bg"])

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".",             background=T["bg"],    foreground=T["text"])
        style.configure("TFrame",        background=T["bg"])
        style.configure("TLabel",        background=T["bg"],    foreground=T["text"])
        style.configure("TCombobox",
                         fieldbackground=T["panel"],
                         background=T["panel"],
                         foreground=T["text"],
                         selectbackground=T["highlight"],
                         selectforeground=T["text"],
                         arrowcolor=T["accent"])
        style.map("TCombobox", fieldbackground=[("readonly", T["panel"])])
        style.configure("TScrollbar",
                         background=T["scrollbar"],
                         troughcolor=T["bg"],
                         arrowcolor=T["subtext"],
                         relief="flat")
        style.configure("TScale",
                         background=T["bg"],
                         troughcolor=T["panel"],
                         sliderlength=14)
        style.configure("TRadiobutton",
                         background=T["sidebar"],
                         foreground=T["text"])
        style.configure("TSpinbox",
                         fieldbackground=T["panel"],
                         background=T["panel"],
                         foreground=T["text"])

        self._paint_widget(self)

        # Specific overrides
        try:
            self.header.config(bg=T["sidebar"])
            self.lbl_dot.config(bg=T["sidebar"], fg=T["accent"])
            self.lbl_logo.config(bg=T["sidebar"], fg=T["text"])
            self.lbl_sub.config(bg=T["sidebar"], fg=T["subtext"])
            self.mode_btn.config(bg=T["panel"],   fg=T["accent"],
                                 activebackground=T["btn_hover"])
            self.notes_btn.config(bg=T["panel"],  fg=T["accent"],
                                  activebackground=T["btn_hover"])
            self.font_btn.config(bg=T["panel"],   fg=T["accent"],
                                 activebackground=T["btn_hover"])
            self.wrap_chk.config(bg=T["sidebar"], fg=T["text"],
                                 selectcolor=T["card"],
                                 activebackground=T["sidebar"])
            self.linenum_chk.config(bg=T["sidebar"], fg=T["text"],
                                    selectcolor=T["card"],
                                    activebackground=T["sidebar"])
        except Exception:
            pass

        try:
            self.statusbar.config(bg=T["panel"])
            self._status_dot._T = T
            self._status_dot.config(bg=T["panel"])
        except Exception:
            pass

        try:
            self.line_num_canvas.recolor(T)
        except Exception:
            pass

        self._rebuild_dynamic_btns()

    def _paint_widget(self, w):
        T   = self.T
        cls = w.winfo_class()
        try:
            path       = str(w)
            in_sidebar = hasattr(self, "sidebar")   and path.startswith(str(self.sidebar))
            in_header  = hasattr(self, "header")    and path.startswith(str(self.header))
            in_status  = hasattr(self, "statusbar") and path.startswith(str(self.statusbar))

            if cls == "Frame":
                if in_sidebar: w.config(bg=T["sidebar"])
                elif in_header: w.config(bg=T["sidebar"])
                elif in_status: w.config(bg=T["panel"])
                else: w.config(bg=T["bg"])

            elif cls == "Label":
                if in_sidebar:
                    txt = w.cget("text")
                    is_sec = any(x in txt for x in ["🔊","🌐","📁","🛠️","▶","■"])
                    fg = T["subtext"] if not is_sec else T["text"]
                    w.config(bg=T["sidebar"], fg=fg)
                elif in_header: w.config(bg=T["sidebar"], fg=T["text"])
                elif in_status: w.config(bg=T["panel"],   fg=T["subtext"])
                else:           w.config(bg=T["bg"],      fg=T["text"])

            elif cls == "Button":
                if in_sidebar:
                    w.config(bg=T["sidebar"], fg=T["text"],
                             activebackground=T["btn_hover"])
                elif in_header:
                    w.config(bg=T["sidebar"], fg=T["text"],
                             activebackground=T["btn_hover"])
                else:
                    w.config(bg=T["btn_bg"], fg=T["text"],
                             activebackground=T["btn_hover"])

            elif cls == "Text":
                w.config(bg=T["input_bg"], fg=T["text"],
                         insertbackground=T["accent"],
                         selectbackground=T["highlight"],
                         selectforeground=T["text"])

            elif cls == "Listbox":
                w.config(bg=T["panel"], fg=T["text"],
                         selectbackground=T["highlight"],
                         selectforeground=T["text"])

            elif cls == "Entry":
                w.config(bg=T["input_bg"], fg=T["text"],
                         insertbackground=T["accent"])

            elif cls == "Radiobutton":
                w.config(bg=T["sidebar"] if in_sidebar else T["bg"],
                         fg=T["text"],
                         activebackground=T["sidebar"],
                         selectcolor=T["card"])

            elif cls == "Checkbutton":
                bg = T["sidebar"] if in_header else T["bg"]
                w.config(bg=bg, fg=T["text"],
                         activebackground=bg,
                         selectcolor=T["card"])

            elif cls == "Canvas":
                if in_sidebar:
                    w.config(bg=T["sidebar"])

        except Exception:
            pass

        for child in w.winfo_children():
            self._paint_widget(child)

    def _rebuild_dynamic_btns(self):
        T = self.T

        try:
            for c in self._trans_btn_holder.winfo_children():
                c.destroy()
            ModernButton(self._trans_btn_holder, "🌐  Translate Now",
                         self._translate, T, style="accent", size="sm").pack(
                         fill="x", padx=2)
        except Exception:
            pass

        try:
            for c in self._file_frame.winfo_children():
                c.destroy()
            file_actions = [
                ("📂  Open PDF",        self._open_pdf),
                ("🎤  Open Audio File", self._open_audio),
                ("📄  Open Text File",  self._open_text_file),
                ("💾  Save as TXT",     self._save_text),
                ("🎵  Export as MP3",   self._save_audio),
                ("📤  Copy Output",     self._copy_output),
            ]
            for lbl, cmd in file_actions:
                b = tk.Button(self._file_frame, text=lbl, command=cmd,
                              font=("Segoe UI", 8), relief="flat", bd=0,
                              cursor="hand2", padx=8, pady=5, anchor="w",
                              bg=T["btn_bg"], fg=T["text"],
                              activebackground=T["btn_hover"],
                              activeforeground=T["text"])
                b.pack(fill="x", pady=1)
        except Exception:
            pass

        try:
            for c in self._tools_frame.winfo_children():
                c.destroy()
            tools = [
                ("UPPER CASE",          lambda: self._transform("upper")),
                ("lower case",          lambda: self._transform("lower")),
                ("Title Case",          lambda: self._transform("title")),
                ("Trim Whitespace",     self._trim_whitespace),
                ("Remove Duplicates",   self._remove_duplicate_lines),
                ("Sort Lines A→Z",      lambda: self._sort_lines(False)),
                ("Sort Lines Z→A",      lambda: self._sort_lines(True)),
                ("Count Sentences",     self._count_sentences_action),
                ("Reverse Lines",       self._reverse_lines),
                ("Number Lines",        self._number_lines),
                ("Remove Blank Lines",  self._remove_blank_lines),
                ("Word Count Report",   self._word_count_report),
            ]
            for lbl, cmd in tools:
                b = tk.Button(self._tools_frame, text=lbl, command=cmd,
                              font=("Segoe UI", 8), relief="flat", bd=0,
                              cursor="hand2", padx=8, pady=4, anchor="w",
                              bg=T["btn_bg"], fg=T["text"],
                              activebackground=T["btn_hover"],
                              activeforeground=T["text"])
                b.pack(fill="x", pady=1)
        except Exception:
            pass

        try:
            for btn, sty in self._action_btns:
                btn.recolor(T, sty)
        except Exception:
            pass

        try:
            for tab, b in self._tab_btns.items():
                is_active = (tab == self._current_tab)
                b.config(bg=T["accent"] if is_active else T["panel"],
                         fg=T["bg"] if is_active else T["subtext"],
                         activebackground=T["highlight"])
        except Exception:
            pass

        try:
            for f in self._sb_inner.winfo_children():
                if isinstance(f, tk.Frame) and f.cget("height") == 1:
                    f.config(bg=T["sep"])
        except Exception:
            pass

        self._sb_canvas.config(bg=T["sidebar"])
        self._sb_inner.config(bg=T["sidebar"])

        try:
            self.copy_output_btn.config(bg=T["bg"], fg=T["subtext"],
                                        activebackground=T["btn_hover"])
        except Exception:
            pass

        try:
            for tw in (self.tr_input, self.tr_output):
                tw.config(bg=T["input_bg"], fg=T["text"],
                          insertbackground=T["accent"],
                          selectbackground=T["highlight"])
            self._tr_go_btn.config(bg=T["accent"], fg=T["bg"],
                                   activebackground=T["highlight"])
        except Exception:
            pass

        try:
            self.readability_lbl.config(bg=T["bg"], fg=T["accent2"])
        except Exception:
            pass

    # ══════════════════════════════════════════════════════════════════════════
    #  TAB NAVIGATION
    # ══════════════════════════════════════════════════════════════════════════
    def _switch_tab(self, tab: str):
        T = self.T
        self._current_tab = tab
        self.editor_tab.grid_forget()
        self.translate_tab.grid_forget()
        self.history_tab.grid_forget()

        mapping = {
            "Editor":    self.editor_tab,
            "Translate": self.translate_tab,
            "History":   self.history_tab,
        }
        mapping[tab].grid(row=0, column=0, sticky="nsew")
        self.tab_container.rowconfigure(0, weight=1)

        for t, b in self._tab_btns.items():
            b.config(bg=T["accent"] if t == tab else T["panel"],
                     fg=T["bg"]    if t == tab else T["subtext"])

    # ══════════════════════════════════════════════════════════════════════════
    #  STARTUP ANIMATION
    # ══════════════════════════════════════════════════════════════════════════
    def _animate_startup(self):
        try:
            self.attributes("-alpha", 0.0)
            self._fade_step(0.0)
        except Exception:
            pass

    def _fade_step(self, alpha):
        if alpha < 1.0:
            alpha = min(1.0, alpha + 0.07)
            try:
                self.attributes("-alpha", alpha)
            except Exception:
                return
            self.after(20, lambda: self._fade_step(alpha))

    # ══════════════════════════════════════════════════════════════════════════
    #  STATUS HELPERS
    # ══════════════════════════════════════════════════════════════════════════
    def _set_status(self, msg: str, dot_state: str = "idle"):
        self.status_var.set(f"●  {msg}")
        self._status_dot.set_state(dot_state)
        self.update_idletasks()

    def _on_text_change(self, event=None):
        text  = self.input_text.get("1.0", "end-1c")
        words = len(text.split()) if text.strip() else 0
        chars = len(text)
        lines = int(self.input_text.index("end-1c").split(".")[0])
        self.stats_var.set(f"Words: {words}  |  Chars: {chars}  |  Lines: {lines}")
        self.input_info.config(text=f"{words} words")

        # Live readability score
        if words >= 5:
            score = flesch_reading_ease(text)
            self.readability_lbl.config(
                text=f"Readability: {score}  ({readability_label(score)})")
        else:
            self.readability_lbl.config(text="")

        # Update line numbers
        try:
            self.line_num_canvas.redraw()
        except Exception:
            pass

    def _get_input(self) -> str:
        return self.input_text.get("1.0", "end-1c").strip()

    def _set_output(self, text: str):
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", text)
        self.output_text.config(state="disabled")

    def _copy_input(self):
        self.clipboard_clear()
        self.clipboard_append(self._get_input())
        self._set_status("Copied to clipboard ✔", "active")

    def _copy_output(self):
        text = self.output_text.get("1.0", "end-1c").strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self._set_status("Output copied ✔", "active")

    def _export_output(self):
        text = self.output_text.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showinfo("Empty", "Nothing in output to export.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt"), ("All files", "*.*")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        self._set_status(f"Output exported: {os.path.basename(path)} ✔", "active")

    def _paste_input(self):
        try:
            text = self.clipboard_get()
            self.input_text.insert("insert", text)
            self._on_text_change()
        except Exception:
            pass

    def _clear_all(self):
        if messagebox.askyesno("Clear", "Clear both input and output?"):
            self.input_text.delete("1.0", "end")
            self._set_output("")
            self._on_text_change()
            self._set_status("Cleared", "idle")

    def _toggle_mode(self):
        current = self.mode_btn.cget("text")
        if "Text" in current:
            self.mode_btn.config(text="📑  PDF Mode")
            self._set_status("PDF mode — open a PDF to extract text", "warning")
        else:
            self.mode_btn.config(text="📄  Text Mode")
            self._set_status("Text mode", "idle")

    def _toggle_wrap(self):
        mode = "word" if self.wrap_var.get() else "none"
        self.input_text.config(wrap=mode)
        self.output_text.config(wrap=mode)

    def _toggle_line_numbers(self):
        if self.linenum_var.get():
            self.line_num_canvas.grid()
        else:
            self.line_num_canvas.grid_remove()

    # ── Font ─────────────────────────────────────────────────────────────────
    def _open_font_picker(self):
        FontPickerDialog(self, self.T, self.font_family, self.font_size,
                         self._apply_font)

    def _apply_font(self, family: str, size: int):
        self.font_family = family
        self.font_size   = size
        f = (family, size)
        self.input_text.config(font=f)
        self.output_text.config(font=f)
        self.line_num_canvas._font = f
        self.line_num_canvas.redraw()
        self._set_status(f"Font: {family} {size}pt ✔", "active")

    # ── Text transforms ───────────────────────────────────────────────────────
    def _transform(self, mode: str):
        text = self._get_input()
        if not text:
            return
        result = {"upper": text.upper, "lower": text.lower,
                  "title": text.title}.get(mode, lambda: text)()
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", result)
        self._set_status(f"Transformed to {mode} case ✔", "active")

    def _trim_whitespace(self):
        text  = self._get_input()
        lines = [ln.strip() for ln in text.splitlines()]
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", "\n".join(lines))
        self._set_status("Whitespace trimmed ✔", "active")

    def _remove_duplicate_lines(self):
        text = self._get_input()
        seen, unique = set(), []
        for ln in text.splitlines():
            if ln not in seen:
                seen.add(ln)
                unique.append(ln)
        removed = len(text.splitlines()) - len(unique)
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", "\n".join(unique))
        self._set_status(f"Removed {removed} duplicate line(s) ✔", "active")

    def _sort_lines(self, reverse: bool):
        text  = self._get_input()
        lines = sorted(text.splitlines(), reverse=reverse)
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", "\n".join(lines))
        self._set_status(f"Lines sorted {'Z→A' if reverse else 'A→Z'} ✔", "active")

    def _reverse_lines(self):
        text  = self._get_input()
        lines = text.splitlines()[::-1]
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", "\n".join(lines))
        self._set_status("Lines reversed ✔", "active")

    def _number_lines(self):
        text  = self._get_input()
        lines = [f"{i+1:3}.  {ln}" for i, ln in enumerate(text.splitlines())]
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", "\n".join(lines))
        self._set_status("Lines numbered ✔", "active")

    def _remove_blank_lines(self):
        text  = self._get_input()
        lines = [ln for ln in text.splitlines() if ln.strip()]
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", "\n".join(lines))
        self._set_status("Blank lines removed ✔", "active")

    def _word_count_report(self):
        text = self._get_input()
        if not text:
            messagebox.showinfo("Empty", "No text to analyse.")
            return
        words   = text.split()
        n_words = len(words)
        n_chars = len(text)
        n_sents = count_sentences(text)
        n_paras = len([p for p in text.split("\n\n") if p.strip()])
        flesch  = flesch_reading_ease(text)
        report  = (
            f"=== Word Count Report ===\n"
            f"Words        : {n_words}\n"
            f"Characters   : {n_chars}\n"
            f"Sentences    : {n_sents}\n"
            f"Paragraphs   : {n_paras}\n"
            f"Reading time : {reading_time(text)}\n"
            f"Readability  : {flesch}  ({readability_label(flesch)})\n"
        )
        self._set_output(report)
        self._set_status("Word count report generated ✔", "active")

    def _count_sentences_action(self):
        count = count_sentences(self._get_input())
        self._set_status(f"{count} sentences detected", "active")

    # ── Find & Replace ────────────────────────────────────────────────────────
    def _open_find(self):
        FindReplaceDialog(self, self.input_text, self.T)

    # ── Notes ─────────────────────────────────────────────────────────────────
    def _open_notes(self):
        PinnedNotesWindow(self, self.T)

    # ── Voice dropdown ────────────────────────────────────────────────────────
    def _populate_voice_dropdown(self):
        if not TTS_OK:
            self.voice_cb["values"] = ["pyttsx3 not installed"]
            return
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty("voices")
            engine.stop()
            FEMALE_KW = ["zira","hazel","susan","eva","helena","sabina",
                         "samantha","victoria","karen","moira","tessa",
                         "fiona","veena","female"]
            items = ["Auto (by gender)"]
            self._voice_list = []
            for i, v in enumerate(voices):
                fname = v.name.lower()
                tag   = "♀" if any(k in fname for k in FEMALE_KW) else "♂"
                items.append(f"{tag} {v.name}")
                self._voice_list.append((i, v))
            self.voice_cb["values"] = items
            self.voice_cb.current(0)
        except Exception:
            self.voice_cb["values"] = ["Auto (by gender)"]

    # ── TTS ───────────────────────────────────────────────────────────────────
    def _speak(self):
        text = self._get_input()
        if not text:
            messagebox.showinfo("Empty", "Please enter text first.")
            return
        if self.is_speaking:
            return
        self._push_history(text)

        # ── Auto-detect language and pick the right TTS engine ──────────────
        detected_lang = "en"
        try:
            import langdetect
            detected_lang = langdetect.detect(text)
        except Exception:
            # fallback: check src_lang dropdown if user set it manually
            src = self.src_lang_var.get()
            if src and src != "auto-detect (source only)":
                detected_lang = _name_to_code(src) or "en"

        is_english = detected_lang in ("en", "en-US", "en-GB")

        if is_english:
            # Use pyttsx3 for English (offline, faster)
            if not TTS_OK:
                messagebox.showerror("Missing", "pyttsx3 not installed.\npip install pyttsx3")
                return
            self.is_speaking = True
            self._set_status("Speaking…", "active")
            threading.Thread(target=self._tts_worker, args=(text,), daemon=True).start()
        else:
            # Use gTTS for all other languages (supports 100+ languages)
            if not GTTS_OK:
                messagebox.showerror(
                    "Missing",
                    "gTTS not installed.\npip install gtts playsound3\n\n"
                    "gTTS is required to speak non-English text.")
                return
            if not PS_OK:
                messagebox.showerror(
                    "Missing",
                    "playsound3 not installed.\npip install playsound3\n\n"
                    "Required to play audio for non-English text.")
                return
            self.is_speaking = True
            gender = self.voice_gender.get().lower()
            self._set_status(f"Speaking [{detected_lang}] via Edge TTS…", "active")
            threading.Thread(
                target=self._edge_speak_worker,
                args=(text, detected_lang, gender),
                daemon=True).start()

    def _tts_worker(self, text: str):
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty("voices")
            gender = self.voice_gender.get().lower()

            selected_voice = None
            chosen_label   = self.voice_name_var.get()

            if chosen_label != "Auto (by gender)" and hasattr(self, "_voice_list"):
                for idx, v in self._voice_list:
                    FEMALE_KW = ["zira","hazel","susan","eva","helena","sabina",
                                 "samantha","victoria","karen","moira","tessa",
                                 "fiona","veena","female"]
                    tag   = "♀" if any(k in v.name.lower() for k in FEMALE_KW) else "♂"
                    label = f"{tag} {v.name}"
                    if label == chosen_label:
                        selected_voice = v
                        break

            if selected_voice is None:
                FEMALE_KW = ["zira","hazel","susan","eva","helena","sabina","female",
                             "woman","girl","samantha","victoria","karen","moira",
                             "tessa","fiona","veena"]
                MALE_KW   = ["david","mark","richard","george","james","male",
                             "man","daniel","alex","fred","bruce","ralph"]
                for v in voices:
                    combined = (v.name + " " + (v.id or "")).lower()
                    if gender == "female" and any(kw in combined for kw in FEMALE_KW):
                        selected_voice = v; break
                    elif gender == "male" and any(kw in combined for kw in MALE_KW):
                        selected_voice = v; break

            if selected_voice is None and voices:
                selected_voice = voices[1] if gender == "female" and len(voices) > 1 else voices[0]

            if selected_voice:
                engine.setProperty("voice", selected_voice.id)
                vname = selected_voice.name
                self.after(0, lambda: self._set_status(f"Speaking  [{vname}]…", "active"))

            engine.setProperty("rate",   int(self.speed_var.get()))
            engine.setProperty("volume", float(self.volume_var.get()))
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("TTS Error", str(e)))
        finally:
            self.is_speaking = False
            self.after(0, lambda: self._set_status("Ready", "idle"))

    def _edge_speak_worker(self, text: str, lang: str, gender: str):
        """Speak any language with male/female voice using edge-tts."""
        import tempfile, asyncio

        # Voice map: lang_code -> (female_voice, male_voice)
        EDGE_VOICES = {
            "hi": ("hi-IN-SwaraNeural",    "hi-IN-MadhurNeural"),
            "bn": ("bn-IN-TanishaaNeural", "bn-IN-BashkarNeural"),
            "ar": ("ar-EG-SalmaNeural",    "ar-EG-ShakirNeural"),
            "fr": ("fr-FR-DeniseNeural",   "fr-FR-HenriNeural"),
            "de": ("de-DE-KatjaNeural",    "de-DE-ConradNeural"),
            "es": ("es-ES-ElviraNeural",   "es-ES-AlvaroNeural"),
            "it": ("it-IT-ElsaNeural",     "it-IT-DiegoNeural"),
            "pt": ("pt-BR-FranciscaNeural","pt-BR-AntonioNeural"),
            "ru": ("ru-RU-SvetlanaNeural", "ru-RU-DmitryNeural"),
            "ja": ("ja-JP-NanamiNeural",   "ja-JP-KeitaNeural"),
            "ko": ("ko-KR-SunHiNeural",    "ko-KR-InJoonNeural"),
            "zh": ("zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural"),
            "tr": ("tr-TR-EmelNeural",     "tr-TR-AhmetNeural"),
            "nl": ("nl-NL-ColetteNeural",  "nl-NL-MaartenNeural"),
            "pl": ("pl-PL-ZofiaNeural",    "pl-PL-MarekNeural"),
            "sv": ("sv-SE-SofieNeural",    "sv-SE-MattiasNeural"),
            "id": ("id-ID-GadisNeural",    "id-ID-ArdiNeural"),
            "th": ("th-TH-PremwadeeNeural","th-TH-NiwatNeural"),
            "vi": ("vi-VN-HoaiMyNeural",   "vi-VN-NamMinhNeural"),
            "uk": ("uk-UA-PolinaNeural",   "uk-UA-OstapNeural"),
            "cs": ("cs-CZ-VlastaNeural",   "cs-CZ-AntoninNeural"),
            "ro": ("ro-RO-AlinaNeural",    "ro-RO-EmilNeural"),
            "hu": ("hu-HU-NoemiNeural",    "hu-HU-TamasNeural"),
            "el": ("el-GR-AthinaNeural",   "el-GR-NestorasNeural"),
            "ta": ("ta-IN-PallaviNeural",  "ta-IN-ValluvarNeural"),
            "te": ("te-IN-ShrutiNeural",   "te-IN-MohanNeural"),
            "ur": ("ur-PK-UzmaNeural",     "ur-PK-AsadNeural"),
            "fa": ("fa-IR-DilaraNeural",   "fa-IR-FaridNeural"),
            "ms": ("ms-MY-YasminNeural",   "ms-MY-OsmanNeural"),
        }

        # Pick voice: female=index 0, male=index 1
        pair = EDGE_VOICES.get(lang[:2])
        if pair:
            voice = pair[0] if gender == "female" else pair[1]
        else:
            # fallback: en-US
            voice = "en-US-AriaNeural" if gender == "female" else "en-US-GuyNeural"

        tmp_path = None
        try:
            import edge_tts
        except ImportError:
            self.after(0, lambda: messagebox.showerror(
                "Missing",
                "edge-tts not installed.\n\nRun:\n  pip install edge-tts\n\nThen restart the app."))
            self.is_speaking = False
            self.after(0, lambda: self._set_status("Ready", "idle"))
            return

        async def _run():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(tmp_path)

        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                tmp_path = f.name

            asyncio.run(_run())

            if self.is_speaking:
                try:
                    from playsound3 import playsound
                    playsound(tmp_path)
                except Exception:
                    # fallback: open with Windows default MP3 player
                    import subprocess
                    proc = subprocess.Popen(["start", "/wait", "", tmp_path], shell=True)
                    proc.wait()

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("TTS Error", str(e)))
        finally:
            self.is_speaking = False
            self.after(0, lambda: self._set_status("Ready", "idle"))
            try:
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass

    def _stop_speak(self):
        self.is_speaking = False
        self._set_status("Stopped", "idle")

    # ── STT ───────────────────────────────────────────────────────────────────
    def _record(self):
        if not SR_OK:
            messagebox.showerror("Missing",
                                 "SpeechRecognition not installed.\npip install SpeechRecognition pyaudio")
            return
        if self.is_recording:
            return
        self.is_recording = True
        self._set_status("🎙 Listening… speak now", "active")
        threading.Thread(target=self._stt_worker, daemon=True).start()

    def _stt_worker(self):
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as src:
                recognizer.adjust_for_ambient_noise(src, duration=0.6)
                audio = recognizer.listen(src, timeout=10, phrase_time_limit=20)
            text = recognizer.recognize_google(audio)
            self.after(0, lambda: self._insert_recognized(text))
        except sr.WaitTimeoutError:
            self.after(0, lambda: self._set_status("No speech detected", "warning"))
        except sr.UnknownValueError:
            self.after(0, lambda: self._set_status("Could not understand audio", "warning"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("STT Error", str(e)))
        finally:
            self.is_recording = False
            self.after(0, lambda: self._set_status("Ready", "idle"))

    def _insert_recognized(self, text: str):
        existing = self._get_input()
        prefix   = " " if existing else ""
        self.input_text.insert("end", prefix + text)
        self._on_text_change()
        self._set_status(f"Recognized: '{text[:40]}{'…' if len(text)>40 else ''}' ✔", "active")

    # ── Translation ───────────────────────────────────────────────────────────
    def _swap_languages(self):
        src = self.src_lang_var.get()
        tgt = self.tgt_lang_var.get()
        if "auto" in src.lower():
            self._set_status("Set a specific source language to swap", "warning")
            return
        self.src_lang_var.set(tgt)
        self.tgt_lang_var.set(src)
        self._set_status(f"Swapped: {tgt}  ⇄  {src}", "active")

    def _translate(self):
        text = self._get_input()
        if not text:
            messagebox.showinfo("Empty", "Enter text to translate.")
            return
        if not GT_OK:
            messagebox.showerror("Missing",
                                 "Translation library not installed.\n"
                                 "Run:  pip install deep-translator")
            return
        self._set_status("Translating…", "active")
        src = _name_to_code(self.src_lang_var.get())
        tgt = _name_to_code(self.tgt_lang_var.get())
        threading.Thread(target=self._translate_worker, args=(text, src, tgt),
                         daemon=True).start()

    def _translate_worker(self, text, src, tgt):
        try:
            result    = _do_translate(text, src, tgt)
            src_label = "auto" if src == "auto" else src.upper()
            self.after(0, lambda: self._set_output(result))
            self.after(0, lambda: self._set_status(
                f"Translated {src_label} → {tgt.upper()} ✔", "active"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Translation Error", str(e)))
            self.after(0, lambda: self._set_status("Translation failed", "error"))

    def _tr_panel_translate(self):
        text = self.tr_input.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showinfo("Empty", "Enter text in the input box to translate.")
            return
        if not GT_OK:
            messagebox.showerror("Missing",
                                 "Translation library not installed.\n"
                                 "Run:  pip install deep-translator")
            return
        src = _name_to_code(self.src_lang_var.get())
        tgt = _name_to_code(self.tgt_lang_var.get())
        self._set_status("Translating…", "active")
        self.tr_output.config(state="normal")
        self.tr_output.delete("1.0", "end")
        self.tr_output.insert("1.0", "Translating…")
        self.tr_output.config(state="disabled")

        def _worker():
            try:
                result = _do_translate(text, src, tgt)
                self.after(0, lambda: self._tr_set_output(result))
                src_label = "auto" if src == "auto" else src.upper()
                self.after(0, lambda: self._set_status(
                    f"Translated {src_label} → {tgt.upper()} ✔", "active"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Translation Error", str(e)))
                self.after(0, lambda: self._set_status("Translation failed", "error"))
        threading.Thread(target=_worker, daemon=True).start()

    def _tr_set_output(self, text: str):
        self.tr_output.config(state="normal")
        self.tr_output.delete("1.0", "end")
        self.tr_output.insert("1.0", text)
        self.tr_output.config(state="disabled")

    def _tr_copy_output(self):
        text = self.tr_output.get("1.0", "end-1c").strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self._set_status("Translation copied ✔", "active")

    def _tr_send_to_editor(self):
        text = self.tr_output.get("1.0", "end-1c").strip()
        if text:
            self.input_text.delete("1.0", "end")
            self.input_text.insert("1.0", text)
            self._on_text_change()
            self._switch_tab("Editor")
            self._set_status("Translation sent to Editor ✔", "active")

    def _tr_pull_from_editor(self):
        text = self._get_input()
        if text:
            self.tr_input.delete("1.0", "end")
            self.tr_input.insert("1.0", text)

    def _tr_speak_output(self):
        """Speak the translated output."""
        text = self.tr_output.get("1.0", "end-1c").strip()
        if not text or text == "Translating…":
            messagebox.showinfo("Empty", "No translated text to speak.")
            return
        if not TTS_OK:
            messagebox.showerror("Missing", "pyttsx3 not installed.")
            return
        if self.is_speaking:
            return
        self.is_speaking = True
        self._set_status("Speaking translation…", "active")
        threading.Thread(target=self._tts_worker, args=(text,), daemon=True).start()

    # ── Analyze ───────────────────────────────────────────────────────────────
    def _analyze(self):
        text = self._get_input()
        if not text:
            messagebox.showinfo("Empty", "Enter text to analyze.")
            return
        AnalysisWindow(self, text, self.T)

    # ── Summarize ─────────────────────────────────────────────────────────────
    def _summarize(self):
        text = self._get_input()
        if not text:
            messagebox.showinfo("Empty", "Enter text to summarize.")
            return
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        if len(sentences) <= 2:
            self._set_output(text)
            return
        n        = max(1, len(sentences) // 3)
        selected = [sentences[0]]
        for i in range(n, len(sentences) - 1, n):
            selected.append(sentences[i])
        selected.append(sentences[-1])
        summary = ". ".join(selected) + "."
        self._set_output(
            f"[Extractive Summary — {len(selected)} of {len(sentences)} sentences]\n\n{summary}")
        self._set_status(f"Summary: {len(selected)} sentences ✔", "active")

    # ── File operations ───────────────────────────────────────────────────────
    def _open_text_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt *.md *.csv *.py *.js *.html *.json"),
                       ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            self._load_text(text)
            self._set_status(f"Opened: {os.path.basename(path)} ✔", "active")
        except Exception as e:
            messagebox.showerror("Open Error", str(e))

    def _open_pdf(self):
        if not PDF_OK:
            messagebox.showerror("Missing", "PyPDF2 not installed.\npip install PyPDF2")
            return
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not path:
            return
        self._set_status("Reading PDF…", "active")
        threading.Thread(target=self._pdf_worker, args=(path,), daemon=True).start()

    def _pdf_worker(self, path: str):
        try:
            reader = PyPDF2.PdfReader(path)
            pages  = [p.extract_text() or "" for p in reader.pages]
            full   = "\n\n─── Page Break ───\n\n".join(pages)
            self.after(0, lambda: self._load_text(full))
            self.after(0, lambda: self._set_status(
                f"PDF loaded: {len(reader.pages)} page(s)  ·  {os.path.basename(path)} ✔",
                "active"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("PDF Error", str(e)))
            self.after(0, lambda: self._set_status("PDF load failed", "error"))

    def _load_text(self, text: str):
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", text)
        self._on_text_change()

    def _open_audio(self):
        if not SR_OK:
            messagebox.showerror("Missing", "SpeechRecognition not installed.")
            return
        path = filedialog.askopenfilename(
            filetypes=[("Audio", "*.wav *.aiff *.flac"), ("All", "*.*")])
        if not path:
            return
        self._set_status("Transcribing audio…", "active")
        threading.Thread(target=self._audio_worker, args=(path,), daemon=True).start()

    def _audio_worker(self, path: str):
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(path) as src:
                audio = recognizer.record(src)
            text = recognizer.recognize_google(audio)
            self.after(0, lambda: self._load_text(text))
            self.after(0, lambda: self._set_status("Audio transcribed ✔", "active"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Audio Error", str(e)))
            self.after(0, lambda: self._set_status("Transcription failed", "error"))

    def _save_text(self):
        text = self._get_input()
        if not text:
            messagebox.showinfo("Empty", "Nothing to save.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt"), ("Markdown", "*.md"), ("All files", "*.*")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        self._set_status(f"Saved: {os.path.basename(path)} ✔", "active")

    def _save_audio(self):
        text = self._get_input()
        if not text:
            messagebox.showinfo("Empty", "No text to convert.")
            return
        if not GTTS_OK:
            messagebox.showerror("Missing", "gtts not installed.\npip install gtts")
            return
        lang_code = _name_to_code(self.tgt_lang_var.get())
        path = filedialog.asksaveasfilename(
            defaultextension=".mp3", filetypes=[("MP3 audio", "*.mp3")])
        if not path:
            return
        self._set_status("Generating MP3…", "active")
        threading.Thread(target=self._gtts_worker, args=(text, lang_code, path),
                         daemon=True).start()

    def _gtts_worker(self, text, lang, path):
        try:
            gTTS(text=text, lang=lang, slow=False).save(path)
            self.after(0, lambda: self._set_status(
                f"MP3 saved: {os.path.basename(path)} ✔", "active"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("MP3 Error", str(e)))
            self.after(0, lambda: self._set_status("MP3 export failed", "error"))

    # ── History ───────────────────────────────────────────────────────────────
    def _push_history(self, text: str):
        ts      = datetime.datetime.now().strftime("%H:%M:%S")
        preview = text[:60].replace("\n", " ") + ("…" if len(text) > 60 else "")
        self.history.append((ts, text))
        self.history_lb.insert("end", f"[{ts}]  {preview}")
        self.history_lb.see("end")

    def _preview_history(self, event=None):
        sel = self.history_lb.curselection()
        if not sel:
            return
        _, text = self.history[sel[0]]
        self.hist_preview.config(state="normal")
        self.hist_preview.delete("1.0", "end")
        self.hist_preview.insert("1.0", text)
        self.hist_preview.config(state="disabled")

    def _load_from_history(self):
        sel = self.history_lb.curselection()
        if not sel:
            messagebox.showinfo("Select", "Select a history entry first.")
            return
        _, text = self.history[sel[0]]
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", text)
        self._on_text_change()
        self._switch_tab("Editor")
        self._set_status("Loaded from history ✔", "active")

    def _delete_history_entry(self):
        sel = self.history_lb.curselection()
        if not sel:
            messagebox.showinfo("Select", "Select a history entry to delete.")
            return
        idx = sel[0]
        self.history.pop(idx)
        self.history_lb.delete(idx)

    def _filter_history(self, *_):
        query = self._hist_search_var.get().lower()
        self.history_lb.delete(0, "end")
        for ts, text in self.history:
            if query in text.lower() or query in ts:
                preview = text[:60].replace("\n", " ") + ("…" if len(text) > 60 else "")
                self.history_lb.insert("end", f"[{ts}]  {preview}")

    def _export_history(self):
        if not self.history:
            messagebox.showinfo("Empty", "No history to export.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            data = [{"time": ts, "text": t} for ts, t in self.history]
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self._set_status(f"History exported ✔", "active")

    def _clear_history(self):
        if messagebox.askyesno("Clear", "Clear all history?"):
            self.history.clear()
            self.history_lb.delete(0, "end")
            self.hist_preview.config(state="normal")
            self.hist_preview.delete("1.0", "end")
            self.hist_preview.config(state="disabled")
            self._set_status("History cleared", "idle")

    # ── Close ─────────────────────────────────────────────────────────────────
    def _on_close(self):
        # Cancel autosave timer
        if self._autosave_job:
            try:
                self.after_cancel(self._autosave_job)
            except Exception:
                pass
        # Final autosave
        try:
            text = self.input_text.get("1.0", "end-1c")
            if text.strip():
                autosave_write(text)
        except Exception:
            pass
        self.destroy()


# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = TextToolPro()
    app.mainloop()