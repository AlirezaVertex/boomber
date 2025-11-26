from data.data import extract_phone_from_file
from processor.register import Register
from utils import print_success


def start():
    for phone in extract_phone_from_file():
        print_success(f"start process for ({phone})")
        action = Register(phone)
        action.start()
        print_success(f"process down for ({phone})")
