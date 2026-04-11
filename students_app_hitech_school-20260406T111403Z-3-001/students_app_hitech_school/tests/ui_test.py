import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "http://localhost:5000"


# -------------------------------------------------
# Fixture של driver
# -------------------------------------------------
@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(3)
    yield driver
    driver.quit()


# -------------------------------------------------
# helper wait
# -------------------------------------------------
def wait_for(driver, by, value):
    return WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((by, value))
    )


# -------------------------------------------------
# 1. דף ראשי
# -------------------------------------------------
def test_homepage(driver):
    driver.get(BASE_URL)

    assert "Students App" in driver.title

    h1 = wait_for(driver, By.TAG_NAME, "h1")
    assert h1.text == "Students Application"


# -------------------------------------------------
# 2. הוספת תלמיד תקין
# -------------------------------------------------
def test_add_student(driver):
    driver.get(BASE_URL)

    wait_for(driver, By.ID, "nameBox").send_keys("David")
    driver.find_element(By.ID, "ageBox").send_keys("22")
    driver.find_element(By.ID, "btAdd").click()

    assert "David" in driver.page_source


# -------------------------------------------------
# 3. הוספה לא חוקית (בדיקת alert)
# -------------------------------------------------
def test_add_invalid_student(driver):
    driver.get(BASE_URL)

    driver.find_element(By.ID, "btAdd").click()

    alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
    text = alert.text
    alert.accept()

    assert "Please enter" in text


# -------------------------------------------------
# 4. עדכון תלמיד
# -------------------------------------------------
def test_update_student(driver):
    driver.get(BASE_URL)

    # יצירה
    driver.find_element(By.ID, "idBox").send_keys("1")
    driver.find_element(By.ID, "nameBox").send_keys("Old Name")
    driver.find_element(By.ID, "ageBox").send_keys("20")
    driver.find_element(By.ID, "btAdd").click()

    # וידוא שהוא קיים
    assert "Old Name" in driver.page_source

    # עדכון ישיר (בלי edit)
    driver.find_element(By.ID, "idBox").clear()
    driver.find_element(By.ID, "idBox").send_keys("1")

    driver.find_element(By.ID, "nameBox").clear()
    driver.find_element(By.ID, "nameBox").send_keys("Updated Name")

    driver.find_element(By.ID, "ageBox").clear()
    driver.find_element(By.ID, "ageBox").send_keys("30")

    driver.find_element(By.ID, "btUpdate").click()

    # בדיקה
    assert "Updated Name" in driver.page_source

# -------------------------------------------------
# 5. מחיקת תלמיד
# -------------------------------------------------
def test_delete_student(driver):
    driver.get(BASE_URL)

    # מוסיפים תלמיד כדי שיהיה מה למחוק
    driver.find_element(By.ID, "nameBox").send_keys("ToDelete")
    driver.find_element(By.ID, "ageBox").send_keys("25")
    driver.find_element(By.ID, "btAdd").click()

    delete_btn = wait_for(driver, By.CSS_SELECTOR, ".delete-btn")
    delete_btn.click()

    alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
    alert.accept()

    # בדיקה שהתלמיד לא קיים יותר
    assert "ToDelete" not in driver.page_source