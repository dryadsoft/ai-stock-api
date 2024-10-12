import yfinance as yf
import pandas as pd
import statsmodels.api as sm  # 회귀분석 패캐지 (statsmodels)


class BetaService:
    """
    * Dep. Variable: 종속변수(Y)는 개별주식 종목
    * Adj. R-squared: 설명력: 높을수록 좋음(현재 0.376 굉장히 높은축)
    * coef(^KS11): 베타 (1.35): 증권주는 코스피의 움직임에 1.35배 반응하는 고베타주
    * t: t-통계값의 절대값이 2보다 크면 통계적으로 유의함. (현재 31 이므로 굉장히 높음)
    * coef(intercept): 알파(0.001): 초과수익률
    * t:0.911 유의하지 않다.
    * 증권주의 수익률은 주식 시장에 대한 노출도인 베타를 제외하면 유의하지 않다.
    RegressionResultsWrapper
    """

    def __init__(self):
        self.KOSPIE = "^KS11"  # 코스피
        self.KIOOM = "039490.KS"  # 키움
        self.reg: RegressionResultsWrapper = None  # type: ignore
        self._calc_beta()

    def _calc_beta(self):
        tickers = [self.KOSPIE, self.KIOOM]  # 코스피, 키움증권

        all_data = {}
        for ticker in tickers:
            all_data[ticker] = yf.download(ticker, start="2018-01-01", end="2024-10-04")

        prices = pd.DataFrame({tic: data["Close"] for tic, data in all_data.items()})
        # 수익률 계산(pct_change)
        ret = prices.pct_change().dropna()
        ret["intercept"] = 1  # 절편
        # 선형회귀분석(OLS)
        # y축: 039490.KS(키움증권): 개별 주식의 수익률
        # x축: 코스피 수익률과 절편
        self.reg = sm.OLS(ret[[self.KIOOM]], ret[[self.KOSPIE, "intercept"]]).fit()

    def get_reg(self):
        return self.reg

    def get_beta(self):
        if self.reg != None:
            return self.reg.params[self.KOSPIE]  # 베타
        return None

    def get_tvalues(self):
        return self.reg.tvalues  # t-통계값(절대값이 2보다 크면 통계적으로 유의함.)

    def rsquared_adj(self):
        return self.reg.rsquared_adj  # 설명력(높을수록 좋음)
