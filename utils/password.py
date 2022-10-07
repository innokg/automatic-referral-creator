
import random

def get_password():
    """
    function to set password in airtable
    """
    password_length = 12
    characters = "abcdefghABCDEFGH1234567890"
    password = ""
    for index in range(password_length):
        password = password + random.choice(characters)
    return password