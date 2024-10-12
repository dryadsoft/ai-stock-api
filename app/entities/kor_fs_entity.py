from sqlalchemy import Column, Float, String

from .base_entity import Base


class KorFsEntity(Base):
    __tablename__ = "kor_fs"
    account = Column(String, primary_key=True, index=True, comment="계정")
    baseDt = Column(String, primary_key=True, index=True, comment="기준일")
    amt = Column(Float, comment="값")
    itemCd = Column(String, primary_key=True, index=True, comment="종목코드")
    fsType = Column(String, primary_key=True, index=True, comment="공시구분")
