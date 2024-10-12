from sqlalchemy import Column, Float, String

from .base_entity import Base


class KorTickerEntity(Base):
    __tablename__ = "kor_ticker"
    baseDt = Column(String, primary_key=True, index=True, comment="기준일")
    itemCd = Column(String, primary_key=True, index=True, comment="종목코드")
    itemNm = Column(String, comment="종목명")
    closePrice = Column(Float, comment="종가")
    mrktCtg = Column(String, comment="시장구분")
    mrktTotAmt = Column(Float, comment="시가총액")
    eps = Column(Float, comment="EPS")
    preEps = Column(Float, comment="선행EPS")
    bps = Column(Float, comment="BPS")
    dvdnAmt = Column(Float, comment="주당배당금")
    itemCtg = Column(String, comment="종목구분")
