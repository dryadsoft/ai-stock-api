from sqlalchemy import Column, String

from .base_entity import Base


class DartCodeEntity(Base):
    __tablename__ = "dart_code"
    corp_code = Column(String, primary_key=True, index=True, comment="고유번호")
    corp_name = Column(String, comment="정식명칭")
    stock_code = Column(String, comment="종목코드")
    modify_date = Column(String, comment="최종변경일자")
