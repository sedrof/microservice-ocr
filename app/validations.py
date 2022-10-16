import datetime

def validate_time(value):
    try:
        new_date = datetime.datetime.strptime(value, "%d/%m/%Y").strftime("%Y-%m-%d")
        return new_date
    except ValueError:
        return value

def mtn(x):
    months = {
        'jan': '01',
        'feb': '02',
        'mar': '03',
        'apr':'04',
         'may':'05',
         'jun':'06',
         'jul':'07',
         'aug':'08',
         'sep':'09',
         'oct':'10',
         'nov':'11',
         'dec':'12'
        }
    a = x.strip()[:3].lower()
    try:
        ez = months[a]
        return ez
    except:
        raise ValueError('Not a month')