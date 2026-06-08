#!/usr/bin/env bash
# ============================================================
# plantuml-expert/scripts/bootstrap.sh
# One-shot bootstrap for macOS and Linux.
# Requires: bash (pre-installed on all macOS and Linux systems)
# No Python or Java needed to run this script.
#
# Usage:
#   chmod +x scripts/bootstrap.sh && scripts/bootstrap.sh
#   scripts/bootstrap.sh --verify     # also run a test render
#   scripts/bootstrap.sh --java-only  # only ensure Java is present
# ============================================================
set -euo pipefail

VERIFY=false
JAVA_ONLY=false
for arg in "$@"; do
  case "$arg" in
    --verify)    VERIFY=true ;;
    --java-only) JAVA_ONLY=true ;;
  esac
done

OS="$(uname -s)"   # Darwin | Linux
ARCH="$(uname -m)" # x86_64 | arm64 | aarch64

ok()   { echo "  ✓  $*"; }
warn() { echo "  ⚠  $*"; }
info() { echo "  →  $*"; }
err()  { echo "  ✗  $*" >&2; }
sep()  { echo; echo "── $* ──────────────────────────────────────────"; }

# ── Brew helper (macOS) ───────────────────────────────────────────────────────
ensure_brew() {
  if ! command -v brew &>/dev/null; then
    warn "Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # Add brew to PATH for Apple Silicon
    [[ "$ARCH" == "arm64" ]] && eval "$(/opt/homebrew/bin/brew shellenv)"
  fi
}

# ── Python detection ──────────────────────────────────────────────────────────
find_python() {
  for cmd in python3 python3.12 python3.11 python3.10 python3.9 python; do
    if command -v "$cmd" &>/dev/null; then
      ver=$("$cmd" -c "import sys; print(sys.version_info[:2])" 2>/dev/null || true)
      # Must be (3, 9) or higher
      if "$cmd" -c "import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)" 2>/dev/null; then
        echo "$cmd"
        return 0
      fi
    fi
  done
  return 1
}

install_python() {
  info "Python 3.9+ not found. Installing..."
  if [[ "$OS" == "Darwin" ]]; then
    ensure_brew
    brew install python
  elif command -v apt-get &>/dev/null; then
    sudo apt-get update -qq && sudo apt-get install -y python3 python3-pip
  elif command -v dnf &>/dev/null; then
    sudo dnf install -y python3
  elif command -v pacman &>/dev/null; then
    sudo pacman -S --noconfirm python
  elif command -v snap &>/dev/null; then
    sudo snap install python312 --classic
  else
    err "Cannot auto-install Python. Please install Python 3.9+ manually."
    err "https://www.python.org/downloads/"
    exit 1
  fi
}

# ── Java detection ────────────────────────────────────────────────────────────
find_java() {
  # 1. java in PATH
  if command -v java &>/dev/null; then
    echo "$(command -v java)"
    return 0
  fi
  # 2. JAVA_HOME
  if [[ -n "${JAVA_HOME:-}" && -x "$JAVA_HOME/bin/java" ]]; then
    echo "$JAVA_HOME/bin/java"
    return 0
  fi
  # 3. macOS java_home helper
  if [[ "$OS" == "Darwin" ]]; then
    jh=$(/usr/libexec/java_home -v 11+ 2>/dev/null || true)
    if [[ -n "$jh" && -x "$jh/bin/java" ]]; then
      echo "$jh/bin/java"
      return 0
    fi
    # Azul/Zulu on macOS
    for f in /Library/Java/JavaVirtualMachines/zulu*/Contents/Home/bin/java \
              /Library/Java/JavaVirtualMachines/*/Contents/Home/bin/java; do
      [[ -x "$f" ]] && { echo "$f"; return 0; }
    done
    # Homebrew openjdk
    brew_prefix=$(brew --prefix 2>/dev/null || true)
    for f in "$brew_prefix"/opt/openjdk*/bin/java "$brew_prefix"/opt/openjdk/bin/java; do
      [[ -x "$f" ]] && { echo "$f"; return 0; }
    done
  fi
  # 4. Linux: SDKMAN + common jvm paths
  sdkman="$HOME/.sdkman/candidates/java/current/bin/java"
  [[ -x "$sdkman" ]] && { echo "$sdkman"; return 0; }
  for f in /usr/lib/jvm/zulu*/bin/java \
            /usr/lib/jvm/temurin*/bin/java \
            /usr/lib/jvm/java-*/bin/java \
            /usr/lib/jvm/*/bin/java; do
    [[ -x "$f" ]] && { echo "$f"; return 0; }
  done
  return 1
}

install_java() {
  info "Java 11+ not found. Installing..."
  if [[ "$OS" == "Darwin" ]]; then
    ensure_brew
    # Prefer Temurin (Adoptium open JDK, widely trusted)
    if brew info --cask temurin &>/dev/null 2>&1; then
      brew install --cask temurin
    else
      brew install openjdk
      jdk_path="$(brew --prefix)/opt/openjdk"
      info "Linking: sudo ln -sfn $jdk_path /Library/Java/JavaVirtualMachines/openjdk.jdk"
      sudo ln -sfn "$jdk_path/libexec/openjdk.jdk" \
           /Library/Java/JavaVirtualMachines/openjdk.jdk 2>/dev/null || true
    fi
  elif command -v apt-get &>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y default-jre-headless
  elif command -v dnf &>/dev/null; then
    sudo dnf install -y java-21-openjdk-headless 2>/dev/null || \
    sudo dnf install -y java-17-openjdk-headless 2>/dev/null || \
    sudo dnf install -y java-11-openjdk-headless
  elif command -v pacman &>/dev/null; then
    sudo pacman -S --noconfirm jre-openjdk-headless
  elif command -v snap &>/dev/null; then
    sudo snap install openjdk
  else
    err "Cannot auto-install Java. Install Java 11+ manually:"
    err "  macOS:  brew install --cask temurin"
    err "  Linux:  sudo apt install default-jre-headless"
    err "  Any:    https://adoptium.net/temurin/releases/"
    exit 1
  fi
}

# ── PlantUML detection / install ─────────────────────────────────────────────
find_plantuml() {
  command -v plantuml &>/dev/null && { command -v plantuml; return 0; }
  # Homebrew jar location
  brew_prefix=$(brew --prefix 2>/dev/null || true)
  for f in "$brew_prefix"/Cellar/plantuml/*/libexec/plantuml.jar \
            "$brew_prefix"/opt/plantuml/libexec/plantuml.jar \
            /usr/share/plantuml/plantuml.jar \
            /usr/share/java/plantuml.jar \
            "$HOME/.plantuml/plantuml.jar"; do
    [[ -f "$f" ]] && { echo "jar:$f"; return 0; }
  done
  return 1
}

install_plantuml() {
  info "PlantUML not found. Installing..."
  if [[ "$OS" == "Darwin" ]]; then
    ensure_brew
    brew install plantuml
  elif command -v apt-get &>/dev/null; then
    sudo apt-get update -qq && sudo apt-get install -y plantuml
  elif command -v dnf &>/dev/null; then
    sudo dnf install -y plantuml
  elif command -v pacman &>/dev/null; then
    sudo pacman -S --noconfirm plantuml
  elif command -v snap &>/dev/null; then
    sudo snap install plantuml
  else
    # Fallback: download jar
    info "No package manager found. Downloading plantuml.jar..."
    java_bin=$(find_java || true)
    if [[ -z "$java_bin" ]]; then
      err "Java required for JAR fallback but not found."
      exit 1
    fi
    mkdir -p "$HOME/.plantuml"
    curl -fsSL \
      "https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar" \
      -o "$HOME/.plantuml/plantuml.jar"
    ok "Downloaded: $HOME/.plantuml/plantuml.jar"
    echo "export PLANTUML_JAR=$HOME/.plantuml/plantuml.jar" >> "$HOME/.bashrc"
    echo "export PLANTUML_JAR=$HOME/.plantuml/plantuml.jar" >> "$HOME/.zshrc" 2>/dev/null || true
    info "Added PLANTUML_JAR to ~/.bashrc / ~/.zshrc"
  fi
}

# ── Main ──────────────────────────────────────────────────────────────────────
echo
echo "╔══════════════════════════════════════════════════╗"
echo "║       plantuml-expert bootstrap ($OS)          ║"
echo "╚══════════════════════════════════════════════════╝"

sep "Python 3"
python_cmd=$(find_python || true)
if [[ -n "$python_cmd" ]]; then
  ver=$("$python_cmd" --version 2>&1)
  ok "Found: $python_cmd  ($ver)"
else
  install_python
  python_cmd=$(find_python || true)
  [[ -z "$python_cmd" ]] && { err "Python install failed."; exit 1; }
  ok "Installed: $python_cmd"
fi

if $JAVA_ONLY; then
  sep "Java"
  java_bin=$(find_java || true)
  if [[ -n "$java_bin" ]]; then
    ver=$("$java_bin" -version 2>&1 | head -1)
    ok "Found: $java_bin  ($ver)"
  else
    install_java
    java_bin=$(find_java || true)
    [[ -z "$java_bin" ]] && { err "Java install failed."; exit 1; }
    ok "Installed: $java_bin"
  fi
  echo
  echo "✅ Java ready."
  exit 0
fi

sep "Setup (Python-based)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if $VERIFY; then
  "$python_cmd" "$SCRIPT_DIR/setup.py" --verify
else
  "$python_cmd" "$SCRIPT_DIR/setup.py"
fi

echo
echo "✅ Bootstrap complete."
echo "   Run: $python_cmd $SCRIPT_DIR/render.py --detect"
