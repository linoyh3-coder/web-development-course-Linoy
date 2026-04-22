import unittest
import uuid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class AppTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 8)
        self.base_url = "http://localhost:5000"

    def tearDown(self):
        self.driver.quit()

    # -------------------------------------------------
    # helpers
    # -------------------------------------------------
    def add_student(self, name, age="22"):
        self.driver.find_element(By.ID, "nameBox").send_keys(name)
        self.driver.find_element(By.ID, "ageBox").send_keys(age)
        self.driver.find_element(By.ID, "btAdd").click()

        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, f"//td[text()='{name}']")
            )
        )

    def get_row(self, name):
        return (By.XPATH, f"//tr[td[text()='{name}']]")

    def get_delete_button(self, name):
        return (By.XPATH, f"//tr[td[text()='{name}']]//button[contains(@class,'delete-btn')]")

    def get_edit_button(self, name):
        return (By.XPATH, f"//tr[td[text()='{name}']]//button[contains(@class,'edit-btn')]")

    def safe_click(self, element):

        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        self.wait.until(EC.element_to_be_clickable(element))
        try:
            element.click()
        except:
            self.driver.execute_script("arguments[0].click();", element)

    # -------------------------------------------------
    # 1. דף ראשי
    # -------------------------------------------------
    def test_homepage(self):
        self.driver.get(self.base_url)

        self.assertIn("Students App", self.driver.title)

        h1 = self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        self.assertEqual(h1.text, "Students Application")

    # -------------------------------------------------
    # 2. הוספה
    # -------------------------------------------------
    def test_add_student(self):
        self.driver.get(self.base_url)

        name = f"Student_{uuid.uuid4()}"
        self.add_student(name)

        tbody = self.driver.find_element(By.ID, "tbody")
        self.assertIn(name, tbody.text)

    # -------------------------------------------------
    # 3. הוספה לא חוקית (בדיקת alert)
    # -------------------------------------------------
    def test_add_invalid_student(self):
        self.driver.get(self.base_url)

        self.driver.find_element(By.ID, "btAdd").click()

        alert = self.wait.until(EC.alert_is_present())
        self.assertIn("Please enter", alert.text)
        alert.accept()

    # -------------------------------------------------
    # 4. עדכון תלמיד
    # -------------------------------------------------
    def test_update_student(self):
        self.driver.get(self.base_url)

        original_name = f"Old_{uuid.uuid4()}"
        self.add_student(original_name)

        # edit על השורה הנכונה
        edit_btn = self.wait.until(
            EC.presence_of_element_located(self.get_edit_button(original_name))
        )
        self.safe_click(edit_btn)

        updated_name = f"Updated_{uuid.uuid4()}"

        name_box = self.driver.find_element(By.ID, "nameBox")
        name_box.clear()
        name_box.send_keys(updated_name)

        age_box = self.driver.find_element(By.ID, "ageBox")
        age_box.clear()
        age_box.send_keys("30")

        self.driver.find_element(By.ID, "btUpdate").click()

        # confirm alert
        alert = self.wait.until(EC.alert_is_present())
        alert.accept()

        # בדיקה על אותה שורה בלבד
        updated_row = self.wait.until(
            EC.presence_of_element_located(self.get_row(updated_name))
        )

        self.assertIn(updated_name, updated_row.text)
        self.assertNotIn(original_name, updated_row.text)

    # -------------------------------------------------
    # 5. מחיקת תלמיד
    # -------------------------------------------------
    def test_delete_student(self):
        self.driver.get(self.base_url)

        name = f"Delete_{uuid.uuid4()}"
        self.add_student(name)

        delete_btn = self.wait.until(
            EC.presence_of_element_located(self.get_delete_button(name))
        )

        self.safe_click(delete_btn)

        # confirm
        alert = self.wait.until(EC.alert_is_present())
        alert.accept()

        # לוודא שהשורה נעלמה
        self.wait.until(
            EC.invisibility_of_element_located(self.get_row(name))
        )

        tbody = self.driver.find_element(By.ID, "tbody")
        self.assertNotIn(name, tbody.text)


if __name__ == "__main__":
    unittest.main()
