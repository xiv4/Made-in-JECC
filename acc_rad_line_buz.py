import RPi.GPIO as GPIO
import tkinter as tk
import time
from mpu6050 import mpu6050
import keyboard
import requests

# 定数
ASSIGN_NUM_PIN = 23
BUZZER_PIN = 10
STR_NOTIFY_TOKEN = 'xJq84nSWGKPRyahHMJPMbm4YviW9f9jZERxu5tOsW3a'
STR_NOTICE_MESSAGE = '鍵！停車しています'
THRESHOLD = 1.0
STOP_THRESHOLD_SECONDS = 60

# グローバル変数
running = True
last_movement_time = time.time()

# センサーを初期化するための関数
def initialize_sensor():
    return mpu6050(0x68)

# キーボードイベントでスクリプトを終了する関数
def exit_script(e):
    global running
    running = False

# LINE通知を送信する関数
def send_line_notification(token, message):
    try:
        line_notify_api = 'https://notify-api.line.me/api/notify'
        headers = {'Authorization': f'Bearer {token}'}
        data = {'message': message}
        response = requests.post(line_notify_api, headers=headers, data=data)
        response.raise_for_status()
        print("LINE通知が送信されました")
    except requests.exceptions.RequestException as e:
        print(f"LINE通知の送信に失敗しました: {e}")

# ブザーの状態を切り替える関数
def toggle_buzzer(state):
    GPIO.output(BUZZER_PIN, state)

# バイクの動きを監視する関数
def monitor_bike_movement(sensor):
    global last_movement_time
    initial_accel_data = sensor.get_accel_data()  # ここで初期化
    buzzer_active = False

    keyboard.on_press_key("esc", exit_script)

    while running:
        accel_data = sensor.get_accel_data()

        x_diff = abs(accel_data['x'] - initial_accel_data['x'])
        y_diff = abs(accel_data['y'] - initial_accel_data['y'])
        z_diff = abs(accel_data['z'] - initial_accel_data['z'])

        if x_diff <= THRESHOLD and y_diff <= THRESHOLD and z_diff <= THRESHOLD:
            # バイクが動いていない場合
            if GPIO.input(ASSIGN_NUM_PIN) == GPIO.LOW:
                print("自転車が動いていませんが、赤外線モジュールが検知されました")
                current_time = time.time()
                if current_time - last_movement_time >= STOP_THRESHOLD_SECONDS:
                    print(f"停車しています。{STOP_THRESHOLD_SECONDS}秒以上経過")
                    if not buzzer_active:
                        send_line_notification(STR_NOTIFY_TOKEN, STR_NOTICE_MESSAGE)
                        toggle_buzzer(GPIO.LOW)
                        buzzer_active = True
                else:
                    # バイクが動いている場合はブザーをリセット
                    if buzzer_active:
                        toggle_buzzer(GPIO.HIGH)
                        buzzer_active = False

        elif x_diff > THRESHOLD or y_diff > THRESHOLD or z_diff > THRESHOLD:
            print("自転車が動いています")
            last_movement_time = time.time()
            # バイクが動いている場合はブザーをリセット
            if buzzer_active:
                toggle_buzzer(GPIO.HIGH)
                buzzer_active = False

        initial_accel_data = accel_data

        time.sleep(1.0)

    keyboard.unhook_all()
    
# GPIOのセットアップを行う関数
def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ASSIGN_NUM_PIN, GPIO.IN)
    GPIO.setup(BUZZER_PIN, GPIO.OUT)

# スクリプトを実行し続ける関数
def loop():
    try:
        sensor = initialize_sensor()  # センサーを初期化
        monitor_bike_movement(sensor)
    except KeyboardInterrupt:
        destroy()

# GPIOをクリーンアップする関数
def destroy():
    GPIO.cleanup()

# スクリプトがメインで実行されるかどうかを確認
if __name__ == '__main__':
    setup()
    loop()
