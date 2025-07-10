import requests
import os
from datetime import datetime
from requests.auth import HTTPDigestAuth
from PIL import Image
import base64


class IntelbrasAccessControlAPI:
    def __init__(self, ip: str, username: str, passwd: str):
        self.ip = ip
        self.username = username
        self.passwd = passwd
        self.digest_auth = requests.auth.HTTPDigestAuth(
            self.username, self.passwd)

    def get_current_time(self) -> datetime:
        try:
            url = f"http://{self.ip}/cgi-bin/global.cgi?action=getCurrentTime"
            result = requests.get(url, auth=self.digest_auth, timeout=20)
            raw = result.text.strip().splitlines()
            data = self._raw_to_dict(raw)
            return data.get("result", "N/A")
        except Exception as e:
            raise Exception(f"ERROR - During Get Current Time: {str(e)}")

    def add_user_v2(self, CardName: str, UserID: int, UserType: int, Password: int, Authority: int, Doors: int, TimeSections: int, ValidDateStart: str, ValidDateEnd: str) -> str:
        ''''
        UserID: Numero de ID do usuário
        CardName: Nome de usuário/Nome do cartão
        UserType: 0- Geral user, by defaut; 1 - Blocklist user (report the blocklist event ACBlocklist); 2 - Guest user: 3 - Patrol user 4 - VIP user; 5 - Disable user
        Password: Senha de acesso do usuário
        Authority: 1 - administrador; 2 - usuário normal
        Doors: Portas que o usúario terá acesso
        TimeSections: Zona de tempo de acesso do usuário, padrão: 255
        ValidDateStart: Data de Inicio de Validade, exemplo: 2019-01-02 00:00:00
        ValidDateEnd: Data de Final de Validade, exemplo: 2037-01-02 01:00:00
        '''
        UserList = (
            '''{
                "UserList": [
                    {
                        "UserID": "''' + str(UserID) + '''",
                        "UserName": "''' + str(CardName) + '''",
                        "UserType": ''' + str(UserType) + ''',
                        "Authority": "''' + str(Authority) + '''",
                        "Password": "''' + str(Password) + '''",
                        "Doors": "''' + '[' + str(Doors) + ']' + '''",
                        "TimeSections": "''' + '[' + str(TimeSections) + ']' + '''",
                        "ValidFrom": "''' + str(ValidDateStart) + '''",
                        "ValidTo": "''' + str(ValidDateEnd) + '''"
                    }
                ]
            }''')
        try:
            url = "http://{}/cgi-bin/AccessUser.cgi?action=insertMulti".format(
                str(self.ip))
            result = requests.get(
                url, data=UserList, auth=self.digest_auth, stream=True, timeout=20)

            if result.status_code != 200:
                raise Exception()
            return str(result.text)
        except Exception:
            raise Exception("ERROR - During Add New User using V2 command - ")

    def get_all_users(self, count: int) -> dict:
        try:
            url = f"http://{self.ip}/cgi-bin/recordFinder.cgi?action=doSeekFind&name=AccessControlCard&count={count}"
            result = requests.get(url, auth=self.digest_auth, timeout=20)
            raw = result.text.strip().splitlines()
            return self._raw_to_dict(raw)
        except Exception as e:
            raise Exception(f"ERROR - During Get All User: {str(e)}")

    def delete_all_users_v2(self) -> str:
        try:
            url = f"http://{self.ip}/cgi-bin/AccessUser.cgi?action=removeAll"
            result = requests.get(url, auth=self.digest_auth, timeout=20)
            if result.status_code != 200:
                raise Exception(
                    f"Falha ao remover todos os usuários. Status: {result.status_code}")
            return result.text
        except Exception as e:
            raise Exception(f"ERROR - During Remove All Users: {str(e)}")

    def _gerar_user_id(self):
        return int(datetime.now().strftime("%Y%m%d%H%M%S"))

    def _raw_to_dict(self, raw):
        data = {}
        for line in raw:
            if "=" in line:
                key, val = line.split("=", 1)
                data[key.strip()] = val.strip()
        return data

    def send_face_to_device(self, user_id: str, image_path: str):
        """
        Envia uma imagem facial convertida em Base64 para o dispositivo Intelbras SS 3532 MF
        usando o endpoint AccessFace.cgi?action=insertMulti.

        Se a imagem estiver fora dos padrões, ela será ajustada automaticamente:
        - JPEG
        - Resolução ajustada entre 150x300 e 600x1200
        - Altura ≤ 2x largura
        - Tamanho final ≤ 100 KB
        """
        try:
           
            img = Image.open(image_path).convert("RGB")
            width, height = img.size

           
            new_width = max(150, min(width, 600))
            new_height = max(300, min(height, 1200))

            
            if new_height > new_width * 2:
                new_height = new_width * 2

           
            img = img.resize((new_width, new_height))

            
            base, _ = os.path.splitext(image_path)
            converted_path = f"{base}_converted.jpg"
            img.save(converted_path, format="JPEG", quality=85)

            
            if os.path.getsize(converted_path) > 100 * 1024:
                os.remove(converted_path)
                raise Exception("Imagem convertida ultrapassa 100 KB mesmo após ajuste.")

            
            with open(converted_path, "rb") as f:
                photo_data = base64.b64encode(f.read()).decode("utf-8")

            os.remove(converted_path)

            
            payload = {
                "FaceList": [
                    {
                        "UserID": str(user_id),
                        "PhotoData": [photo_data]
                    }
                ]
            }

            url = f"http://{self.ip}/cgi-bin/AccessFace.cgi?action=insertMulti"
            headers = {'Content-Type': 'application/json'}

            response = requests.post(
                url,
                auth=self.digest_auth,
                headers=headers,
                json=payload,
                timeout=15
            )

            if response.text.strip() == "OK":
                return "Cadastro da face realizado com sucesso."
            else:
                raise Exception(f"Erro ao cadastrar: {response.text.strip()}")

        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception(f"ERROR - During Upload Face Image: {e}")

    def testar_comunicacao(self):
        try:
            url = f"http://{self.ip}/cgi-bin?action=getProductDefiniton"
            response = requests.get(url, auth=HTTPDigestAuth(
                self.username, self.passwd), timeout=10)
            if response.status_code == 200:
                print("Comunicação e autentificação DIGEST funcionando!")
                print("Resposta:", response.text)
                return True
            else:
                print(f"Erro: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print("Erro de comunicação com o dispositivo:", e)
            return False
