# scraper.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

def run_scraper(query="company", max_results=25):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    driver.get(f"https://www.google.com/maps/search/{query}/@28.6105798,77.3574076,14z/data=!3m1!4b1?entry=ttu")
    time.sleep(5)

    data = []
    seen = set()
    index = 0

    scrollable_div = driver.find_element(By.XPATH, '//div[@role="feed"]')

    while len(data) < max_results:
        elems = driver.find_elements(By.CLASS_NAME, "hfpxzc")

        if index >= len(elems):
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
            time.sleep(2)
            continue

        try:
            elem = elems[index]
            driver.execute_script("arguments[0].scrollIntoView();", elem)
            time.sleep(1)
            ActionChains(driver).key_down(Keys.CONTROL).click(elem).key_up(Keys.CONTROL).perform()
            time.sleep(3)

            driver.switch_to.window(driver.window_handles[1])
            time.sleep(2)

            name = driver.find_element(By.CLASS_NAME, "DUwDvf").text.strip()
            if name in seen:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(1)
                index += 1
                continue

            seen.add(name)

            try:
                address = driver.find_element(By.XPATH, '//button[@data-item-id="address"]//div[contains(@class, "Io6YTe")]').text.strip()
            except:
                address = 'N/A'
            try:
                phone = driver.find_element(By.XPATH, '//button[contains(@data-item-id, "phone")]//div[contains(@class, "Io6YTe")]').text.strip()
            except:
                phone = 'N/A'

            data.append({"Name": name, "Address": address, "Phone": phone})

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(1)

        except Exception as e:
            print(f"Error on index {index}: {e}")
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            time.sleep(1)

        index += 1

    df = pd.DataFrame(data)
    df.to_csv("frisson_task.csv", index=False)
    driver.quit()
    return df
