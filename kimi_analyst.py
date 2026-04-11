# ~/ColdTemplar-Labs/scripts/kimi_analyst.py
import openai
import sys
import os

client = openai.OpenAI(
    api_key="TU_MOONSHOT_API_KEY",
    base_url="https://api.moonshot.cn/v1",
)

def run_audit(project_name, query):
    file_path = f"/home/coldtemplar/ColdTemplar-Labs/{project_name}_context.txt"
    
    if not os.path.exists(file_path):
        return f"Error: No se encontró el archivo de contexto para {project_name}. Ejecuta primero el empaquetador."

    with open(file_path, 'r') as f:
        context = f.read()

    print(f"🚀 Enviando {project_name} a Kimi (Moonshot AI)...")
    
    response = client.chat.completions.create(
        model="moonshot-v1-128k",
        messages=[
            {"role": "system", "content": f"Eres el Senior DevOps & Arquitecto de {project_name}. Analiza el código buscando optimizaciones para syncrond.cl y estabilidad en Supabase/Flutter."},
            {"role": "user", "content": f"Contexto:\n{context}\n\nConsulta: {query}"}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python kimi_analyst.py <nombre-proyecto> '<consulta>'")
    else:
        print(run_audit(sys.argv[1], sys.argv[2]))
