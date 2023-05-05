import time
import requests

# Telegram channel URL
TELEGRAM_URL = 'https://api.telegram.org/bot5370584924:AAHUC-AwSEyzlnlcWVAgZ-TpVkDwRPMoiDA/sendmessage?chat_id=-1001556285353&text='

# Thresholds for water levels
VV1_HIGH = 190
VV1_LOW = 45
VV2_HIGH = 150
VV2_LOW = 60
RETRY_COUNT = 5
SLEEP_DURATION = 2
CONSECUTIVE_ALERT_COUNT = 10
CONSECUTIVE_SAME_LEVEL_COUNT = 10

# Function to send a message to the Telegram channel
def send_telegram_message(message: str):
    try:
        requests.get(TELEGRAM_URL + message)
    except:
        print('telegram error')

def get_water_levels():
    response = requests.get('http://gdch.iptime.org:18000/statuses')
    return response.json().get('water_level_1'), response.json().get('water_level_2')

def check_water_levels(water_level_1, water_level_2, alert_counts, prev_levels, same_level_counts):
    if water_level_1 > VV1_HIGH or water_level_1 < VV1_LOW:
        alert_counts[0] += 1
    else:
        alert_counts[0] = 0

    if water_level_2 > VV2_HIGH or water_level_2 < VV2_LOW:
        alert_counts[1] += 1
    else:
        alert_counts[1] = 0

    if water_level_1 == prev_levels[0]:
        same_level_counts[0] += 1
    else:
        same_level_counts[0] = 1

    if water_level_2 == prev_levels[1]:
        same_level_counts[1] += 1
    else:
        same_level_counts[1] = 1

    if alert_counts[0] >= CONSECUTIVE_ALERT_COUNT:
        send_telegram_message(f'[문제발생] 출입구 아래 수위 : {water_level_1}')
        alert_counts[0] = 0

    if alert_counts[1] >= CONSECUTIVE_ALERT_COUNT:
        send_telegram_message(f'[문제발생] 주방 아래 수위 : {water_level_2}')
        alert_counts[1] = 0

    if same_level_counts[0] >= CONSECUTIVE_SAME_LEVEL_COUNT:
        send_telegram_message(f'[알림] 출입구 아래 수위 연속 동일: {water_level_1}')
        same_level_counts[0] = 0

    if same_level_counts[1] >= CONSECUTIVE_SAME_LEVEL_COUNT:
        send_telegram_message(f'[알림] 주방 아래 수위 연속 동일: {water_level_2}')
        same_level_counts[1] = 0

    return alert_counts, same_level_counts

def main():
    alert_counts = [0, 0]
    prev_levels = [0, 0]
    same_level_counts = [0, 0]

    while True:
        retry_count = RETRY_COUNT
        is_connection_ok = False

        while retry_count > 0:
            try:
                water_level_1, water_level_2 = get_water_levels()

                if water_level_1 == 0 or water_level_2 == 0:
                    continue

                alert_counts, same_level_counts = check_water_levels(water_level_1, water_level_2, alert_counts, prev_levels, same_level_counts)
                prev_levels = [water_level_1, water_level_2]
                is_connection_ok = True
                print(f'정상 water_level_1: {water_level_1}, water_level_2: {water_level_2}')
                break
            except:
                print('some error')
                time.sleep(SLEEP_DURATION)
            finally:
                retry_count -= 1

        if not is_connection_ok:
            send_telegram_message('[문제발생] 접속불가')

        time.sleep(SLEEP_DURATION)

if __name__ == '__main__':
    main()
