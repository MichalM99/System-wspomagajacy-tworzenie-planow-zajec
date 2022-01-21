import random
import string


def create_username(first_name, last_name):
    username = first_name[0:3] + last_name[0:3] + str(random.randint(0,99))
    return username

def get_random_password():
    random_source = string.ascii_letters.lower() + string.digits
    # select 1 lowercase
    password = random.choice(string.ascii_lowercase)


    # generate other characters
    for i in range(6):
        password += random.choice(random_source)

    password_list = list(password)
    # shuffle all characters
    random.SystemRandom().shuffle(password_list)
    password = ''.join(password_list)
    return password