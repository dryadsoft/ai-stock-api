from ...services.kor_sector_service import KorSectorService
from ...connection.scope_session import session_scope


class KorSectorTask:
    def __init__(self):
        pass

    def start(self):
        with session_scope() as session:
            kor_sector_service = KorSectorService(session)
            kor_sector_service.insert_data()
