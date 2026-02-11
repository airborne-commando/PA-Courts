from playwright.sync_api import sync_playwright, Playwright

from tqdm import tqdm
import pandas as pd

import datetime as dt
import random
import time

from pdf_downloader import main as download_pdfs
from pdf_downloader import BASE_URL
import os


START = dt.datetime(year=2025, month=1, day=1)
END = dt.datetime(year=2026, month=8, day=28)
STEP = 179


def run(playwright: Playwright) -> list:
    firefox = playwright.firefox
    browser = firefox.launch(headless=True)
    page = browser.new_page()
    page.goto("https://ujsportal.pacourts.us/CaseSearch")

    date_ranges = get_date_ranges(START, END, 179)

    select_by = page.locator('xpath=//select[@title="Search By"]')
    select_by.select_option(label='Date Filed')

    start_date_enter = page.locator('xpath=//div[@id="FiledStartDate-Control"]/input')
    end_date_enter = page.locator('xpath=//div[@id="FiledEndDate-Control"]/input')

    search_button = page.locator('xpath=//button[@id="btnSearch"]')

    docket_numbers = []
    grabbed_docket_numbers = []

    print('Scraping Docket Numbers')
    for date_range in date_ranges:
        try:
            print(f'{date_range[0]} to {date_range[1]}')
            start_date_enter.fill(date_range[0])
            end_date_enter.fill(date_range[1])

            search_button.click()
            page.wait_for_load_state('load')

            time.sleep(random.randint(1, 3))

            tr_count = page.locator('xpath=//tr').count()
            for i in tqdm(range(tr_count)):
                row_data = {'query_start_date': date_range[0], 'query_end_date': date_range[1]}

                tr = page.locator(f'xpath=//tr').nth(i)
                td = tr.locator('td')
                a_tags = tr.locator('a')

                if td.count() < 7:
                    continue

                docket_number = td.nth(2)
                docket_number = docket_number.text_content()

                row_data['docket_number'] = docket_number

                filing_date = td.nth(6)
                filing_date = filing_date.text_content()

                row_data['filing_date'] = filing_date

                if a_tags.count() >= 2:
                    row_data['link_1'] = a_tags.nth(0).get_attribute('href')
                    row_data['link_2'] = a_tags.nth(1).get_attribute('href')

                if 'PENNSYLVANIA' in docket_number:
                    continue

                docket_numbers.append(row_data)
                grabbed_docket_numbers.append(docket_number)

        except Exception as exp:
            print(exp)

    browser.close()

    return docket_numbers


def get_date_ranges(start: dt.datetime, end: dt.datetime, step: int) -> list:
    date_ranges = []

    date_step_less_1 = dt.timedelta(days=step - 1)
    date_step = dt.timedelta(days=step)

    date_from = start
    date_to = start + date_step_less_1

    if step > (end - start).days:
        date_to = end

    while date_to <= end:
        date_ranges.append((date_from.strftime('%Y-%m-%d'), date_to.strftime('%Y-%m-%d')))

        date_to += date_step
        date_from += date_step

    if step <= (end - start).days:
        date_ranges.append((date_from.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')))

    return date_ranges


if __name__ == '__main__':
    print('=' * 34)
    print('PA Court Data Puller Initiated')
    print(f'Date Range: {START.strftime("%Y-%m-%d")}: {END.strftime("%Y-%m-%d")}')
    print('=' * 34, '\n')
    with sync_playwright() as playwright:
        docket_numbers = run(playwright)

    df = pd.DataFrame(docket_numbers)
    df.drop_duplicates(subset=['docket_number', 'link_1'], inplace=True)

    df.to_csv('docket_numbers.csv', index=False)

    if os.path.isdir('Docket Info') is False:
        os.mkdir('Docket Info')

    df.to_csv(os.path.join(
        'Docket Info', f'docket_info {df["query_start_date"].min()} | {df["query_end_date"].max()}.csv'
    ), index=False)

    print(f'Docket Numbers Grabbed: {len(df.index)}')
    quit()
    print('\nDownloading PDFs')
    download_pdfs(df)
