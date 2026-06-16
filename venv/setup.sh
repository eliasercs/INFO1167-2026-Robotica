#!/usr/bin/env bash
VENV_DIR="venv"

# Si no existe el entorno virtual
if [ ! -d "$VENV_DIR" ]; then
    echo "Creando entorno virtual..."
    virtualenv "$VENV_DIR"
fi

# Si el primer argumento es "activate"
if [ "$1" = "activate" ]; then
    echo "Activando entorno virtual..."
    
    # IMPORTANTE: usar "source" para activar en la sesión actual
    source "$VENV_DIR/bin/activate"
fi