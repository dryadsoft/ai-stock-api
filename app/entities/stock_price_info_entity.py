from sqlalchemy import Column, Float, Integer, String

from .base_entity import Base


class StockPriceInfoEntity(Base):
    __tablename__ = "stock_price_info"
    # id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    basDt = Column(String, primary_key=True, index=True)  # "기준일자": item[""],
    srtnCd = Column(
        String, primary_key=True, index=True
    )  # "srtnCd": item[""],  # 900110</srtnCd>
    isinCd = Column(String)  # "isinCd": item[""],  # HK0000057197</isinCd>
    itmsNm = Column(String)  # "itmsNm": item[""],  # 이스트아시아홀딩스</itmsNm>
    mrktCtg = Column(String)  # "mrktCtg": item[""],  # KOSDAQ</mrktCtg>
    clpr = Column(Integer)  # "close": int(item[""]),
    vs = Column(Integer)  # "close": int(item[""]),
    fltRt = Column(Float)  # "close": int(item[""]),
    mkp = Column(Integer)  # "open": int(item[""]),
    hipr = Column(Integer)  # "high": int(item[""]),
    lopr = Column(Integer)  # "low": int(item[""]),
    trqu = Column(Integer)  # "거래량": int(item[""]),  # 체결수량의 누적 합계
    trPrc = Column(
        Integer
    )  # "거래대금": int(item[""]),  # 거래건 별 체결가격 * 체결수량의 누적 합계
    lstgStCnt = Column(Integer)  # "상장주식수": int(item[""]),  # 종목의 상장주식수
    mrktTotAmt = Column(Integer)  # "시가총액": int(item[""]),  # 종가 * 상장주식수
