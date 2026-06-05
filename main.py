import os
import requests
import urllib.parse
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CHAVES CORRIGIDAS E SEGURAS
# O Render lerá estas variáveis do painel "Environment"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") 
FOLDER_ID = os.getenv("FOLDER_ID")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

MAPA_GENEROS = {28: "Ação", 12: "Aventura", 16: "Animação", 35: "Comédia", 80: "Crime", 18: "Drama", 27: "Terror", 878: "Ficção Científica"}

def buscar_info_tmdb(titulo):
    titulo_limpo = titulo.rsplit(".", 1)[0].split("-")[0].strip()
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={urllib.parse.quote(titulo_limpo)}&language=pt-BR"
    try:
        response = requests.get(url, timeout=5)
        dados = response.json()
        if dados.get("results"):
            filme = dados["results"][0]
            genero_id = filme.get("genre_ids", [0])[0]
            genero_nome = MAPA_GENEROS.get(genero_id, "Outros")
            capa = f"https://image.tmdb.org/t/p/w500{filme.get('poster_path')}"
            return genero_nome, capa
    except Exception as e:
        print(f"Erro ao buscar TMDB: {e}")
    return "Outros", "https://via.placeholder.com/500x750/141414/FFFFFF?text=Sem+Capa"

@app.get("/api/filmes/catalogo")
def listar_catalogo():
    query = f"'{FOLDER_ID}' in parents and trashed = false"
    url = f"https://www.googleapis.com/drive/v3/files?q={query}&fields=files(id,name,mimeType)&key={GOOGLE_API_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        arquivos = response.json().get("files", [])
    except:
        return {"categorias": {}}
    
    categorias = {}
    for f in arquivos:
        if "video" in f.get("mimeType", ""):
            genero, capa = buscar_info_tmdb(f["name"])
            if genero not in categorias: 
                categorias[genero] = []
            
            categorias[genero].append({
                "titulo": f["name"].rsplit(".", 1)[0],
                "capa_url": capa,
                "video_url": f"https://www.googleapis.com/drive/v3/files/{f['id']}?alt=media&key={GOOGLE_API_KEY}"
            })
    return {"categorias": categorias}
# Adicione isso logo após definir a rota /api/filmes/catalogo
    @app.get("/{full_path:path}")
    def catch_all(full_path: str):
        return {"message": "Rota não encontrada", "path_acessado": full_path}