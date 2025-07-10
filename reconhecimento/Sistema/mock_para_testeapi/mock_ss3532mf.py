
from flask import Flask, request, jsonify
from datetime import datetime
from intelbras_api import IntelbrasAccessControlAPI
import os

app = Flask(__name__)

@app.route('/')
def home():
    return 'Mock SS 3532 MF ativo.'

@app.route('/cgi-bin/AccessUser.cgi', methods=['POST'])
def access_user():
    action = request.args.get('action')
    if action == 'insertMulti':
        # Simula sucesso no cadastro de usuário
        print("➡️ Recebido insertMulti:")
        print(request.data.decode())  # mostra os dados recebidos

        return jsonify({"result": "Insert success"}), 200
    else:
        print("❌ Ação desconhecida:", action)
        return jsonify({"error": "Ação não suportada"}), 400

if __name__ == '__main__':
    print("🔧 Mock SS 3532 MF rodando em http://localhost:8080")
    app.run(port=8080)
