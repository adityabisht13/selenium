from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import logging

logging.basicConfig(
    filename='scraper.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def init_driver():
    logging.info("Initializing headless Chrome WebDriver")
    options = Options()
    options.add_argument("--headless")
    return webdriver.Chrome(options=options)

def extract_place_details(driver):
    try:
        name = driver.find_element(By.CLASS_NAME, "DUwDvf").text.strip()
    except:
        name = "N/A"
    try:
        address = driver.find_element(By.XPATH, '//button[@data-item-id="address"]//div[contains(@class, "Io6YTe")]').text.strip()
    except:
        address = 'N/A'
    try:
        phone = driver.find_element(By.XPATH, '//button[contains(@data-item-id, "phone")]//div[contains(@class, "Io6YTe")]').text.strip()
    except:
        phone = 'N/A'
    return name, address, phone

def scrape_maps(query="company", max_results=25):
    logging.info(f"Starting scrape for query: {query} | Max results: {max_results}")
    driver = init_driver()
    driver.get(f"https://www.google.com/maps/search/{query}/@28.6105798,77.3574076,14z/data=!3m1!4b1?entry=ttu")
    time.sleep(5)

    data = []
    seen = set()
    index = 0

    scroll_div = driver.find_element(By.XPATH, '//div[@role="feed"]')

    while len(data) < max_results:
        results = driver.find_elements(By.CLASS_NAME, "hfpxzc")

        if index >= len(results):
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scroll_div)
            time.sleep(2)
            continue

        try:
            elem = results[index]
            driver.execute_script("arguments[0].scrollIntoView();", elem)
            time.sleep(1)
            ActionChains(driver).key_down(Keys.CONTROL).click(elem).key_up(Keys.CONTROL).perform()
            time.sleep(3)

            driver.switch_to.window(driver.window_handles[1])
            time.sleep(2)

            name, address, phone = extract_place_details(driver)

            if name in seen:
                logging.info(f"Duplicate found: {name}, skipping")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                index += 1
                continue

            seen.add(name)
            data.append({"Name": name, "Address": address, "Phone": phone})
            

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(1)

        except Exception as e:
            logging.error(f"Error on index {index}: {e}")
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            time.sleep(1)

        index += 1
    
    df = pd.DataFrame(data)
    df.to_csv("frisson_task.csv", index=False)
    logging.info(f"Scrapping done")
    driver.quit()
    return df
