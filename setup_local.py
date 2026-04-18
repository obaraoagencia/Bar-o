"""Assistente simples para instalação e execução local do Bar-o.

Uso recomendado para iniciantes:
    python setup_local.py
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
VENV_DIR = PROJECT_ROOT / ".venv"
PYTHON_IN_VENV = VENV_DIR / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
PIP_IN_VENV = VENV_DIR / ("Scripts/pip.exe" if os.name == "nt" else "bin/pip")


def run(cmd: list[str]) -> None:
    print("\n> Executando:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def ensure_python_version() -> None:
    if sys.version_info < (3, 10):
        raise RuntimeError(
            "Python 3.10+ é obrigatório. Instale uma versão mais recente e tente novamente."
        )


def ensure_venv() -> None:
    if not VENV_DIR.exists():
        run([sys.executable, "-m", "venv", str(VENV_DIR)])


def install_dependencies() -> None:
    run([str(PYTHON_IN_VENV), "-m", "pip", "install", "--upgrade", "pip"])
    run([str(PIP_IN_VENV), "install", "-r", str(PROJECT_ROOT / "requirements.txt")])


def run_app() -> None:
    run([str(PYTHON_IN_VENV), str(PROJECT_ROOT / "main.py")])


def print_header() -> None:
    print("=" * 60)
    print("Bar-o | Instalação e execução assistida")
    print("Sistema:", platform.system(), platform.release())
    print("Projeto:", PROJECT_ROOT)
    print("=" * 60)


def main() -> None:
    print_header()
    ensure_python_version()
    ensure_venv()
    install_dependencies()
    print("\nInstalação concluída. Abrindo o sistema...")
    run_app()


if __name__ == "__main__":
    main()
