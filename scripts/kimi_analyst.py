import os
import openai
import sys

# 1. Validación de la API Key
api_key = os.getenv("MOONSHOT_API_KEY")
if not api_key:
    print("❌ Error: La variable MOONSHOT_API_KEY no está definida en el sistema.")
    sys.exit(1)

# 2. Configuración del cliente Moonshot
client = openai.OpenAI(
    api_key=api_key,
    base_url="https://api.moonshot.cn/v1",
)

# Edita solo esta parte en tu kimi_analyst.py (Línea 19 aprox)
def run_audit(project_name, query):
    # CORRECCIÓN: Eliminamos el sufijo extra para que coincida con el bash
    file_path = f"/home/coldtemplar/ColdTemplar-Labs/{project_name}_context.txt"    
    if not os.path.exists(file_path):
        return f"❌ Error: No se encontró el contexto en {file_path}. Ejecuta el empaquetador primero."

    try:
        with open(file_path, 'r') as f:
            context = f.read()

        print(f"🚀 Enviando contexto de {project_name} a Kimi AI...")
        
        response = client.chat.completions.create(
            model="moonshot-v1-128k",
            messages=[
                {"role": "system", "content": f"Eres el Senior DevOps & Arquitecto de {project_name}. Analiza el código buscando optimizaciones para syncrond.cl."},
                {"role": "user", "content": f"CONTEXTO DEL PROYECTO:\n{context}\n\nCONSULTA TÉCNICA: {query}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error durante la llamada a la API: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python kimi_analyst.py <nombre-proyecto> '<consulta>'")
    else:
        # sys.argv[1] es el nombre del proyecto (tea-connect)
        # sys.argv[2] es el prompt del usuario
        result = run_audit(sys.argv[1], sys.argv[2])
        print("\n--- 🤖 RESPUESTA DE KIMI AI ---\n")
        print(result)
