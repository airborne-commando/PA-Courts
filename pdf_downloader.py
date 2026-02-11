from playwright.sync_api import sync_playwright
import pandas as pd
from tqdm import tqdm
import requests

import time
import os
import random


BASE_URL = 'https://ujsportal.pacourts.us'
WAIT_RANGE = (2, 5)  # range for seconds to wait between pulls, inclusive


def main(df: pd.DataFrame):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context()
        page = context.new_page()

        # Proxy file
        with open('tested_proxies.txt', 'r') as f:
            proxies = f.read().split('\n')

        for i, r in tqdm(df.iterrows()):
            year = r['docket_number'].split('-')[-1]
            # Saves into Docker-Info/PDFs/YYYY/*.pdf
            save_dir = os.path.join('Docket-Info','PDFs', year)
            os.makedirs(save_dir, exist_ok=True)
            if not os.path.isdir(save_dir):
                os.mkdir(save_dir)

            file_name = f'{r["docket_number"]}-{r["link_1"].split("=")[-1].replace("%", "-")}.pdf'
            save_path = os.path.join(save_dir, file_name)
            url = f'{BASE_URL}{r["link_1"]}'

            time.sleep(random.randint(WAIT_RANGE[0], WAIT_RANGE[1]))

            requests_cookies = {cookie['name']: cookie['value'] for cookie in context.cookies()}

            header = {
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

            resp = requests.get(url, cookies=requests_cookies, headers=header)

            if resp.status_code == 200:
                with open(save_path, 'wb') as file:
                    file.write(resp.content)
            else:
                print(f"Failed to download PDF. Status code: {resp.status_code}: {resp.text}| {save_path}")
                page.goto(url)

        browser.close()


if __name__ == '__main__':
    # Example: load your docket data from CSV
    df = pd.read_csv('docket_numbers.csv')  # make sure this file exists and has the right columns
    main(df)
