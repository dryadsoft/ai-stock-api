from sqlalchemy.orm import Session
import numpy as np

# import matplotlib.pyplot as plt
# import seaborn as sns
from ...services.kor_ticker_service import KorTickerService
from ...services.kor_value_service import KorValueService

# from ...services.kor_price_service import KorPriceService


class ValuePortfolio:
    """Value Portfolio
    밸류(가치) 포트폴리오(PBR, PER)
    """

    def __init__(self, session: Session):
        self.kor_ticker_service = KorTickerService(session)
        self.kor_value_service = KorValueService(session)

    def get_value_pivot(self):

        values = self.kor_value_service.get_values(isDf=True)
        # 0보다 작은값 nan처리
        values.loc[values["amt"] <= 0, "amt"] = np.nan
        # 피벗
        value_pivot = values.pivot(index="itemCd", columns="metrics", values="amt")
        return value_pivot

    def _get_data_bind(self):
        tickers = self.kor_ticker_service.get_tickers(isDf=True)
        # 티커리스트와 join
        data_bind = tickers[["itemCd", "itemNm"]].merge(
            self.get_value_pivot(),
            how="left",
            on="itemCd",
        )
        return data_bind

    def get_value_portfolio_by_pbr_per(self, rank=20):
        """PER, PBR을 이용한 밸류 포트폴리오"""

        _data_bind = self._get_data_bind()

        # PBR, PER 이 낮은 종목 찾기(랭킹이 낮을 수록 PER, PBR이 낮은 저평가(저벨류에이션) 종목
        # axis=0 열방향으로 랭킹 구하기
        value_rank = _data_bind[["PER", "PBR"]].rank(axis=0)
        # PER, PBR 랭킹을 더한다. na가 존재하면 더해진값 na로 표시(PER, PBR이 동시에 싼 값)
        value_sum = value_rank.sum(axis=1, skipna=False).rank()
        # 20위까지 구하기
        value = _data_bind.loc[value_sum <= rank, ["itemCd", "itemNm", "PER", "PBR"]]
        return value

    def get_value_portfolio_by_all(self, rank=20):
        """PER, PBR, PCR, PSR, DY를 이용한 밸류 포트폴리오"""
        _data_bind = self._get_data_bind()
        value_list_copy = _data_bind.copy()
        # 배당수익률은 높을수록 좋기때문에 역수로 만들어준다.
        value_list_copy["DY"] = 1 / value_list_copy["DY"]
        value_list_copy = value_list_copy[["PER", "PBR", "PCR", "PSR", "DY"]]
        value_rank_all = value_list_copy.rank(axis=0)
        value_sum_all = value_rank_all.sum(axis=1, skipna=False).rank()
        value = _data_bind.loc[value_sum_all <= rank]
        return value

    # def paint_graph(self, momentum):
    #     """그래프 그리기"""
    #     data_bind = tickers[["itemCd", "itemNm"]].merge(
    #         momentum, how="inner", on="itemCd"
    #     )
    #     # 1년치 가격정보 필터링
    #     momentum = self._prices[self._prices["itemCd"].isin(data_bind["itemCd"])]
    #     # 그래프
    #     plt.rc("font", family="AppleGothic")
    #     g = sns.relplot(
    #         data=momentum,
    #         x="baseDt",
    #         y="closePrice",
    #         col="itemCd",
    #         col_wrap=5,
    #         kind="line",
    #         facet_kws={
    #             "sharey": False,
    #             "sharex": True,
    #         },
    #     )
