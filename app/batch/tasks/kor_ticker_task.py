from ...services.kor_ticker_service import KorTickerService
from ...connection.scope_session import session_scope


class KorTickerTask:
    def __init__(self):
        pass

    def start(self):
        with session_scope() as session:
            kor_ticker_service = KorTickerService(session)
            kor_ticker_service.insert_data()
