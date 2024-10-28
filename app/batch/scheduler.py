from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.batch.tasks.kor_value_task import KorValueTask

from ..batch.tasks.kor_sector_task import KorSectorTask
from ..batch.tasks.kor_fs_task import KorFsTask
from ..batch.tasks.kor_price_task import KorPriceTask
from ..batch.tasks.kor_ticker_task import KorTickerTask

scheduler = BackgroundScheduler()

ticker_task_trigger = CronTrigger(hour=23, minute=0)
scheduler.add_job(KorTickerTask().start, trigger=ticker_task_trigger)

sector_task_trigger = CronTrigger(hour=23, minute=0)
scheduler.add_job(KorSectorTask().start, trigger=sector_task_trigger)

price_task_trigger = CronTrigger(hour=1, minute=0)
scheduler.add_job(KorPriceTask().start, trigger=price_task_trigger)

# insert or update 로 바꿔야함
fs_task_trigger = CronTrigger(month="1-12", day=1, hour=1, minute=0)
scheduler.add_job(KorFsTask().start, trigger=fs_task_trigger)

# 네이버 날짜가 새벽5시에 전날기준으로 가져오는지 확인필요함
value_task_trigger = CronTrigger(hour=5, minute=0)
scheduler.add_job(KorValueTask().start, trigger=value_task_trigger)

# scheduler.add_job(KorPriceTask().start, "interval", seconds=5)
