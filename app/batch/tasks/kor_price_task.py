from ...services.kor_price_service import KorPriceService
from ...connection.scope_session import session_scope


class KorPriceTask:
    def __init__(self):
        pass

    def start(self):
        with session_scope() as session:
            kor_price_service = KorPriceService(session)
            kor_price_service.insert_data()
