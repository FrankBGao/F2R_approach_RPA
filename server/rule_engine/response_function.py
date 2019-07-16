def equal(put_in, arg):
    return put_in[0]


def minus(put_in, arg):
    return put_in[0] - arg["minus"]


def plus(put_in, arg):
    return put_in[0] + arg["plus"]


function_list = {
    "equal": equal,
    "minus": minus,
    "plus": plus
}
