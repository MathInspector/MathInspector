"""
Based on: https://stackoverflow.com/questions/48567935/get-parameterarg-count-of-builtin-functions-in-python
"""
import re

def numargs(func):
    arg_test = 0
    while arg_test < 999:
        try:
            s = [None] * arg_test
            func(*s)
        except TypeError as e:
            message = str(e)
            found = re.match(
                r"[\w]+\(\) takes ([0-9]{1,3}) positional argument[s]* but " +
                str(arg_test) + " were given", message)

            if "takes no positional arguments" in message:
                return 0
            if found:
                return int(found.group(1))

            if "takes no arguments" in message:
                return 0
            elif "takes at most" in message:
                found = re.match(
                    r"[\w]+\(\) takes at most ([0-9]{1,3}).+", message)
                if found:
                    return int(found.group(1))
            elif "takes exactly" in message:
                # string can contain 'takes 1' or 'takes one',
                # depending on the Python version
                found = re.match(
                    r"[\w]+\(\) takes exactly ([0-9]{1,3}|[\w]+).+", message)
                if found:
                    return 1 if found.group(1) == "one" \
                            else int(found.group(1))
        arg_test += 1
    return -1  # *args
