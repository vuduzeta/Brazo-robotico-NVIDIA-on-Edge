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

def arm_clamp(enable):
    if enable == 0:
        Arm.Arm_serial_servo_write(6, 60, 400)
    else:
        Arm.Arm_serial_servo_write(6, 135, 400)
    time.sleep(.5)

def arm_calibration(s_time):
    Arm.Arm_serial_servo_write6(90, 90, 90, 90, 90, 180, s_time)
    time.sleep(s_time/1000)

def arm_pos_initial(s_time):
    Arm.Arm_serial_servo_write6(90, 130, 0, 0, 90, 90, s_time)
    time.sleep(s_time/1000)

arm_pos_initial(1000)
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
time.sleep(2)
for i in range(5):
    arm_clamp(0)
    arm_clamp(1)
time.sleep(2)
arm_calibration(1000)
time.sleep(2)
arm_pos_initial(1000)



