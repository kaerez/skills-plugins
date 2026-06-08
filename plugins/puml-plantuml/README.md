# 🌿 PUML-PlantUML — Claude Code/Desktop Plugin

> Full-stack PlantUML expert, packaged as a Claude Code plugin. Generate diagrams from text, reverse-engineer images to PUML code, and render locally — **fully offline**.

[![Version](https://img.shields.io/badge/version-2.0.0-blue)](.claude-plugin/plugin.json)
[![License](https://img.shields.io/badge/license-AGPL--3.0-green)](skills/puml-plantuml/LICENSE)
[![PlantUML](https://img.shields.io/badge/PlantUML-v1.2025.0-orange)](https://plantuml.com)
[![Platform](https://img.shields.io/badge/platform-Claude%20Code-blueviolet)](https://claude.ai/code)
[![Platform](https://img.shields.io/badge/platform-Claude%20Desktop-blueviolet)](https://claude.ai/downloads)
[![Platform](https://img.shields.io/badge/platform-Claude%20Web-blueviolet)](https://claude.ai)

---

## What This Plugin Can Do

On **first render**, the plugin automatically checks your environment and bootstraps anything missing — Python, OpenJDK, and PlantUML — with no manual steps required.

Once ready, it can:

1. **Image → PUML** &nbsp;— Reverse-engineer any diagram image (screenshot, photo, export) into editable PlantUML code *(Diagram as Code)*
2. **PUML → Image** &nbsp;— Render `.puml` code locally as PNG, SVG, or PDF, fully offline
3. **Author & Edit** — Create new diagrams from plain-English descriptions, fix errors, refactor, explain syntax, and apply styling

Covers all **27 chapters** of the PlantUML Language Reference Guide v1.2025.0 (607 pages).

---

## Installation
[![Install on Claude Code](https://img.shields.io/badge/Install%20on Claude%20Code-black?style=for-the-badge)](https://kaerez.github.io/skills-plugins/plugins/puml-plantuml/redir.html)

### Via Plugin Marketplace

#### Inside Claude Code
##### Add the marketplace
```
/plugin marketplace add kaerez/skills-plugins
```
##### Install the plugin
```
/plugin install puml-plantuml@kaerez-skills-plugins
```
##### Activate
```
/reload-plugins
```

#### Via Terminal (Claude Code CLI)
##### Add the marketplace
```bash
claude plugin marketplace add kaerez/skills-plugins
```
##### Install the plugin
```bash
claude plugin install puml-plantuml@kaerez-skills-plugins
```
Then run `/reload-plugins` inside Claude Code to activate.

### Local / Development
#### Point Claude Code at the plugin directory
```bash
claude --plugin-dir /path/to/skills-plugins/plugins/puml-plantuml
```

---

## Usage

The plugin activates automatically when you ask Claude to draw diagrams, create PUML, convert images, render `.puml` files, or debug PlantUML syntax:

- *"Draw a sequence diagram for OAuth 2.0 login"*
- *"Convert this architecture screenshot to PlantUML code"*
- *"Render my `diagram.puml` as SVG"*
- *"Fix my class diagram — it shows an unknown command error"*
- *"Explain how to use `skinparam`"*
- *"Add swimlanes to this activity diagram"*

Or invoke explicitly:
```
/puml-plantuml:puml-plantuml
```

---

## First Run — Automated Bootstrap

No pre-installed tools required. The first time you invoke `/puml-plantuml:puml-plantuml`, the plugin **automatically detects your environment, installs anything missing, and runs a test render** — Python, OpenJDK, and PlantUML (binary or JAR depending on platform). Nothing to run manually.

**What gets installed (only if missing):**

| Component | macOS | Linux | Windows |
|-----------|-------|-------|---------|
| Homebrew | auto-installed if missing | — | — |
| Python 3.9+ | brew | apt / dnf / pacman / snap | winget / choco / scoop |
| Java JRE 11+ | brew cask Temurin | apt / dnf / pacman | winget Temurin / Zulu |
| PlantUML | brew | apt / dnf / pacman / snap / JAR¹ | winget / choco / scoop |

> ¹ If no package manager is found on Linux, downloads `plantuml.jar` directly to `~/.plantuml/`.

### Advanced — Manual Bootstrap

For troubleshooting or local/dev installs, bootstrap can be triggered manually from the plugin root.

#### macOS / Linux

##### Install everything
```bash
bash skills/puml-plantuml/scripts/bootstrap.sh
```
##### Install everything + test render
```bash
bash skills/puml-plantuml/scripts/bootstrap.sh --verify
```

#### Windows (PowerShell — built into Windows 10/11)

##### Allow script execution (run once)
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
##### Install everything
```powershell
.\skills\puml-plantuml\scripts\bootstrap.ps1
```
##### Install everything + test render
```powershell
.\skills\puml-plantuml\scripts\bootstrap.ps1 -Verify
```

#### If Python is already available

##### Show what's detected
```bash
python3 skills/puml-plantuml/scripts/render.py --detect
```
##### Install Java + PlantUML
```bash
python3 skills/puml-plantuml/scripts/setup.py
```
##### Install Java + PlantUML + test render
```bash
python3 skills/puml-plantuml/scripts/setup.py --verify
```

---

## Rendering

### macOS / Linux
#### PNG (default)
```bash
python3 skills/puml-plantuml/scripts/render.py diagram.puml
```
#### SVG
```bash
python3 skills/puml-plantuml/scripts/render.py diagram.puml -f svg -o ./output/
```
#### SVG from stdin
```bash
cat diagram.puml | python3 skills/puml-plantuml/scripts/render.py --stdin -f svg -n "name" -o /tmp/
```
#### PDF
```bash
python3 skills/puml-plantuml/scripts/render.py diagram.puml -f pdf -o ./output/
```
#### Validate syntax only
```bash
python3 skills/puml-plantuml/scripts/render.py diagram.puml --check
```

### Windows
#### PNG (default)
```powershell
py skills\puml-plantuml\scripts\render.py diagram.puml
```
#### SVG
```powershell
py skills\puml-plantuml\scripts\render.py diagram.puml -f svg -o .\output\
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
plugins/puml-plantuml/
├── .claude-plugin/
│   └── plugin.json                    # Plugin metadata
├── README.md                          # This file
└── skills/
    └── puml-plantuml/                 # Bundled skill
        ├── SKILL.md                   # AI instruction file
        ├── LICENSE                    # AGPL-3.0
        ├── references/
        │   ├── syntax-quick-ref.md    # 2700+ lines — all 27 chapters
        │   ├── image-to-puml.md       # Vision reverse-engineering guide
        │   └── local-rendering.md     # Setup, CLI flags, formats, troubleshooting
        └── scripts/
            ├── bootstrap.sh           # macOS/Linux — zero-dep installer
            ├── bootstrap.ps1          # Windows — zero-dep installer
            ├── setup.py               # Detect/install Java + PlantUML
            └── render.py              # Cross-platform renderer (binary or JAR)
```

---

## Reference Files

| File | Content |
|------|---------|
| [`skills/puml-plantuml/references/syntax-quick-ref.md`](skills/puml-plantuml/references/syntax-quick-ref.md) | **2700+ lines** — complete syntax for all 27 chapters |
| [`skills/puml-plantuml/references/image-to-puml.md`](skills/puml-plantuml/references/image-to-puml.md) | Visual analysis guide for image → PUML reverse engineering |
| [`skills/puml-plantuml/references/local-rendering.md`](skills/puml-plantuml/references/local-rendering.md) | Setup, CLI flags, output formats, troubleshooting |

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

The bundled skill is [AGPL-3.0-only](skills/puml-plantuml/LICENSE). PlantUML itself is GPL/LGPL depending on the distribution you install.

## Author

**Erez Kalman / KSEC** · kaerez@gmail.com
