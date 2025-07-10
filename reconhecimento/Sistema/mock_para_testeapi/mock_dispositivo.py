from flask import Flask, request

app = Flask(__name__)

@app.route('/cgi-bin/faceRecognition.cgi', methods=['POST'])
def upload_face_image():
    user_id = request.args.get('UserID')
    action = request.args.get('action')

    if action == 'uploadFaceImage' and user_id:
        print(f"[MOCK] Rosto recebido para o usuário {user_id}")
        return f"Imagem facial de {user_id} recebida com sucesso!", 200
    else:
        return "Requisição inválida", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
