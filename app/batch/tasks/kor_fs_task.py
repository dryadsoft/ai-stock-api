from ...services.kor_fs_service import KorFsService
from ...connection.scope_session import session_scope


class KorFsTask:
    def __init__(self):
        pass

    def start(self):
        with session_scope() as session:
            kor_fs_service = KorFsService(session)
            kor_fs_service.insert_data()
