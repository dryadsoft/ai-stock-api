from sqlalchemy.orm import Session
from ..apis.external_data_api.public_stock_price_api import PublicStockPriceApi
from ..entities.stock_price_info_entity import StockPriceInfoEntity


class PublicStockPriceService:

    def __init__(self, session):
        self.public_stock_price_api = PublicStockPriceApi()
        self.session: Session = session

    def _fetch_api_data(self, start_date, end_date, page_no):
        return self.public_stock_price_api.fetch_api_data(
            start_date=start_date,
            end_date=end_date,
            page_no=page_no,
        )

    def insert_data(self):
        isLoop = True
        page_no = 1
        while isLoop:

            json = self._fetch_api_data(
                start_date="20200201", end_date="20201231", page_no=page_no
            )
            numOfRows = json["response"]["body"]["numOfRows"]
            pageNo = json["response"]["body"]["pageNo"]
            totalCount = json["response"]["body"]["totalCount"]
            items = json["response"]["body"]["items"]["item"]

            for item in items:
                stockPriceInfoEntity = StockPriceInfoEntity(**item)
                self.session.add(stockPriceInfoEntity)

            self._close()
            print(page_no, numOfRows, pageNo, totalCount)
            if numOfRows * pageNo >= totalCount:
                isLoop = False
            else:
                page_no = page_no + 1

    def select_datas(self):
        print("select")
        result = self.session.query(StockPriceInfoEntity).all()
        print(result)

    def _close(self):
        self.session.commit()
        self.session.close()
