import numpy as np
import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..entities.kor_value_entity import KorValueEntity
from ..services.kor_fs_service import KorFsService
from ..services.kor_ticker_service import KorTickerService


class KorValueService:
    def __init__(self, session):
        self.session: Session = session
        self.kor_fs_service = KorFsService(session)
        self.kor_ticker_service = KorTickerService(session)

    def get_ttm(self):
        """PSR, PCR, PBR 구하기"""
        kor_fs_q = self.kor_fs_service.get_fs(
            "q",
            ["당기순이익", "자본", "영업활동으로인한현금흐름", "매출액"],
        )
        # TTM 구하기
        kor_fs_q["ttm"] = (
            kor_fs_q.groupby(["itemCd", "account"], as_index=False)["amt"]
            .rolling(window=4, min_periods=4)
            .sum()["amt"]
        )
        # 자본은 평균 구하기
        kor_fs_q["ttm"] = np.where(
            kor_fs_q["account"] == "자본", kor_fs_q["ttm"] / 4, kor_fs_q["ttm"]
        )
        # 분모값
        kor_fs_q = kor_fs_q.groupby(["account", "itemCd"]).tail(1)

        # 티커리스트와 합성
        tickers = self.kor_ticker_service.get_tickers(isDf=True)
        kor_fs_q_merge = kor_fs_q[["account", "itemCd", "ttm"]].merge(
            tickers[["itemCd", "mrktTotAmt", "baseDt"]], on="itemCd"
        )

        # 시가총액과 제무재표 단위가 달라서 맞춰준다.
        kor_fs_q_merge["mrktTotAmt"] = kor_fs_q_merge["mrktTotAmt"] / 100000000
        # 가치지표 계산
        kor_fs_q_merge["value"] = kor_fs_q_merge["mrktTotAmt"] / kor_fs_q_merge["ttm"]
        kor_fs_q_merge["value"] = kor_fs_q_merge["value"].round(4)  # 반올림
        # 지표구분값 입력
        kor_fs_q_merge["지표"] = np.where(
            kor_fs_q_merge["account"] == "매출액",
            "PSR",
            np.where(
                kor_fs_q_merge["account"] == "영업활동으로인한현금흐름",
                "PCR",
                np.where(
                    kor_fs_q_merge["account"] == "자본",
                    "PBR",
                    np.where(kor_fs_q_merge["account"] == "당기순이익", "PER", None),
                ),
            ),
        )

        # 열이름 변경
        kor_fs_q_merge.rename(
            columns={"itemCd": "종목코드", "baseDt": "기준일", "value": "값"},
            inplace=True,
        )
        kor_fs_q_merge = kor_fs_q_merge[
            ["종목코드", "기준일", "지표", "값"]
        ]  # 원하는 열만 선택
        kor_fs_q_merge = kor_fs_q_merge.replace(
            [np.inf, -np.inf, np.nan], None
        )  # inf, nan을 None으로 변경
        return kor_fs_q_merge

    def get_dvdn(self):
        """배당 수익률 구하기"""
        tickers = self.kor_ticker_service.get_tickers(isDf=True)
        tickers["값"] = tickers["dvdnAmt"] / tickers["closePrice"]  # 주당배당금 / 종가
        tickers["값"] = tickers["값"].round(4)  # 반올림
        tickers["지표"] = "DY"
        dy_list = tickers[["itemCd", "baseDt", "지표", "값"]]
        dy_list = dy_list.replace([np.inf, -np.inf, np.nan], None)
        dy_list = dy_list[dy_list["값"] != 0]  # 배당수익률이 0이 아닌 값만 선택
        return dy_list

    def insert(self, data):
        kor_value_entity = KorValueEntity(**data)
        self.session.add(kor_value_entity)

    def insert_data(self):
        ttm = self.get_ttm()
        for ttm_item in ttm.values:
            trans_data = {
                "itemCd": ttm_item[0],
                "baseDt": ttm_item[1],
                "metrics": ttm_item[2],
                "amt": ttm_item[3],
            }
            self.insert(trans_data)
        dvdn = self.get_dvdn()
        for item in dvdn.values:
            trans_data = {
                "itemCd": item[0],
                "baseDt": item[1],
                "metrics": item[2],
                "amt": item[3],
            }
            self.insert(trans_data)
        self.close()

    def get_values(self, isDf=False):
        """
        최근 지표조회
        """
        max_subquery = self.session.query(func.max(KorValueEntity.baseDt))
        query_set = self.session.query(KorValueEntity).filter(
            KorValueEntity.baseDt == max_subquery.scalar_subquery(),
        )
        if isDf == False:
            return query_set.all()
        else:
            df = pd.read_sql(query_set.statement, query_set.session.bind)
            return df

    def get_values_by_metrics(self, metrics: str, isDf=False):
        max_subquery = self.session.query(func.max(KorValueEntity.baseDt))
        query_set = self.session.query(KorValueEntity).filter(
            KorValueEntity.baseDt == max_subquery.scalar_subquery(),
            KorValueEntity.metrics == metrics,
        )
        if isDf == False:
            return query_set.all()
        else:
            df = pd.read_sql(query_set.statement, query_set.session.bind)
            return df

    def close(self):
        self.session.commit()
        self.session.close()
