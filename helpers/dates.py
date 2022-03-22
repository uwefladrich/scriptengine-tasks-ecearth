"""Helper module for dealing with dates (mostly months)"""

_month_names = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


def month_number(month):
    "Returns number of month (1..12) for month (int or string)"
    nums = dict()
    # Allow all of "January", "january", "jan", 1
    for num, name in enumerate(_month_names):
        nums[name] = nums[num + 1] = nums[name.lower()[:3]] = nums[name.lower()] = (
            num + 1
        )
    try:
        return nums[month]
    except KeyError:
        raise ValueError(f"Invalid month: '{month}'")


def month_name(month):
    return _month_names[month_number(month) - 1]
