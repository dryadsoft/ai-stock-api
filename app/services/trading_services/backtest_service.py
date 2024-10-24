import bt
from pandas import DataFrame
import pandas_ta as ta
import pandas as pd
import numpy as np


class BacktestService:
    def __init__(self):
        pass

    def buy_and_hold(self, data, name):
        """매수 후 보유"""
        strategy = bt.Strategy(
            name,
            [
                bt.algos.SelectAll(),  # 전체데이터사용
                bt.algos.WeighEqually(),  # 투자비중
                bt.algos.RunOnce(),
                bt.algos.Rebalance(),
            ],
        )
        # Return the backtest
        return bt.Backtest(strategy, data)

    def sma(self, name: str, data: DataFrame, length=200):
        """추세추종전력: 입력값이 True일때만 투자하도록 정의"""

        sma = data.apply(lambda x: ta.sma(x, length))
        strategy = bt.Strategy(
            name,  # 백테스트 이름
            [
                bt.algos.SelectWhere(
                    data > sma
                ),  # 입력값이 True일때만 투자를 하도록 정의
                bt.algos.WeighEqually(),  # 투자비중
                bt.algos.Rebalance(),
            ],
        )
        return bt.Backtest(strategy, data)  # 백테스트 생성

    def _golden_dead_cross_signal(self, data, long=200, short=60):
        sma_long = data.apply(lambda x: ta.sma(x, long))
        sma_short = data.apply(lambda x: ta.sma(x, short))

        signal = sma_long.copy()
        signal[sma_short >= sma_long] = 1
        signal[sma_short < sma_long] = -1
        signal[signal.isnull()] = 0

        bind = pd.concat([data, sma_long, sma_short, signal], axis=1)
        bind.columns = ["Ticker", "SMA 200", "SMA 60", "signal"]
        return signal, bind

    def golden_dead_cross(self, data, long=200, short=60):
        """추세추종전략: 골든크로스, 데드크로스"""
        signal, bind = self._golden_dead_cross_signal(data, long, short)
        # 입력된 비중은 당일부터가 아니라 다음날 시가부터 적용됨
        strategy = bt.Strategy(
            "SMA crossover",
            [
                bt.algos.SelectAll(),
                bt.algos.WeighTarget(signal),  # 해당 시점과 비중에 맞춰 리벨런싱 실시
                bt.algos.Rebalance(),
            ],
        )
        return bt.Backtest(strategy, data), bind

    def rsi(self, data: DataFrame, length=14):
        """평균회귀전략: RSI"""
        target_rsi = data.apply(lambda x: ta.rsi(x, length))

        signal = target_rsi.copy()
        signal[target_rsi > 70] = -1
        signal[target_rsi < 30] = 1
        signal[(target_rsi <= 70) & (target_rsi >= 30)] = 0
        signal[signal.isnull()] = 0

        strategy = bt.Strategy(
            "RSI_MeanReversion",
            [
                bt.algos.WeighTarget(signal),
                bt.algos.Rebalance(),
            ],
        )
        return bt.Backtest(strategy, data)

    def bb_band(self, data: DataFrame, length=20, width=2):
        """평균회귀전략: 볼린저밴드"""

        bb = ta.bbands(data["closePrice"], length, width)[
            ["BBU_20_2.0", "BBM_20_2.0", "BBL_20_2.0"]
        ]
        bb = pd.concat([bb, data["closePrice"]], axis=1)
        bb.columns = ["Upper Band", "Mid Band", "Lower Band", "Ticker"]

        signal = data.copy()
        signal["closePrice"] = np.nan

        signal[bb["Ticker"] > bb["Upper Band"]] = -1
        signal[bb["Ticker"] < bb["Lower Band"]] = 1
        signal[signal.isnull()] = 0

        strategy = bt.Strategy(
            "BB Band",
            [
                bt.algos.WeighTarget(signal),
                bt.algos.Rebalance(),
            ],
        )
        return bt.Backtest(strategy, data)

    def run_backtest(self, *strategies):
        return bt.run(*strategies)
