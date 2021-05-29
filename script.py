'''
Script: Covid Vaccine Slot Availability Notifier
By Shreeyansh Jain
'''

import argparse
import requests
import time

from datetime import datetime, timedelta

from pygame import mixer

URL_ENDPOINT = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={}&date={}"


def check_available_slot(age, pincodes, dose1, dose2, num_days=2):
    """
    This method will check Cowin available slot for given age and pincodes locations.
    :param age: User age
    :param pincodes: Locations where user is searching for coWin
    :param dose1: check for the available_capacity_dose1
    :param dose2:  check for the available_capacity_dose2
    :param num_days: number of days default value is 2

    :return:
    """
    actual = datetime.today()
    list_format = [actual + timedelta(days=i) for i in range(num_days)]
    actual_dates = [i.strftime("%d-%m-%Y") for i in list_format]
    search_dose = 'available_capacity_dose1'
    if dose2:
        search_dose = 'available_capacity_dose2'

    while True:
        counter = 0
        for pincode in pincodes:
            for given_date in actual_dates:
                url = URL_ENDPOINT.format(pincode, given_date)
                header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}

                result = requests.get(url, headers=header)

                if result.ok:
                    response_json = result.json()
                    if response_json["centers"]:
                        for center in response_json["centers"]:
                            for session in center["sessions"]:
                                if session["min_age_limit"] <= age and session["available_capacity"] > 0 and session[search_dose] > 0:
                                    print('Pin-code: ' + pincode)
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

        dt = datetime.now() + timedelta(minutes=3)

        while datetime.now() < dt:
            time.sleep(1)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='CoWin Script to check the available slot for 1st and 2nd Dose')
    parser.add_argument('--age', default=35, type=int, help='Provide your age')
    parser.add_argument('--num_days', default=2, type=int, help='number of day look for slot')
    parser.add_argument('--dose1', default=True,  type=bool, help='Output dir path where we temporarily save csv')
    parser.add_argument('--dose2', default=False, type=bool, help='CSV will generate for given hours')
    parser.add_argument('--pincodes', default=['470001', '470002'], metavar='N', type=str, nargs='+',
                        help='Search by Pincode pass as list')
    args = parser.parse_args()

    check_available_slot(age=args.age, dose1=args.dose1, dose2=args.dose2, pincodes=args.pincodes)