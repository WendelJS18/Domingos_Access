# DomingosAccess

**DomingosAccess** é um sistema completo de controle de acesso biométrico por reconhecimento facial, desenvolvido para a **Escola São Domingos**. O sistema utiliza câmera em tempo real via navegador, validação com base de dados e integração direta com o dispositivo de controle de acesso facial da **Intelbras (SS 3532 MF)** por meio de uma **API RESTful**.

## 📌 Objetivo

Automatizar e centralizar o controle de entrada de usuários (alunos, professores ou funcionários) na escola, garantindo segurança e praticidade no processo de cadastro e verificação biométrica facial.

---

## 🔧 Tecnologias Utilizadas

| Camada         | Tecnologia                       |
|----------------|----------------------------------|
| Back-end       | Python 3.10, Flask, requests     |
| Front-end      | HTML5, JavaScript (vanilla), CSS |
| Reconhecimento | OpenCV + PIL (captura e ajustes) |
| Integração     | HTTP Digest Auth + API Intelbras |
| Banco de dados | *(Integração futura com Kinto)*  |

---

## ⚙️ Funcionalidades Principais

### ✅ Cadastro de Usuário
- Rota: `POST /cadastrar_usuario`
- Gera um ID único incremental para o usuário.
- Envia os dados ao dispositivo via endpoint oficial da Intelbras (`insertMulti`).
- Verifica se o usuário está previamente autorizado via base de dados.

### ✅ Captura da Foto via Navegador
- A interface web utiliza a **câmera do próprio dispositivo** para capturar uma imagem do rosto em tempo real.
- A imagem é validada (resolução, proporção, tamanho máximo) e convertida para Base64.
- A imagem é enviada e vinculada ao `UserID`.

### ✅ Envio da Foto ao Dispositivo
- Rota: `POST /enviar_foto_dispositivo`
- API realiza requisição com `PhotoData` em JSON para:  
  `http://<device_ip>/cgi-bin/AccessFace.cgi?action=insertMulti`
- Se a imagem não cumprir os critérios (600x1200px e < 100KB), ela é automaticamente redimensionada.

### ✅ Listagem e Exclusão
- Rota `GET /listar_usuarios`: Retorna lista dos usuários cadastrados.
- Rota `DELETE /deletar_todos_usuarios`: Remove todos os usuários do dispositivo e **reseta a contagem de ID** no backend.

---

## 🧠 Lógica de Geração de ID

O sistema utiliza um contador `user_id` sequencial e controlado por `threading.Lock` para garantir que **em caso de múltiplos cadastros simultâneos**, cada usuário receba um ID único corretamente — evitando conflitos ou duplicações.

---

## 🔒 Verificação Prévia via Base de Dados

Antes de permitir o cadastro facial, o sistema validará o nome completo e CPF com uma base externa da Kinto Escola, através de uma **API (em desenvolvimento)**.  
Somente usuários autorizados seguem para o processo de reconhecimento facial.

---

## 💡 Como Usar o Projeto

### 1. Inicie o back-end:
```bash
python app.py
````
---

### 2. Acesse via navegador:
```text
http://localhost:5000
````

---

### 3. Tela de cadastro:
Preencha nome e senha

Capture sua foto com a câmera

Aguarde o retorno da API

---

## 📁 Estrutura do Projeto
```
DomingosAccess/
│
├── app.py                   # Servidor Flask
├── intelbras_api.py         # Lógica de integração com dispositivo Intelbras
├── templates/               # HTML do front-end
│   └── index.html
├── temp_upload/             # Pasta temporária de fotos capturadas
├── README.md
```
# 🤝 Colaboração
Desenvolvido por Wendel Samora, com apoio da Escola São Domingos.
Agradecimentos ao suporte técnico da Intelbras pelas documentações e coleções Postman.

