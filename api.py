import os
import pandas as pd
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from ultralytics import YOLO
from collections import Counter
from werkzeug.utils import secure_filename

# Configuração do App Flask
app = Flask(__name__)
CORS(app) # Permite que o React (de outra porta) chame esta API

# --- Configuração do Modelo (Baseado na sua Célula 10) ---
# Garanta que o modelo 'best.pt' esteja no caminho correto
MODEL_PATH = "modelo_yolo/best.pt"
# Se estiver rodando localmente, mude este caminho:
# MODEL_PATH = "runs/detect/treino_sala/weights/best.pt" 

model = YOLO(MODEL_PATH)

CLASS_TO_ID = {
    "cadeira_aluno": 0, "mesa_aluno": 1, "mesa_prof": 2, "cadeira_prof": 3,
    "lousa": 4, "palco_prof": 5, "caixa_som": 6, "camera": 7,
    "janela": 8, "projetor": 9, "extintor": 10,
}
# Mapeamento reverso para facilitar a leitura do resultado
ID_TO_CLASS = {v: k for k, v in CLASS_TO_ID.items()}

# Pasta temporária para uploads
UPLOAD_FOLDER = 'temp_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Função de Detecção (da sua Célula 10) ---
def detectar_objetos(img_path, iou=0.6):
    res = model(img_path, iou=iou)[0]
    ids = [int(c) for c in res.boxes.cls]
    contagens = Counter(ids)

    if contagens.get(CLASS_TO_ID["mesa_prof"], 0) > 0 and contagens.get(CLASS_TO_ID["palco_prof"], 0) == 0:
        contagens[CLASS_TO_ID["palco_prof"]] = 1
    return contagens

# --- O Endpoint da API ---
@app.route('/processar-projeto', methods=['POST'])
def processar_projeto():
    try:
        # 1. Salvar arquivos recebidos
        if 'planejamento' not in request.files:
            return jsonify({"erro": "Arquivo 'planejamento.xlsx' não encontrado"}), 400
        
        planejamento_file = request.files['planejamento']
        planejamento_path = os.path.join(UPLOAD_FOLDER, secure_filename(planejamento_file.filename))
        planejamento_file.save(planejamento_path)

        imagens_files = request.files.getlist('imagens')
        paths_imagens = {}
        for img_file in imagens_files:
            img_filename = secure_filename(img_file.filename)
            img_path = os.path.join(UPLOAD_FOLDER, img_filename)
            img_file.save(img_path)
            # Armazena o caminho pelo nome do arquivo para referência
            paths_imagens[img_filename] = img_path

        # 2. Processar Lógica (Baseado na sua Célula 10)
        df = pd.read_excel(planejamento_path)
        resultados_json = []

        # Mapeamento de nome de imagem (como no seu notebook)
        nome_imagens_map = {
            1: "Dia1-Inicio.png", 2: "Dia2-Cameras.png", 3: "Dia3-10Cadeiras.png",
            4: "Dia4-20Cadeiras.png", 5: "Dia5-Completo.png"
        }

        for idx, linha in df.iterrows():
            dia = int(linha["dia"])
            nome_arquivo_esperado = nome_imagens_map.get(dia)
            
            if not nome_arquivo_esperado or nome_arquivo_esperado not in paths_imagens:
                print(f"Aviso: Imagem para o Dia {dia} não foi enviada ou nome não corresponde.")
                continue
                
            img_path = paths_imagens[nome_arquivo_esperado]
            print(f"Analisando Dia {dia} - Imagem: {img_path}")

            detectado = detectar_objetos(img_path)
            linha_resultado = {"dia": dia, "imagem": nome_arquivo_esperado} # Adiciona o nome da imagem ao resultado

            for classe_nome in df.columns[1:]:
                esperado = int(linha[classe_nome])
                cls_id = CLASS_TO_ID.get(classe_nome)
                
                if cls_id is None: continue # Ignora colunas que não são classes

                qtd_detectada = detectado.get(cls_id, 0)
                status = "OK" if qtd_detectada >= esperado else f"Faltando {esperado - qtd_detectada}"
                
                linha_resultado[classe_nome] = {
                    "detectado": qtd_detectada,
                    "esperado": esperado,
                    "status": status
                }
            
            resultados_json.append(linha_resultado)

        # 3. Limpar arquivos temporários (opcional, mas recomendado)
        # os.remove(planejamento_path)
        # for path in paths_imagens.values():
        #     os.remove(path)

        # 4. Retornar o resultado como JSON
        return jsonify(resultados_json)

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# --- Iniciar o Servidor ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)