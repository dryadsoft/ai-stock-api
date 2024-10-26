import numpy as np
from app.services.kor_fs_service import KorFsService
from app.services.kor_ticker_service import KorTickerService
import matplotlib.pyplot as plt
import seaborn as sns


class MagicPortfolioService:
    """조엘 그린블라트(고담 캐피탈의 설립자)
    1. 이익 수익률(Earnings Yield)
    기업의 수익을 기업의 가치로 나눈 값
    이는 PER의 역수와 비숫하며, 밸류 지표 중 하나

    2. 투하자본 수익률(Return on Captial)
    기업의 수익을 투자한 자본으로 나눈 값
    이는 ROE와도 비슷하며, 퀄리티 지표 중 하나

    마법공식은 이 두 가지 지표의 순위를 각각 구한 후
    순위의 합 기준 상위 30~50개 종목을 1년간 보유한 후 리밸런싱

    """

    def __init__(self, session):
        self.kor_ticker_service = KorTickerService(session)
        self.kor_fs_service = KorFsService(session)
        self.get_init_data()

    def get_init_data(self):
        self.tickers = self.kor_ticker_service.get_tickers(isDf=True)
        self.fs_list = self.kor_fs_service.get_fs(
            "q",
            [
                "매출액",
                "당기순이익",
                "법인세비용",
                "이자비용",  # 없음
                "현금및현금성자산",  # 없음
                "부채",
                "유동부채",
                "유동자산",
                "비유동자산",
                "감가상각비",
            ],
        )

    def get_magic(self, rank=20):
        self.fs_list = self.fs_list.sort_values(["itemCd", "account", "baseDt"])
        self.fs_list["ttm"] = (
            self.fs_list.groupby(["itemCd", "account"], as_index=False)["amt"]
            .rolling(window=4, min_periods=4)
            .sum()["amt"]
        )
        fs_list_clean = self.fs_list.copy()
        # "부채", "유동부채", "유동자산", "비유동자산" 는 재무상태표이기때문에 평균으로 바꿔준다.
        fs_list_clean["ttm"] = np.where(
            fs_list_clean["account"].isin(
                ["부채", "유동부채", "유동자산", "비유동자산"]
            ),
            fs_list_clean["ttm"] / 4,
            fs_list_clean["ttm"],
        )

        fs_list_clean = fs_list_clean.groupby(["itemCd", "account"]).tail(1)
        fs_list_pivot = fs_list_clean.pivot(
            index="itemCd", columns="account", values="ttm"
        )

        data_bind = self.tickers[["itemCd", "itemNm", "mrktTotAmt"]].merge(
            fs_list_pivot, how="left", on="itemCd"
        )
        # 시가총액을 억으로나눠서 나머지 데이터와 기준을 맞춰준다.
        data_bind["mrktTotAmt"] = data_bind["mrktTotAmt"] / 100000000

        # 이자비용, 현금및현금성자산, 감가상각비 데이터가 없어서 임시로 0으로 만들어준다.
        # data_bind["이자비용"] = 0
        # data_bind["현금및현금성자산"] = 0
        # data_bind["감가상각비"] = 0

        # 분자(EBIT)
        magic_ebit = (
            data_bind["당기순이익"] + data_bind["법인세비용"] + data_bind["이자비용"]
        )

        # 분모
        magic_cap = data_bind["mrktTotAmt"]  # 시가총액
        magic_debt = data_bind["부채"]
        # 분모: 여유자금
        magic_excess_cash = (
            data_bind["유동부채"]
            - data_bind["유동자산"]
            + data_bind["현금및현금성자산"]
        )
        magic_excess_cash[magic_excess_cash < 0] = 0
        magic_excess_cash_final = data_bind["현금및현금성자산"] - magic_excess_cash

        magic_ev = magic_cap + magic_debt - magic_excess_cash_final

        # 이익수익률(PER의 역수와 비숫하게 나온다)
        magic_ey = magic_ebit / magic_ev
        ###############################################################

        # 투하자본 수익률
        # 분자(위의 EBIT 그대로 사용)

        # 분모
        magic_ic = (data_bind["유동자산"] - data_bind["유동부채"]) + (
            data_bind["비유동자산"] - data_bind["감가상각비"]
        )
        # ROC (ROE와 거의 비슷한 결과가 나옴)
        magic_roc = magic_ebit / magic_ic

        # 열 입력하기
        data_bind["이익 수익률"] = magic_ey
        data_bind["투하자본 수익률"] = magic_roc

        magic_rank = (
            magic_ey.rank(ascending=False, axis=0)
            + magic_roc.rank(ascending=False, axis=0)
        ).rank(axis=0)

        magic = data_bind.loc[
            magic_rank <= rank, ["itemCd", "itemNm", "이익 수익률", "투하자본 수익률"]
        ].round(4)

        return magic, data_bind, magic_rank

    def paint_graph(self, data_bind, magic_rank, rank=20):
        data_bind["투자구분"] = np.where(magic_rank <= rank, "마법공식", "기타")

        plt.rc("font", family="AppleGothic")
        plt.subplots(1, 1, figsize=(10, 6))
        sns.scatterplot(
            data=data_bind,
            x="이익 수익률",
            y="투하자본 수익률",
            hue="투자구분",
            style="투자구분",
            s=200,
        )
        plt.xlim(0, 1)
        plt.ylim(0, 1)
