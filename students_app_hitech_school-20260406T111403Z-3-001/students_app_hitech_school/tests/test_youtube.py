from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()
driver.maximize_window()
wait = WebDriverWait(driver, 15)

driver.get("https://www.youtube.com")

try:
    # שדה חיפוש
    search_box = wait.until(
        EC.element_to_be_clickable((By.NAME, "search_query"))
    )
    search_box.click()
    search_box.send_keys("selenium tutorial python")
    search_box.send_keys(Keys.ENTER)

    # לחכות לתוצאות
    time.sleep(3)

    # ללחוץ על הסרטון הראשון
    first_video = wait.until(
        EC.element_to_be_clickable((By.ID, "video-title"))
    )
    first_video.click()

    print("נפתח סרטון בהצלחה")

except Exception as e:
    print("שגיאה:", e)

time.sleep(10)
driver.quit()