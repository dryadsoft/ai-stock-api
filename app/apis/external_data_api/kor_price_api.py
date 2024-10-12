import requests as rq
from io import BytesIO
import pandas as pd


class KorPriceApi:

    def __init__(self):
        pass

    def fetch_data(self, ticker, from_dt, end_dt):
        url = f"https://m.stock.naver.com/front-api/external/chart/domestic/info?symbol={ticker}&requestType=1&startTime={from_dt}&endTime={end_dt}&timeframe=day"

        data = rq.get(url).content
        data_price = pd.read_csv(BytesIO(data))
        # 데이터 클렌징
        price = data_price.iloc[:, 0:6]
        price.columns = ["날짜", "시가", "고가", "저가", "종가", "거래량"]
        price = price.dropna()
        price["날짜"] = price["날짜"].str.extract("(\\d+)")
        price["종목코드"] = ticker
        return price
