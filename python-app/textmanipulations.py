import re

def delete_zeros_at_beginning(input):
    """
    Funkcja usuwająca wszystkie '0', które znajdują się na początku stringu

    Parameters:
            input (str): modyfikowany string
    Returns:
            output (str): zmodyfikowany string
    """
    regex = "^0+(?!$)"
    output = re.sub(regex, "", input)
    return output


def match_datetime_midnight_formatting(time, date_today, date_tomorrow):
    """
    Funkcja modyfikująca format stringu daty po północy, by odpowiadał temu z biblioteki datetime

    Parameters:
            time (str): HH:MM:SS string
            date_today (str): string dzisiejszej daty
            date_tomorrow (str): string jutrzejszej daty
    Returns:
            output (str): data w prawidłowym formacie
    """
    if int(time[:2]) >= 24:
        time = "0" + str(int(time[:2]) - 24) + time[2:]
        output = f"{date_tomorrow} {time}"
    else:
        output = f"{date_today} {time}"
    return output