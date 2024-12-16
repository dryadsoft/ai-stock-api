import os
import requests as rq
from app.services.hantu_services.auth_service import AuthService
from app.services.hantu_services.domain import Domain


class TradingService:
    def __init__(self, access_token: str):
        self._APP_KEY = os.environ.get("HAN_TU_APP_KEY")
        self._SECRET_KEY = os.environ.get("HAN_TU_SECRET_KEY")
        self._IS_PROD = Domain.get_is_prod()
        self._BASE_URL = Domain.get_url()
        self._CANO = Domain.get_cano()
        self._ACNT_PRDT_CD = Domain.get_acnt_prdt_cd()
        self._ACCESS_TOKEN = access_token
        self._auth_service = AuthService()

    def order_cash(self, ticker: str, order_qty: str, order_price: str):
        """주식주문(현금)
        [실전투자]
            TTTC0802U : 주식 현금 매수 주문
            TTTC0801U : 주식 현금 매도 주문
        [모의투자]
            VTTC0802U : 주식 현금 매수 주문
            VTTC0801U : 주식 현금 매도 주문
        """
        json_body = {
            "CANO": self._CANO,  # 계좌번호 체계(8-2)의 앞 8자리
            "ACNT_PRDT_CD": self._ACNT_PRDT_CD,  # 계좌번호 체계(8-2)의 뒤 2자리
            "PDNO": ticker,  # 종목코드(6자리), ETN의 경우, Q로 시작 (EX. Q500001)
            "ORD_DVSN": "00",  # 주문구분 (지정가)
            "ORD_QTY": order_qty,  # 주문주식수
            "ORD_UNPR": order_price,  # 1주당 가격
        }
        hash_res = self._auth_service.get_hash_key(json_body)
        # print(hash_res)
        headers = {
            "content-type": "application/json; utf-8",
            "authorization": f"Bearer {self._ACCESS_TOKEN}",
            "appkey": self._APP_KEY,
            "appsecret": self._SECRET_KEY,
            "tr_id": (
                "TTTC0802U" if self._IS_PROD else "VTTC0802U"
            ),  # 주식 현금 매수 주문
            "tr_cont": "",
            "custtype": "P",  # 개인
            "hashkey": hash_res["HASH"],
        }

        response = rq.post(
            f"{self._BASE_URL}/uapi/domestic-stock/v1/trading/order-cash",
            headers=headers,
            json=hash_res["BODY"],
        )

        if response.status_code != 200:

            raise Exception(
                f"주식주문(현금)에 실패하였습니다.[{response.status_code}]\n error_message: {response.text}"
            )
        else:
            return response.json()

    def inquire_psbl_rvsecncl(self):
        """주식정정취소가능주문조회[v1_국내주식-004]: 모의투자 사용 불가
        [실전투자]
            TTTC8036R :
            정정취소가능수량(output > psbl_qty)
        """
        headers = {
            "content-type": "application/json; utf-8",
            "authorization": f"Bearer {self._ACCESS_TOKEN}",
            "appkey": self._APP_KEY,
            "appsecret": self._SECRET_KEY,
            "tr_id": "TTTC8036R",  # 주식 정정 취소 가능 주문 조회
            "tr_cont": "",
            "custtype": "P",  # 개인
        }
        params = {
            "CANO": self._CANO,  # 계좌번호 체계(8-2)의 앞 8자리
            "ACNT_PRDT_CD": self._ACNT_PRDT_CD,  # 계좌번호 체계(8-2)의 뒤 2자리
            "CTX_AREA_FK100": "",  # 종연속조회검색조건100
            "CTX_AREA_NK100": "",  # 주연속조회키100
            "INQR_DVSN_1": "0",  # 조회구분1, 0 : 조회순서, 1 : 주문순, 2 : 종목순
            "INQR_DVSN_2": "0",  # 1조회구분2, 0 : 전체, 1 : 매도, 2 : 매수
        }
        response = rq.get(
            f"{self._BASE_URL}/uapi/domestic-stock/v1/trading/inquire-psbl-rvsecncl",
            headers=headers,
            params=params,
        )
        if response.status_code != 200:
            raise Exception(
                f"주주식정정취소가능주문조회에 실패하였습니다.[{response.status_code}]\n error_message: {response.text}"
            )
        else:
            response = response.json()
            if response["rt_cd"] != "0":
                raise Exception(
                    f"주주식정정취소가능주문조회에 실패하였습니다.[rt_cd: {response["rt_cd"]}]\n error_message: [{response["msg_cd"]}] {response["msg1"]}"
                )
            print(f"[{response["msg_cd"]}] {response["msg1"]}")
            return response["output"]

    def inquire_daily_ccld(self):
        """주식일별주문체결조회[v1_국내주식-005]
        [실전투자]
        TTTC8001R : 주식 일별 주문 체결 조회(3개월이내)
        CTSC9115R : 주식 일별 주문 체결 조회(3개월이전)

        [모의투자]
        VTTC8001R : 주식 일별 주문 체결 조회(3개월이내)
        VTSC9115R : 주식 일별 주문 체결 조회(3개월이전)
        * 일별 조회로, 당일 주문내역은 지연될 수 있습니다.
        * 3개월이내 기준: 개월수로 3개월
        오늘이 4월22일이면 TTC8001R에서 1월~ 3월 + 4월 조회 가능
        5월이 되면 1월 데이터는 TTC8001R에서 조회 불가, TSC9115R로 조회 가능
        """
        headers = {
            "content-type": "application/json; utf-8",
            "authorization": f"Bearer {self._ACCESS_TOKEN}",
            "appkey": self._APP_KEY,
            "appsecret": self._SECRET_KEY,
            "tr_id": (
                "TTTC8001R" if self._IS_PROD else "VTTC8001R"
            ),  # 주식 정정 취소 가능 주문 조회
            "tr_cont": "",
            "custtype": "P",  # 개인
        }
        params = {
            "CANO": self._CANO,  # 계좌번호 체계(8-2)의 앞 8자리
            "ACNT_PRDT_CD": self._ACNT_PRDT_CD,  # 계좌번호 체계(8-2)의 뒤 2자리
            "INQR_STRT_DT": "",  # 조회시작일자
            "INQR_END_DT": "",  # 조회종료일자
            "SLL_BUY_DVSN_CD": "00",  # 매도매수구분코드, 00 : 전체, 01 : 매도, 02 : 매수
            "INQR_DVSN": "00",  # 조회구분, 00 : 역순, 01 : 정순
            "PDNO": "",  # 종목번호(6자리), 공란 : 전체 조회
            "CCLD_DVSN": "02",  # 체결구분, 00 : 전체, 01 : 체결, 02 : 미체결
            "ORD_GNO_BRNO": "",  # 주문채번지점번호, "" (Null 값 설정)
            "ODNO": "",  # 주문번호
            "INQR_DVSN_3": "00",  # 조회구분3, 00 : 전체, 01 : 현금, 02 : 융자, 03 : 대출, 04 : 대주
            "INQR_DVSN_1": "",  # 조회구분1, 공란 : 전체, 1 : ELW, 2 : 프리보드
            "CTX_AREA_FK100": "",  # 연속조회검색조건100
            "CTX_AREA_NK100": "",  # 연속조회키100
        }
        response = rq.get(
            f"{self._BASE_URL}/uapi/domestic-stock/v1/trading/inquire-daily-ccld",
            headers=headers,
            params=params,
        )
        if response.status_code != 200:
            raise Exception(
                f"주식일별주문체결조회 실패하였습니다.[{response.status_code}]\n error_message: {response.text}"
            )
        else:
            response_json = response.json()
            if response_json["rt_cd"] != "0":
                raise Exception(
                    f"주식일별주문체결조회 실패하였습니다.[rt_cd: {response_json["rt_cd"]}]\n error_message: [{response_json["msg_cd"]}] {response_json["msg1"]}"
                )
            print(f"[{response_json["msg_cd"]}] {response_json["msg1"]}")
            return response_json["output1"]

    def order_rvsecncl(self, orgn_odno: str):
        """주식주문(정정취소)[v1_국내주식-003]
        [실전투자]
        TTTC0803U : 주식 정정 취소 주문

        [모의투자]
        VTTC0803U : 주식 정정 취소 주문
        """

        headers = {
            "content-type": "application/json; utf-8",
            "authorization": f"Bearer {self._ACCESS_TOKEN}",
            "appkey": self._APP_KEY,
            "appsecret": self._SECRET_KEY,
            "tr_id": (
                "TTTC0803U" if self._IS_PROD else "VTTC0803U"
            ),  # 주식 정정 취소 주문
            "tr_cont": "",
            "custtype": "P",  # 개인
            "hashkey": "",
        }

        json_body = {
            "CANO": self._CANO,  # 계좌번호 체계(8-2)의 앞 8자리
            "ACNT_PRDT_CD": self._ACNT_PRDT_CD,  # 계좌번호 체계(8-2)의 뒤 2자리
            "KRX_FWDG_ORD_ORGNO": "",  # 한국거래소전송주문조직번호
            "ORGN_ODNO": orgn_odno,  # 원주문번호(주식일별주문체결조회 API output1의 odno(주문번호) 값 입력)
            "ORD_DVSN": "00",  # 주문구분 (지정가)
            "RVSE_CNCL_DVSN_CD": "02",  # 정정 : 01, 취소 : 02
            "ORD_QTY": "0",  # 잔량전부
            "ORD_UNPR": "0",  # 주문단가(취소: 0설정)
            "QTY_ALL_ORD_YN": "Y",  # Y : 잔량전부, N : 잔량일부
        }
        response = rq.post(
            f"{self._BASE_URL}/uapi/domestic-stock/v1/trading/order-rvsecncl",
            headers=headers,
            json=json_body,
        )

        if response.status_code != 200:

            raise Exception(
                f"주식주문(정정취소)에 실패하였습니다.[{response.status_code}]\n error_message: {response.text}"
            )
        else:
            response_json = response.json()
            print(response_json)
            return response_json
