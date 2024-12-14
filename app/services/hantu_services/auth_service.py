import requests as rq
from app.services.hantu_services.domain import Domain


class AuthService:
    def __init__(self):
        self.BASE_URL = Domain.get_url()
        self.APP_KEY = Domain.get_app_key()
        self.SECRET_KEY = Domain.get_secret_key()

    def get_approval_key(self):
        """실시간 접속키 발급"""
        headers = {"content-type": "application/json; utf-8"}
        json_body = {
            "grant_type": "client_credentials",
            "appkey": self.APP_KEY,
            "secretkey": self.SECRET_KEY,
        }
        response = rq.post(
            f"{self.BASE_URL}/oauth2/Approval",
            headers=headers,
            json=json_body,
        )
        if response.status_code != 200:

            raise Exception(
                f"실시간 접속키 발급에 실패하였습니다.[{response.status_code}]\n error_message: {response.text}"
            )
        else:
            print(response)
            json = response.json()
            return json.get("approval_key")

    def get_hash_key(self, json_data):
        """Hashkey 발급"""
        headers = {
            "content-type": "application/json; utf-8",
            "appkey": self.APP_KEY,
            "appsecret": self.SECRET_KEY,
        }

        response = rq.post(
            f"{self.BASE_URL}/uapi/hashkey",
            headers=headers,
            json=json_data,
        )
        if response.status_code != 200:

            raise Exception(
                f"Hash 발급에 실패하였습니다.[{response.status_code}]\n error_message: {response.text}"
            )
        else:
            print(response)
            # json = response.json()
            return response.json()

    def get_access_token(self):
        """access token 발급"""
        headers = {
            "content-type": "application/json; utf-8",
        }
        json_body = {
            "grant_type": "client_credentials",
            "appkey": self.APP_KEY,
            "appsecret": self.SECRET_KEY,
        }
        response = rq.post(
            f"{self.BASE_URL}/oauth2/tokenP",
            headers=headers,
            json=json_body,
        )
        if response.status_code != 200:

            raise Exception(
                f"access token 발급에 실패하였습니다.[{response.status_code}]\n error_message: {response.text}"
            )
        else:
            print(response)
            return response.json()

    def revoke_access_token(self, access_token):
        """access token 폐기"""
        headers = {
            "content-type": "application/json; utf-8",
        }
        json_body = {
            "appkey": self.APP_KEY,
            "appsecret": self.SECRET_KEY,
            "token": access_token,
        }
        response = rq.post(
            f"{self.BASE_URL}/oauth2/revokeP",
            headers=headers,
            json=json_body,
        )
        if response.status_code != 200:

            raise Exception(
                f"access token 폐기에 실패하였습니다.[{response.status_code}]\n error_message: {response.text}"
            )
        else:
            return response.json()
