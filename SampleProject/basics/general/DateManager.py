import datetime


def date_manager(year, month, day_of_month, no_of_days):
    """
     Question:
     Create a method which add or subtract number of days from today's date without
     using built-in classes
     <br>
     Imp Trick
     For calculating leap years in a range of years, first check number of leap years in range
     excluding first and last year, and then check if first or last year is a leap year and
     in counting the extra day 29th of May will be considered.
     <br>
     Topics : abs(),/ and //
    """
    if abs(no_of_days) > 365:
        no_of_years = abs(no_of_days) // 365

        if no_of_days<0:
            no_of_years=-no_of_years

        no_of_days -= (no_of_years * 365)
        no_of_days -= get_leap_years(year, month, day_of_month, no_of_years)
        year += no_of_years

    while no_of_days != 0:
        if no_of_days > 0:
            if (month + 1) in (1, 3, 5, 7, 8, 10, 12,13):
                days_in_month = 31
            elif (month + 1) in (4, 6, 9, 11):
                days_in_month = 30
            else:
                days_in_month = 29 if year % 4 == 0 else 28

            if no_of_days > (days_in_month - day_of_month):
                # +1 because we have to come to first day of the month
                no_of_days = no_of_days - (days_in_month - day_of_month)+1
                if month==12:
                    month=0
                    year += 1
                month += 1
                day_of_month = 1
            else:
                day_of_month = int(no_of_days)
                no_of_days = 0
        else:
            if (month - 1) in (1, 3, 5, 7, 8, 10, 12):
                days_in_month = 31
            elif (month - 1) in (4, 6, 9, 11):
                days_in_month = 30
            else:
                days_in_month = 29 if year % 4 == 0 else 28

            if abs(no_of_days) > day_of_month:
                no_of_days += day_of_month
                month -= 1
                day_of_month = days_in_month
            else:
                day_of_month = days_in_month+no_of_days-1
                no_of_days = 0

    return f"{year}/{month:2}/{day_of_month}"


def get_leap_years(year, month, day_of_month, no_of_years):
    if no_of_years > 0:
        starting_year = year + 1
        ending_year = year + no_of_years - 1
        leap_years = ((ending_year // 4) - (starting_year // 4))

        if year % 4 == 0 and month < 2 and day_of_month < 29:
            leap_years += 1
        elif (year + no_of_years) % 4 == 0 and month > 3 and day_of_month > 1:
            leap_years += 1

    else:
        starting_year = year + no_of_years + 1
        ending_year = year - 1
        leap_years = ((ending_year // 4) - (starting_year // 4))
        if (year + no_of_years) % 4 == 0 and month < 2 and day_of_month < 29:
            leap_years += 1
        elif year % 4 == 0 and month > 3 and day_of_month > 1:
            leap_years += 1

        leap_years=-leap_years

    print("Leap Year : ", leap_years)
    return leap_years


if __name__ == "__main__":
    year = 2026
    month = 6
    day_of_month = 9
    value = 3731
    print((datetime.datetime(year=year, month=month, day=day_of_month) +
           datetime.timedelta(days=value)).strftime(
        "%Y/%m/%d"))
    print(date_manager(year, month, day_of_month, value))
