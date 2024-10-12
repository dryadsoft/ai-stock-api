from ..apis.external_data_api.biz_day_api import BizDayApi


class BizDayService:

    def __init__(self) -> None:
        self.biz_day_api = BizDayApi()

    def get_biz_day(self):
        return self.biz_day_api.fetch_api()
