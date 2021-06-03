'''
Script: Covid Vaccine Slot Availability Notifier
By Shreeyansh Jain
'''

import argparse
import requests
import pytz
import time

from datetime import datetime, timedelta

from pygame import mixer

PIN_URL_ENDPOINT = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={}"
DIS_URL_ENDPOINT = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict?district_id={}"
# Vaccine Type
VACCINE_TYPE = {"CV": "COVAXIN", "CD": "COVISHIELD", "SV": "SPUTNIK V"}


def get_actual_dates(num_days=2):
    """
    This will return the date range for which we want to check the slot availability
    :param num_days (int): number of days
    :return: Return date list
    """
    tz_NY = pytz.timezone('Asia/Kolkata')
    actual = datetime.now(tz_NY).today()
    list_format = [actual + timedelta(days=i) for i in range(num_days)]
    actual_dates = [i.strftime("%d-%m-%Y") for i in list_format]
    return actual_dates


def check_availability_by_pincode(age, pincodes, dose2, vaccine_type, num_days=2):
    """
    This method will use to search the Vaccination slot using Pin Code
    """
    actual_dates = get_actual_dates(num_days)
    while True:
        counter = 0
        for pincode in pincodes:
            url = PIN_URL_ENDPOINT.format(pincode)
            url += "&date={}"
            print("Searching Vaccination slot for pincode {}".format(pincode))
            if check_available_slot(counter, age, dose2, actual_dates, vaccine_type, url):
                play_sound()
                break;
            else:
                print("No Vaccination slot available!")

        dt = datetime.now() + timedelta(minutes=3)

        while datetime.now() < dt:
            time.sleep(1)


def check_availability_by_district(age, district_id, dose2, vaccine_type, num_days=2):
    """
    This method will use to search the Vaccination slot using Pin Code
    """
    actual_dates = get_actual_dates(num_days)
    url = DIS_URL_ENDPOINT.format(district_id)
    url += "&date={}"

    while True:
        counter = 0
        if check_available_slot(counter, age, dose2, actual_dates, vaccine_type, url):
            play_sound()
            break;
        else:
            print("No Vaccination slot available!")

        dt = datetime.now() + timedelta(minutes=3)

        while datetime.now() < dt:
            time.sleep(1)


def check_available_slot(counter, age, dose2, actual_dates, vaccine_type, url=None):
    """
    This method will check Cowin available slot for given age and pincodes locations.
    :param counter: Counter to indicate slot is available
    :param age: User age
    :param url: CoWin look up url
    :param dose2:  check for the available_capacity_dose2
    :param actual_dates: list of dates
    :param vaccine_type: search for specific vaccine type only

    :return:
    """

    search_dose = 'available_capacity_dose1' if not dose2 else 'available_capacity_dose2'

    if vaccine_type not in VACCINE_TYPE:
        vaccine_type = "ALL"

    vaccine = VACCINE_TYPE.values() if vaccine_type == "ALL" else [VACCINE_TYPE.get(vaccine_type)]

    url = url.format(actual_dates[0])
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}

    result = requests.get(url, headers=header)

    if not result.ok:
        print ("No Response!")
    else:
        response_json = result.json()
        if response_json["centers"]:
            for center in response_json["centers"]:
                for session in center["sessions"]:
                    if session["min_age_limit"] <= age and session["available_capacity"] > 0\
                            and session[search_dose] > 0 and session['date'] in actual_dates \
                            and session["vaccine"] in vaccine:
                        print('Age Group: ', session["min_age_limit"])
                        print('Pin-code: ', center["pincode"])
                        print("Available on: {}".format(session['date']))
                        print("\t", center["name"])
                        print("\t", center["block_name"])
                        print("\t Price: ", center["fee_type"])
                        print("\t Availability : ", session["available_capacity"])

                        if dose2:
                            print("\t Dose-2 : ", session["available_capacity_dose2"])
                        else:
                            print("\t Dose-1 : ", session["available_capacity_dose1"])

                        if session["vaccine"] != '':
                            print("\t Vaccine type: ", session["vaccine"])
                        print("\n")
                        counter = counter + 1
    return counter


def play_sound():
    """
        This method will play ding dong song if slot is available for provided age group
    """
    mixer.init()
    mixer.music.load('sound/dingdong.wav')
    mixer.music.play()
    print("Search Completed!")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="CoWin Script to check the available slot for 1st and 2nd Dose")
    parser.add_argument('--age', default=35, type=int, help='Provide your age')
    parser.add_argument('--num_days', default=2, type=int, help='number of day look for slot')
    parser.add_argument('--dose2', default=False, type=bool, help='CSV will generate for given hours')
    parser.add_argument('--pincodes', default=['470001', '470002', '470004'], metavar='N', type=str, nargs='+',
                        help='Search by Pincode pass as list')
    parser.add_argument('--district_id', type=int, help='Search by district_id as a signle integer value')
    parser.add_argument('--vaccine_type', type=str, default="ALL",  help="""
                                    Search by vaccine type such as CV: COVAXIN, CD: COVISHIELD, SV: Sputnik V""")
    args = parser.parse_args()

    if args.district_id:
        check_availability_by_district(age=args.age, dose2=args.dose2, vaccine_type=args.vaccine_type,
                                       district_id=args.district_id, num_days=args.num_days)
    else:
        check_availability_by_pincode(age=args.age, dose2=args.dose2, vaccine_type=args.vaccine_type,
                                      pincodes=args.pincodes, num_days=args.num_days)