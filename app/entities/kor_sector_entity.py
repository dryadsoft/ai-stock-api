from sqlalchemy import Column, String

from .base_entity import Base


class KorSectorEntity(Base):
    __tablename__ = "kor_sector"
    baseDt = Column(String, primary_key=True, index=True, comment="기준일")
    cmpCd = Column(String, primary_key=True, index=True, comment="종목코드")
    cmpKor = Column(String, comment="종목명")
    secNmKor = Column(String, comment="섹터명")
    idxCd = Column(String, comment="섹터코드")
