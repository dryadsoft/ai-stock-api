import numpy as np
import requests as rq
from io import BytesIO
import pandas as pd


class KorTickerApi:
    gen_otp_url = "http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd"
    down_url = "http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd"
    biz_day = None

    def __init__(self, biz_day):
        self.biz_day = biz_day

    def _get_headers(self):
        return {
            "Referer": "http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020506",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        }

    def _get_params(self, mktId):
        if mktId == "ALL":
            return {
                "locale": "ko_KR",
                "searchType": "1",
                "mktId": "ALL",
                "trdDd": self.biz_day,
                "param1isuCd_finder_stkisu0_1": "ALL",
                "csvxls_isNo": "false",
                "name": "fileDown",
                "url": "dbms/MDC/STAT/standard/MDCSTAT03501",
            }
        else:
            return {
                "locale": "ko_KR",
                "mktId": mktId,
                "trdDd": self.biz_day,
                "money": "1",
                "csvxls_isNo": "false",
                "name": "fileDown",
                "url": "dbms/MDC/STAT/standard/MDCSTAT03901",
            }

    def _get_otp(self, mktId):
        otp = rq.post(
            self.gen_otp_url,
            self._get_params(mktId),
            headers=self._get_headers(),
        ).text
        return otp

    def _download_sector(self, mktId):
        down_sector = rq.post(
            self.down_url, {"code": self._get_otp(mktId)}, headers=self._get_headers()
        )
        # BytesIO(down_sector_stk.content)# 바이너리 스트림형태로 변경
        sector = pd.read_csv(BytesIO(down_sector.content), encoding="EUC-KR")
        return sector

    def get_krx_sectors(self):
        sector_stk = self._download_sector("STK")
        sector_ksq = self._download_sector("KSQ")
        krx_ind = self._download_sector("ALL")

        krx_sectors = pd.concat([sector_stk, sector_ksq]).reset_index(drop=True)
        krx_sectors["종목명"] = krx_sectors["종목명"].str.strip()
        krx_sectors["기준일"] = self.biz_day

        krx_ind["종목명"] = krx_ind["종목명"].str.strip()
        krx_ind["기준일"] = self.biz_day
        return krx_sectors, krx_ind

    def merge_data(self):

        [krx_sectors, krx_ind] = self.get_krx_sectors()

        # 교집합에 해당한는 데이터를 합친다.
        kor_ticker = pd.merge(
            krx_sectors,
            krx_ind,
            on=krx_sectors.columns.intersection(
                krx_ind.columns,
            ).to_list(),
            how="outer",
        )

        diff = list(
            set(krx_sectors["종목명"]).symmetric_difference(set(krx_ind["종목명"]))
        )
        kor_ticker["종목구분"] = np.where(
            kor_ticker["종목명"].str.contains("스팩|제[0-9]+호"),
            "스팩",
            np.where(
                kor_ticker["종목코드"].str[-1:] != "0",
                "우선주",
                np.where(
                    kor_ticker["종목명"].str.endswith("리츠"),
                    "리츠",
                    np.where(kor_ticker["종목명"].isin(diff), "기타", "보통주"),
                ),
            ),
        )

        kor_ticker = kor_ticker.reset_index(drop=True)
        kor_ticker.columns = kor_ticker.columns.str.replace(" ", "")
        kor_ticker = kor_ticker[
            [
                "종목코드",
                "종목명",
                "시장구분",
                "종가",
                "시가총액",
                "기준일",
                "EPS",
                "선행EPS",
                "BPS",
                "주당배당금",
                "종목구분",
            ]
        ]  # 컬럼 지정
        kor_ticker = kor_ticker.replace(
            {np.nan: None}
        )  # NaN데이터를 모두 None로 변경한다.
        return kor_ticker
