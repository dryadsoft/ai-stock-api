from enum import Enum
from app import config_yaml


class Domain(Enum):
    IS_PROD = config_yaml.get_propertity("is_prod_hantu")

    @classmethod
    def _get_properties(self):
        if self.get_is_prod():
            return config_yaml.get_propertity("hantu_prod")
        return config_yaml.get_propertity("hantu_dev")

    @classmethod
    def get_is_prod(self):
        return self.IS_PROD.value

    @classmethod
    def get_url(self):
        hantu = self._get_properties()
        return hantu["api_base_url"]

    @classmethod
    def get_cano(self):
        hantu = self._get_properties()
        return hantu["cano"]

    @classmethod
    def get_acnt_prdt_cd(self):
        hantu = self._get_properties()
        return hantu["acnt_prdt_cd"]
