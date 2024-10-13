from sqlalchemy.orm import Session
from scipy.stats import zscore
import pandas as pd
from ...services.kor_price_service import KorPriceService
from ...services.kor_sector_service import KorSectorService
from ...services.kor_ticker_service import KorTickerService

# 섹터 중립 포트폴리오
# 펙터 전략의 단점 중 하나는 선택된 종목들이 특정 섹터로 쏠리는 경우가 있음


class SectorNeuralPortfolioService:
    def __init__(self, session: Session):
        kor_price_service = KorPriceService(session)
        kor_ticker_service = KorTickerService(session)
        kor_sector_service = KorSectorService(session)

        self.tickers = kor_ticker_service.get_tickers(isDf=True)
        # 날짜, 종목코드, 종가 조회
        self.prices = kor_price_service.get_year_price(is_df=True)
        self.sectors = kor_sector_service.get_sectors(is_df=True)

    def set_default(self):
        price_pivot = self.prices.pivot(
            index="baseDt", columns="itemCd", values="closePrice"
        )
        # 최근 1년 기준 누적수익률
        ret_list = pd.DataFrame(
            data=(price_pivot.iloc[-1] / price_pivot.iloc[0]) - 1, columns=["return"]
        )

        # ticker, sector, 누적수익률 merge
        data_bind = (
            self.tickers[["itemCd", "itemNm"]]
            .merge(
                self.sectors[["cmpCd", "secNmKor"]],
                how="left",
                left_on="itemCd",
                right_on="cmpCd",
            )
            .merge(ret_list, how="left", on="itemCd")
        )
        return data_bind

    def get_sector_data(self, rank=20):
        data_bind = self.set_default()
        # 12개월 수익률 기준 순위 구하기(내림차순)
        data_bind["rank"] = data_bind["return"].rank(axis=0, ascending=False)

        sector_top_rank = data_bind.loc[data_bind["rank"] <= rank].sort_values(
            by=["rank"], ascending=True
        )
        sector_count = pd.DataFrame(
            data_bind.loc[data_bind["rank"] <= rank, "secNmKor"].value_counts()
        )
        return sector_count, sector_top_rank

    def get_sector_z_score(self, rank=20):
        data_bind = self.set_default()
        # 섹터 중립 포트폴리오
        # 쏠림현상 제거

        # 섹터정보가 없는경우 기타로 표시
        data_bind.loc[data_bind["secNmKor"].isnull(), "secNmKor"] = "기타"
        # z-score를 통해 그룹별로 정규화
        data_bind["z-score"] = data_bind.groupby("secNmKor", dropna=False)[
            "return"
        ].transform(lambda x: zscore(x, nan_policy="omit"))
        # z-score로 정규화된 값을 기준으로 랭킹을 구해준다.
        data_bind["z-rank"] = data_bind["z-score"].rank(axis=0, ascending=False)
        # z-score 기준 상위 20개 종목 선택 후 섹터 갯수 구한다.
        sector_top_rank = data_bind.loc[data_bind["z-rank"] <= rank].sort_values(
            by=["z-rank"], ascending=True
        )
        sector_neutral_count = pd.DataFrame(
            data_bind.loc[data_bind["z-rank"] <= rank, "secNmKor"].value_counts()
        )
        return sector_neutral_count, sector_top_rank
