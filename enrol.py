from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
import re

department_name = 'Department name"
class_number = "course number and title"
lec_section = "lecture section you want"
dis_section = "discussion section; can leave as empty."
grade_dict = {
    "Letter":0,
    "Passed":1
}
grade_type = "Letter or passed" #Passed
first_search = True
check_freq = 'frequency you want to check the website' #in seconds
candidate_courses = []

driver = webdriver.Firefox()
driver.get("http://my.ucla.edu/")

sign_in_button = driver.find_element(By.XPATH,".//*[@id='ctl00_signInLink']")
sign_in_button.click()


element = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID,"logon")))
element.send_keys("Your ucla logon id")

element = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID,"pass")))
element.send_keys("your password")

element = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.NAME,"_eventId_proceed")))
element.click()

driver.get("https://be.my.ucla.edu/ClassPlanner/ClassPlan.aspx")


element = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID,"ctl00_MainContent_cs_searchBy")))
sel = Select(element)
sel.select_by_visible_text("Subject Area")

while True:
    search_div = WebDriverWait(driver,10,poll_frequency=1).until(EC.presence_of_element_located((By.XPATH, "//div[@id='panelSearch']//div[contains(@class,'searchFields panel-10')]")))
    if search_div != None:
        if first_search:
            department = WebDriverWait(driver,10,poll_frequency=1).until(EC.visibility_of_element_located((By.ID,'searchTier0')))
            department.clear()
            department.send_keys(department_name)
            auto_complete_list_li = WebDriverWait(driver,10,poll_frequency=1).until(EC.visibility_of_all_elements_located((By.XPATH,"//ul[contains(@class,'ui-autocomplete')]//li")))
            for li in auto_complete_list_li:
                li.click()

            time.sleep(3)
            course_listing = WebDriverWait(driver,10,poll_frequency=1).until(EC.visibility_of_element_located((By.ID,'searchTier1')))
            course_listing.send_keys(class_number)
            auto_complete_list_li = WebDriverWait(driver,10,poll_frequency=1).until(EC.visibility_of_all_elements_located((By.XPATH,"//ul[contains(@class,'ui-autocomplete')]//li")))
            for li in auto_complete_list_li:
                print(li.text)
                li.click()

        go_button = WebDriverWait(driver,10,poll_frequency=1).until(EC.element_to_be_clickable((By.XPATH,"//div[@class='goPanel']//input")))
        go_button.click()
        first_search = False

        search_list = WebDriverWait(driver,10,poll_frequency=1).until(EC.visibility_of_element_located((By.XPATH,"//div[contains(@class,'ClassSearchList')]")))
        courses = search_list.find_elements_by_css_selector("div[id^='data_course']")
        for course in courses:
            checkbox = course.find_element(By.CLASS_NAME,'span1').find_element_by_tag_name("input")
            if len(re.findall(lec_section,checkbox.get_attribute('section'))) > 0 and len(re.findall(lec_section,checkbox.get_attribute('sectionlabel'))) > 0:
                checkbox.click()
                break

        prev_len = len(courses)
        while len(courses) == prev_len:
            search_list = WebDriverWait(driver,10,poll_frequency=0.2).until(EC.visibility_of_element_located((By.XPATH,"//div[contains(@class,'ClassSearchList')]")))
            courses = search_list.find_elements_by_css_selector("div[id^='data_course']")

        #try to get the status of discussions
        okay_section = []
        wait_section = []
        for course in courses:
            status = course.find_element(By.CLASS_NAME,'span3')
            print(status.text)
            if len(re.findall('Open', status.text)) > 0:
                okay_section.append(course)
            elif len(re.findall('Waitlist',status.text)) > 0:
                wait_section.append(course)

        if len(okay_section) == 0 and len(wait_section) == 0:
            print("No course is open or wailisted now. The program will check in {0}s".format(check_freq))
            time.sleep(check_freq)
            continue
        else:
            #if there is a course
            if dis_section == "":
                if len(okay_section) != 0:
                    candidate_courses.append(okay_section[0])
                else:
                    candidate_courses.append(wait_section[0])
                print("There is some availabe section. Since you did not pick your desired discussion section, the program will pick one for you")
                break
            else:
                for section in okay_section:
                    link = section.find_element(By.CLASS_NAME,'span2').find_element_by_tag_name("a")
                    if len(re.findall(dis_section,link.text)) > 0:
                        candidate_courses.append(section)
                        break

                for section in wait_section:
                    link = section.find_element(By.CLASS_NAME,'span2').find_element_by_tag_name("a")
                    if len(re.findall(dis_section,link.text)) > 0:
                        candidate_courses.append(section)
                        break

                if len(candidate_courses) != 0:
                    print("Find your desired course in open or waitlist section")
                    break
                else:
                    print("There are open or waitlist sections but they are not your desired section. The program will check in {0}s".format(check_freq))
                    time.sleep(check_freq)
                    continue
    else:
        print("cannot find search list")
        driver.quit()


for course in candidate_courses:
    checkbox = course.find_element(By.CLASS_NAME,'span1').find_element_by_tag_name("input")
    if len(re.findall(dis_section,checkbox.get_attribute('section'))) > 0 and len(re.findall(dis_section,checkbox.get_attribute('sectionlabel'))) > 0:
        checkbox.click()
        break

enrol_button = WebDriverWait(driver,10,poll_frequency=1).until(EC.presence_of_element_located((By.CLASS_NAME,"btn_enroll"))).find_element_by_css_selector("button[class*='enroll']")
enrol_button.click()


urgent_panel = WebDriverWait(driver,10,poll_frequency=1).until(EC.presence_of_element_located((By.ID,"enrPanel")))
warning_check_boxes = urgent_panel.find_elements_by_class_name("flyout_warnings_checkbox")

for box in warning_check_boxes:
    box.click()


grade_type_sels = urgent_panel.find_elements_by_tag_name("select")
if len(grade_type_sels) > 0:
    for grade_type_sel in grade_type_sels:
        if len(re.findall('gradeType',grade_type_sel.get_attribute('name'))) > 0:
            sel = Select(grade_type_sel)
            sel.select_by_index(grade_dict[grade_type])
            break

try:
    enrol_button = WebDriverWait(driver,10,poll_frequency=1).until(EC.presence_of_element_located((By.CLASS_NAME,"btn_enroll"))).find_element_by_css_selector("button[class*='enroll']")
    enrol_button.click()

    time.sleep(20)
    driver.quit()
except:
    print("Some errors occurred so I could not enrol")
