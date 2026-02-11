# Project Objective
This project is meant to download public Pennsylvania court information and store in a usable format for researchers

# How-To Use
## Install required packages and Install Playwright

```
py -m pip install -r requirements.txt && py -m playwright install
```

## Install Playwright if running into issues
```
py -m playwright install
```

## Run

Simply run main.py when in the project directory:

```
py main.py
```

You can also download pfs with

```
pdf_downloader.py
```

and to pull json files simply use:

```
pull_json.py
```

and to format the json files run

```
format_json_files.py
```


## Configure
Configurable constants are at the top of main.py and pdf_downloader.py, documented with comments of course.