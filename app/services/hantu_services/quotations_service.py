import requests as rq
from app.services.hantu_services.auth_service import AuthService
from app.services.hantu_services.domain import Domain


class QuotationsService:
    """국내주식 기본시세"""

    def __init__(self):
        self.BASE_URL = Domain.get_url()
        self.APP_KEY = Domain.get_app_key()
        self.SECRET_KEY = Domain.get_secret_key()
        self.access_token = AuthService().get_access_token()

    def inquire_price(self, ticker: str):
        """주식현재가 시세
        [실전투자/모의투자]
            FHKST01010100 : 주식현재가 시세
        """
        headers = {
            "content-type": "application/json; utf-8",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.APP_KEY,
            "appsecret": self.SECRET_KEY,
            "tr_id": "FHKST01010100",  # 주식현재가 시세
            "tr_cont": "",
            "custtype": "P",  # 개인
            "hashkey": "",
        }
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",  # J : 주식, ETF, ETN,   W: ELW
            "FID_INPUT_ISCD": ticker,
        }
        response = rq.get(
            f"{self.BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price",
            headers=headers,
            params=params,
        )
        if response.status_code != 200:
            raise Exception(
                f"주식현재가 시세 조회에 실패하였습니다.[{response.status_code}]\n error_message: {response.text}"
            )
        else:
            response_json = response.json()
            if response_json["rt_cd"] != "0":
                raise Exception(
                    f"주식현재가 시세 조회에 실패하였습니다.[rt_cd: {response_json['rt_cd']}]\n error_message: [{response_json['msg_cd']}] {response_json['msg1']}"
                )

            print(f"[{response_json['msg_cd']}] {response_json['msg1']}")
            return response_json["output"]

    def inquire_daily_price(self, ticker: str):
        """주식현재가 일자별
        [실전투자/모의투자]
            FHKST01010400 : 주식현재가 일자별
        """
        headers = {
            "content-type": "application/json; utf-8",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.APP_KEY,
            "appsecret": self.SECRET_KEY,
            "tr_id": "FHKST01010400",  # 주식현재가 일자별
            "tr_cont": "",
            "custtype": "P",  # 개인
            "hashkey": "",
        }
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",  # J : 주식, ETF, ETN,   W: ELW
            "FID_INPUT_ISCD": ticker,
            "FID_PERIOD_DIV_CODE": "M",  # D: (일)최근 30거래일, W: (주)최근 30주, M: (월)최근 30개월
            "FID_ORG_ADJ_PRC": "0",  # FID 수정주가 원주가 가격, 0: 수정주가반영, 1 : 수정주가미반영
        }
        response = rq.get(
            f"{self.BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-daily-price",
            headers=headers,
            params=params,
        )
        if response.status_code != 200:
            raise Exception(
                f"주식현재가 일자별 시세 조회에 실패하였습니다.[{response.status_code}]\n error_message: {response.text}"
            )
        else:
            response = response.json()
            if response["rt_cd"] != "0":
                raise Exception(
                    f"주식현재가 일자별 시세 조회에 실패하였습니다.[rt_cd: {response['rt_cd']}]\n error_message: [{response['msg_cd']}] {response['msg1']}"
                )
            print(f"[{response['msg_cd']}] {response['msg1']}")
            return response["output"]

    def inquire_daily_itemchartprice(self, ticker: str, start_dt: str, end_dt: str):
        """국내주식기간별시세(일/주/월/년)[v1_국내주식-016]: 최대 100건 조회
        [실전투자/모의투자]
            FHKST03010100 : 주주국내주식기간별시세

        """
        headers = {
            "content-type": "application/json; utf-8",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.APP_KEY,
            "appsecret": self.SECRET_KEY,
            "tr_id": "FHKST03010100",
            "custtype": "P",  # 개인
        }
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",  # J : 주식, ETF, ETN,   W: ELW
            "FID_INPUT_ISCD": ticker,
            "FID_INPUT_DATE_1": start_dt,  # 입력 날짜 (시작)
            "FID_INPUT_DATE_2": end_dt,  # 입력 날짜 (종료)
            "FID_PERIOD_DIV_CODE": "D",  # D:일봉, W:주봉, M:월봉, Y:년봉
            "FID_ORG_ADJ_PRC": "0",  # 0:수정주가 1:원주가
        }
        response = rq.get(
            f"{self.BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
            headers=headers,
            params=params,
        )
        if response.status_code != 200:
            raise Exception(
                f"주국내주식기간별시세 시세 조회에 실패하였습니다.[{response.status_code}]\n error_message: {response.text}"
            )
        else:
            response = response.json()
            if response["rt_cd"] != "0":
                raise Exception(
                    f"주식현재가 일자별 시세 조회에 실패하였습니다.[rt_cd: {response['rt_cd']}]\n error_message: [{response['msg_cd']}] {response['msg1']}"
                )
            print(f"[{response['msg_cd']}] {response['msg1']}")
            return response
