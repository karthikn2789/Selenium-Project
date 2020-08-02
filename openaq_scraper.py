from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import selenium.common.exceptions as exception
from logzero import logger, logfile
import json
import time


def get_countries():

    countries_list = []

    # driver = webdriver.Chrome() # To open a new browser window and navigate it

    # Use the headless option to avoid opening a new browser window
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    desired_capabilities = options.to_capabilities()
    driver = webdriver.Chrome(desired_capabilities=desired_capabilities)

    # Getting webpage with the list of countries

    driver.get("https://openaq.org/#/countries")

    # Implicit wait
    driver.implicitly_wait(10)

    # Explicit wait
    wait = WebDriverWait(driver, 5)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "card__title")))

    countries = driver.find_elements_by_class_name("card__title")
    for country in countries:
        countries_list.append(country.text)

    driver.quit()

    # Write countries_list to json file
    with open("countries_list.json", "w") as f:
        json.dump(countries_list, f)


def get_urls():
    # Load the countries list written by get_countries()
    with open("countries_list.json", "r") as f:
        countries_list = json.load(f)

    # driver = webdriver.Chrome()

    # Use headless option to not open a new browser window
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    desired_capabilities = options.to_capabilities()
    driver = webdriver.Chrome(desired_capabilities=desired_capabilities)
    urls_final = []
    for country in countries_list:
        # Opening locations webpage
        driver.get("https://openaq.org/#/locations")
        driver.implicitly_wait(5)
        urls = []
        # Scrolling down the country filter till the country is visible
        action = ActionChains(driver)
        action.move_to_element(driver.find_element_by_xpath("//span[contains(text()," + '"' + country + '"' + ")]"))
        action.perform()
        # Identifying country and PM2.5 checkboxes
        country_button = driver.find_element_by_xpath("//label[contains(@for," + '"' + country + '"' + ")]")
        values_button = driver.find_element_by_xpath("//span[contains(text(),'PM2.5')]")

        # Clicking the checkboxes
        country_button.click()
        time.sleep(2)
        values_button.click()
        time.sleep(2)
        while True:
            # Navigating subpages where there are more PM2.5 data. For example, Australia has 162 PM2.5 readings
            # from 162 different locations that are spread across 11 subpages.
            locations = driver.find_elements_by_xpath("//h1[@class='card__title']/a")
            for loc in locations:
                link = loc.get_attribute("href")
                urls.append(link)
            try:
                next_button = driver.find_element_by_xpath("//li[@class='next']")
                next_button.click()
            except exception.NoSuchElementException:
                logger.debug(f"Last page reached for {country}")
                break
        logger.info(f"{country} has {len(urls)} PM2.5 URLs")
        urls_final.extend(urls)
    logger.info(f"Total PM2.5 URLs: {len(urls_final)}")
    driver.quit()
    # Write the URLs to a file
    with open("urls.json", "w") as f:
        json.dump(urls_final, f)


def get_pm_data():
    # Load the URLs list written by get_urls()
    with open("urls.json", "r") as f:
        urls = json.load(f)
    # Use headless option to not open a new browser window
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    desired_capabilities = options.to_capabilities()
    driver = webdriver.Chrome(desired_capabilities=desired_capabilities)
    list_data_dict = []
    count = 0
    for i, url in enumerate(urls):
        data_dict = {}
        # Open the webpage corresponding to each URL
        driver.get(url)
        driver.implicitly_wait(10)
        time.sleep(2)
        try:
            # Extract Location and City
            loc = driver.find_element_by_xpath("//h1[@class='inpage__title']").text.split("\n")
            location = loc[0]
            city_country = loc[1].replace("in ", "", 1).split(",")
            city = city_country[0]
            country = city_country[1]
            data_dict["country"] = country
            data_dict["city"] = city
            data_dict["location"] = location
            pm = driver.find_element_by_xpath("//dt[text()='PM2.5']/following-sibling::dd[1]").text
            if pm is not None:
                # Extract PM2.5 value, Date and Time of recording
                split = pm.split("µg/m³")
                pm = split[0]
                date_time = split[1].replace("at ", "").split(" ")
                date_pm = date_time[1]
                time_pm = date_time[2]
                data_dict["pm25"] = pm
                data_dict["url"] = url
                data_dict["date"] = date_pm
                data_dict["time"] = time_pm
                list_data_dict.append(data_dict)
                count += 1
        except exception.NoSuchElementException:
            # Logging the info of locations that do not have PM2.5 data for manual checking
            logger.error(f"{location} in {city},{country} does not have PM2.5")
        except IndexError:
            logger.error(f"IndexError for URL: {url}")
        except exception.StaleElementReferenceException:
            logger.error(f"StaleElement Exception for URL: {url}")

        # Terminating and re-instantiating webdriver every 200 URL to reduce the load on RAM
        if (i != 0) and (i % 200 == 0):
            driver.quit()
            driver = webdriver.Chrome(desired_capabilities=desired_capabilities)
            logger.info("Chromedriver restarted")
    # Write the extracted data into a JSON file
    with open("openaq_data_1.json", "w") as f:
        json.dump(list_data_dict, f)
    logger.info(f"Scraped {count} PM2.5 readings.")
    driver.quit()


if __name__ == "__main__":
    # Initializing log file
    logfile("openaq_selenium.log", maxBytes=1e6, backupCount=3)

    logger.info(f"Scraping started at {time.strftime('%H:%M:%S')}")
    tic = time.time()

    get_countries()
    get_urls()
    get_pm_data()

    toc = time.time()
    logger.info(f"Scraping ended at {time.strftime('%H:%M:%S')}")
    logger.info(f"Elapsed time: {toc-tic}")
