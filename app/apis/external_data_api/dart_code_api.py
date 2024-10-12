import os
import requests as rq
from io import BytesIO
import zipfile

import xmltodict
import json
import pandas as pd


class DartCodeApi:

    def __init__(self, service_key):
        self.base_url = "https://opendart.fss.or.kr/api/corpCode.xml"
        self.params = {"crtfc_key": service_key}

    def fetch_api(self):
        codezip_data = rq.get(self.base_url, params=self.params)
        code_data = self.extract_zip(codezip_data)
        corp_list = self.xml_to_dataframe(code_data)
        return self.cleaning_data(corp_list)

    def extract_zip(self, codezip_data):
        codezip_file = zipfile.ZipFile(BytesIO(codezip_data.content))
        file_name = codezip_file.namelist()[0]
        return codezip_file.read(file_name).decode("utf-8")

    def xml_to_dataframe(self, code_data):
        data_odict = xmltodict.parse(code_data)  # xml -> dict
        data_dict = json.loads(json.dumps(data_odict))
        data = data_dict.get("result").get("list")
        return pd.DataFrame(data)  # 데이터프레임으로 변경

    def cleaning_data(self, corp_list):
        corp_list = corp_list[~corp_list.stock_code.isin([None])].reset_index(drop=True)
        return corp_list
