import requests
import json
from hilink import Hilink
import time


def main():
    data = read_settings('settings.json')
    sms_dump = read_settings('last_sms_time.json')
    
    # when script dont executed yet, save to file current time
    # sms newer than now - is what we looking for
    if not sms_dump:
        sms_dump = {}
        sms_dump['last_message_date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        save_to_settings(sms_dump, 'last_sms_time.json')

    api = Hilink(data['hilink_url'])
    
    while True:
        # for infinity working in background
        try:
            api.get_session_key()

            device_info = api.get_device_info()
            number = device_info['Msisdn']

            sms_list = api.get_sms_list(data['count_of_sms_per_time'])

            # reverse sorting for natural reading and resending
            # from old to new
            for sms in sms_list['Messages']['Message'][::-1]:
                sms_date = time.strptime(sms['Date'], "%Y-%m-%d %H:%M:%S")
                last_sms_time = time.strptime(sms_dump['last_message_date'], "%Y-%m-%d %H:%M:%S")

                if last_sms_time < sms_date:
                    text = sms['Content']
                    phone = sms['Phone']
                    
                    send_to_telegram(data['telegram_chat_id'], data['telegram_token'], f'{number} - {phone} - {text}')

                    sms_dump['last_message_date'] = sms['Date']
                    save_to_settings(sms_dump, 'last_sms_time.json')
                else:
                    continue
        except:
            print('Something went wrong, check your internet connection. Im goint to sleep for 10s')
            time.sleep(10)

def send_to_telegram(chat_id, token, data):
    url = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={data}'

    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'})

    if r.status_code != 200:
        print("Telegram pushing error" + str(r.status_code))

def read_settings(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        print(f'Unable to read {filename} file')
        return None

def save_to_settings(data, filename):
    try:
        with open('last_sms_time.json', 'w', encoding='utf-8') as f:
            return json.dump(data, f, indent=4)
    except:
        print(f'Unable to save data to {filename}')


if __name__ == '__main__':
    main()