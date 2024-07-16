import time
import requests
from PIL import Image
from io import BytesIO
from IPython.display import display
import concurrent.futures
from bs4 import BeautifulSoup


with open('token.txt', 'r') as file:
    jsessionid = file.read().strip()

cookies = {
    'JSESSIONID': jsessionid,
}

headers2 = {
    'Cookie': f'JSESSIONID={jsessionid}'
}

def CheckSiteIsOpen():
    response = requests.get('https://portal.aut.ac.ir/aportal/regadm/student.portal/student.portal.jsp?action=edit&st_info=register&st_sub_info=0', cookies=cookies, headers=headers2)
    return 'درس را اضافه کن' in response.text

def get_captcha_code():
    response = requests.get('https://portal.aut.ac.ir/aportal/PassImageServlet', cookies=cookies, headers=headers2)
    image = Image.open(BytesIO(response.content))
    image.show()
    addpassline = input("captcha Code: ")
    return addpassline

def send_request(st_reg_courseid, st_reg_groupno, addpassline, failed_requests):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    url = "https://portal.aut.ac.ir/aportal/regadm/student.portal/student.portal.jsp?action=apply_reg&st_info=drop"
    
    data = {
        'st_reg_courseid': st_reg_courseid,
        'st_reg_groupno': st_reg_groupno,
        'addpassline': addpassline,
        'st_course_add': 'درس را اضافه کن',
        'st_comments1': '',
        'st_date1': '',
        'st_date1_disp': ''
    }

    response = requests.post(url, cookies=cookies, headers=headers, data=data)
    
    if 'درس را اضافه کن' in response.text:
        print(f"Course {st_reg_courseid} added successfully")
    elif 'تداخل دارد' in response.text:
        print(f"Course {st_reg_courseid} It interferes with other lessons")
    elif 'فيلد حروف تصوير معتبر نميباشد' in response.text:
        failed_requests.append((st_reg_courseid, st_reg_groupno))
        print(f"Invalid captcha for course {st_reg_courseid}. Restarting program...")
    elif 'خطاي نامشخص' in response.text:
        failed_requests.append((st_reg_courseid, st_reg_groupno))
        print(f"Unknown error for course {st_reg_courseid}. Restarting program...")
    elif 'سال ورود دانشجو در محدوده مجاز ثبت نام نميباشد' in response.text:
        print(f"Time is not a unit choice")
    else:
        print(response.text)

while True:
    if CheckSiteIsOpen():
        print("site open ....")
        addpassline = get_captcha_code()

        failed_requests = []

        with open('course.txt', 'r') as file:
            lines = [line.strip().split() for line in file]

        while True:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(send_request, st_reg_courseid, st_reg_groupno, addpassline, failed_requests) for st_reg_courseid, st_reg_groupno in lines]
                for future in concurrent.futures.as_completed(futures):
                    future.result()
            
            if not failed_requests:
                break

            print("Retrying failed requests...")
            lines = failed_requests.copy()
            failed_requests.clear()
            addpassline = get_captcha_code()
        
        print("The mission was successfully completed :)")
        exit()
    else:
        print("site not open ...")
        time.sleep(1)
