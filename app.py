from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "API de Download Ativa!"

@app.route('/api/extrair', methods=['GET'])
def extrair():
    url = request.args.get('url')
    if not url:
        return jsonify({"erro": "URL nao fornecida"}), 400

    # Usando o serviço do Cobalt como motor de extração principal
    cobalt_url = "https://api.cobalt.tools/api/json"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    payload = {
        "url": url,
        "vQuality": "1080",
        "filenamePattern": "basic"
    }

    try:
        response = requests.post(cobalt_url, json=payload, headers=headers, timeout=15)
        data = response.json()

        # Resposta com sucesso do Cobalt
        if response.status_code == 200 and data.get("status") in ["stream", "redirect"]:
            return jsonify({
                "titulo": "Video_Download",
                "download_url": data.get("url")
            })
        elif data.get("status") == "picker":
            # Caso seja um carrossel ou escolha de múltiplos itens
            picker_items = data.get("picker", [])
            if picker_items:
                return jsonify({
                    "titulo": "Video_Download",
                    "download_url": picker_items[0].get("url")
                })

        return jsonify({"erro": f"Cobalt erro: {data.get('text', 'Nao foi possivel extrair o video')}"}), 400

    except Exception as e:
        return jsonify({"erro": f"Exceção no servidor: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
