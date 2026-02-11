# Project Objective
This project is meant to download public Pennsylvania court information and store in a usable format for researchers

# How-To Use
## Install required packages and Install Playwright
```bash
pip install -r requirements.txt
```
or
```bash
py -m pip install -r requirements.txt && py -m playwright install
```

## Install Playwright if running into issues
```
py -m playwright install
```

## Run
Simply run main.py

When in the project directory, run the following command
```
py main.py
```

## Configure
Configurable constants are at the top of main.py and pdf_downloader.py in all uppercase for ease of access.