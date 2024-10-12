from ...services.kor_value_service import KorValueService
from ...connection.scope_session import session_scope


class KorValueTask:
    def __init__(self):
        pass

    def start(self):
        with session_scope() as session:
            kor_value_service = KorValueService(session)
            kor_value_service.insert_data()
