from sqlalchemy import Column, Double, String

from .base_entity import Base


class KorPriceEntity(Base):
    __tablename__ = "kor_price"
    baseDt = Column(String, primary_key=True, index=True, comment="기준일")
    openPrice = Column(Double, comment="시가")
    highPrice = Column(Double, comment="고가")
    lowPrice = Column(Double, comment="저가")
    closePrice = Column(Double, comment="종가")
    stockQty = Column(Double, comment="거래량")
    itemCd = Column(String, primary_key=True, index=True, comment="종목코드")
