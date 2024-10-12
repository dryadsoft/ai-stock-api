import re
from bs4 import BeautifulSoup
import pandas as pd
import requests as rq


class KorFsApi:
    def __init__(self) -> None:
        pass

    def fetch_api(self, ticker):
        url = (
            f"https://comp.fnguide.com/SVO2/ASP/SVD_finance.asp?pGB=1&gicode=A{ticker}"
        )
        data = pd.read_html(url, displayed_only=True)
        # print(data[0].columns.to_list())  # 연간기준 포괄손익계산서
        # print(data[2].columns.to_list())  # 연간기준 재무제표
        # print(data[4].columns.to_list())  # 연간기준 현금흐름표
        # 결산년 찾기
        fiscal_date = self.get_fiscal_date(url)
        data_fs_y = self.get_fs_y(ticker, data, fiscal_date)  # 년간 제무재표
        data_fs_q = self.get_fs_q(ticker, data)  # 분기 제무재표

        return self.bind_fs(data_fs_y, data_fs_q)

    def bind_fs(self, data_fs_y, data_fs_q):
        return pd.concat([data_fs_y, data_fs_q])  # 두개 합치기

    def get_fs_y(self, ticker, data, fiscal_date):
        data_fs_y = pd.concat(
            [
                data[0].iloc[:, ~data[0].columns.str.contains("전년동기")],
                data[2],
                data[4],
            ]
        )
        data_fs_y = data_fs_y.rename(columns={data_fs_y.columns[0]: "계정"})

        # 연간결산데이터만 필터링
        data_fs_y = data_fs_y.loc[
            :,
            (data_fs_y.columns == "계정")
            | (data_fs_y.columns.str[-2:].isin(fiscal_date)),
        ]

        return self.clean_fs(data_fs_y, ticker, "y")

    def get_fs_q(self, ticker, data):
        data_fs_q = pd.concat(
            [
                data[1].iloc[:, ~data[1].columns.str.contains("전년동기")],
                data[3],
                data[5],
            ]
        )
        data_fs_q = data_fs_q.rename(columns={data_fs_q.columns[0]: "계정"})
        return self.clean_fs(data_fs_q, ticker, "q")

    def get_fiscal_date(self, url):
        page_data = rq.get(url)
        page_data_html = BeautifulSoup(page_data.content, "html.parser")
        fiscal_data = page_data_html.select("div.corp_group1 > h2")
        fiscal_data_text = fiscal_data[1].text
        fiscal_data_text = re.findall("[0-9]+", fiscal_data_text)
        return fiscal_data_text

    def clean_fs(self, df, ticker, frequency):
        df = df[~df.loc[:, ~df.columns.isin(["계정"])].isna().all(axis=1)]
        df.loc[:, "계정"] = df["계정"].replace(
            {"계산에 참여한 계정 펼치기": ""}, regex=True
        )
        df = df.drop_duplicates(["계정"], keep="first")
        df = pd.melt(df, id_vars="계정", var_name="기준일", value_name="값")
        df = df[~pd.isnull(df["값"])]
        # df["계정"] = df["계정"].replace({"계산에 참여한 계정 펼치기": ""}, regex=True)
        df["기준일"] = (
            pd.to_datetime(df["기준일"], format="%Y/%m") + pd.tseries.offsets.MonthEnd()
        )
        df["기준일"] = df["기준일"].dt.strftime("%Y%m%d")
        type
        df["종목코드"] = ticker
        df["공시구분"] = frequency

        return df
