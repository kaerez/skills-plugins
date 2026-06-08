# Local PlantUML Rendering Reference

Fully offline after setup. All rendering happens locally with no network calls.

## Setup (One-Time)

**Bootstrap — no Python/Java required to start:**

```bash
# macOS / Linux (bash is always available)
bash scripts/bootstrap.sh
bash scripts/bootstrap.sh --verify     # + test render

# Windows (PowerShell 5+ built into Windows 10/11)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\bootstrap.ps1
.\scripts\bootstrap.ps1 -Verify
```

**If Python is already available:**
```bash
python3 scripts/render.py --detect     # show what's found
python3 scripts/setup.py              # install anything missing
python3 scripts/setup.py --verify     # install + test render
python3 scripts/render.py --install-hint  # manual install instructions
```

Manual install by platform:

| Platform | Command |
|----------|---------|
| macOS    | `brew install plantuml` |
| Ubuntu/Debian | `sudo apt install plantuml` |
| Fedora/RHEL | `sudo dnf install plantuml` |
| Arch | `sudo pacman -S plantuml` |
| Snap (any Linux) | `sudo snap install plantuml` |
| Windows (winget) | `winget install plantuml.plantuml` |
| Windows (choco) | `choco install plantuml` |
| Windows (scoop) | `scoop install plantuml` |
| Any (JAR download) | See fallback section below |

### JAR Fallback (requires Java 11+)

```bash
mkdir -p ~/.plantuml
curl -L -o ~/.plantuml/plantuml.jar \
  https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar
export PLANTUML_JAR=~/.plantuml/plantuml.jar
```

Add `export PLANTUML_JAR=~/.plantuml/plantuml.jar` to `~/.bashrc`, `~/.zshrc`, or `$PROFILE` (PowerShell).

### Java Detection

The render script auto-detects Java from:
- `java` in PATH
- `$JAVA_HOME/bin/java`
- macOS: `/usr/libexec/java_home`, Zulu/Azul in `/Library/Java/JavaVirtualMachines/`
- Windows: `%JAVA_HOME%`, Azul `C:\Program Files\Zulu\`, Adoptium, Microsoft JDK
- Linux: SDKMAN `~/.sdkman/candidates/java/`, `/usr/lib/jvm/*/`

---

## Render Script Usage

```bash
# Render a file (PNG by default)
python3 scripts/render.py diagram.puml

# SVG output to specific directory
python3 scripts/render.py diagram.puml -f svg -o ./output/

# From stdin with a name
cat diagram.puml | python3 scripts/render.py --stdin -f svg -n "auth_flow" -o ./output/

# Syntax check (no image generated)
python3 scripts/render.py diagram.puml --check

# Detect available backend
python3 scripts/render.py --detect
```

## Direct CLI (if `plantuml` binary is in PATH)

```bash
plantuml diagram.puml                      # PNG
plantuml -tsvg diagram.puml               # SVG
plantuml -tpdf diagram.puml               # PDF
plantuml -ttxt diagram.puml               # ASCII art
plantuml -tsvg -o ./output/ diagram.puml  # custom outdir
plantuml -checkonly diagram.puml          # syntax only
plantuml -v diagram.puml                  # verbose
```

## Direct CLI (if using JAR directly)

```bash
java -jar ~/.plantuml/plantuml.jar -tsvg diagram.puml
java -jar $PLANTUML_JAR -tsvg -o ./output/ diagram.puml
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `PLANTUML_JAR` | Path to plantuml.jar (used if binary not in PATH) |
| `JAVA_HOME` | Java installation root |
| `GRAPHVIZ_DOT` | Path to `dot` executable (only if Graphviz not in PATH) |
| `PLANTUML_LIMIT_SIZE` | Max diagram dimension in pixels (default: 4096) |

## Output Formats

| Format | Flag | Extension | Notes |
|--------|------|-----------|-------|
| PNG | `-tpng` | `.png` | Default; raster |
| SVG | `-tsvg` | `.svg` | Vector; best for web/docs |
| PDF | `-tpdf` | `.pdf` | For documents |
| EPS | `-teps` | `.eps` | Print/vector |
| ASCII | `-ttxt` | `.txt` | Terminal |
| Unicode ASCII | `-tutxt` | `.utxt` | Better terminal |
| LaTeX/Tikz | `-tlatex` | `.tex` | LaTeX embedding |
| XMI | `-txmi` | `.xmi` | Class diagrams only |

## Layout Control Skinparams

```plantuml
skinparam nodesep 80        ' horizontal spacing between nodes
skinparam ranksep 100       ' vertical spacing between ranks
skinparam linetype ortho    ' orthogonal (right-angle) lines
skinparam linetype polyline ' polyline connections
skinparam dpi 150           ' raster output DPI (PNG only)
!pragma layout smetana      ' Graphviz-free pure-Java layout
```

## Troubleshooting

**`plantuml` not found after install**
→ Restart terminal / reload shell profile, then `python3 scripts/render.py --detect`

**Java not detected (Azul/Zulu)**
→ `export JAVA_HOME=/Library/Java/JavaVirtualMachines/zulu-21.jdk/Contents/Home` (macOS)
→ `set JAVA_HOME=C:\Program Files\Zulu\zulu-21` (Windows)

**Graphviz errors on class/component diagrams**
→ Install Graphviz: `brew install graphviz` / `apt install graphviz` / `choco install graphviz`
→ Or use `!pragma layout smetana` in diagram for Java-only layout

**Diagram truncated / too large**
→ `PLANTUML_LIMIT_SIZE=8192 plantuml -tsvg diagram.puml`

**Unicode/character encoding issues**
→ `plantuml -charset UTF-8 diagram.puml`
→ Ensure PUML file is saved as UTF-8
