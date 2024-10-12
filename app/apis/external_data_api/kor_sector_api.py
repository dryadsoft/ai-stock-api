import time
import requests as rq
import json
import pandas as pd
from tqdm import tqdm


class KorSectorApi:
    url = ""
    biz_day = None
    sector_code = ["G25", "G35", "G50", "G40", "G10", "G20", "G55", "G30", "G15", "G45"]

    def __init__(self, biz_day):
        self.biz_day = biz_day

    def fetch_data(self):
        data_sector = []
        for i in tqdm(self.sector_code):
            url = f"https://www.wiseindex.com/Index/GetIndexComponets?ceil_yn=0&dt={self.biz_day}&sec_cd={i}"
            data = rq.get(url).json()
            data_pd = pd.json_normalize(data["list"])

            data_sector.append(data_pd)
            time.sleep(2)
        return data_sector
