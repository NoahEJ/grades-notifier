import json
import random
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import re as re
import time
import smtplib
from email.message import EmailMessage
from datetime import datetime

# Configure global variables
with open('project_config.json') as config_file:
    config = json.load(config_file)

sender_email = config['user_info']['email']
sender_password = config['user_info']['password']
sender_name = config['user_info']['name']
sender_server = config['user_info']['smtp_server']
sender_port = config['user_info']['port']

my_email = config['recipients']['myself']
other_recipients = config['recipients']['others']

authentication_url = config['site_info']['authentication_page_url']
grades_url = config['site_info']['grades_page_url']
auth_username = config['site_info']['username']
auth_password = config['site_info']['password']

driverPath = config['path_to_driver']


# Functions to send different emails
def send_error_email(e):

    recipient_email = my_email
    msg = EmailMessage()
    msg.set_content("An error has occured.\n" + str(e))

    msg["Subject"] = "Error occurred"
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = recipient_email

    # Connect to the email server and send the email
    with smtplib.SMTP_SSL(sender_server, sender_port) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

    print("Email sent successfully!")

def send_alive_email():

    recipient_email = my_email
    msg = EmailMessage()
    msg.set_content("Grades checker is still alive!")

    msg["Subject"] = "Still alive!"
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = recipient_email

    # Connect to the email server and send the email
    with smtplib.SMTP_SSL(sender_server, sender_port) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

    print("Email sent successfully!")

def send_personal_email(course, grade, mark):

    recipient_email = my_email
    msg = EmailMessage()
    msg.set_content(f"Course: {course}\nMark: {mark}\nGrade: {grade}")

    msg["Subject"] = course + " GRADE RELEASED"
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = recipient_email

    # Connect to the email server and send the email
    with smtplib.SMTP_SSL(sender_server, sender_port) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

    print("Email sent successfully!")

def send_average_email(averages):
        recipient_email = my_email
        bcc_recipients = other_recipients 
        msg = EmailMessage()
        content = ""
        i = 0
        
        # For winter session, start at i=6
        for course in averages:
            i += 1
            if i > 6:
                content = content + "\n" + str(course) + ": " + averages[course]
        msg.set_content(content)

        msg["Subject"] = "COURSE AVERAGES RELEASED!"
        msg["From"] = f"{sender_name} <{sender_email}>"
        msg["To"] = recipient_email
        msg["Bcc"] = ", ".join(bcc_recipients)

        # Connect to the email server and send the email
        with smtplib.SMTP_SSL(sender_server, sender_port) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print("Email sent successfully!")

def send_friends_emails(course):
    recipient_email = my_email
    bcc_recipients = other_recipients

    msg = EmailMessage()
    msg.set_content(course + " final grades have been released!")

    msg["Subject"] = course + " GRADE RELEASED"
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = recipient_email
    msg["Bcc"] = ", ".join(bcc_recipients)

    # Connect to the email server and send the email
    with smtplib.SMTP_SSL(sender_server, sender_port) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

    print("Email sent successfully!")


def authenticate(driver):
    driver.get(authentication_url)
    email = driver.find_element(By.ID, "username")
    email.send_keys(auth_username)
    password = driver.find_element(By.ID, "password")
    password.send_keys(auth_password)
    time.sleep(1)
    password.send_keys(Keys.RETURN)
    time.sleep(2)

driver = webdriver.Chrome(driverPath)

# Log in through the authentication screen
authenticate(driver)
driver.get(grades_url)
time.sleep(3)
mark_dict = {}
average_dict = {}
num_checks_today = 0
date_today = datetime.now().date()



while(True):
    try:
        driver.refresh()
        # print("REFRESHED")
        time.sleep(6)
        if (driver.current_url != grades_url):
            authenticate(driver)
            driver.get(grades_url)
            time.sleep(3)
        # print("PROCESSING")
        page = driver.page_source
        linkedin_soup = bs(page.encode("utf-8"), "html")
        linkedin_soup.prettify()
        courses = linkedin_soup.findAll("tr",{"class":"courses"})

        # iterate through each course element and extract the course codes, grades, and course averages
        for course in courses:
            course_str = str(course)
            course_soup = bs(course_str, "html.parser")
            course_code = course_soup.find_all("td")[0].get_text()
            course_mark_dirty = str(course_soup.find_all("td", {"class": "course-mark"})[0])
            pattern = r"[^\d\*]"
            course_mark = re.sub(pattern, "", course_mark_dirty)
            course_grade_dirty = str(course_soup.find_all("td", {"class": "course-grade"})[0])
            course_grade = course_grade_dirty.replace('<td class="course-grade">', '').replace('</td>', '')
            course_average_dirty = str(course_soup.find_all("td", {"class": "course-average"})[0])
            course_average = course_average_dirty.replace('<td class="course-average">', '').replace('</td>', '')

            if (course_code in mark_dict):
                old_mark = mark_dict.get(course_code)
                if old_mark != course_mark:
                    send_personal_email(course_code, course_grade, course_mark)
                    send_friends_emails(course_code)
            mark_dict[course_code] = course_mark

            averages_changed = False
            if (course_code in average_dict):
                old_average = average_dict.get(course_code)
                if old_average != course_average:
                    averages_changed = True
            average_dict[course_code] = course_average
        if averages_changed:
            send_average_email(average_dict)
    
    except Exception as e: 
        print(e)
        send_error_email(e)
        sys.exit()

    current_time = datetime.now().time()
    date_today = datetime.now().date()
    
# Change refresh frequency based on time of day and day of week
    if current_time >= datetime.strptime("08:55", "%H:%M").time() and current_time <= datetime.strptime("08:57", "%H:%M").time():
        send_alive_email()
    elif current_time >= datetime.strptime("14:00", "%H:%M").time() and current_time <= datetime.strptime("14:02", "%H:%M").time():
        send_alive_email()

    random_int = random.randint(-7, 7)
    if date_today.weekday() >= 5:
        refresh_time = 60*60*6 + random_int
    elif current_time >= datetime.strptime("19:00", "%H:%M").time() or current_time <= datetime.strptime("08:30", "%H:%M").time():
        refresh_time = 60*60*4 + random_int
    else:
        refresh_time = 60*60*2 + random_int
    

    if (date_today != datetime.now().date()):
        date_today = datetime.now().date()
        num_checks_today = 0
    
    num_checks_today += 1

    print("Date: " + str(date_today) + ". Time: " + str(current_time) + ". Checked grades today: " + str(num_checks_today) + " times.")
    time.sleep(refresh_time)