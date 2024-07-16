import time
import requests
from PIL import Image
from io import BytesIO
import random
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
    CheckSiteIsOpen()
    response = requests.get('https://portal.aut.ac.ir/aportal/PassImageServlet', cookies=cookies, headers=headers2)
    image = Image.open(BytesIO(response.content))
    image.show()
    addpassline = input("captcha Code: ")
    return addpassline

while True:
    if CheckSiteIsOpen():
        print("site open ....")
        addpassline = get_captcha_code()

        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]

        url = "https://portal.aut.ac.ir/aportal/regadm/student.portal/student.portal.jsp?action=apply_reg&st_info=drop"

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        def send_request(st_reg_courseid, st_reg_groupno, addpassline):
            headers['User-Agent'] = random.choice(user_agents)
            
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
            elif 'تداخل دارد' in response.text :
                print(f"Course {st_reg_courseid} It interferes with other lessons")
            elif 'فيلد حروف تصوير معتبر نميباشد' in response.text:
                #add to list
                print(f"Invalid captcha for course {st_reg_courseid}. Restarting program...")
            elif 'خطاي نامشخص' in response.text:
                #add to list
                print('selecte again')
            else:
                print(response.text)

        with open('course.txt', 'r') as file:
            lines = [line.strip().split() for line in file]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(send_request, st_reg_courseid, st_reg_groupno, addpassline) for st_reg_courseid, st_reg_groupno in lines]
            for future in concurrent.futures.as_completed(futures):
                future.result()

        print("The mission was successfully completed :)")
        time.sleep(10)
        exit()

    else:
        print("site not open ...")
        time.sleep(1)
