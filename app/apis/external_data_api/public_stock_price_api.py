import os
import requests

public_api_key = os.environ.get("PUBLIC_DATA_API_KEY")


class PublicStockPriceApi:
    def __init__(self):
        self.service_key = public_api_key
        self.base_url = "http://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo"

    def fetch_api_data(self, start_date, end_date, num_rows=9999, page_no=1):
        """Makes an API request to fetch stock price information."""
        params = {
            "serviceKey": self.service_key,
            "numOfRows": num_rows,
            "pageNo": page_no,
            "resultType": "json",
            "beginBasDt": start_date,
            "endBasDt": end_date,
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch data with HTTP Status {response.status_code}: {response.text}"
            )
        response_json = response.json()
        result_code = response_json["response"]["header"]["resultCode"]
        if result_code != "00":
            raise Exception(
                f"Failed to fetch data with Response resultCode {result_code}"
            )
        return response_json
