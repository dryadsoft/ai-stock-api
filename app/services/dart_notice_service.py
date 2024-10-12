import os
from sqlalchemy.orm import Session
from ..apis.external_data_api.dart_notice_api import DartNoticeApi
from ..services.dart_code_service import DartCodeService

_SERVICE_KEY = os.environ.get("DART_GOOGLE_API_KEY")


class DartNoticeService:
    def __init__(self, session) -> None:
        self.session: Session = session
        self.dart_notice_api = DartNoticeApi(_SERVICE_KEY)
        self.dart_code_service = DartCodeService(self.session)
        self.rcp_url = "https://dart.fss.or.kr/dsaf001/main.do?rcpNo="

    def fetch_api_data(self, stock_code):
        dart_code_entity = self.dart_code_service.get_corp(stock_code)
        if dart_code_entity:
            return self.dart_notice_api.fetch_api(dart_code_entity.corp_code)
