from fastapi import Depends
from sqlalchemy.orm import Session

from app.services.kor_price_service import KorPriceService
from ..connection.session import get_session
from .base_router import router


@router.get("/price/{ticker}", tags=["price"])
async def users(ticker, session: Session = Depends(get_session)):
    kor_price_service = KorPriceService(session)

    return kor_price_service.get_ticker_price(ticker=ticker)
