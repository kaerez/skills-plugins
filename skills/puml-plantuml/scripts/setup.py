#!/usr/bin/env python3
"""
plantuml-expert/scripts/setup.py
Detect and install PlantUML + Java on any platform.
Requires: Python 3.9+ (stdlib only — no pip needed)

If Python itself is missing, run the bootstrap script first:
  macOS/Linux:  bash scripts/bootstrap.sh
  Windows:      PowerShell -File scripts\\bootstrap.ps1

Usage:
  python3 setup.py            # Auto-detect and install
  python3 setup.py --check    # Status check only
  python3 setup.py --java     # Only handle Java
  python3 setup.py --jar      # Force JAR download
  python3 setup.py --verify   # Run test render after setup
"""

import argparse
import glob
import os
import platform
import shutil
import subprocess
import sys
import urllib.request

OS          = platform.system()   # Darwin | Linux | Windows
HOME_PUML   = os.path.expanduser("~/.plantuml")
HOME_JAR    = os.path.join(HOME_PUML, "plantuml.jar")
JAR_URL     = "https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar"

# ── Terminal helpers ──────────────────────────────────────────────────────────
def ok(m):   print(f"  ✓  {m}")
def warn(m): print(f"  ⚠  {m}")
def info(m): print(f"  →  {m}")
def err(m):  print(f"  ✗  {m}", file=sys.stderr)
def sep(m):  print(f"\n── {m} " + "─" * max(0, 46 - len(m)))

def _run(cmd, check=True, capture=True, timeout=120):
    kw = {"capture_output": True, "text": True} if capture else {}
    return subprocess.run(cmd, check=check, timeout=timeout, **kw)

def _which(name):
    return shutil.which(name)

def _glob_last(patterns):
    """Return last (highest version) glob match across patterns."""
    for pat in patterns:
        matches = sorted(glob.glob(os.path.expanduser(pat)))
        if matches:
            return matches[-1]
    return None

# ── Python self-detection ─────────────────────────────────────────────────────
def find_python():
    """Return path to the current Python (or best available 3.9+)."""
    # The current interpreter is always the most reliable
    if sys.version_info >= (3, 9):
        return sys.executable
    # Otherwise search
    candidates = ["python3", "python3.12", "python3.11", "python3.10",
                  "python3.9", "py", "python"]
    for cmd in candidates:
        exe = _which(cmd)
        if not exe:
            continue
        try:
            r = subprocess.run([exe, "-c",
                                "import sys; sys.exit(0 if sys.version_info>=(3,9) else 1)"],
                               capture_output=True, timeout=5)
            if r.returncode == 0:
                return exe
        except (OSError, subprocess.TimeoutExpired):
            pass
    return None

def python_version_str(exe):
    try:
        r = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=5)
        return (r.stdout + r.stderr).strip()
    except Exception:
        return "unknown"

# ── Java detection ────────────────────────────────────────────────────────────
def find_java():
    """Return path to a working java 11+ binary, or None."""
    # 1. JAVA_HOME env
    jh = os.environ.get("JAVA_HOME")
    if jh:
        c = os.path.join(jh, "bin", "java" + (".exe" if OS == "Windows" else ""))
        if os.path.isfile(c):
            return c
    # 2. PATH
    j = _which("java")
    if j and _java_version_ok(j):
        return j
    # 3. macOS
    if OS == "Darwin":
        try:
            r = _run(["/usr/libexec/java_home", "-v", "11+"])
            c = os.path.join(r.stdout.strip(), "bin", "java")
            if os.path.isfile(c):
                return c
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
        found = _glob_last([
            "/Library/Java/JavaVirtualMachines/zulu*/Contents/Home/bin/java",
            "/Library/Java/JavaVirtualMachines/temurin*/Contents/Home/bin/java",
            "/Library/Java/JavaVirtualMachines/*/Contents/Home/bin/java",
        ])
        if found:
            return found
        brew = _brew_prefix()
        if brew:
            found = _glob_last([
                os.path.join(brew, "opt/openjdk*/bin/java"),
                os.path.join(brew, "opt/openjdk/bin/java"),
            ])
            if found:
                return found
    # 4. Windows
    if OS == "Windows":
        found = _glob_last([
            r"C:\Program Files\Zulu\zulu*\bin\java.exe",
            r"C:\Program Files\Eclipse Adoptium\jdk*\bin\java.exe",
            r"C:\Program Files\Eclipse Adoptium\jre*\bin\java.exe",
            r"C:\Program Files\Microsoft\jdk*\bin\java.exe",
            r"C:\Program Files\Java\jdk*\bin\java.exe",
            r"C:\Program Files\Java\jre*\bin\java.exe",
        ])
        if found:
            return found
    # 5. Linux
    if OS == "Linux":
        sdkman = os.path.expanduser("~/.sdkman/candidates/java/current/bin/java")
        if os.path.isfile(sdkman):
            return sdkman
        found = _glob_last([
            "/usr/lib/jvm/zulu*/bin/java",
            "/usr/lib/jvm/temurin*/bin/java",
            "/usr/lib/jvm/java-2*/bin/java",
            "/usr/lib/jvm/java-1*/bin/java",
            "/usr/lib/jvm/*/bin/java",
        ])
        if found:
            return found
    return None

def _java_version_ok(java_bin):
    """True if java_bin is version 11+."""
    try:
        r = subprocess.run([java_bin, "-version"],
                           capture_output=True, text=True, timeout=10)
        out = r.stderr + r.stdout
        # Formats: "11.0.x", "17", "21", "1.8.0" (old)
        import re
        m = re.search(r'version "([^"]+)"', out)
        if m:
            ver = m.group(1)
            major = int(ver.split(".")[0]) if not ver.startswith("1.") else int(ver.split(".")[1])
            return major >= 11
    except Exception:
        pass
    return False

def java_version_str(java_bin):
    try:
        r = subprocess.run([java_bin, "-version"],
                           capture_output=True, text=True, timeout=10)
        return (r.stderr + r.stdout).strip().splitlines()[0]
    except Exception:
        return "unknown"

def _brew_prefix():
    try:
        r = _run(["brew", "--prefix"])
        return r.stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None

# ── Java installation ─────────────────────────────────────────────────────────
def install_java():
    """Install Java 21 JRE via package manager. Returns True on success."""
    info("Java 11+ not found. Installing Java 21 JRE...")
    if OS == "Darwin":
        brew = _brew_prefix()
        if not brew:
            warn("Homebrew not found. Cannot auto-install Java on macOS.")
            warn("Install manually: https://adoptium.net  or  brew install --cask temurin")
            return False
        # Try Temurin cask first, fall back to formula
        for cmd in [
            ["brew", "install", "--cask", "temurin"],
            ["brew", "install", "--cask", "temurin@21"],
            ["brew", "install", "openjdk"],
        ]:
            try:
                _run(cmd, capture=False)
                ok("Java installed via Homebrew")
                return True
            except subprocess.CalledProcessError:
                pass
        err("Homebrew Java install failed. Try: brew install --cask temurin")
        return False

    if OS == "Linux":
        pkg_cmds = [
            (["apt-get"], ["sudo", "apt-get", "install", "-y", "default-jre-headless"]),
            (["dnf"],     ["sudo", "dnf", "install", "-y", "java-21-openjdk-headless"]),
            (["dnf"],     ["sudo", "dnf", "install", "-y", "java-17-openjdk-headless"]),
            (["pacman"],  ["sudo", "pacman", "-S", "--noconfirm", "jre-openjdk-headless"]),
            (["snap"],    ["sudo", "snap", "install", "openjdk"]),
            (["zypper"],  ["sudo", "zypper", "install", "-y", "java-21-openjdk-headless"]),
        ]
        for (detect, cmd) in pkg_cmds:
            if _which(detect[0]):
                try:
                    if detect[0] == "apt-get":
                        _run(["sudo", "apt-get", "update", "-qq"], capture=False)
                    _run(cmd, capture=False)
                    ok(f"Java installed via {detect[0]}")
                    return True
                except subprocess.CalledProcessError:
                    warn(f"{detect[0]} install failed, trying next...")
        err("Could not auto-install Java. Install manually: https://adoptium.net")
        return False

    if OS == "Windows":
        pkg_cmds = [
            (["winget"], ["winget", "install", "--id",
                          "EclipseAdoptium.Temurin.21.JRE", "-e", "--silent",
                          "--accept-package-agreements", "--accept-source-agreements"]),
            (["winget"], ["winget", "install", "--id",
                          "Azul.Zulu.21.JRE", "-e", "--silent",
                          "--accept-package-agreements", "--accept-source-agreements"]),
            (["choco"],  ["choco", "install", "temurin21", "-y"]),
            (["choco"],  ["choco", "install", "zulu21",    "-y"]),
            (["scoop"],  ["scoop", "install", "temurin-jre"]),
        ]
        for (detect, cmd) in pkg_cmds:
            if _which(detect[0]):
                try:
                    _run(cmd, capture=False)
                    ok(f"Java installed via {detect[0]}")
                    return True
                except subprocess.CalledProcessError:
                    warn(f"{detect[0]} install failed, trying next...")
        err("Could not auto-install Java. Install from: https://adoptium.net/temurin/releases/")
        return False

    return False

# ── PlantUML detection ────────────────────────────────────────────────────────
def find_plantuml_binary():
    return _which("plantuml")

def find_plantuml_jar():
    env_jar = os.environ.get("PLANTUML_JAR")
    if env_jar and os.path.isfile(env_jar):
        return env_jar
    if os.path.isfile(HOME_JAR):
        return HOME_JAR
    if OS == "Darwin":
        brew = _brew_prefix()
        if brew:
            found = _glob_last([
                os.path.join(brew, "Cellar/plantuml/*/libexec/plantuml.jar"),
                os.path.join(brew, "opt/plantuml/libexec/plantuml.jar"),
            ])
            if found:
                return found
    if OS == "Linux":
        for c in ["/usr/share/plantuml/plantuml.jar", "/usr/share/java/plantuml.jar"]:
            if os.path.isfile(c):
                return c
    if OS == "Windows":
        found = _glob_last([
            r"C:\ProgramData\chocolatey\lib\plantuml\tools\plantuml.jar",
            os.path.expanduser(r"~\scoop\apps\plantuml\current\plantuml.jar"),
        ])
        if found:
            return found
    return None

# ── PlantUML installation ─────────────────────────────────────────────────────
def install_plantuml():
    info("PlantUML not found. Installing...")
    if OS == "Darwin":
        brew = _brew_prefix()
        if brew and _which("brew"):
            try:
                _run(["brew", "install", "plantuml"], capture=False)
                ok("PlantUML installed via Homebrew")
                return True
            except subprocess.CalledProcessError:
                pass
    if OS == "Linux":
        for pm, cmd in [
            ("apt-get", ["sudo", "apt-get", "install", "-y", "plantuml"]),
            ("dnf",     ["sudo", "dnf",     "install", "-y", "plantuml"]),
            ("pacman",  ["sudo", "pacman",  "-S", "--noconfirm", "plantuml"]),
            ("snap",    ["sudo", "snap",    "install", "plantuml"]),
        ]:
            if _which(pm):
                try:
                    if pm == "apt-get":
                        _run(["sudo", "apt-get", "update", "-qq"], capture=False)
                    _run(cmd, capture=False)
                    ok(f"PlantUML installed via {pm}")
                    return True
                except subprocess.CalledProcessError:
                    warn(f"{pm} install failed, trying next...")
    if OS == "Windows":
        for pm, cmd in [
            ("winget", ["winget", "install", "--id", "plantuml.plantuml", "-e", "--silent",
                        "--accept-package-agreements", "--accept-source-agreements"]),
            ("choco",  ["choco", "install", "plantuml", "-y"]),
            ("scoop",  ["scoop", "install", "plantuml"]),
        ]:
            if _which(pm):
                try:
                    _run(cmd, capture=False)
                    ok(f"PlantUML installed via {pm}")
                    return True
                except subprocess.CalledProcessError:
                    warn(f"{pm} install failed, trying next...")
    # Fallback: JAR download
    return _download_jar()

def _download_jar():
    java = find_java()
    if not java:
        err("Java not found; cannot use JAR fallback. Run setup.py again (Java will be installed).")
        return False
    os.makedirs(HOME_PUML, exist_ok=True)
    info(f"Downloading plantuml.jar → {HOME_JAR}")

    def _progress(count, bsize, total):
        pct = min(100, int(count * bsize * 100 / total)) if total > 0 else 0
        print(f"\r  Downloading... {pct}%", end="", flush=True)

    try:
        urllib.request.urlretrieve(JAR_URL, HOME_JAR, _progress)
        print()
        ok(f"Downloaded: {HOME_JAR}  ({os.path.getsize(HOME_JAR)//1024} KB)")

        hint = os.path.join(HOME_PUML, "env-hint.txt")
        with open(hint, "w") as f:
            f.write(f"# Add to ~/.bashrc, ~/.zshrc, or PowerShell $PROFILE:\n")
            f.write(f"export PLANTUML_JAR={HOME_JAR}\n")
        info(f"Add to your shell profile:  export PLANTUML_JAR={HOME_JAR}")
        return True
    except Exception as e:
        err(f"Download failed: {e}")
        return False

# ── Test render ───────────────────────────────────────────────────────────────
_TEST_PUML = """@startuml
title plantuml-expert: setup verified
actor User
User -> App : request
App --> User : 200 OK
@enduml
"""

def verify():
    import tempfile
    binary = find_plantuml_binary()
    jar    = find_plantuml_jar()
    java   = find_java()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".puml",
                                     delete=False, encoding="utf-8") as f:
        f.write(_TEST_PUML)
        tmp = f.name
    outdir = tempfile.mkdtemp()
    try:
        cmd = (
            [binary, "-tsvg", "-o", outdir, tmp] if binary else
            [java, "-jar", jar, "-tsvg", "-o", outdir, tmp] if (java and jar) else None
        )
        if not cmd:
            err("Nothing to verify with — no backend available")
            return False
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if r.returncode == 0:
            ok("Test render succeeded ✓")
            return True
        else:
            err(f"Test render failed:\n{r.stderr}\n{r.stdout}")
            return False
    except Exception as e:
        err(f"Verify error: {e}")
        return False
    finally:
        os.unlink(tmp)
        import shutil as _sh; _sh.rmtree(outdir, ignore_errors=True)

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--check",  action="store_true", help="Status only, no install")
    p.add_argument("--java",   action="store_true", help="Ensure Java only")
    p.add_argument("--jar",    action="store_true", help="Force JAR download")
    p.add_argument("--verify", action="store_true", help="Test render after setup")
    a = p.parse_args()

    print(f"\n{'='*52}")
    print(f"  plantuml-expert setup  |  {OS} {platform.machine()}")
    print(f"{'='*52}")

    # ── Python self-report ────────────────────────────────────────────────────
    sep("Python")
    py = find_python()
    print(f"  executable : {py or '???'}")
    print(f"  version    : {python_version_str(py) if py else 'unknown'}")

    # ── Java ─────────────────────────────────────────────────────────────────
    sep("Java")
    java = find_java()
    if java:
        ok(f"{java}")
        print(f"  version : {java_version_str(java)}")
    else:
        warn("Java 11+ not detected")
        if not a.check:
            ok_java = install_java()
            java = find_java()
            if java:
                ok(f"Now available: {java}")
            else:
                err("Java still not found after install attempt")
                if a.java:
                    sys.exit(1)

    if a.java:
        print()
        sys.exit(0 if java else 1)

    # ── PlantUML ──────────────────────────────────────────────────────────────
    sep("PlantUML")
    binary = find_plantuml_binary()
    jar    = find_plantuml_jar()

    if binary:
        ok(f"Binary: {binary}")
    elif jar and java:
        ok(f"JAR: {jar}")
        ok(f"Java: {java}")
    else:
        warn("PlantUML not available")
        if a.check:
            print()
            sys.exit(1)
        if a.jar or not (binary or jar):
            ok_puml = install_plantuml()
            binary = find_plantuml_binary()
            jar    = find_plantuml_jar()
            if not (binary or (jar and find_java())):
                err("PlantUML install failed — see messages above")
                sys.exit(1)

    # ── Verify ────────────────────────────────────────────────────────────────
    if a.verify:
        sep("Test Render")
        verify()

    print()
    ok("Setup complete.")
    print(f"  Run: {py or 'python3'} render.py --detect\n")

if __name__ == "__main__":
    main()
