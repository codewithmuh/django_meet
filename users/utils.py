import random
import string


def get_random_str(l):
    ran = ''.join(random.choices("{0}{1}".format(string.ascii_uppercase, string.digits), k=l))
    return ran
