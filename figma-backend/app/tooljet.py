from typing import Tuple, List, Dict
import requests

headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9,ja;q=0.8,it;q=0.7',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IjAxZDJhMzE2LWIyY2YtNGY5Yy1iZjYyLTRlNWViYTMyOWViMiIsInN1YiI6ImpheWhhY2suMEBnbWFpbC5jb20iLCJvcmdhbml6YXRpb25JZCI6IjcxYTIwNjMyLTczMDctNGIwYy05NGUxLTNjMzEyYTdkODVkYSIsImlzU1NPTG9naW4iOnRydWUsImlzUGFzc3dvcmRMb2dpbiI6ZmFsc2UsImlhdCI6MTY2Njc1OTcxNCwiZXhwIjoxNjY5MzUxNzE0fQ.pHLuuOVbOnJudmDNr2hE6reRHVsSVBM360oQM-CfDhk',
    'Connection': 'keep-alive',
    'Origin': 'https://app.tooljet.com',
    'Referer': 'https://app.tooljet.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
}


def create_app(app_json: dict) -> Tuple[str, dict]:
    response = requests.post('https://nlb.tooljet.com/api/apps/import', headers=headers, json=app_json)
    slug = response.json()['slug']
    url = f'https://app.tooljet.com/apps/{slug}'
    return url, response.json()


def get_data_sources(app_id: str, version_id: str) -> List[Dict]:
    params = {
        'app_id': app_id,
        'app_version_id': version_id
    }
    response = requests.get('https://nlb.tooljet.com/api/data_sources', params=params, headers=headers)
    return response.json()['data_sources']


def set_password(app_id, dvdrental_id) -> Dict:
    json_data = {
        'app_id': app_id,
        'name': 'dvdrental',
        'options': [
            {
                'key': 'host',
                'value': 'db.uywwpkevldwuonjtxpkr.supabase.co',
                'encrypted': False,
            },
            {
                'key': 'port',
                'value': 5432,
                'encrypted': False,
            },
            {
                'key': 'database',
                'value': 'postgres',
                'encrypted': False,
            },
            {
                'key': 'username',
                'value': 'postgres',
                'encrypted': False,
            },
            {
                'key': 'password',
                'value': 'dvdrentalpassword-123',
                'encrypted': True,
            },
            {
                'key': 'ssl_enabled',
                'value': True,
                'encrypted': False,
            },
            {
                'key': 'ssl_certificate',
                'value': 'none',
                'encrypted': False,
            },
        ],
    }

    response = requests.put(f'https://nlb.tooljet.com/api/data_sources/{dvdrental_id}', headers=headers, json=json_data)
    return response.json()