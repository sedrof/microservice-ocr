import re
import itertools
from .validations import validate_time, mtn


def total_amount_func(pdf_all_pages):
    patterns = re.compile(r'(due\s|due)[$](\d{3}|\d{4}|\d{2}|\d{1})[.](\d{2}|\d{1})')
    matches = patterns.finditer(pdf_all_pages)
    total_amount = [ result.group(0) for result in matches][-1].split('$')[-1]
    return float(total_amount)

def inv_ref_func(pdf_all_pages):
    patterns = re.compile(r'Ref\sno.:\s\d{4}\s\d{3}\s\d{4}')
    matches = patterns.finditer(pdf_all_pages)
    ref = [ result.group(0) for result in matches][0].replace("Refno.:",'').split(':')[1].replace(" ",'')
    return int(ref)

def description_func(pdf_all_pages):
    patterns = re.compile(r'(Account\sfor\s)\d.+?(Card)')
    matches = patterns.finditer(pdf_all_pages)
    ref = [ result.group(0) for result in matches][0].split('Card')[0].split("for ")[1]
    print(ref)
    if 'Prospect' in ref:
        patterns = re.compile(r'(Account\sfor\s)\d.+?(ProspectWATERB)')
        matches = patterns.finditer(pdf_all_pages)
        ref = [ result.group(0) for result in matches][0].split('ProspectWATERB')[0]
    if 'WATE' in ref:
        patterns = re.compile(r'(Account\sfor\s)\d.+?(WATE)')
        matches = patterns.finditer(pdf_all_pages)
        ref = [ result.group(0) for result in matches][0].split('WATE')[0]
    return ref

def supplier_code_func(pdf_all_pages):
    patterns = patt = re.compile(r'Biller\s{2}code:\s{2}\d{5}')
    matches = patterns.finditer(pdf_all_pages)
    ref = [result.group(0) for result in matches][0].split()[-1]
    return ref

def invoice_date_func(pdf_all_pages):
    patterns = re.compile(r'Date\sof(\s|\s{1})issue\s(\d{2}|\d)\s\w{3}\s\d{4}')
    matches = patterns.finditer(pdf_all_pages)
    ref = [result.group(0) for result in matches][0].split()
    new = mtn(ref[-2])
    date = str(ref[-3]) + " " + str(new) + " " + str(ref[-1])
    new_data = validate_time(date.replace(" ", '/'))

    return new_data

def due_date_func(pdf_all_pages):
    patterns = re.compile(r'\d{2}/\d{2}/\d{2}')
    matches = patterns.finditer(pdf_all_pages)
    ref = [result.group(0) for result in matches][0]
    year_4_char = int(ref.split('/')[-1]) + int(2000)
    month = ref.split('/')[-2]
    day = ref.split('/')[0]
    date = str(year_4_char) + "-" + str(month) + "-" + str(day)
    return date

def total_water_usage_func(pdf_all_pages):
    patterns = re.compile(r'details\s{2}(\d{1}|\d{2}|\d{3}|\d{4}).(\d{2})')
    matches = patterns.finditer(pdf_all_pages)
    ref = [result.group(0) for result in matches]
    return (ref)

def total_water_rate_func(pdf_all_pages):
    patterns = re.compile(r'\d{2}/\d{2}\s{2}\d{2}')
    matches = patterns.finditer(pdf_all_pages)
    ref = [result.group(0) for result in matches][0].split()[-1]
    return float(ref)

def total_other_amount_func(pdf_all_pages):
    patterns = re.compile(r'\d{2}/\d{2}\s{2}\d{2}')
    matches = patterns.finditer(pdf_all_pages)
    ref = [result.group(0) for result in matches][0].split()[-1]
    return ref

def meter_length(pdf_all_pages):
    meter_numbers = re.compile(r'[A-Z](\w{3}|\w{4}|\w{5}|\w{6})\d{3}\s{2}\d')
    meter_numbers_matches = meter_numbers.finditer(pdf_all_pages)
    meter_numbers_ref = [result.group(0) for result in meter_numbers_matches]

    return len(meter_numbers_ref)

def meter_no_func(pdf_all_pages):
    patterns = re.compile(r'([(kl)]\w{4}\d{4}|[EST*]\w{4}\d{4})')
    matches = patterns.finditer(pdf_all_pages)
    ref = [result.group(0) for result in matches]
    final_list = []
    try:
        removetable = str.maketrans('', '', '@*#%')
        for i in range(len(ref)):
            ref[i].split('*',1)
            final_list.append("".join(ref[i].split(')',1)))
        f = [s.translate(removetable) for s in final_list]
        if len(final_list) == 0:
            try:
                print('ss')
                patterns = re.compile(r'Meter\sNo.\w{4}\d{4}')
                matches = patterns.finditer(pdf_all_pages)
                ref = [result.group(0) for result in matches][0].split(".")[1]
                lis = []
                lis.append(ref)
                return lis
            except:
                pass
            try:
                print("jk")
                patterns = re.compile(r'Consumption.+?EST')
                matches = patterns.finditer(pdf_all_pages)
                ref = [result.group(0) for result in matches][0].split(".")[0].split(")")[1].split(" ")[0]
                lis = []
                lis.append(ref)
                return lis
            except:
                pass
        return f
    except:
        return []

def this_reading_func(pdf_all_pages):
    patterns = re.compile(r'\bkL.\w{4}\d{4}.............|[EST*]\w{4}\d{4}................')
    matches = patterns.finditer(pdf_all_pages)
    ref = [result.group(0) for result in matches]
    this_reading = []
    try:
        for i in range(len(ref)):
            this_reading.append(ref[i].split(" ")[1])
        return (this_reading)
    except:
        return []

def last_reading_func(pdf_all_pages):
    patterns = re.compile(r'\bkL.\w{4}\d{4}.............|[EST*]\w{4}\d{4}................')
    matches = patterns.finditer(pdf_all_pages)
    ref = [result.group(0) for result in matches]
    last_reading = []
    try:
        for i in range(len(ref)):
            last_reading.append(ref[i].split(" ")[2])
        return (last_reading)
    except:
        return []

def consumption_func(pdf_all_pages):
    patterns = re.compile(r'\bkL.\w{4}\d{4}.............|[EST*]\w{4}\d{4}................')
    matches = patterns.finditer(pdf_all_pages)
    ref = [result.group(0) for result in matches]
    last_reading = []
    try:
        for i in range(len(ref)):
            last_reading.append(ref[i].split(" ")[3])
        
        numbers = [re.findall(r'\d+', s) for s in last_reading]
        
        return list(itertools.chain.from_iterable(numbers))
    except:
        return []