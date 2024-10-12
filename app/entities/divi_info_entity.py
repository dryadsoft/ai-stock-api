from sqlalchemy import Column, Integer, String

from .base_entity import Base


class DiviInfoEntity(Base):
    __tablename__ = "divi_info"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    basDt = Column(String, index=True)  # "기준일자": item["basDt"],
    crno = Column(String, index=True)  # "법인등록번호": item["crno"],
    isinCd = Column(String)  # "ISIN코드": item["isinCd"],
    stckIssuCmpyNm = Column(String)  # "주식발행회사명": item["stckIssuCmpyNm"],
    isinCdNm = Column(String)  # "ISIN코드명": item["isinCdNm"],
    scrsItmsKcd = Column(String)  # "유가증권종목종류코드": item["scrsItmsKcd"],
    scrsItmsKcdNm = Column(String)  # "유가증권종목종류코드명": item["scrsItmsKcdNm"],
    stckParPrc = Column(String)  # "주식액면가": item["stckParPrc"],
    trsnmDptyDcd = Column(String)  # "명의개서대리인구분코드": item["trsnmDptyDcd"],
    trsnmDptyDcdNm = Column(
        String
    )  # "명의개서대리인구분코드명": item["trsnmDptyDcdNm"],
    stckStacMd = Column(String)  # "주식결산월일": item["stckStacMd"],
    dvdnBasDt = Column(String, index=True)  # "배당기준일자": item["dvdnBasDt"],
    cashDvdnPayDt = Column(
        String, index=True
    )  # "현금배당지급일자": item["cashDvdnPayDt"],
    stckHndvDt = Column(String)  # "주식교부일자": item["stckHndvDt"],
    stckDvdnRcd = Column(String)  # "주식배당사유코드": item["stckDvdnRcd"],
    stckDvdnRcdNm = Column(String)  # "주식배당사유코드명": item["stckDvdnRcdNm"],
    stckGenrDvdnAmt = Column(String)  # "주식일반배당금액": item["stckGenrDvdnAmt"],
    stckGrdnDvdnAmt = Column(String)  # "주식차등배당금액": item["stckGrdnDvdnAmt"],
    stckGenrCashDvdnRt = Column(
        String
    )  # "주식일반현금배당률": item["stckGenrCashDvdnRt"],
    stckGenrDvdnRt = Column(String)  # "주식일반배당률": item["stckGenrDvdnRt"],
    cashGrdnDvdnRt = Column(String)  # "현금차등배당률": item["cashGrdnDvdnRt"],
    stckGrdnDvdnRt = Column(String)  # "주식차등배당률": item["stckGrdnDvdnRt"],
