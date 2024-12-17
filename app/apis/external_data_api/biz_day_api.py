import requests as rq
from bs4 import BeautifulSoup
import re


class BizDayApi:
    def __init__(self) -> None:
        self.url = "https://finance.naver.com/sise/sise_index.naver?code=KOSPI"

    def fetch_api(self):
        """최근 영업일 가져오기"""
        data = rq.get(self.url)
        return self._parse_html(data)

    def _parse_html(self, data):
        data_html = BeautifulSoup(data.content, features="lxml")
        parse_day = data_html.select_one(
            "#wrap > #newarea> #contentarea > #contentarea_left > .group_heading > .ly_realtime > span#time"
        ).text
        biz_day = re.findall("[0-9]+", parse_day)[0:3]
        return "".join(biz_day)
