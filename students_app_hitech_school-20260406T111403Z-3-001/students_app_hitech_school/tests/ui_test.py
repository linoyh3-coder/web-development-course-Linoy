import unittest
import uuid  # משמש ליצירת מזהה ייחודי (כדי שלא יהיו כפילויות)
from selenium import webdriver  # שליטה בדפדפן
from selenium.webdriver.common.by import By  # איך למצוא אלמנטים (ID, XPATH וכו')
from selenium.webdriver.support.ui import WebDriverWait  # המתנה חכמה
from selenium.webdriver.support import expected_conditions as EC  # תנאים להמתנה


class AppTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()  # פתיחת דפדפן כרום
        self.wait = WebDriverWait(self.driver, 8)  # המתנה עד 8 שניות לאלמנטים
        self.base_url = "http://localhost:5000"  # כתובת האפליקציה

    def tearDown(self):
        self.driver.quit()  # סגירת הדפדפן אחרי כל טסט

    # -------------------------------------------------
    # helpers (פונקציות עזר)
    # -------------------------------------------------
    def add_student(self, name, age="22"):
        # הכנסת שם
        self.driver.find_element(By.ID, "nameBox").send_keys(name)
        # הכנסת גיל
        self.driver.find_element(By.ID, "ageBox").send_keys(age)
        # לחיצה על כפתור Add
        self.driver.find_element(By.ID, "btAdd").click()

        # המתנה עד שהתלמיד מופיע בטבלה
        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, f"//td[text()='{name}']")
            )
        )

    def get_row(self, name):
        # מחזיר locator של שורה בטבלה לפי שם תלמיד
        return (By.XPATH, f"//tr[td[text()='{name}']]")

    def get_delete_button(self, name):
        # מחזיר locator של כפתור מחיקה בשורה של תלמיד
        return (By.XPATH, f"//tr[td[text()='{name}']]//button[contains(@class,'delete-btn')]")

    def get_edit_button(self, name):
        # מחזיר locator של כפתור עריכה בשורה של תלמיד
        return (By.XPATH, f"//tr[td[text()='{name}']]//button[contains(@class,'edit-btn')]")

    def safe_click(self, element):
        # גלילה לאלמנט (כדי שיהיה באמצע המסך)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)

        # המתנה עד שהאלמנט קליקבילי
        self.wait.until(EC.element_to_be_clickable(element))  #  עדיף להשתמש ב-locator

        try:
            element.click()  # ניסיון קליק רגיל
        except:
            # אם לא הצליח (למשל מכוסה) - קליק דרך JavaScript
            self.driver.execute_script("arguments[0].click();", element)

    # -------------------------------------------------
    # 1. דף ראשי
    # -------------------------------------------------
    def test_homepage(self):
        self.driver.get(self.base_url)  # פתיחת האתר

        # בדיקה שכותרת הדף מכילה טקסט מסוים
        self.assertIn("Students App", self.driver.title)

        # המתנה עד ש־h1 מופיע
        h1 = self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )

        # בדיקה שהתוכן של h1 נכון
        self.assertEqual(h1.text, "Students Application")

    # -------------------------------------------------
    # 2. הוספה
    # -------------------------------------------------
    def test_add_student(self):
        self.driver.get(self.base_url)

        # יצירת שם ייחודי
        name = f"Student_{uuid.uuid4()}"

        # הוספת תלמיד
        self.add_student(name)

        # מציאת גוף הטבלה
        tbody = self.driver.find_element(By.ID, "tbody")

        # בדיקה שהשם מופיע בטבלה
        self.assertIn(name, tbody.text)

    # -------------------------------------------------
    # 3. הוספה לא חוקית (בדיקת alert)
    # -------------------------------------------------
    def test_add_invalid_student(self):
        self.driver.get(self.base_url)

        # לחיצה על Add בלי למלא שדות
        self.driver.find_element(By.ID, "btAdd").click()

        # המתנה להופעת alert
        alert = self.wait.until(EC.alert_is_present())

        # בדיקה שהטקסט של ההודעה תקין
        self.assertIn("Please enter", alert.text)

        # אישור ההודעה
        alert.accept()

    # -------------------------------------------------
    # 4. עדכון תלמיד
    # -------------------------------------------------
    def test_update_student(self):
        self.driver.get(self.base_url)

        # יצירת תלמיד מקורי
        original_name = f"Old_{uuid.uuid4()}"
        self.add_student(original_name)

        # מציאת כפתור edit בשורה המתאימה
        edit_btn = self.wait.until(
            EC.presence_of_element_located(self.get_edit_button(original_name))
        )

        # לחיצה על edit
        self.safe_click(edit_btn)

        # יצירת שם חדש
        updated_name = f"Updated_{uuid.uuid4()}"

        # עדכון שם
        name_box = self.driver.find_element(By.ID, "nameBox")
        name_box.clear()  # ניקוי השדה
        name_box.send_keys(updated_name)  # הכנסת שם חדש

        # עדכון גיל
        age_box = self.driver.find_element(By.ID, "ageBox")
        age_box.clear()
        age_box.send_keys("30")

        # לחיצה על Update
        self.driver.find_element(By.ID, "btUpdate").click()

        # אישור alert
        alert = self.wait.until(EC.alert_is_present())
        alert.accept()

        # המתנה עד שהשורה עם השם החדש מופיעה
        updated_row = self.wait.until(
            EC.presence_of_element_located(self.get_row(updated_name))
        )

        # בדיקה שהשם החדש מופיע
        self.assertIn(updated_name, updated_row.text)

        # בדיקה שהשם הישן לא מופיע
        self.assertNotIn(original_name, updated_row.text)

    # -------------------------------------------------
    # 5. מחיקת תלמיד
    # -------------------------------------------------
    def test_delete_student(self):
        self.driver.get(self.base_url)

        # יצירת תלמיד
        name = f"Delete_{uuid.uuid4()}"
        self.add_student(name)

        # מציאת כפתור delete
        delete_btn = self.wait.until(
            EC.presence_of_element_located(self.get_delete_button(name))
        )

        # לחיצה על delete
        self.safe_click(delete_btn)

        # אישור alert
        alert = self.wait.until(EC.alert_is_present())
        alert.accept()

        # המתנה עד שהשורה נעלמת מהטבלה
        self.wait.until(
            EC.invisibility_of_element_located(self.get_row(name))
        )

        # בדיקה שהשם כבר לא קיים בטבלה
        tbody = self.driver.find_element(By.ID, "tbody")
        self.assertNotIn(name, tbody.text)


if __name__ == "__main__":
    unittest.main()  # הרצת כל הטסטים