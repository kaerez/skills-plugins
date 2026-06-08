# 🌿 PUML-PlantUML Expert Skill

> Full-stack PlantUML expert for AI coding assistants. Generate diagrams from text, reverse-engineer images to PUML code, and render locally — **fully offline, any OS**.

[![Version](https://img.shields.io/badge/version-2.0.0-blue)](SKILL.md)
[![License](https://img.shields.io/badge/license-AGPL--3.0-green)](LICENSE)
[![PlantUML](https://img.shields.io/badge/PlantUML-v1.2025.0-orange)](https://plantuml.com)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey)](references/local-rendering.md)
[![skills.sh](https://skills.sh/b/kaerez/skills-plugins)](https://skills.sh/kaerez/skills-plugins)
---

## What This Skill Can Do

On **first run**, the skill automatically checks your environment and bootstraps anything missing — Python, OpenJDK, and PlantUML — with no manual steps required.

Once ready, it can:

1. **Image → PUML** &nbsp;— Reverse-engineer any diagram image (screenshot, photo, export) into editable PlantUML code *(Diagram as Code)*
2. **PUML → Image** &nbsp;— Render `.puml` code locally as PNG, SVG, or PDF, fully offline
3. **Author & Edit** — Create new diagrams from plain-English descriptions, fix errors, refactor, explain syntax, and apply styling

Covers all **27 chapters** of the PlantUML Language Reference Guide v1.2025.0 (607 pages).

---

## Installation

Choose the path that matches how you use your AI assistant.

### SKILLS.SH - NPX SKILLS
```bash
npx skills add https://github.com/kaerez/skills-plugins --skill puml-plantuml
```

### 🖥️ Desktop Applications
*Claude Desktop · CoWork · ChatGPT Desktop · Gemini Desktop*

1. Download [`puml-plantuml.skill`](https://raw.githubusercontent.com/kaerez/skills-plugins/main/skills/puml-plantuml/puml-plantuml.skill)
2. **Double-click** the `.skill` file — the app will prompt to install, **or**
3. Open the app → **Settings → Skills / Extensions / Customization (or equivalent panel) → Add Skill** → browse to `puml-plantuml.skill`

### 🌐 Web UIs
*claude.ai · chatgpt.com · gemini.google.com*

1. Download [`puml-plantuml.skill`](https://raw.githubusercontent.com/kaerez/skills-plugins/main/skills/puml-plantuml/puml-plantuml.skill)
2. Open **Settings → Skills / Extensions / Customization** (or equivalent panel)
3. Upload or drag-and-drop `puml-plantuml.skill`

### ⌨️ AI Coding Assistants (CLI)
*Claude Code · Gemini Code · Cursor · Copilot · any assistant with terminal access*

#### Claude Code
```bash
unzip -o puml-plantuml.skill -d ~/.claude/skills/
```
#### Gemini Code
```bash
unzip -o puml-plantuml.skill -d ~/.gemini/skills/
```
#### Other tools — unzip to your tool's skills directory
```bash
unzip -o puml-plantuml.skill -d <your-tool-skills-dir>/
```
Restart your assistant or reload skills. The skill self-configures on first use.

---

## First Run — Automated Bootstrap

No pre-installed tools required. On first use, the skill detects your environment and **automatically installs anything missing** — Python, OpenJDK, and PlantUML (binary or JAR depending on platform). This is what it does behind the scenes:

### macOS / Linux

#### Install everything
```bash
bash scripts/bootstrap.sh
```
#### Install everything + test render
```bash
bash scripts/bootstrap.sh --verify
```

### Windows (PowerShell — built into Windows 10/11)

#### Allow script execution (run once)
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
#### Install everything
```powershell
.\scripts\bootstrap.ps1
```
#### Install everything + test render
```powershell
.\scripts\bootstrap.ps1 -Verify
```

### If Python is already available

#### Show what's detected
```bash
python3 scripts/render.py --detect
```
#### Install Java + PlantUML
```bash
python3 scripts/setup.py
```
#### Install Java + PlantUML + test render
```bash
python3 scripts/setup.py --verify
```

**What gets installed (only if missing):**

| Component | macOS | Linux | Windows |
|-----------|-------|-------|---------|
| Homebrew | auto-installed if missing | — | — |
| Python 3.9+ | brew | apt / dnf / pacman / snap | winget / choco / scoop |
| Java JRE 11+ | brew cask Temurin | apt / dnf / pacman | winget Temurin / Zulu |
| PlantUML | brew | apt / dnf / pacman / snap / JAR¹ | winget / choco / scoop |

> ¹ If no package manager is found on Linux, downloads `plantuml.jar` directly to `~/.plantuml/`.

---

## Usage

Tell your AI assistant to:

- *"Draw a sequence diagram for OAuth 2.0 login"*
- *"Convert this architecture screenshot to PlantUML code"*
- *"Render my `diagram.puml` as SVG"*
- *"Fix my class diagram — it shows an unknown command error"*
- *"Explain how to use `skinparam`"*
- *"Add swimlanes to this activity diagram"*

---

## Rendering

### macOS / Linux
#### PNG (default)
```bash
python3 scripts/render.py diagram.puml
```
#### SVG
```bash
python3 scripts/render.py diagram.puml -f svg -o ./output/
```
#### SVG from stdin
```bash
cat diagram.puml | python3 scripts/render.py --stdin -f svg -n "name" -o /tmp/
```
#### PDF
```bash
python3 scripts/render.py diagram.puml -f pdf -o ./output/
```
#### Validate syntax only
```bash
python3 scripts/render.py diagram.puml --check
```

### Windows
#### PNG (default)
```powershell
py scripts\render.py diagram.puml
```
#### SVG
```powershell
py scripts\render.py diagram.puml -f svg -o .\output\
```

### Direct CLI (if `plantuml` is in PATH)
#### SVG
```bash
plantuml -tsvg diagram.puml
```
#### PNG (batch)
```bash
plantuml -tpng -o ./output/ *.puml
```
#### Validate syntax only
```bash
plantuml -checkonly diagram.puml
```

---

## Diagram Types (20+)

| Type | Use For |
|------|---------|
| **Sequence** | API flows, call chains, message passing |
| **Class** | OOP, inheritance, interfaces |
| **Activity** | Workflows, flowcharts, branching logic |
| **Component** | Architecture, microservices |
| **Deployment** | Infrastructure, servers, nodes |
| **State** | Lifecycle, status machines |
| **ER** | Database schemas, entity relationships |
| **Use Case** | Actor/system interactions |
| **Object** | Runtime instances, snapshots |
| **Timing** | Signal waveforms, concise / robust |
| **MindMap** | Brainstorming, concept maps |
| **Gantt** | Project timelines, milestones |
| **WBS** | Work breakdown structures |
| **Salt** | UI wireframes, form mockups |
| **JSON / YAML** | Structured data visualization |
| **nwdiag** | Network topology, subnets |
| **Archimate** | Enterprise architecture |
| **Maths** | LaTeX / AsciiMath formulas |
| **Ditaa** | ASCII art diagrams |

---

## Directory Structure

```text
puml-plantuml/
├── SKILL.md                       # AI instruction file
├── LICENSE                        # AGPL-3.0
├── README.md                      # This file
├── references/
│   ├── syntax-quick-ref.md        # 2700+ lines — all 27 chapters
│   ├── image-to-puml.md           # Vision reverse-engineering guide
│   └── local-rendering.md         # Setup, CLI flags, formats, troubleshooting
└── scripts/
    ├── bootstrap.sh               # macOS/Linux — zero-dep installer
    ├── bootstrap.ps1              # Windows — zero-dep installer
    ├── setup.py                   # Detect/install Java + PlantUML
    └── render.py                  # Cross-platform renderer (binary or JAR)
```

---

## Reference Files

| File | Content |
|------|---------|
| [`references/syntax-quick-ref.md`](references/syntax-quick-ref.md) | **2700+ lines** — complete syntax for all 27 chapters |
| [`references/image-to-puml.md`](references/image-to-puml.md) | Visual analysis guide for image → PUML reverse engineering |
| [`references/local-rendering.md`](references/local-rendering.md) | Setup, CLI flags, output formats, troubleshooting |

---

## Requirements

> **All requirements are automatically installed on first run** via the bootstrap scripts — no manual setup needed.

| Component | Minimum | Notes |
|-----------|---------|-------|
| Python | 3.9+ | stdlib only — no pip installs |
| Java JRE | 11+ | Auto-detected: Azul/Zulu, Temurin, OpenJDK, Homebrew, SDKMAN |
| PlantUML | Latest | Binary or JAR — auto-installed by bootstrap |

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `PLANTUML_JAR` | Path to `plantuml.jar` (used if binary not in PATH) |
| `JAVA_HOME` | Java installation root |
| `GRAPHVIZ_DOT` | Path to `dot` executable |
| `PLANTUML_LIMIT_SIZE` | Max diagram dimension in pixels (default: 4096) |

---

## License

[AGPL-3.0-only](LICENSE)

## Author

**Erez Kalman / KSEC**
