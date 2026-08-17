from flask import Flask, request, jsonify
import yt_dlp
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

    # Limpa parâmetros extras da URL se houver
    if '?' in url:
        url = url.split('?')[0]

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        # Simula um navegador real para o YouTube não bloquear o servidor
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Pega a URL do vídeo extraído
            download_url = info.get('url')
            
            # Caso a estrutura do JSON venha encadeada em formatos
            if not download_url and 'requested_formats' in info:
                download_url = info['requested_formats'][0].get('url')

            return jsonify({
                "titulo": info.get('title', 'Video'),
                "download_url": download_url
            })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
