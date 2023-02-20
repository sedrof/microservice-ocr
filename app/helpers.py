import re
from .validations import validate_time, mtn

def extract_inv_ref(pdf_all_pages):
    phone_number = re.findall(r"\b\d{4}\s\d{3}\s\d{4}\b", pdf_all_pages)
    if phone_number:
        return phone_number[0]
    else:
        phone_number = re.findall(r"\b\d{16}\b", pdf_all_pages)
        if phone_number:
            return phone_number[0]
        else:
            return 'dddf'

def extract_meter_reading_period(string):
    lines = string.split("\n")
    for line in lines:
        if "Moter Reading Period" in line:
            return line.split(":")[1].strip()
    return None

def total_amount_func(pdf_all_pages):
    try:
        pattern = re.compile(r'(due|Total amount due|duo) (\$|)(\d{1,4}(,\d{3})*\.\d{2})')
        match = pattern.search(pdf_all_pages)
        if match:
            total_amount = match.group(3)
            return float(total_amount.replace(',',''))
        else:
            return None
    except:
        return None

def inv_ref_func(pdf_all_pages):
    try:
        patterns = re.compile(r'\d{4}\s\d{3}\s\d{4}')
        matches = patterns.finditer(pdf_all_pages)
        ref = [ result.group(0) for result in matches][0].replace("Refno.:",'').split(':')[1].replace(" ",'')
        return int(ref)
    except:
        return 'null'
    
def description_func(pdf_all_pages):
    try:
        patterns = re.compile(r'(Account\sfor\s)\d.+?(Card)')
        matches = list(patterns.finditer(pdf_all_pages))
        if matches:
            ref = matches[0].group(0).split('ProspectWATER')[0]
        else:
            ref = None
            return ref
        if 'Prospect' in ref:
            patterns = re.compile(r'(Account\sfor\s)\d.+?(ProspectWATERB)')
            matches = patterns.finditer(pdf_all_pages)
            ref = [ result.group(0) for result in matches][0].split('ProspectWATERB')[0]
        if 'WATE' in ref:
            patterns = re.compile(r'(Account\sfor\s)\d.+?(WATE)')
            matches = patterns.finditer(pdf_all_pages)
            ref = [ result.group(0) for result in matches][0].split('WATE')[0]
        return ref
    except:
        return 'null'

def supplier_code_func(pdf_all_pages):
    try:
        patterns = patt = re.compile(r'Biller\s{2}code:\s{2}\d{5}')
        matches = patterns.finditer(pdf_all_pages)
        ref = [result.group(0) for result in matches][0].split()[-1]
        return ref
    except:
        return 'null'

def invoice_date_func(pdf_all_pages):
    try:
        patterns = re.compile(r'Date\sof(\s|\s{1})issue\s(\d{2}|\d)\s\w{3}\s\d{4}')
        matches = patterns.finditer(pdf_all_pages)
        ref = [result.group(0) for result in matches][0].split()
        new = mtn(ref[-2])
        date = str(ref[-3]) + " " + str(new) + " " + str(ref[-1])
        new_data = validate_time(date.replace(" ", '/'))
        return new_data
    except:
        return 'null'

def due_date_func(pdf_all_pages):
    try:
        patterns = re.compile(r'\d{2}/\d{2}/\d{2}')
        matches = patterns.finditer(pdf_all_pages)
        ref = [result.group(0) for result in matches][0]
        year_4_char = int(ref.split('/')[-1]) + int(2000)
        month = ref.split('/')[-2]
        day = ref.split('/')[0]
        date = str(year_4_char) + "-" + str(month) + "-" + str(day)
        return date
    except:
        return 'null'

def total_water_usage_func(pdf_all_pages):
    try:
        patterns = re.compile(r'details\s{2}(\d{1}|\d{2}|\d{3}|\d{4}).(\d{2})')
        matches = patterns.finditer(pdf_all_pages)
        ref = [result.group(0) for result in matches]
        return (ref)
    except:
        return 'null'

def total_water_rate_func(pdf_all_pages):
    try:
        patterns = re.compile(r'\d{2}/\d{2}\s{2}\d{2}')
        matches = patterns.finditer(pdf_all_pages)
        ref = [result.group(0) for result in matches][0].split()[-1]
        return float(ref)
    except:
        return 'null'

def total_other_amount_func(pdf_all_pages):
    try:
        patterns = re.compile(r'\d{2}/\d{2}\s{2}\d{2}')
        matches = patterns.finditer(pdf_all_pages)
        ref = [result.group(0) for result in matches][0].split()[-1]
        return ref
    except:
        return 'null'

def meter_length(pdf_all_pages):
    try:
        meter_numbers = re.compile(r'[A-Z](\w{3}|\w{4}|\w{5}|\w{6})\d{3}\s{2}\d')
        meter_numbers_matches = meter_numbers.finditer(pdf_all_pages)
        meter_numbers_ref = [result.group(0) for result in meter_numbers_matches]

        return len(meter_numbers_ref)
    except:
        return 'null'



def extract_meter_no(string):
    try:
        pattern = re.compile(r"([A-Z]{1,5}\d{1,5} \d{1,4} \d{1,4} \d{1,4})")
        matches = pattern.finditer(string)
        patterns = []
        for match in matches:
            patterns.append(match.group().split())
        return patterns
    except:
        return 'null'

def add_data_to_object(text):
    try:
        formed_data = {}
        formed_data['total_amount'] = total_amount_func(text)
        formed_data['description'] = description_func(text)
        formed_data['inv_ref']= extract_inv_ref(text)
        formed_data['due_date'] = extract_meter_reading_period(text)
        formed_data['invoice_date']= invoice_date_func(text)
        
        # formed_data_2 = {}
        meters = []
        for i in range(len(extract_meter_no(text))):
                meters.append(
                    {
                        'meter_no':extract_meter_no(text)[i][0],
                        'this_reading':extract_meter_no(text)[i][1] ,
                        'last_reading':extract_meter_no(text)[i][2],
                        'consumption':extract_meter_no(text)[i][3]
                    },
                    )
    except:
            pass
    return formed_data, meters




    #ssh -i "newtagasdfdsfsdafdasfasdf.pem" ec2-user@ec2-3-26-242-191.ap-southeast-2.compute.amazonaws.com