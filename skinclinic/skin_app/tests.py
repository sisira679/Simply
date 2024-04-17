# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import unittest

# class LoginTest(unittest.TestCase):
#     def setUp(self):
#         self.driver = webdriver.Chrome()  # Initialize your WebDriver
#         self.driver.get("http://127.0.0.1:3000/login.html")  # Replace with your login page URL

#     def test_valid_login(self):
#         username = "Aswin20"
#         password = "Aswin@2000"

#         # Find username and password fields
#         username_field = WebDriverWait(self.driver, 30).until(
#             EC.presence_of_element_located((By.ID, "username"))  # Update with your username field locator
#         )
#         password_field = WebDriverWait(self.driver, 30).until(
#             EC.presence_of_element_located((By.ID, "password"))  # Update with your password field locator
#         )

#         # Enter username and password
#         username_field.send_keys(username)
#         password_field.send_keys(password)

#         # Trigger change events after entering username and password
#         self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", username_field)
#         self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", password_field)

#         # Find and click the login button
#         login_button = WebDriverWait(self.driver, 60).until(
#             EC.element_to_be_clickable((By.ID, "login-button"))  # Update with your login button locator
#         )
#         login_button.click()

#         # Add assertions to verify successful login
#         expected_url = "/doctordashboard.html"
#         self.assertIn(expected_url, self.driver.current_url)  # Update with assertion to check if expected_url is present in the current URL
#     def tearDown(self):
#         self.driver.quit()
# if __name__ == "__main__":
#     unittest.main()

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import unittest

# class ChangePasswordTest(unittest.TestCase):
#     def setUp(self):
#         self.driver = webdriver.Chrome()
#         self.driver.get("http://127.0.0.1:3000/login.html")  # Replace with your login page URL

#     def test_change_password(self):
#         # Login
#         username = "Aswin20"
#         password = "234"

#         username_field = WebDriverWait(self.driver, 30).until(
#             EC.presence_of_element_located((By.ID, "username"))
#         )
#         password_field = WebDriverWait(self.driver, 30).until(
#             EC.presence_of_element_located((By.ID, "password"))
#         )

#         username_field.send_keys(username)
#         password_field.send_keys(password)

#         login_button = WebDriverWait(self.driver, 60).until(
#             EC.element_to_be_clickable((By.ID, "login-button"))
#         )
#         login_button.click()

#         # Navigate to Change Password
#         welcome_message = WebDriverWait(self.driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "welcomeMessage"))
#         )
#         welcome_message.click()

#         change_password_link = WebDriverWait(self.driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "changePasswordLink"))
#         )
#         change_password_link.click()

#         # Change Password form
#         old_password_field = WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.ID, "old_password"))
#         )
#         new_password1_field = WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.ID, "new_password1"))
#         )
#         new_password2_field = WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.ID, "new_password2"))
#         )

#         # Enter old and new passwords
#         old_password_field.send_keys("234")
#         new_password1_field.send_keys("Aswin@2000")
#         new_password2_field.send_keys("Aswin@2000")

#         # Submit the form
#         submit_button = WebDriverWait(self.driver, 10).until(
#             EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Change Password']"))
#         )
#         submit_button.click()

#         # Assert if redirected to the login page or any other expected behavior after changing password

#         # Log in again with the updated credentials
#         self.driver.get("http://127.0.0.1:3000/login.html")  # Redirect to login page
#         username_field = WebDriverWait(self.driver, 30).until(
#             EC.presence_of_element_located((By.ID, "username"))
#         )
#         password_field = WebDriverWait(self.driver, 30).until(
#             EC.presence_of_element_located((By.ID, "password"))
#         )
#         username_field.send_keys(username)
#         password_field.send_keys("Aswin@2000")  # Use the updated password

#         login_button = WebDriverWait(self.driver, 60).until(
#             EC.element_to_be_clickable((By.ID, "login-button"))
#         )
#         login_button.click()

#         # Add assertions to verify successful login after changing the password

#     def tearDown(self):
#         self.driver.quit()

# if __name__ == "__main__":
#     unittest.main()



# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import unittest
# import pyautogui
# import time

# class SchedulingTest(unittest.TestCase):
#     def setUp(self):
#         self.driver = webdriver.Chrome()
#         self.driver.get("http://127.0.0.1:3000/login.html")  # Replace with your login page URL

#     def test_schedule_appointment(self):
#         # Login
#         username = "Aswin20"
#         password = "Aswin@2000"

#         username_field = WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.ID, "username"))
#         )
#         password_field = WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.ID, "password"))
#         )

#         username_field.send_keys(username)
#         password_field.send_keys(password)

#         login_button = WebDriverWait(self.driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "login-button"))
#         )
#         login_button.click()

#         # Verify redirection to doctordashboard.html
#         expected_dashboard_url = "http://127.0.0.1:3000/doctordashboard.html"
#         WebDriverWait(self.driver, 10).until(
#             EC.url_to_be(expected_dashboard_url),
#             f"Expected URL to be {expected_dashboard_url}, but got {self.driver.current_url}"
#         )

#         # Navigate to scheduling page
#         scheduling_link = WebDriverWait(self.driver, 10).until(
#             EC.element_to_be_clickable((By.XPATH, "//li[@id='Scheduling']/a"))
#         )
#         scheduling_link.click()

#         # Verify redirection to scheduling.html
#         expected_scheduling_url = "http://127.0.0.1:3000/scheduling.html"
#         WebDriverWait(self.driver, 10).until(
#             EC.url_to_be(expected_scheduling_url),
#             f"Expected URL to be {expected_scheduling_url}, but got {self.driver.current_url}"
#         )

#         # Click the date input to open the date picker
#         date_input = WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.ID, "id_date"))
#         )
#         date_input.click()

#         # Replace the coordinates with the actual coordinates of the date you want to select
#         target_date_x, target_date_y = 400, 200

#         # Move the mouse to the target date and click
#         pyautogui.moveTo(target_date_x, target_date_y)
#         pyautogui.click()

#         # Select timeslot
#         timeslot_select = WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.ID, "time_slot"))
#         )
#         timeslot_option = WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.ID, "option_9"))  # Replace with the corresponding option ID for your desired timeslot
#         )
#         timeslot_option.click()

#         # Click the "Add Schedule" button
#         add_schedule_button = WebDriverWait(self.driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "add_schedule"))
#         )
#         add_schedule_button.click()

#         # Add a short delay to ensure the success message has time to appear
#         time.sleep(2)

#         # Verify success message or any other expected behavior after adding a schedule
#         success_message = WebDriverWait(self.driver, 10).until(
#             EC.visibility_of_element_located((By.XPATH, "//ul[@class='messages']/li[@class='success']")),
#             "Success message not found after adding a schedule"
#         )
#         self.assertEqual(success_message.text, "Schedule added successfully.")

#     def tearDown(self):
#         self.driver.quit()

# if __name__ == "__main__":
#     unittest.main()



# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
# import unittest

# class SchedulingTest(unittest.TestCase):
#     def setUp(self):
#         self.driver = webdriver.Chrome()
#         self.driver.get("http://127.0.0.1:3000/login.html")  # Replace with your login page URL

#     def test_schedule_appointment(self):
#         # Login
#         username = "Aswin20"
#         password = "Aswin@2000"

#         username_field = WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.ID, "username"))
#         )
#         password_field = WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.ID, "password"))
#         )

#         username_field.send_keys(username)
#         password_field.send_keys(password)

#         login_button = WebDriverWait(self.driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "login-button"))
#         )
#         login_button.click()

#         # Verify redirection to doctordashboard.html
#         expected_dashboard_url = "http://127.0.0.1:3000/doctordashboard.html"
#         WebDriverWait(self.driver, 10).until(
#             EC.url_to_be(expected_dashboard_url),
#             f"Expected URL to be {expected_dashboard_url}, but got {self.driver.current_url}"
#         )

#         # Navigate to scheduling page
#         scheduling_link = WebDriverWait(self.driver, 10).until(
#             EC.element_to_be_clickable((By.XPATH, "//li[@id='Scheduling']/a"))
#         )
#         scheduling_link.click()

#         # Verify redirection to scheduling.html
#         expected_scheduling_url = "http://127.0.0.1:3000/scheduling.html"
#         WebDriverWait(self.driver, 10).until(
#             EC.url_to_be(expected_scheduling_url),
#             f"Expected URL to be {expected_scheduling_url}, but got {self.driver.current_url}"
#         )

#         # Select date
#         date_input = WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.ID, "id_date"))
#         )
#         date_input.send_keys("2023-12-06")  # Replace with your desired date

#         # Select timeslot
#         timeslot_select = WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.ID, "time_slot"))
#         )
#         timeslot_option = WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.ID, "option_9"))  # Replace with the corresponding option ID for your desired timeslot
#         )
#         timeslot_option.click()

#         # Click the "Add Schedule" button
#         add_schedule_button = WebDriverWait(self.driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "add_schedule"))
#         )
#         add_schedule_button.click()

#         # Verify success message or any other expected behavior after adding a schedule
#         success_message = WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, "//ul[@class='messages']/li[@class='success']")),
#             "Success message not found after adding a schedule"
#         )
#         self.assertEqual(success_message.text, "Schedule added successfully.")

#     def tearDown(self):
#         self.driver.quit()

# if __name__ == "__main__":
#     unittest.main()



# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import unittest
# import time

# class DoctorManagementTest(unittest.TestCase):
#     def setUp(self):
#         self.driver = webdriver.Chrome()
#         self.driver.get("http://127.0.0.1:3000/login.html")

#     def test_doctor_management(self):
#         # Login
#         username = "admin"
#         password = "123"

#         username_field = WebDriverWait(self.driver, 30).until(
#             EC.presence_of_element_located((By.ID, "username"))
#         )
#         password_field = WebDriverWait(self.driver, 30).until(
#             EC.presence_of_element_located((By.ID, "password"))
#         )

#         username_field.send_keys(username)
#         password_field.send_keys(password)

#         self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", username_field)
#         self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", password_field)

#         login_button = WebDriverWait(self.driver, 60).until(
#             EC.element_to_be_clickable((By.ID, "login-button"))
#         )
#         login_button.click()

#         expected_url = "/indexadmin.html"
#         self.assertIn(expected_url, self.driver.current_url)

#         # Navigate to doctor list
#         doctor_list_link = WebDriverWait(self.driver, 10).until(
#             EC.element_to_be_clickable((By.XPATH, "//li[@id='doctor_button']/a"))
#         )
#         doctor_list_link.click()

#         # Add a doctor
#         add_doctor_button = WebDriverWait(self.driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "add-buttons"))
#         )
#         add_doctor_button.click()

#         # Fill in the form
#         self.driver.find_element(By.ID, "first-name-input").send_keys("Karthika")
#         self.driver.find_element(By.ID, "last_name").send_keys("S")
#         self.driver.find_element(By.ID, "username-input").send_keys("Karthika20")
#         self.driver.find_element(By.ID, "email-input").send_keys("karthika2000@gmail.com")
#         self.driver.find_element(By.NAME, "password").send_keys("Karthika@2000")
#         self.driver.find_element(By.NAME, "confirm_password").send_keys("Karthika@2000")

#         gender_female = self.driver.find_element(By.ID, "female")
#         self.driver.execute_script("arguments[0].click();", gender_female)

#         specialization_dropdown = self.driver.find_element(By.ID, "specializations")
#         specialization_dropdown.send_keys("Cosmetic Dermatology")

#         # Click the Create Doctor button
#         create_doctor_button = WebDriverWait(self.driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "create-doctor"))
#         )
#         create_doctor_button.click()

#         # Wait for the doctor list to update
#         time.sleep(2)

#         # Delete a doctor
#         delete_button = WebDriverWait(self.driver, 10).until(
#             EC.element_to_be_clickable((By.XPATH, "//a[@class='delete-button']"))
#         )
#         delete_button.click()

#         # Confirm the deletion
#         confirm_button = WebDriverWait(self.driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "confirm-button"))
#         )
#         confirm_button.click()

#         # Wait for the doctor list to update
#         time.sleep(2)

#     def tearDown(self):
#         self.driver.quit()

# if __name__ == "__main__":
#     unittest.main()



