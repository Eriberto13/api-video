from flask import Flask, request, jsonify
import yt_dlp
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

    # Método 1: Tentativa direta com yt-dlp atualizado
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            download_url = info.get('url')
            
            if download_url:
                return jsonify({
                    "titulo": info.get('title', 'Video'),
                    "download_url": download_url
                })
    except Exception as e:
        print(f"Erro yt-dlp: {e}")

    # Método 2: Fallback usando API espelho (Invidious) caso o Render esteja bloqueado
    try:
        video_id = ""
        if "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1].split("?")[0]
        elif "watch?v=" in url:
            video_id = url.split("watch?v=")[1].split("&")[0]

        if video_id:
            inv_res = requests.get(f"https://inv.nadeko.net/api/v1/videos/{video_id}", timeout=10)
            if inv_res.status_code == 200:
                data = inv_res.json()
                formatos = data.get('formatStreams', [])
                if formatos:
                    # Pega o formato de maior qualidade disponível com vídeo/áudio combinados
                    melhor_formato = formatos[-1]
                    return jsonify({
                        "titulo": data.get('title', 'Video'),
                        "download_url": melhor_formato.get('url')
                    })
    except Exception as e:
        print(f"Erro Invidious Fallback: {e}")

    return jsonify({"erro": "Nao foi possivel extrair o video do YouTube no momento"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
