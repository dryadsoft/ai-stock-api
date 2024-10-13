from enum import Enum
from pandas import DataFrame
from sqlalchemy.orm import Session
from scipy.stats import zscore
import numpy as np
from ...services.kor_sector_service import KorSectorService
from ...services.kor_ticker_service import KorTickerService
from ...services.portfolio_services.quality_portfolio_service import (
    QualityPortfolioService,
)
from ...services.portfolio_services.value_portfolio_service import ValuePortfolio
from ...services.portfolio_services.momentum_portfolio_service import MomentumPortfolio
import matplotlib.pyplot as plt


class OutlierMethod(Enum):
    TRIM = "trim"
    WINSER = "winser"


class MultiFactorPortfolioService:
    """멀티팩터 포트폴리오 서비스
    - 퀄리티: 자기자본이익률(ROE), 매출총이익(GPA), 영업활동현금흐름(CFO)
    - 밸류: PER, PBR, PSR, PCR, DY
    - 모멘텀: 12개월 수익률, K-Ratio
    - 섹터 중립화, 랭킹 후 Z-Score 변환
    """

    def __init__(self, session: Session):
        self._quality_protfolio_service = QualityPortfolioService(session)
        self._value_portfolio_service = ValuePortfolio(session)
        self._momentum_portfolio_service = MomentumPortfolio(session)
        self._kor_ticker_service = KorTickerService(session)
        self._kor_sector_service = KorSectorService(session)

        self._fs_list_pivot: DataFrame = None
        self._value_pivot: DataFrame = None
        self._ret_list: DataFrame = None
        self._k_ratio_bind: DataFrame = None
        self._ticker_list: DataFrame = None
        self._sector_list: DataFrame = None
        self._data_bind: DataFrame = None
        self._data_bind_group: DataFrameGroupBy[Scalar] = None  # type: ignore
        self._data_bind_final: DataFrame = None

    def get_data(self):
        # 퀄리티
        self._fs_list_pivot = self._quality_protfolio_service.get_fs_list_pivot()
        # 밸류
        self._value_pivot = self._value_portfolio_service.get_value_pivot()
        # 모멘텀
        self._ret_list = (
            self._momentum_portfolio_service.get_simple_momentum()
        )  # 12개월 누적수익률
        self._k_ratio_bind = (
            self._momentum_portfolio_service.get_k_ratio_momentum()
        )  # k_ratio

        self._ticker_list = self._kor_ticker_service.get_tickers(isDf=True)
        self._sector_list = self._kor_sector_service.get_sectors(is_df=True)

    def merge_data(self):
        """팩터 데이터 합치기"""
        self.get_data()
        # 퀄리티, 밸류, 모멘텀 데이터 합치기
        data_bind = (
            self._ticker_list[["itemCd", "itemNm"]]
            .merge(
                self._sector_list[["cmpCd", "secNmKor"]],
                how="left",
                left_on="itemCd",
                right_on="cmpCd",
            )
            .merge(self._fs_list_pivot[["ROE", "GPA", "CFO"]], how="left", on="itemCd")
            .merge(self._value_pivot, how="left", on="itemCd")
            .merge(self._ret_list, how="left", on="itemCd")
            .merge(self._k_ratio_bind, how="left", on="itemCd")
        )

        data_bind.loc[data_bind["secNmKor"].isnull(), "secNmKor"] = "기타"
        data_bind = data_bind.drop(["cmpCd"], axis=1)
        self._data_bind = data_bind

    def get_group_data(self):
        self.merge_data()
        # 섹터 별 그룹 묶기( 섹터별로 그룹이 묶인 부분에 함수를 적용하면 섹터중립화, 트림(극단치 제거), 랭킹의 z-score계산)
        data_bind_group = self._data_bind.set_index(["itemCd", "secNmKor"]).groupby(
            "secNmKor", as_index=False
        )
        self._data_bind_group = data_bind_group

    def get_sector_quality_zscore(self, method: OutlierMethod = OutlierMethod.TRIM):
        """퀄리티(섹터 중립화된 수익성 순위의 Z-Score)"""

        z_quality = (
            self._data_bind_group[["ROE", "GPA", "CFO"]]
            .apply(lambda x: self.col_clean(x, 0.01, False, method))
            .sum(axis=1, skipna=False)
            .to_frame("z_quality")
        )

        self._data_bind = self._data_bind.merge(
            z_quality, how="left", on=["itemCd", "secNmKor"]
        )

    def get_sector_value_zscore(self, method: OutlierMethod = OutlierMethod.TRIM):
        """벨류 z-score"""
        # PBR, PCR,PER,PSR은 오름차순
        value_1 = self._data_bind_group[["PBR", "PCR", "PER", "PSR"]].apply(
            lambda x: self.col_clean(x, 0.01, True, method)
        )
        # DY는 내림차순
        value_2 = self._data_bind_group[["DY"]].apply(
            lambda x: self.col_clean(x, 0.01, False, method)
        )

        z_value = (
            value_1.merge(value_2, on=["itemCd", "secNmKor"])
            .sum(axis=1, skipna=False)
            .to_frame("z_value")
        )
        self._data_bind = self._data_bind.merge(
            z_value, how="left", on=["itemCd", "secNmKor"]
        )

    def get_sector_momentum_zscore(self, method: OutlierMethod = OutlierMethod.TRIM):
        """모멘텀 z-score"""
        z_momentum = (
            self._data_bind_group[["12M", "k_ratio"]]
            .apply(lambda x: self.col_clean(x, 0.01, False, method))
            .sum(axis=1, skipna=False)
            .to_frame("z_momentum")
        )
        self._data_bind = self._data_bind.merge(
            z_momentum, how="left", on=["itemCd", "secNmKor"]
        )

    def get_sector_neutral_zscore(self, method: OutlierMethod = OutlierMethod.TRIM):
        """섹터 중립화된 수익성 순위의 Z-Score"""
        self.get_group_data()
        self.get_sector_quality_zscore(method)  # 퀄리티
        self.get_sector_value_zscore(method)  # 밸류
        self.get_sector_momentum_zscore(method)  # 모멘텀

    def get_zscore_reblance(self, method: OutlierMethod = OutlierMethod.TRIM):

        self.get_sector_neutral_zscore(method)
        # 다시 z-score를 계산하여 분포를 비슷하게 맞춰준다.
        # 분포를 완벽하게 맞추기위해 z-score를 몇번을 돌리기도 하는데 그럴필요는 없음
        data_bind_final = (
            self._data_bind[["itemCd", "z_quality", "z_value", "z_momentum"]]
            .set_index("itemCd")
            .apply(zscore, nan_policy="omit")
        )
        data_bind_final.columns = ["quality", "value", "momentum"]
        self._data_bind_final = data_bind_final

    def get_final_portfolio(self, method: OutlierMethod = OutlierMethod.TRIM):
        self.get_zscore_reblance(method)
        wts = [0.3, 0.3, 0.3]  # 동일비중
        # 비중 곱해서 해응로 더하기
        data_bind_final_sum = (
            (self._data_bind_final * wts).sum(axis=1, skipna=False).to_frame()
        )
        # 컬럼명 변경
        data_bind_final_sum.columns = ["qvm"]
        port_qvm = self._data_bind.merge(data_bind_final_sum, on="itemCd")
        # 20위 이내는 Y 아니면 N
        port_qvm["invest"] = np.where(port_qvm["qvm"].rank() <= 20, "Y", "N")
        return port_qvm

    def col_clean(
        self,
        df,
        cutoff=0.01,
        ascending=False,
        method: OutlierMethod = OutlierMethod.TRIM,
    ):
        """데이터 클린징"""
        # q_low, q_high는 벡터로 되어있음
        q_low = df.quantile(cutoff)
        q_high = df.quantile(1 - cutoff)

        if method == OutlierMethod.TRIM:
            # 트림: 이상치 제거
            df_cleaned = df[(df > q_low) & (df < q_high)]
        else:
            # 윈저라이징: 이상치 데이터를 경계값으로 대체
            df_cleaned = df.copy()  # 원본을 유지하기 위해 복사본 사용
            # q_low와 q_high는 각 열의 quantile 값을 반환하므로 apply를 사용하여 열별로 처리
            df_cleaned = df_cleaned.apply(
                lambda col: np.where(col < q_low[col.name], q_low[col.name], col),
                axis=0,
            )
            df_cleaned = df_cleaned.apply(
                lambda col: np.where(col > q_high[col.name], q_high[col.name], col),
                axis=0,
            )

        # Z-Score 계산
        df_z_score = df_cleaned.rank(axis=0, ascending=ascending).apply(
            zscore, nan_policy="omit"
        )

        return df_z_score

    def paint_graph(self, data_bind: DataFrame):
        """
        * 세개의 Z-Score 를 단순하게 합하면 안된다.
        * 퀄리티 지표는 3개, 밸류는 5개 모멘텀은 2개를 이용하여 계산
        * 지표를 많이 쓸수록 합이 많아지므로 Z-score가 넓게 퍼진다.
        """
        # 분포 시각화
        data_z = data_bind.copy()

        plt.rc("axes", unicode_minus=False)
        fig, axes = plt.subplots(3, 1, figsize=(10, 6), sharex=True, sharey=True)
        for n, ax in enumerate(axes.flatten()):
            ax.hist(data_z.iloc[:, n])
            ax.set_title(data_z.columns[n], size=12)
        fig.tight_layout()
