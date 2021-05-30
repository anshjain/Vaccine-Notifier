'''
Script: Covid Vaccine Slot Availability Notifier
By Shreeyansh Jain
'''

import argparse
import requests
import time

from datetime import datetime, timedelta

from pygame import mixer

PIN_URL_ENDPOINT = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={}"
DIS_URL_ENDPOINT = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict?district_id={}"


def get_actual_dates(num_days=2):
    """
    This will return the date range for which we want to check the slot availability
    :param num_days (int): number of days
    :return: Return date list
    """
    actual = datetime.today()
    list_format = [actual + timedelta(days=i) for i in range(num_days)]
    actual_dates = [i.strftime("%d-%m-%Y") for i in list_format]
    return actual_dates


def check_availability_by_pincode(age, pincodes, dose1, dose2, num_days=2):
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
            if check_available_slot(counter, age, dose1, dose2, actual_dates, url):
                break;

        dt = datetime.now() + timedelta(minutes=3)

        while datetime.now() < dt:
            time.sleep(1)


def check_availability_by_district(age, district_id, dose1, dose2, num_days=2):
    """
    This method will use to search the Vaccination slot using Pin Code
    """
    actual_dates = get_actual_dates(num_days)
    url = DIS_URL_ENDPOINT.format(district_id)
    url += "&date={}"

    while True:
        counter = 0
        if check_available_slot(counter, age, dose1, dose2, actual_dates, url):
            break;

        dt = datetime.now() + timedelta(minutes=3)

        while datetime.now() < dt:
            time.sleep(1)


def check_available_slot(counter, age, dose1, dose2, actual_dates, url=None):
    """
    This method will check Cowin available slot for given age and pincodes locations.
    :param counter: Counter to indicate slot is available
    :param age: User age
    :param url: CoWin look up url
    :param dose1: check for the available_capacity_dose1
    :param dose2:  check for the available_capacity_dose2
    :param actual_dates: list of dates

    :return:
    """

    search_dose = 'available_capacity_dose1' if not dose2 else 'available_capacity_dose2'

    for given_date in actual_dates:
        url = url.format(given_date)
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}

        result = requests.get(url, headers=header)

        if result.ok:
            response_json = result.json()
            if response_json["centers"]:
                for center in response_json["centers"]:
                    for session in center["sessions"]:
                        if session["min_age_limit"] <= age and session["available_capacity"] > 0 and session[search_dose] > 0:
                            # print('Pin-code: ' + pincode)
                            print("Available on: {}".format(given_date))
                            print("\t", center["name"])
                            print("\t", center["block_name"])
                            print("\t Price: ", center["fee_type"])
                            print("\t Availability : ", session["available_capacity"])

                            if dose1:
                                print("\t Dose-1 : ", session["available_capacity_dose1"])
                            if dose2:
                                print("\t Dose-2 : ", session["available_capacity_dose2"])

                            if session["vaccine"] != '':
                                print("\t Vaccine type: ", session["vaccine"])
                            print("\n")
                            counter = counter + 1
        else:
            print("No Response!")

        if not counter:
            print("No Vaccination slot available!")
        else:
            mixer.init()
            mixer.music.load('sound/dingdong.wav')
            mixer.music.play()
            print("Search Completed!")
    return counter


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='CoWin Script to check the available slot for 1st and 2nd Dose')
    parser.add_argument('--age', default=35, type=int, help='Provide your age')
    parser.add_argument('--num_days', default=2, type=int, help='number of day look for slot')
    parser.add_argument('--dose1', default=True,  type=bool, help='Output dir path where we temporarily save csv')
    parser.add_argument('--dose2', default=False, type=bool, help='CSV will generate for given hours')
    parser.add_argument('--pincodes', default=['470001', '470002', '470004'], metavar='N', type=str, nargs='+',
                        help='Search by Pincode pass as list')
    parser.add_argument('--district_id', type=int, help='Search by district_id as a signle integer value')
    args = parser.parse_args()

    if args.district_id:
        check_availability_by_district(age=args.age, dose1=args.dose1, dose2=args.dose2,
                                       district_id=args.district_id, num_days=args.num_days)
    else:
        check_availability_by_pincode(age=args.age, dose1=args.dose1, dose2=args.dose2,
                                      pincodes=args.pincodes, num_days=args.num_days)