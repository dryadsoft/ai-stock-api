from datetime import datetime
import os
import requests as rq
from app.services.hantu_services.domain import Domain


class AuthService:
    def __init__(self):
        self.BASE_URL = Domain.get_url()
        self.APP_KEY = os.environ.get("HAN_TU_APP_KEY")
        self.SECRET_KEY = os.environ.get("HAN_TU_SECRET_KEY")
        self.access_token_obj = None

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
            return response.json()

    def _valid_access_token(self):
        """access token 유효성 검사"""
        access_token = ""
        if self.access_token_obj != None:
            access_token_token_expired = self.access_token_obj[
                "access_token_token_expired"
            ]
            now = datetime.now().date()
            date_format = "%Y-%m-%d %H:%M:%S"
            expired_date = datetime.strptime(
                access_token_token_expired, date_format
            ).date()
            if expired_date > now:
                print("access token이 유효합니다.")
                access_token = self.access_token_obj["access_token"]
            else:
                print("access token이 유효하지 않습니다. 폐기후 재발급요청 하겠습니다.")
                self.revoke_access_token(self.access_token_obj["access_token"])
                self.access_token_obj = None
        return access_token

    def get_access_token(self) -> str:
        """access token 발급"""
        access_token = self._valid_access_token()
        if access_token != "":
            return access_token
        else:
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
                print("access token이 발급되었습니다.")
                self.access_token_obj = response.json()
                access_token = self._valid_access_token()
                return access_token

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
