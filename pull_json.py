import requests
import json
import pandas as pd
import os
from tqdm import tqdm


def main():
    base_url = r'https://services.pacourts.us/public/v1/cases/'

    docket_df = pd.read_csv(r'docket_numbers.csv')

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'ujsportal.pacourts.us',
        'Referer': 'https://ujsportal.pacourts.us/CaseSearch',
        'Sec-Ch-Ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    }

    for docket_number in tqdm(docket_df['docket_number'].unique()):
        r = requests.get(f'{base_url}{docket_number}', headers=headers)

        if r.status_code == 200:
            json_data = json.loads(r.text)

            with open(os.path.join('Docket-Info', 'json-files', f'{docket_number}.json'), 'w') as f:
                json.dump(fp=f, obj=json_data)
                f.close()

        else:
            print(f'{docket_number} | {r} {r.text}')


if __name__ == '__main__':
    main()
