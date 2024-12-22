import pandas as pd
import time
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from tqdm import tqdm

from ..services.biz_day_service import BizDayService
from ..apis.external_data_api.kor_price_api import KorPriceApi
from ..entities.kor_price_entity import KorPriceEntity
from ..services.kor_ticker_service import KorTickerService


class KorPriceService:

    error_list = []

    def __init__(self, session):
        self.session: Session = session
        self.kor_price_api = KorPriceApi()
        self.biz_day_service = BizDayService()
        self.kor_ticker_service = KorTickerService(self.session)
        # self.from_dt = (date.today() + relativedelta(years=-10)).strftime("%Y%m%d")
        # self.end_dt = (date.today()).strftime("%Y%m%d")
        from_dt, end_dt = self.get_from_end_date()
        self.from_dt = from_dt
        self.end_dt = end_dt
        self.error_list.clear()

    def get_from_end_date(self):
        # DB에 등록된 최근일자
        from_dt = self.session.query(func.max(KorPriceEntity.baseDt)).scalar()
        end_dt = self.biz_day_service.get_biz_day()  # 최근 영업일

        if from_dt == None:
            from_dt = (date.today() + relativedelta(years=-10)).strftime("%Y%m%d")
            return from_dt, end_dt
        if end_dt > from_dt:  # 영업일이 max등록일보다 크면 max + 1
            date_type_from_dt = datetime.strptime(from_dt, "%Y%m%d")
            from_dt = (date_type_from_dt + relativedelta(days=1)).strftime("%Y%m%d")
            return from_dt, end_dt

        return "", ""

    def _fetch_api_data(self, ticker, from_dt, end_dt):
        return self.kor_price_api.fetch_data(
            ticker=ticker, from_dt=from_dt, end_dt=end_dt
        )

    def _insert(self, data):
        kor_price_entity = KorPriceEntity(**data)
        self.session.add(kor_price_entity)

    def insert_data(self):
        if self.from_dt != "" and self.end_dt != "":
            tickers = self.kor_ticker_service.get_tickers()
            for i in tqdm(range(0, len(tickers))):
                ticker = tickers[i]
                try:
                    kor_price = self._fetch_api_data(
                        ticker.itemCd, self.from_dt, self.end_dt
                    )
                    for price in kor_price.values:
                        trans_data = {
                            "baseDt": price[0],
                            "openPrice": price[1],
                            "highPrice": price[2],
                            "lowPrice": price[3],
                            "closePrice": price[4],
                            "stockQty": price[5],
                            "itemCd": price[6],
                        }
                        self._insert(trans_data)
                    self.session.commit()
                except:
                    print(ticker.__dict__)
                    self.error_list.append(
                        {"ticker": ticker.itemCd, "ticker_name": ticker.itemNm}
                    )
                time.sleep(2)  # 종목 사이 2초간 sleep
            self._close()
            self._print_err_list(self.error_list)
        else:
            print(
                f"from_dt: {self.from_dt}, end_dt: {self.end_dt}: 종가를 가져올 수 없습니다."
            )

    def _print_err_list(self, err_list):
        for err in err_list:
            print(err)

    def get_prev_date(self, years=1):
        end_date = self.session.query(func.max(KorPriceEntity.baseDt)).scalar()
        # 문자열을 datetime 객체로 변환
        date_obj = datetime.strptime(end_date, "%Y%m%d")

        # 1년(365일)을 뺀 날짜 계산
        new_date = date_obj - relativedelta(years=years)

        # 새로운 날짜를 다시 문자열로 변환
        from_date = new_date.strftime("%Y%m%d")
        return from_date, end_date

    def get_year_price(self, is_df=False, years=1):
        """
        1년치 데이터 조회
        """
        from_date, end_date = self.get_prev_date(years)
        query_set = self.session.query(
            KorPriceEntity.baseDt,
            KorPriceEntity.closePrice,
            KorPriceEntity.itemCd,
        ).filter(
            KorPriceEntity.baseDt >= from_date,
            KorPriceEntity.baseDt <= end_date,
        )
        if is_df != True:
            return query_set.all()

        return pd.read_sql(query_set.statement, query_set.session.bind)

    def get_ticker_price(self, ticker, is_df=False):
        """
        ticker의 1년치 데이터 조회
        """
        from_date, end_date = self.get_prev_date()
        query_set = self.session.query(KorPriceEntity).filter(
            KorPriceEntity.itemCd == ticker,
            KorPriceEntity.baseDt >= from_date,
            KorPriceEntity.baseDt <= end_date,
        )
        if is_df != True:
            return query_set.all()

        return pd.read_sql(query_set.statement, query_set.session.bind)

    def get_ticker_price_all(self, ticker, is_df=False):
        """
        ticker의 모든 데이터 조회
        """
        query_set = self.session.query(KorPriceEntity).filter(
            KorPriceEntity.itemCd == ticker,
        )
        if is_df != True:
            return query_set.all()

        return pd.read_sql(query_set.statement, query_set.session.bind)

    def _close(self):
        self.session.commit()
        self.session.close()
