from machine import Pin, I2C
from m5stack import lcd
import time
import math

# BMX055のI2Cアドレス
BMX055_MAG_ADDRESS = 0x13
BMX055_ACC_ADDRESS = 0x19
BMX055_GYRO_ADDRESS = 0x69

# I2Cバスの初期化
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)

# BMX055センサーの初期化
def init_bmx055():
    # 加速度センサーの初期化
    i2c.writeto_mem(BMX055_ACC_ADDRESS, 0x0F, b'\x03')  # 2Gレンジで初期化
    i2c.writeto_mem(BMX055_ACC_ADDRESS, 0x10, b'\x0C')  # 出力データレートを100Hzに設定
    i2c.writeto_mem(BMX055_ACC_ADDRESS, 0x11, b'\x08')  # スリープモードを解除
    
    # ジャイロセンサーの初期化
    i2c.writeto_mem(BMX055_GYRO_ADDRESS, 0x0F, b'\x04')  # 2000dpsレンジで初期化
    i2c.writeto_mem(BMX055_GYRO_ADDRESS, 0x10, b'\x07')  # 出力データレートを100Hzに設定
    
    # 磁気センサーの初期化
    i2c.writeto_mem(BMX055_MAG_ADDRESS, 0x4B, b'\x83')     # パワーモードとデータレートを設定
    i2c.writeto_mem(BMX055_MAG_ADDRESS, 0x4C, b'\x00')     # レジスタAに書き込みを許可

# 加速度値の読み取り
def read_acceleration():
    data = i2c.readfrom_mem(BMX055_ACC_ADDRESS, 0x02, 6)  # 加速度データを読み取る
    x = int.from_bytes(data[0:2], 'little', True) / 16.0  # X軸の値（16ビット符号付整数）
    y = int.from_bytes(data[2:4], 'little', True) / 16.0  # Y軸の値（16ビット符号付整数）
    z = int.from_bytes(data[4:6], 'little', True) / 16.0  # Z軸の値（16ビット符号付整数）
    return (x, y, z)

# ジャイロ値の読み取り
def read_gyroscope():
    data = i2c.readfrom_mem(BMX055_GYRO_ADDRESS, 0x02, 6)  # ジャイロデータを読み取る
    x = int.from_bytes(data[0:2], 'little', True) / 131.0  # X軸の値（16ビット符号付整数）
    y = int.from_bytes(data[2:4], 'little', True) / 131.0  # Y軸の値（16ビット符号付整数）
    z = int.from_bytes(data[4:6], 'little', True) / 131.0  # Z軸の値（16ビット符号付整数）
    return (x, y, z)

# 磁気値の読み取り
def read_magnetometer():
    data = i2c.readfrom_mem(BMX055_MAG_ADDRESS, 0x42, 6)  # 磁気データを読み取る
    x = int.from_bytes(data[0:2], 'little', True) * 0.3  # X軸の値（16ビット符号付整数）
    y = int.from_bytes(data[2:4], 'little', True) * 0.3  # Y軸の値（16ビット符号付整数）
    z = int.from_bytes(data[4:6], 'little', True) * 0.3  # Z軸の値（16ビット符号付整数）
    return (x, y, z)

# 方位の計算
def calculate_heading(magnetometer):
    x, y, z = magnetometer
    heading = math.atan2(y, x)
    if heading < 0:
        heading += 2 * math.pi
    return math.degrees(heading)

# M5Stackの初期化
lcd.setRotation(3)

# BMX055センサーの初期化
init_bmx055()
lcd.clear()

# メインループ
while True:
    acceleration = read_acceleration()
    gyroscope = read_gyroscope()
    magnetometer = read_magnetometer()
    
    heading = calculate_heading(magnetometer)
    
    lcd.clear()
    lcd.print('Acceleration:', 0, 0)
    lcd.print('X: {:.2f} m/s^2'.format(acceleration[0]), 0, 20)
    lcd.print('Y: {:.2f} m/s^2'.format(acceleration[1]), 0, 40)
    lcd.print('Z: {:.2f} m/s^2'.format(acceleration[2]), 0, 60)
    
    lcd.print('Gyroscope:', 0, 100)
    lcd.print('X: {:.2f} dps'.format(gyroscope[0]), 0, 120)
    lcd.print('Y: {:.2f} dps'.format(gyroscope[1]), 0, 140)
    lcd.print('Z: {:.2f} dps'.format(gyroscope[2]), 0, 160)
    
    lcd.print('Magnetometer:', 0, 200)
    lcd.print('X: {:.2f} uT'.format(magnetometer[0]), 0, 220)
    lcd.print('Y: {:.2f} uT'.format(magnetometer[1]), 0, 240)
    lcd.print('Z: {:.2f} uT'.format(magnetometer[2]), 0, 260)
    
    lcd.print('Heading: {:.2f} deg'.format(heading), 0, 300)
    
    time.sleep(0.1)