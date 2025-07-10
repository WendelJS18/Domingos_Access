import os
import cv2
import traceback
import base64
from threading import Lock
from flask import Flask, request, jsonify, send_from_directory, render_template
from datetime import datetime
from intelbras_api import IntelbrasAccessControlAPI
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s_files")
if not os.path.exists(save_dir):
    os.makedirs(save_dir)


DEVICE_IP = '123.456.789.10'
USERNAME = 'admin'
PASSWORD = '123456'

api = IntelbrasAccessControlAPI(DEVICE_IP, USERNAME, PASSWORD)
api.testar_comunicacao()

user_id_lock = Lock()
current_user_id = 1

@app.route ('/')
def home():
    return render_template("index.html")
@app.route('/cadastro')
def cadastro():
    return send_from_directory(directory=os.path.dirname(__file__), path="index.html")

@app.route('/ping_dispositivo', methods=['POST'])
def ping_dispositivo():
    try:
        resultado = api.get_current_time()
        return jsonify({'status': 'sucesso', 'mensagem': resultado}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'erro', 'mensagem': str(e)}), 500


def gerar_user_id():
    id_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ultimo_id.txt")

    with user_id_lock:
        if not os.path.exists(id_path):
            with open(id_path, "w") as f:
                f.write("1")  

        with open(id_path, "r") as f:
            last_id = int(f.read().strip())

        new_id = last_id + 1

        with open(id_path, "w") as f:
            f.write(str(new_id))

    return str(new_id)


@app.route('/cadastrar_usuario', methods=['POST'])
def cadastrar_usuario():
    
    global current_user_id    
    try:
        
        
        data = request.get_json()
        nome = data.get('nome')
        senha = data.get('senha') or '1234'
        inicio = data.get('inicio') or '2025-01-01 00:00:00'
        fim = data.get('fim') or '2030-01-01 00:00:00'

        with user_id_lock:
            user_id = current_user_id
            current_user_id += 1

        resultado = api.add_user_v2(
            CardName=nome,
            UserID=user_id,
            UserType=0,
            Password=senha,
            Authority=2,
            Doors=0,
            TimeSections=255,
            ValidDateStart=inicio,
            ValidDateEnd=fim
        )

        return jsonify({'status': 'sucesso', 'mensagem': {'UserID': user_id, 'retorno': resultado}}), 201
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'erro', 'mensagem': str(e)}), 500

@app.route('/listar_usuarios', methods=['GET'])
def listar_usuarios():
    try:
        resultado = api.get_all_users(count=10)
        return jsonify({'status': 'sucesso', 'usuarios': resultado}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'Erro', 'mensagem': str(e)}), 500


@app.route('/deletar_todos_usuarios', methods=['DELETE'])
def deletar_todos_usuarios():
    try:
        resultado = api.delete_all_users_v2()

        with user_id_lock:
            
            current_user_id = 1
        
        return jsonify({'status': 'sucesso', 'mensagem': resultado})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'Erro', 'mnesagem': str(e)})


@app.route("/enviar_foto_dispositivo", methods=["POST"])
def enviar_foto_dispositivo():
    try:
        user_id = request.json.get("user_id") if request.is_json else request.form.get("user_id")
        photo_base64 = request.json.get("photo_base64") if request.is_json else request.form.get("photo_base64")
        foto_file = request.files.get("foto")

        if not user_id:
            return jsonify({"erro": "User ID ausente."}), 400

        os.makedirs("temp_upload", exist_ok=True)
        filepath = None

        if foto_file:
            # Caso a imagem tenha vindo via upload (form-data)
            filepath = os.path.join("temp_upload", foto_file.filename)
            foto_file.save(filepath)

        elif photo_base64:
            from PIL import Image
            from io import BytesIO
            import base64

            img_data = base64.b64decode(photo_base64)
            img = Image.open(BytesIO(img_data)).convert("RGB")

            # Definir filepath com nome padrão
            filepath = os.path.join("temp_upload", f"{user_id}_captura.jpg")
            img.save(filepath, format="JPEG")

        else:
            return jsonify({"erro": "Nenhuma imagem enviada."}), 400

        # Envio para o dispositivo
        resultado = api.send_face_to_device(user_id=user_id, image_path=filepath)

        if os.path.exists(filepath):
            os.remove(filepath)

        return jsonify({"resultado": resultado})
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500



if __name__ == "__main__":

    app.run(debug=False, host="0.0.0.0")
