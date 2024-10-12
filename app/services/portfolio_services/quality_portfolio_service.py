from pandas import to_numeric
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from app.services.kor_fs_service import KorFsService
from app.services.kor_ticker_service import KorTickerService

# from app.services.kor_price_service import KorPriceService


class QualityPortfolioService:
    """우량주"""

    def __init__(self, session: Session):
        kor_ticker_service = KorTickerService(session)
        kor_fs_service = KorFsService(session)
        # kor_price_service = KorPriceService(session)

        self._tickers = kor_ticker_service.get_tickers(isDf=True)
        self._fs_list = kor_fs_service.get_fs(
            "q",
            ["당기순이익", "매출총이익", "영업활동으로인한현금흐름", "자산", "자본"],
        )

        # 날짜, 종목코드, 종가 조회
        # self._prices = kor_price_service.get_year_price(is_df=True)

    def _get_ttm(self):
        # TTM구하기
        # 종목코드, 계정, 날짜 순으로 정렬
        fs_list = self._fs_list.sort_values(["itemCd", "account", "baseDt"])
        fs_list["ttm"] = (
            fs_list.groupby(["itemCd", "account"], as_index=False)["amt"]
            .rolling(window=4, min_periods=4)
            .sum()["amt"]
        )
        fs_list_clean = fs_list.copy()
        # 자산, 자본은 재무상태표 항목이므로 합이 아닌 평균을 구한다.
        fs_list_clean["ttm"] = np.where(
            fs_list_clean["account"].isin(["자산", "자본"]),
            fs_list_clean["ttm"] / 4,
            fs_list_clean["ttm"],
        )
        # 최근기준일 ttm 데이터만 필터링
        fs_list_clean = fs_list_clean.groupby(["itemCd", "account"]).tail(1)
        return fs_list_clean

    def get_fs_list_pivot(self):
        """
        ROE: 당기순이익 / 자본
        GPA: 매출총이익 / 자산
        CFO: 영업활동으로인한현금흐름 / 자산
        """
        # 피벗
        fs_list_pivot = self._get_ttm().pivot(
            index="itemCd", columns="account", values="ttm"
        )
        # 수익성 지표 구하기
        fs_list_pivot["ROE"] = fs_list_pivot["당기순이익"] / fs_list_pivot["자본"]
        fs_list_pivot["GPA"] = fs_list_pivot["매출총이익"] / fs_list_pivot["자산"]
        fs_list_pivot["CFO"] = (
            fs_list_pivot["영업활동으로인한현금흐름"] / fs_list_pivot["자산"]
        )
        return fs_list_pivot

    def get_quality_momentum(self, rank=20):

        fs_list_pivot = self.get_fs_list_pivot()

        # ticker 리스트와 조인
        quality_list = self._tickers[["itemCd", "itemNm"]].merge(
            fs_list_pivot, how="left", on="itemCd"
        )
        # 수익성 지표만 copy
        quality_list_copy = quality_list[["ROE", "GPA", "CFO"]].copy()
        # 랭킹 구하기
        quality_rank = quality_list_copy.rank(ascending=False, axis=0)
        # 지표들의 랭킹의합을 다시 랭킹
        quality_sum = quality_rank.sum(axis=1, skipna=False).rank()
        # 20위 이내 구하기
        quality = quality_list.loc[
            quality_sum <= rank, ["itemCd", "itemNm", "ROE", "GPA", "CFO"]
        ].round(4)
        return quality

    # def paint_graph(self, momentum):
    #     """그래프 그리기"""
    #     data_bind = self._tickers[["itemCd", "itemNm"]].merge(
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

    def paint_french_portfolio(self, url, title):
        """
        파마프렌치 데이터
        프렌치데이터로 퀄리티 전략 수익률 확인하기
        """
        df_op = pd.read_csv(url, skiprows=24, encoding="cp1252", index_col=0)
        # 시가총액가중 기준 포트폴리오만 필터링(동일가중 기준 포트폴리오 제거)
        end_point = np.where(pd.isna(df_op.iloc[:, 2]))[0][0]
        df_op_vw = df_op.iloc[0:end_point][
            ["Lo 20", "Qnt 2", "Qnt 3", "Qnt 4", "Hi 20"]
        ].apply(to_numeric)
        # 로그 누적 수익률
        df_op_cum = np.log(1 + df_op_vw / 100).cumsum()

        plt.rc("font", family="AppleGothic")
        plt.rc(
            "axes",
            unicode_minus=False,  # 마이너스부분의 오류발생 방지를 위한 옵션
        )

        df_op_cum.plot(
            figsize=(10, 6),
            legend="reverse",
            title=title,
        )
