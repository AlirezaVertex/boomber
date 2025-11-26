import re


def check_phone(phone):
    phone = phone.replace("\n", "")
    if re.match(r"^09\d{9}$", phone):
        return phone


def extract_phone_from_file():
    with open("phones.txt", mode="r") as file:
        phones = file.readlines()

    for phone in phones:
        result = check_phone(phone)
        if result:
            yield result
