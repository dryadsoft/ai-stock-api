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

fs_task_trigger = CronTrigger(hour=1, minute=0)
scheduler.add_job(KorFsTask().start, trigger=fs_task_trigger)

value_task_trigger = CronTrigger(hour=5, minute=0)
scheduler.add_job(KorValueTask().start, trigger=value_task_trigger)

# scheduler.add_job(KorPriceTask().start, "interval", seconds=5)
