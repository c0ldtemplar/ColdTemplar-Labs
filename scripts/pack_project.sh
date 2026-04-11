#!/bin/bash
BASE_DIR="/home/coldtemplar/Proyectos2026"
PROYECTO=$1

if [ -z "$PROYECTO" ]; then
    echo "Uso: ./pack_project.sh <nombre-carpeta>"
    exit 1
fi

TARGET_DIR="$BASE_DIR/$PROYECTO"
OUTPUT="$HOME/ColdTemplar-Labs/${PROYECTO}_context.txt"

if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: La carpeta $TARGET_DIR no existe."
    exit 1
fi

echo "📦 Empaquetando: $PROYECTO..."
echo "--- CONTEXTO GENERADO EL $(date) ---" > "$OUTPUT"

# Buscamos archivos en lib, src y functions
find "$TARGET_DIR" -maxdepth 10     \( -path "*/lib/*" -o -path "*/src/*" -o -path "*/functions/*" \)     -not -path "*/.*"     -not -path "*/build/*"     -not -path "*/node_modules/*"     \( -name "*.dart" -o -name "*.ts" -o -name "*.js" -o -name "pubspec.yaml" -o -name "package.json" \) | while read file; do
        echo -e "\n\n--- FILE: $file ---" >> "$OUTPUT"
        cat "$file" >> "$OUTPUT"
done

echo "✅ Contexto listo en: $OUTPUT"
echo "Líneas totales: $(wc -l < "$OUTPUT")"
