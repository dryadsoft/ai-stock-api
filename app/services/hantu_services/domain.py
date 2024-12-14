from enum import Enum
import os
from app import config_yaml


class Domain(Enum):
    IS_PROD = config_yaml.get_propertity("is_prod_hantu")
    DEV = "https://openapivts.koreainvestment.com:29443"
    PROD = "https://openapi.koreainvestment.com:9443"
    HAN_TU_APP_KEY = os.environ.get("HAN_TU_APP_KEY")
    HAN_TU_SECRET_KEY = os.environ.get("HAN_TU_SECRET_KEY")

    @classmethod
    def get_url(self):
        if self.IS_PROD.value:
            return self.PROD.value
        return self.DEV.value

    @classmethod
    def get_app_key(self):
        if self.IS_PROD.value:
            return self.HAN_TU_APP_KEY.value
        return self.HAN_TU_APP_KEY.value

    @classmethod
    def get_secret_key(self):
        if self.IS_PROD.value:
            return self.HAN_TU_SECRET_KEY.value
        return self.HAN_TU_SECRET_KEY.value
