def equal(left, right):
    return left == right


def inside(left, right):
    return left in right


def smaller(left, right):
    return left < right


def larger(left, right):
    return left < right


def smaller_equal(left, right):
    return left <= right


def larger_equal(left, right):
    return left >= right


function_list = {
    "equal": equal,
    "inside": inside,
    "smaller": smaller,
    "larger": larger,
    "smaller_equal": smaller_equal,
    "larger_equal": larger_equal,
}
