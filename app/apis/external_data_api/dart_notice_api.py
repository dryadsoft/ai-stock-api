import pandas as pd
import requests as rq
from datetime import date
from matplotlib.dates import relativedelta


class DartNoticeApi:
    def __init__(self, service_key):
        self.service_key = service_key
        self.base_url = "https://opendart.fss.or.kr/api/list.json"
        self.bgn_date = (date.today() + relativedelta(days=-7)).strftime("%Y%m%d")
        self.end_date = (date.today()).strftime("%Y%m%d")

    def fetch_api(self, corp_code=""):
        notice_data = rq.get(
            self.base_url,
            params={
                "crtfc_key": self.service_key,
                "bgn_de": self.bgn_date,
                "end_de": self.end_date,
                "corp_code": corp_code,
                "page_no": 1,
                "page_count": 100,
            },
        )
        notice_data_df = self.json_to_dataframe(notice_data)
        return self.cleaning_data(notice_data_df)

    def json_to_dataframe(self, notice_data):
        notice_data_json = notice_data.json().get("list")
        notice_data_df = pd.DataFrame(notice_data_json)
        # stock_code 없는 데이터 제거
        return notice_data_df[~notice_data_df.stock_code.isin([""])].reset_index(
            drop=True
        )

    def cleaning_data(self, notice_data_df):
        return notice_data_df[~notice_data_df.stock_code.isin([""])].reset_index(
            drop=True
        )
