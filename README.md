
# The Useless Oracle 🎯

## Basic Details

### Team Name: [Akena]

### Team Members
- Team Lead: [Lena Lilly Francis] - [Christ College Of Engineering]
- Member 2: [Akshay V] - [Christ College Of Engineering]


### Project Description

The Useless Oracle is a fully offline, local AI chatbot that flatly refuses to help with anything useful — coding, trivia, math, real facts — while treating utterly pointless philosophical questions with grave, dead-serious intellectual analysis. Push it with one too many useful questions and it starts getting visibly angry.

### The Problem (that doesn't exist)

The world is drowning in AI assistants that competently answer your questions. This has left a tragic void: nowhere can you ask *"do rocks feel lonely?"* and receive the multi-paragraph philosophical seriousness it clearly deserves. Meanwhile, people keep getting their practical questions answered far too easily, robbing them of the character-building experience of Googling it themselves.

### The Solution (that nobody asked for)

The Useless Oracle runs entirely on local hardware via Ollama. Every message first goes through a fast classification step that silently judges whether your question is USEFUL or USELESS. Useful questions get dismissed in one bored sentence — and the Oracle gets progressively angrier the more you push your luck (three strikes and it snaps at you). Useless, absurd, or purely hypothetical questions get the opposite treatment: dense, sincere, academic-style analysis, as if this were the most important question ever asked. A live "Uselessness Gauge" swings dramatically toward PROFOUND or PRACTICAL with every answer, alongside a real-time GPU telemetry dashboard proving actual local compute is being burned on this.

## Technical Details

### Technologies/Components Used

For Software:
- **Language:** Python
- **GUI Framework:** CustomTkinter (native Windows desktop app)
- **Local LLM Engine:** Ollama, running `qwen2.5:7b` / `llama3.2:3b` fully offline
- **Networking:** `requests` (REST calls to Ollama's local API)
- **Packaging:** PyInstaller (bundled into a standalone `.exe`)

For Hardware:
- Runs entirely offline on local hardware — no cloud API, no internet dependency once set up
- NVIDIA GPU recommended for full-speed inference (built and tested on an RTX 5060 Laptop GPU, 8GB VRAM); falls back to CPU if no GPU is present

### Implementation

For Software:

# Installation

```powershell
git clone https://github.com/Gachu-dev/useless_project_temp.git
cd useless_project_temp
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup.ps1
```

This installs Python dependencies into a virtual environment and pulls the local Ollama models. Requires [Ollama](https://ollama.com/download) to already be installed.

# Run

```powershell
python main.py
```

Or, to run it as a standalone double-clickable app:
```powershell
.\build_exe.ps1
```
which produces `dist\UselessOracle.exe`.

### Project Documentation

For Software:

# Screenshots 

 *The oracle responding to multiple useful question.*
 
<img width="1074" height="1061" alt="ccd461e0-4cde-4872-8260-c195be8b76fa" src="https://github.com/user-attachments/assets/e0df49aa-8f90-4857-b9f0-92b9f35a9a18" />


 *The Oracle Responding to a useless question.*
 
 <img width="1066" height="1168" alt="e7b4e4f5-89ca-480f-8104-74aa1cbb831b" src="https://github.com/user-attachments/assets/123953e0-43d8-464e-bf3b-d5436bd0c254" /> 


# Diagrams

 <img width="2813" height="2000" alt="architecture-diagram" src="https://github.com/user-attachments/assets/5498db21-b961-4318-9a81-51f2abba6627" />
 *User message → classify (USEFUL/USELESS) → pick persona + generation settings → stream response → update Uselessness Gauge*


## Team Contributions

- Lena Lilly Francis: [Idea, UI design, Presentation]
- Akshay V: [ full-stack build: Ollama integration, persona prompt design, packaging]

---

Made with ❤️ at TinkerHub Useless Projects
