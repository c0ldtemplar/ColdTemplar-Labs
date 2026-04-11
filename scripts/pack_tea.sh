#!/bin/bash
# Ruta de tu proyecto tea-rocalian (ajústala si es necesario)
PROJECT_DIR="/home/coldtemplar/proyectos2026/tea-rocalian"
OUTPUT="tea_context.txt"

echo "📦 Empaquetando código de tea-rocalian..."
echo "--- CONTEXTO GENERADO EL $(date) ---" > $OUTPUT

# Buscamos archivos .dart (Flutter) y .ts/.js (Node/Supabase)
# Excluimos carpetas generadas para no saturar tokens
find $PROJECT_DIR -maxdepth 10 \( -path "*/lib/*" -o -path "*/src/*" \)     -not -path "*/.*"     -not -path "*/build/*"     -not -path "*/node_modules/*"     \( -name "*.dart" -o -name "*.ts" -o -name "*.js" \) | while read file; do
        echo -e "\n\n--- FILE: $file ---" >> $OUTPUT
        cat "$file" >> $OUTPUT
done

echo "✅ Contexto listo en $OUTPUT ($(wc -l < $OUTPUT) líneas)"
