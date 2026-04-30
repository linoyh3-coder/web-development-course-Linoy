from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()
driver.maximize_window()

driver.get("https://www.asos.com")

time.sleep(2)
print("Site opened ✔")

wait = WebDriverWait(driver, 20)

# 🔍 חיפוש
search = wait.until(
    EC.presence_of_element_located((By.NAME, "q"))
)

time.sleep(1)
print("Search box found ✔")

search.click()
time.sleep(1)

search.send_keys("dress")
time.sleep(1)
print("Typed product ✔")

search.send_keys(Keys.ENTER)
time.sleep(2)
print("Search submitted ✔")

# ⏳ חיכוי לטעינת תוצאות
wait.until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a"))
)

time.sleep(2)
print("Results loaded ✔")

results = driver.find_elements(By.CSS_SELECTOR, "a")

print("Results found:", len(results))

time.sleep(2)

assert len(results) > 10
print("Search test passed ✔")

time.sleep(3)

driver.quit()