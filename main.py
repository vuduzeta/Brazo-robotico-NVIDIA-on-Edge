import time
from Arm_Lib import Arm_Device

Arm = Arm_Device()
time.sleep(.1)

def arm_retracted(s_time = 500):
    Arm.Arm_serial_servo_write(2, 130, s_time)
    time.sleep(.01)
    Arm.Arm_serial_servo_write(3, 0, s_time)
    time.sleep(.01)
    Arm.Arm_serial_servo_write(4, 0, s_time)
    time.sleep(.01)
    Arm.Arm_serial_servo_write(5, 90, int(s_time*1.2))
    time.sleep(s_time/1000)

def arm_center(s_time = 500):
    Arm.Arm_serial_servo_write(2, 66, s_time)
    time.sleep(.01)
    Arm.Arm_serial_servo_write(3, 20, s_time)
    time.sleep(.01)
    Arm.Arm_serial_servo_write(4, 29, s_time)
    time.sleep(.01)
    Arm.Arm_serial_servo_write(5, 270, int(s_time*1.2))
    time.sleep(s_time/1000)

def arm_extended(s_time = 500):
    Arm.Arm_serial_servo_write(2, 22, s_time)
    time.sleep(.01)
    Arm.Arm_serial_servo_write(3, 64, s_time)
    time.sleep(.01)
    Arm.Arm_serial_servo_write(4, 56, s_time)
    time.sleep(.01)
    Arm.Arm_serial_servo_write(5, 270, int(s_time*1.2))
    time.sleep(s_time/1000)

def arm_move_right(s_time = 500):
    Arm.Arm_serial_servo_write(1, 0, s_time)
    time.sleep(s_time/1000)

def arm_move_center(s_time = 500):
    Arm.Arm_serial_servo_write(1, 90, s_time)
    time.sleep(s_time/1000)

def arm_move_left(s_time = 500):
    Arm.Arm_serial_servo_write(1, 180, s_time)
    time.sleep(s_time/1000)

arm_extended(1000)
arm_move_right(1000)
arm_move_center(1000)
arm_move_left(1000)
time.sleep(2)
arm_center(1000)
arm_move_right(1000)
arm_move_center(1000)
arm_move_left(1000)
time.sleep(2)
arm_retracted(1000)
arm_move_right(1000)
arm_move_center(1000)
arm_move_left(1000)




