import json
import time
import pandas as pd
from sqlalchemy.orm import Session
from tqdm import tqdm

from ..apis.external_data_api.kor_fs_api import KorFsApi
from ..entities.kor_fs_entity import KorFsEntity
from ..services.kor_ticker_service import KorTickerService


class KorFsService:

    error_list = []

    def __init__(self, session):
        self.session: Session = session
        self.kor_fs_api = KorFsApi()
        self.kor_ticker_service = KorTickerService(self.session)
        self.error_list.clear()

    def _fetch_api_data(self, ticker):
        return self.kor_fs_api.fetch_api(ticker)

    def _insert(self, data):
        kor_fs_entity = KorFsEntity(**data)
        self.session.add(kor_fs_entity)

    def insert_data(self):
        tickers = self.kor_ticker_service.get_tickers()
        for i in tqdm(range(0, len(tickers))):
            ticker = tickers[i]
            try:
                kor_fs = self._fetch_api_data(ticker.itemCd)
                for item in kor_fs.values:
                    trans_data = {
                        "account": item[0],
                        "baseDt": item[1],
                        "amt": item[2],
                        "itemCd": item[3],
                        "fsType": item[4],
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

    def _print_err_list(self, err_list):
        for err in err_list:
            print(err)

    def get_fs(self, fsType, accounts: list[str]):
        """
        분기데이터 조회
        """
        query_set = (
            self.session.query(KorFsEntity)
            .filter(
                KorFsEntity.account.in_(accounts),
                KorFsEntity.fsType == fsType,
            )
            .order_by(
                KorFsEntity.itemCd.asc(),
                KorFsEntity.account.asc(),
                KorFsEntity.baseDt.asc(),
            )
        )
        df = pd.read_sql(query_set.statement, query_set.session.bind)
        return df

    def _close(self):
        self.session.commit()
        self.session.close()
