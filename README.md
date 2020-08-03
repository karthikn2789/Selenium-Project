## Selenium Web Scraping Project

The project contains a selenium example written in Python to demonstrate web scraping. In this project, PM2.5 values from https://openaq.org are extracted and stored in a JSON file using Selenium.

To run the `openaq_scraper.py` file, Selenium and a webdriver needs to be installed. Selenium can be installed using the following command. 

`pip install selenium`

Webdriver for 5 major browsers are supported by Selenium. Chromedriver for Chrome browser can be installed using the following commands.

```
wget https://chromedriver.storage.googleapis.com/83.0.4103.39/chromedriver_linux64.zip

unzip chromedriver_linux64.zip

sudo mv chromedriver /usr/local/bin/
```

Geckodriver for Firefox can be installed with the following command.

`sudo apt install firefox-geckodriver`

To run the project, execute `openaq_scraper.py` file and it will generate 3 JSON files as output. 
