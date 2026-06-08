#!/usr/bin/env python3
"""
plantuml-expert/scripts/render.py
Cross-platform PlantUML renderer — no hardcoded paths, no internet required at render time.

Auto-detects (in priority order):
  1. `plantuml` binary in PATH (installed via brew/apt/choco/scoop/winget)
  2. PLANTUML_JAR env var + any detected Java
  3. ~/.plantuml/plantuml.jar + any detected Java
  4. Platform-specific well-known JAR locations

Usage:
  python3 render.py <file.puml> [-f FORMAT] [-o OUTDIR]
  cat file.puml | python3 render.py --stdin [-f FORMAT] [-o OUTDIR] [-n NAME]
  python3 render.py <file.puml> --check
  python3 render.py --detect        # Show what was found on this system
  python3 render.py --install-hint  # Show install instructions for this platform

Formats: png (default), svg, pdf, eps, txt, utxt, latex, xmi
"""

# PEP 563: make all annotations lazy strings so PEP 604 unions (e.g. `str | None`)
# parse on Python 3.9 as well (they would otherwise be evaluated eagerly and raise
# TypeError at function-definition time on < 3.10). Keeps the stated 3.9+ floor true.
from __future__ import annotations

import argparse
import glob
import os
import platform
import shutil
import subprocess
import sys
import tempfile

# ── Output format maps ────────────────────────────────────────────────────────
FMT_FLAG = {
    "png": "-tpng", "svg": "-tsvg", "pdf": "-tpdf", "eps": "-teps",
    "txt": "-ttxt", "utxt": "-tutxt", "latex": "-tlatex", "xmi": "-txmi",
}
FMT_EXT = {
    "png": "png", "svg": "svg", "pdf": "pdf", "eps": "eps",
    "txt": "txt", "utxt": "utxt", "latex": "tex", "xmi": "xmi",
}
OS = platform.system()  # "Darwin" | "Windows" | "Linux"

# ── Python self-detection ─────────────────────────────────────────────────────
def find_python() -> str | None:
    """Return the current Python executable (or best available 3.9+)."""
    if sys.version_info >= (3, 9):
        return sys.executable
    for cmd in ["python3", "python3.12", "python3.11", "python3.10",
                "python3.9", "py", "python"]:
        exe = shutil.which(cmd)
        if not exe:
            continue
        try:
            r = subprocess.run(
                [exe, "-c", "import sys; sys.exit(0 if sys.version_info>=(3,9) else 1)"],
                capture_output=True, timeout=5)
            if r.returncode == 0:
                return exe
        except (OSError, subprocess.TimeoutExpired):
            pass
    return None

# ── Java detection ────────────────────────────────────────────────────────────

def _glob_first(patterns: list) -> str | None:
    """Return the first file that matches any of the glob patterns."""
    for pat in patterns:
        matches = sorted(glob.glob(os.path.expanduser(pat)))
        if matches:
            return matches[-1]  # highest version (last alphabetically)
    return None

def find_java() -> str | None:
    """Return path to a working `java` executable, or None."""
    # 1. JAVA_HOME env var
    jh = os.environ.get("JAVA_HOME")
    if jh:
        candidate = os.path.join(jh, "bin", "java" + (".exe" if OS == "Windows" else ""))
        if os.path.isfile(candidate):
            return candidate

    # 2. java already in PATH
    java = shutil.which("java")
    if java:
        return java

    # 3. Platform-specific well-known locations
    if OS == "Darwin":
        # macOS java_home helper
        try:
            result = subprocess.run(
                ["/usr/libexec/java_home", "-v", "11+"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                candidate = os.path.join(result.stdout.strip(), "bin", "java")
                if os.path.isfile(candidate):
                    return candidate
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        # Azul/Zulu on macOS
        azul = _glob_first([
            "/Library/Java/JavaVirtualMachines/zulu*/Contents/Home/bin/java",
            "/Library/Java/JavaVirtualMachines/*/Contents/Home/bin/java",
        ])
        if azul:
            return azul
        # Homebrew OpenJDK
        brew_prefix = _get_brew_prefix()
        if brew_prefix:
            brew_java = _glob_first([
                os.path.join(brew_prefix, "opt/openjdk*/bin/java"),
                os.path.join(brew_prefix, "opt/openjdk/bin/java"),
            ])
            if brew_java:
                return brew_java

    elif OS == "Windows":
        # Azul/Zulu on Windows
        azul = _glob_first([
            r"C:\Program Files\Zulu\zulu*\bin\java.exe",
            r"C:\Program Files\Eclipse Adoptium\jdk*\bin\java.exe",
            r"C:\Program Files\Microsoft\jdk*\bin\java.exe",
            r"C:\Program Files\Java\jdk*\bin\java.exe",
            r"C:\Program Files\Java\jre*\bin\java.exe",
        ])
        if azul:
            return azul

    elif OS == "Linux":
        # SDKMAN
        sdkman = os.path.expanduser("~/.sdkman/candidates/java/current/bin/java")
        if os.path.isfile(sdkman):
            return sdkman
        # Azul/Zulu on Linux + generic jvm paths
        jvm = _glob_first([
            "/usr/lib/jvm/zulu*/bin/java",
            "/usr/lib/jvm/temurin*/bin/java",
            "/usr/lib/jvm/java-*/bin/java",
            "/usr/lib/jvm/*/bin/java",
        ])
        if jvm:
            return jvm

    return None

# ── PlantUML JAR / binary detection ──────────────────────────────────────────

def _get_brew_prefix() -> str | None:
    try:
        r = subprocess.run(["brew", "--prefix"], capture_output=True, text=True, timeout=5)
        return r.stdout.strip() if r.returncode == 0 else None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None

def find_plantuml_binary() -> str | None:
    """Return `plantuml` binary path if available."""
    return shutil.which("plantuml")

def find_plantuml_jar() -> str | None:
    """Return path to plantuml.jar if found."""
    # 1. Explicit env var
    env_jar = os.environ.get("PLANTUML_JAR")
    if env_jar and os.path.isfile(env_jar):
        return env_jar

    # 2. Our own download location
    home_jar = os.path.expanduser("~/.plantuml/plantuml.jar")
    if os.path.isfile(home_jar):
        return home_jar

    if OS == "Darwin":
        brew_prefix = _get_brew_prefix()
        if brew_prefix:
            jar = _glob_first([
                os.path.join(brew_prefix, "Cellar/plantuml/*/libexec/plantuml.jar"),
                os.path.join(brew_prefix, "opt/plantuml/libexec/plantuml.jar"),
            ])
            if jar:
                return jar

    elif OS == "Linux":
        candidates = [
            "/usr/share/plantuml/plantuml.jar",
            "/usr/share/java/plantuml.jar",
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c

    elif OS == "Windows":
        jar = _glob_first([
            r"C:\ProgramData\chocolatey\lib\plantuml\tools\plantuml.jar",
            os.path.expanduser(r"~\scoop\apps\plantuml\current\plantuml.jar"),
            os.path.expanduser(r"~\AppData\Local\Programs\plantuml\plantuml.jar"),
        ])
        if jar:
            return jar

    return None

# ── Backend resolution ────────────────────────────────────────────────────────

class Backend:
    """Resolved PlantUML execution backend."""
    def __init__(self, mode: str, binary: str = None, java: str = None, jar: str = None):
        self.mode = mode        # "binary" | "jar"
        self.binary = binary
        self.java = java
        self.jar = jar

    def base_cmd(self) -> list:
        if self.mode == "binary":
            return [self.binary]
        return [self.java, "-jar", self.jar]

    def __str__(self):
        if self.mode == "binary":
            return f"binary: {self.binary}"
        return f"jar: {self.jar}  java: {self.java}"

def resolve_backend() -> Backend | None:
    """Find the best available PlantUML backend."""
    binary = find_plantuml_binary()
    if binary:
        return Backend(mode="binary", binary=binary)

    jar = find_plantuml_jar()
    java = find_java()
    if jar and java:
        return Backend(mode="jar", java=java, jar=jar)

    return None

# ── Install hints ─────────────────────────────────────────────────────────────

INSTALL_HINTS = {
    "Darwin": """
PlantUML not found on macOS. Install with one of:

  brew install plantuml           # Homebrew (recommended, installs Java too)
  sdk install java && \\
    curl -L -o ~/.plantuml/plantuml.jar \\
    https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar

Set PLANTUML_JAR=~/.plantuml/plantuml.jar if using the manual JAR method.
""",
    "Linux": """
PlantUML not found on Linux. Install with one of:

  sudo apt install plantuml       # Debian/Ubuntu
  sudo dnf install plantuml       # Fedora/RHEL
  sudo pacman -S plantuml         # Arch
  sudo snap install plantuml      # Snap (universal)

Or download the JAR manually (requires Java 11+):
  mkdir -p ~/.plantuml
  curl -L -o ~/.plantuml/plantuml.jar \\
    https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar
  export PLANTUML_JAR=~/.plantuml/plantuml.jar
""",
    "Windows": """
PlantUML not found on Windows. Install with one of:

  winget install plantuml.plantuml         # winget
  choco install plantuml                   # Chocolatey
  scoop install plantuml                   # Scoop

Or download the JAR manually (requires Java 11+):
  New-Item -ItemType Directory -Force "$HOME\\.plantuml"
  Invoke-WebRequest -Uri "https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar" `
    -OutFile "$HOME\\.plantuml\\plantuml.jar"
  $env:PLANTUML_JAR = "$HOME\\.plantuml\\plantuml.jar"

Java (if not installed): winget install EclipseAdoptium.Temurin.21.JRE
                      or winget install Azul.Zulu.21.JRE
""",
}

# ── Core rendering ────────────────────────────────────────────────────────────

def _run(cmd: list, timeout: int = 120) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError((result.stderr + result.stdout).strip() or "PlantUML failed")
    return result

def render_file(path: str, fmt: str = "png", outdir: str = None,
                backend: Backend = None) -> str:
    """Render a .puml file. Returns absolute path of output file."""
    backend = backend or resolve_backend()
    if not backend:
        raise EnvironmentError(
            "PlantUML not found.\n" +
            INSTALL_HINTS.get(OS, INSTALL_HINTS["Linux"])
        )
    path = os.path.abspath(path)
    cmd = backend.base_cmd() + [FMT_FLAG.get(fmt, "-tpng")]
    if outdir:
        os.makedirs(outdir, exist_ok=True)
        cmd += ["-o", os.path.abspath(outdir)]
    cmd.append(path)
    _run(cmd)
    base = os.path.splitext(os.path.basename(path))[0]
    d = os.path.abspath(outdir) if outdir else os.path.dirname(path)
    return os.path.join(d, f"{base}.{FMT_EXT.get(fmt, 'png')}")

def render_string(content: str, fmt: str = "png", outdir: str = None,
                  name: str = "diagram", backend: Backend = None) -> str:
    """Render PlantUML string. Returns output file path."""
    backend = backend or resolve_backend()
    outdir = os.path.abspath(outdir or tempfile.mkdtemp())
    os.makedirs(outdir, exist_ok=True)
    tmp = os.path.join(outdir, f"{name}.puml")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(content)
    try:
        return render_file(tmp, fmt, outdir, backend)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

def check_syntax(source: str, is_file: bool = True,
                 backend: Backend = None) -> tuple:
    """Returns (ok: bool, message: str)."""
    backend = backend or resolve_backend()
    if not backend:
        return False, "PlantUML not found. Run: python3 render.py --install-hint"

    if is_file:
        tmp = os.path.abspath(source)
        cleanup = False
    else:
        tmp_f = tempfile.NamedTemporaryFile(mode="w", suffix=".puml",
                                            delete=False, encoding="utf-8")
        tmp_f.write(source)
        tmp_f.close()
        tmp = tmp_f.name
        cleanup = True

    try:
        cmd = backend.base_cmd() + ["-checkonly", tmp]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        out = (r.stdout + r.stderr).strip()
        ok = r.returncode == 0 and "error" not in out.lower()
        return ok, out or ("OK" if ok else "Error")
    finally:
        if cleanup and os.path.exists(tmp):
            os.unlink(tmp)

# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(
        description="Cross-platform PlantUML renderer (offline)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("input", nargs="?", help="Input .puml file")
    p.add_argument("-f", "--format", default="png", choices=list(FMT_FLAG))
    p.add_argument("-o", "--output", help="Output directory")
    p.add_argument("-n", "--name", default="diagram",
                   help="Base filename (used with --stdin)")
    p.add_argument("--stdin", action="store_true", help="Read PUML from stdin")
    p.add_argument("--check", action="store_true", help="Syntax check only")
    p.add_argument("--detect", action="store_true",
                   help="Show detected backend and exit")
    p.add_argument("--install-hint", action="store_true",
                   help="Show install instructions for this platform")
    a = p.parse_args()

    if a.install_hint:
        print(INSTALL_HINTS.get(OS, INSTALL_HINTS["Linux"]))
        return

    if a.detect:
        backend = resolve_backend()
        java = find_java()
        jar = find_plantuml_jar()
        binary = find_plantuml_binary()
        python = find_python()
        print(f"Platform  : {OS} ({platform.machine()})")
        print(f"python    : {python or '(not found)'}")
        print(f"plantuml  : {binary or '(not found)'}")
        print(f"java      : {java or '(not found)'}")
        print(f"puml jar  : {jar or '(not found)'}")
        print(f"Backend   : {backend or '*** NONE — run bootstrap script ***'}")
        if not (binary or (jar and java)):
            print()
            print("  To fix:")
            if OS == "Windows":
                print(r"    PowerShell -ExecutionPolicy Bypass -File scripts\bootstrap.ps1")
            else:
                print("    bash scripts/bootstrap.sh")
        return

    backend = resolve_backend()

    if a.stdin:
        content = sys.stdin.read()
        if a.check:
            ok, msg = check_syntax(content, is_file=False, backend=backend)
            print(f"{'✓' if ok else '✗'} {msg}")
            sys.exit(0 if ok else 1)
        out = render_string(content, a.format, a.output, a.name, backend)
        print(f"Rendered: {out}")

    elif a.input:
        if a.check:
            ok, msg = check_syntax(a.input, is_file=True, backend=backend)
            print(f"{'✓' if ok else '✗'} {msg}")
            sys.exit(0 if ok else 1)
        out = render_file(a.input, a.format, a.output, backend)
        print(f"Rendered: {out}")

    else:
        p.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
