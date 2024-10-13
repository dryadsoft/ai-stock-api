# 모멘텀 포트폴리오
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
from ...services.kor_price_service import KorPriceService
from ...services.kor_ticker_service import KorTickerService


class MomentumPortfolio:
    """Momentum portfolio
    3~12개월 수익률을 함께 보거나, 변동성을 같이 고려하기도함
    모멤텀의 꾸준함을 측정하는 지표 중 하나가 K-Ratio
    K-Ratio: 추세가 꾸준하게 많이 상승할수록 K-Ratio는 증가
    K-Ratio는 단순누적 수익률이 아닌 로그누적 수익률로 구해야한다.
    """

    def __init__(self, session: Session):
        self.kor_price_service = KorPriceService(session)
        self.kor_ticker_service = KorTickerService(session)

    def get_price_pivot(self):
        """price pivot 데이터 조회"""

        # 날짜, 종목코드, 종가 조회
        prices = self.kor_price_service.get_year_price(is_df=True)
        # 피벗으로 날짜를 인덱스로 종목코드를 컬럼으로 변환
        price_pivot = prices.pivot(
            index="baseDt", columns="itemCd", values="closePrice"
        )
        return price_pivot

    def get_simple_momentum(self):
        """단순 모멘텀: 12개월 누적수익률"""

        price_pivot = self.get_price_pivot()
        # 각 종목의 1년 누적 수익률
        ret_list = pd.DataFrame(
            data=(price_pivot.iloc[-1] / price_pivot.iloc[0]) - 1,
            columns=["12M"],
        )
        return ret_list

    def get_k_ratio_momentum(self):
        """K-ratio momentum"""

        price_pivot = self.get_price_pivot()
        tickers = self.kor_ticker_service.get_tickers(isDf=True)
        data_bind = tickers[["itemCd", "itemNm"]]
        # 종목별 일간 수익률 계산
        ret = price_pivot.pct_change().iloc[1:]
        # 로그 누적 수익률
        ret_cum = np.log(1 + ret).cumsum()

        x = np.array(range(len(ret)))
        k_ratio = {}  # 전종목 K-Ratio

        for i in range(0, len(tickers)):
            ticker = data_bind.loc[i, "itemCd"]
            try:
                y = ret_cum.loc[:, price_pivot.columns == ticker]
                # 선형회귀분석
                reg = sm.OLS(y, x).fit()
                res = float((reg.params / reg.bse).iloc[0])
            except:
                res = np.nan
            k_ratio[ticker] = res

        k_radio_bind = pd.DataFrame.from_dict(k_ratio, orient="index").reset_index()
        k_radio_bind.columns = ["itemCd", "k_ratio"]
        return k_radio_bind

    def get_momentum_rank(self, type="k_ratio", rank=20):
        "랭킹 구하기"
        tickers = self.kor_ticker_service.get_tickers(isDf=True)
        data_bind: pd.DataFrame = None
        if type == "k_ratio":
            base_data = self.get_k_ratio_momentum()
            # 티커리스트와 join
            data_bind = tickers[["itemCd", "itemNm"]].merge(
                base_data, how="left", on="itemCd"
            )
            # rank 구하기
            result_rank = data_bind["k_ratio"].rank(axis=0, ascending=False)
            # rank 순위 이내까지만 필터링
            result = data_bind[result_rank <= rank].sort_values(
                by=["k_ratio"], ascending=False
            )
        else:
            base_data = self.get_simple_momentum()
            # 티커리스트와 join
            data_bind = tickers[["itemCd", "itemNm"]].merge(
                base_data, how="left", on="itemCd"
            )
            # rank 구하기
            result_rank = data_bind["12M"].rank(axis=0, ascending=False)
            # rank 순위 이내까지만 필터링
            result = data_bind[result_rank <= rank].sort_values(
                by=["12M"], ascending=False
            )
        return result

    def paint_graph(self, momentum):
        """그래프 그리기"""
        tickers = self.kor_ticker_service.get_tickers(isDf=True)
        # 날짜, 종목코드, 종가 조회
        prices = self.kor_price_service.get_year_price(is_df=True)

        data_bind = tickers[["itemCd", "itemNm"]].merge(
            momentum, how="inner", on="itemCd"
        )
        # 1년치 가격정보 필터링
        momentum = prices[prices["itemCd"].isin(data_bind["itemCd"])]
        # 그래프
        plt.rc("font", family="AppleGothic")
        g = sns.relplot(
            data=momentum,
            x="baseDt",
            y="closePrice",
            col="itemCd",
            col_wrap=5,
            kind="line",
            facet_kws={
                "sharey": False,
                "sharex": True,
            },
        )


def test(price_pivot):
    # 종목별 일간 수익률 계산
    ret = price_pivot.pct_change().iloc[1:]
    # 로그 누적 수익률
    ret_cum = np.log(1 + ret).cumsum()
    # x, y축 구하기
    x = np.array(range(len(ret)))
    y = ret_cum.iloc[
        :, 0
    ].values  # 전체행의 0번째 열의 values를 구한다.(첫번째 종목만 선정)
    # 선형회귀분석
    reg = sm.OLS(y, x).fit()
    # 회구분석 결과 조회
    reg.summary()

    # coef: 기울기, std err: 표준오차
    # K-Ratio: coef / std err
    print(reg.params, reg.bse, (reg.params / reg.bse))
