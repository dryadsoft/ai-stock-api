import requests


class DartFsApi:
    """
    분기보고서 : 11013 반기보고서 : 11012 3분기보고서 : 11014 사업보고서 : 11011
    fs_div: OFS:재무제표, CFS: 연결재무제표
    sj_div: BS : 재무상태표, IS : 손익계산서, CIS : 포괄손익계산서, CF : 현금흐름표, SCE : 자본변동표
    """

    def __init__(self, dart_api_key):
        self.dart_api_key = dart_api_key
        self.base_url = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"

    def fetch_api_data(self, corp_code, bsns_years, reprt_code, fs_div="CFS"):
        """
        OFS:재무제표
        CFS:연결재무제표
        11013: 1분기보고서
        11012: 반기보고서
        11014: 3분기보고서
        11011: 사업보고서
        """
        report_codes = ["11013", "11012", "11014", "11011"]
        all_data = []
        for year in bsns_years:
            for reprCode in report_codes:
                params = {
                    "crtfc_key": self.dart_api_key,
                    "corp_code": corp_code,
                    "bsns_year": year,
                    "reprt_code": reprCode,
                    "fs_div": fs_div,  # OFS:재무제표, CFS:연결재무제표
                }
                response = requests.get(self.base_url, params=params)
                if response.status_code == 200:
                    data = response.json().get("list", [])
                    if data:
                        all_data.extend(data)
                    elif fs_div == "CFS":
                        return self.fetch_api_data(
                            corp_code, bsns_years, reprt_code, "OFS"
                        )
                else:
                    print(f"Error: {response.status_code}")
        return all_data
