from sqlalchemy.orm import Session
from ..apis.external_data_api.get_divi_info import GetDiviInfo
from ..entities.divi_info_entity import DiviInfoEntity


class GetDiviInfoService:

    def __init__(self, session):
        self.get_divi_info = GetDiviInfo()
        self.session: Session = session

    def _fetch_api_data(self, page_no):
        return self.get_divi_info.fetch_api_data(
            page_no=page_no,
        )

    def insert_data(self):
        isLoop = True
        page_no = 1
        while isLoop:

            json = self._fetch_api_data(page_no=page_no)
            numOfRows = json["response"]["body"]["numOfRows"]
            pageNo = json["response"]["body"]["pageNo"]
            totalCount = json["response"]["body"]["totalCount"]
            items = json["response"]["body"]["items"]["item"]

            for item in items:
                diviInfoEntity = DiviInfoEntity(**item)
                self.session.add(diviInfoEntity)

            self._close()
            print(page_no, numOfRows, pageNo, totalCount)
            if numOfRows * pageNo >= totalCount:
                isLoop = False
            else:
                page_no = page_no + 1

    def select_datas(self):
        print("select")
        result = self.session.query(DiviInfoEntity).all()
        print(result)

    def _close(self):
        self.session.commit()
        self.session.close()
