from sqlalchemy import Column, Double, String

from .base_entity import Base


class KorValueEntity(Base):
    __tablename__ = "kor_value"
    itemCd = Column(String, primary_key=True, index=True, comment="종목코드")
    baseDt = Column(String, primary_key=True, index=True, comment="기준일")
    metrics = Column(String, primary_key=True, index=True, comment="지표")
    amt = Column(Double, comment="값")
