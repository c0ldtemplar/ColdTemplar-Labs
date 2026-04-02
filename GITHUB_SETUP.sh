#!/bin/bash
# Script para configurar y subir a GitHub

echo "🚀 ColdTemplar - Setup GitHub"
echo "=============================="
echo ""

# Validar que git está configurado
if ! git config --global user.email >/dev/null 2>&1; then
    echo "❌ Git no está configurado. Configúralo primero:"
    echo ""
    echo "git config --global user.name 'Tu Nombre'"
    echo "git config --global user.email 'tu.email@example.com'"
    exit 1
fi

echo "✅ Git configurado: $(git config --global user.name)"
echo ""

# Inicializar repositorio si no existe
if [ ! -d ".git" ]; then
    echo "📦 Inicializando repositorio local..."
    git init
    echo "✅ Repositorio inicializado"
else
    echo "✅ Repositorio ya existe"
fi

# Agregar archivos
echo ""
echo "📄 Agregando archivos..."
git add .
git status

# Commit inicial
echo ""
echo "💾 Haciendo commit inicial..."
git commit -m "Initial commit: ColdTemplar Voice Assistant v2.0

- Asistente de voz inteligente en español
- Reconocimiento de voz con Whisper
- Procesamiento LLM con Ollama
- Síntesis de voz femenina con Piper
- Detección inteligente de intenciones
- Documentación completa con 10 casos de uso
- Logging automático en JSON"

echo ""
echo "=============================="
echo "✅ Repositorio local listo"
echo "=============================="
echo ""
echo "📋 PASOS SIGUIENTES (en GitHub):"
echo ""
echo "1. Ve a https://github.com/new"
echo "2. Crea un repositorio público llamado: 'ColdTemplar-Labs'"
echo "3. NO inicialices con README (ya lo tenemos)"
echo "4. Copia comandos similares a estos:"
echo ""
echo "   git remote add origin https://github.com/TU_USUARIO/ColdTemplar-Labs.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "5. Si quieres usar SSH (más seguro):"
echo "   git remote add origin git@github.com:TU_USUARIO/ColdTemplar-Labs.git"
echo ""
echo "6. Verifica:"
echo "   git remote -v"
echo "   git branch -a"
echo ""
echo "=============================="
