import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..apis.external_data_api.kor_sector_api import KorSectorApi
from ..entities.kor_sector_entity import KorSectorEntity
from ..services.biz_day_service import BizDayService


class KorSectorService:

    def __init__(self, session) -> None:
        biz_day_service = BizDayService()
        self.biz_day = biz_day_service.get_biz_day()
        self.kor_sector_api = KorSectorApi(self.biz_day)
        self.session: Session = session

    def _fetch_api_data(self):
        data_sector = self.kor_sector_api.fetch_data()
        kor_sector = pd.concat(data_sector, axis=0)
        kor_sector = kor_sector[["IDX_CD", "CMP_CD", "CMP_KOR", "SEC_NM_KOR"]]
        kor_sector["기준일"] = self.biz_day
        return kor_sector

    def _insert(self, data):
        kor_sector_entity = KorSectorEntity(**data)
        self.session.add(kor_sector_entity)

    def insert_data(self):
        datas = self._fetch_api_data()
        for item in datas.values:
            trans_data = {
                "baseDt": item[4],
                "cmpCd": item[1],
                "cmpKor": item[2],
                "secNmKor": item[3],
                "idxCd": item[0],
            }
            self._insert(trans_data)
        self._close()

    def get_sectors(self, is_df=False):
        max_subquery = self.session.query(func.max(KorSectorEntity.baseDt))
        query_set = self.session.query(KorSectorEntity).filter(
            KorSectorEntity.baseDt == max_subquery.scalar_subquery()
        )
        if is_df == False:
            return query_set.all()
        else:
            return pd.read_sql(query_set.statement, query_set.session.bind)

    def _close(self):
        self.session.commit()
        self.session.close()
