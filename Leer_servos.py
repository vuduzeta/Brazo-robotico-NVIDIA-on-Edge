import os
import time
import sys
from Arm_Lib import Arm_Device

Arm = Arm_Device()
time.sleep(.1)

f = open("angles_servos.txt", "w")
j=1
while True:
    try:
        option = "s"
        Arm.Arm_serial_set_torque(0)
        f.write("radio%d = {"%j)
        for r in range(20):
            while option != "m":
                option = input("Presione la tecla M para memorizar...")
                if option == "m" or option == 'M':
                    angles = []
                    for i in range(2,6,1):
                        angles.append(Arm.Arm_serial_servo_read(i))
                    angles = list(reversed(angles))
                    f.write("\n    \"step%d\":"%(r+1) + "%s"%angles + ",")
            option = "s"
            print("Step%d finalizado."%(r+1))
        f.write("\n    }\n\n")
        print("Radio%d finalizado."%j)
        j+=1

    except KeyboardInterrupt:
        f.close()
        Arm.Arm_serial_set_torque(1)
        sys.exit("\nPrograma finalizado.\n")





