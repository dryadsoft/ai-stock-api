import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..services.biz_day_service import BizDayService
from ..apis.external_data_api.kor_ticker_api import KorTickerApi
from ..entities.kor_ticker_entity import KorTickerEntity


class KorTickerService:
    def __init__(self, session):
        biz_day_service = BizDayService()
        self.biz_day = biz_day_service.get_biz_day()
        self.kor_ticker_api = KorTickerApi(self.biz_day)
        self.session: Session = session

    def _fetch_api_data(self):
        return self.kor_ticker_api.merge_data()

    def _insert(self, data):
        kor_stock_entity = KorTickerEntity(**data)
        self.session.add(kor_stock_entity)

    def _is_exists(self):
        """biz_day의 ticker 데이터가 존재하는지 확인"""
        max_dt = self.session.query(func.max(KorTickerEntity.baseDt)).scalar()
        if self.biz_day == max_dt:
            return True
        return False

    def insert_data(self):
        if self._is_exists() == True:
            print(f"{self.biz_day}의 ticker 데이터가 이미 존재합니다.")
        else:
            datas = self._fetch_api_data()
            for item in datas.values:
                trans_data = {
                    "baseDt": item[5],
                    "itemCd": item[0],
                    "itemNm": item[1],
                    "closePrice": item[3],
                    "mrktCtg": item[2],
                    "mrktTotAmt": item[4],
                    "eps": item[6],
                    "preEps": item[7],
                    "bps": item[8],
                    "dvdnAmt": item[9],
                    "itemCtg": item[10],
                }
                self._insert(trans_data)
            self._close()

    def get_tickers(self, isDf=False):
        max_subquery = self.session.query(func.max(KorTickerEntity.baseDt))
        query_set = self.session.query(KorTickerEntity).filter(
            KorTickerEntity.baseDt == max_subquery.scalar_subquery(),
            KorTickerEntity.itemCtg == "보통주",
        )
        if isDf == False:
            return query_set.all()
        else:
            df = pd.read_sql(query_set.statement, query_set.session.bind)
            return df

    def _close(self):
        self.session.commit()
        self.session.close()
