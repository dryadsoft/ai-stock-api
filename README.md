# AI_STOCK_ANALYSIS

```note
/corpcode/all
/corpcode/name/{name}
/corpcode/corp/{corp_code}
/corpcode/stock/{stock_code}

/daily_stock/{stock_code}
/daily_stock/{stock_code}/download
http://localhost:4000/apis/daily_stock/006660
http://localhost:4000/apis/daily_stock/005930/download
http://localhost:4000/apis/daily_stock/045880

/item_info

/stock_divi/{stock_code}
/stock_divi/{stock_code}/download
http://localhost:4000/apis/stock_divi/005930
http://localhost:4000/apis/stock_divi/005930/download

/finalcial/{stock_code}
/finalcial/{stock_code}/download
http://localhost:4000/apis/finalcial/005930/download
http://localhost:4000/apis/finalcial/045880
```

## 실행방법

```sh

python3 -m krx_api.main
python3 -m uvicorn krx_api.main:app --reload --host=0.0.0.0 --port=4000

python3 -m uvicorn app.main:app --reload --host=0.0.0.0 --port=4001

nohup python3 -m uvicorn app.main:app --reload --host=0.0.0.0 --port=4003 > /home/ubuntu/logs/ai_stock_api.log 2>&1 &

# test-api 실행했던 명령어
gunicorn -k uvicorn.workers.UvicornWorker --access-logfile ./gunicorn-access.log main:app --bind 0.0.0.0:4000 --workers 2 --daemon
```

## fastapi doc 접속경로

```sh
http://localhost:{서버실행포트}/docs
```

```python
https://chaechae.life/blog/fastapi-scheduler

```

[스케줄러](https://chaechae.life/blog/fastapi-scheduler)

```python

# from krx_api.services.dart_code_service import DartCodeService
# from krx_api.services.dart_notice_service import DartNoticeService

# from krx_api.services.kor_fs_service import KorFsService

# from krx_api.services.kor_value_service import KorValueService

# from krx_api.services.kor_fs_service import KorFsService
# from krx_api.services.kor_price_service import KorPriceService
# from krx_api.services.kor_sector_service import KorSectorService
# from krx_api.services.kor_ticker_service import KorTickerService

# public_stock_price_service = PublicStockPriceService(session)
# public_stock_price_service.insert_data()
# public_stock_price_service.select_datas()

# divi_info_service = GetDiviInfoService(session)
# divi_info_service.insert_data()

# kor_ticker_service = KorTickerService(session)
# kor_ticker_service.insert_data()
# tickers = kor_ticker_service.get_tickers()
# for ticker in tickers:
#     print(ticker.__dict__)

# kor_sector_service = KorSectorService(session)
# kor_sector_service.insert_data()

# kor_price_service = KorPriceService(session)
# kor_price_service.insert_data()

# kor_fs_service = KorFsService(session)
# kor_fs_service.insert_data()

# kor_value_service = KorValueService(session)
# kor_value_service.insert_data()

# dart_code_service = DartCodeService(session)
# dart_code_service.insert_data()

# dart_notice_service = DartNoticeService(session)
# dart_notice_service.fetch_api_data("005930")

```
