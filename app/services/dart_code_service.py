import os
from sqlalchemy.orm import Session
from ..apis.external_data_api.dart_code_api import DartCodeApi
from ..entities.dart_code_entity import DartCodeEntity

_SERVICE_KEY = os.environ.get("DART_GOOGLE_API_KEY")


class DartCodeService:
    def __init__(self, session):
        self.dart_code_api = DartCodeApi(_SERVICE_KEY)
        self.session: Session = session

    def _fetch_api_data(self):
        return self.dart_code_api.fetch_api()

    def _delete_all(self):
        dart_code_entity = DartCodeEntity()
        dart_code_entity
        self.session.query(DartCodeEntity).delete()
        self.close()

    def _insert(self, data):
        dart_code_entity = DartCodeEntity(**data)
        self.session.add(dart_code_entity)

    def insert_data(self):
        corp_list = self._fetch_api_data()
        if len(corp_list) > 0:
            self._delete_all()

        for dart_code in corp_list.values:
            trans_data = {
                "corp_code": dart_code[0],
                "corp_name": dart_code[1],
                "stock_code": dart_code[2],
                "modify_date": dart_code[3],
            }
            self._insert(trans_data)
        self._close()

    def get_corp(self, stock_code):
        return (
            self.session.query(DartCodeEntity)
            .filter(DartCodeEntity.stock_code == stock_code)
            .one()
        )

    def _close(self):
        self.session.commit()
        self.session.close()
