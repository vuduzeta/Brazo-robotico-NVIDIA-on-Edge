import time
from Arm_Lib import Arm_Device
import os

Arm = Arm_Device()
time.sleep(.1)

# Función utilizada para retraer el brazo robótico.
# Los servos manipulados con esta función son S2, S3, S4 y S5.
# Ángulo de los servos S2=130°,S3=0°,S4=0° ,S5=90°.
# Entrada : entero que representa el tiempo de rotación de los servos.
#           Cuanto mayor sea el valor de tiempo, más lenta será la rotación.
# Salida  : no retorna datos de salida.
def arm_retracted(s_time = 500):
    Arm.Arm_serial_servo_write(2, 130, s_time)
    time.sleep(.01)
    Arm.Arm_serial_servo_write(3, 0, s_time)
    time.sleep(.01)
    Arm.Arm_serial_servo_write(4, 0, s_time)
    time.sleep(.01)
    Arm.Arm_serial_servo_write(5, 90, int(s_time*1.2))
    time.sleep(s_time/1000)

# Función utilizada para extender el brazo robótico al centro.
# Los servos manipulados con esta función son S2, S3, S4 y S5.
# Ángulo de los servos S2=66°,S3=20°,S4=29° ,S5=270°.
# Entrada : entero que representa el tiempo de rotación de los servos.
#           Cuanto mayor sea el valor de tiempo, más lenta será la rotación.
# Salida  : no retorna datos de salida.
def arm_center(s_time = 500):
    Arm.Arm_serial_servo_write(2, 66, s_time)
    time.sleep(.01)
    Arm.Arm_serial_servo_write(3, 20, s_time)
    time.sleep(.01)
    Arm.Arm_serial_servo_write(4, 29, s_time)
    time.sleep(.01)
    Arm.Arm_serial_servo_write(5, 270, int(s_time*1.2))
    time.sleep(s_time/1000)

# Función utilizada para extender completamente el brazo robótico.
# Los servos manipulados con esta función son S2, S3, S4 y S5.
# Ángulo de los servos S2=22°,S3=64°,S4=56° ,S5=270°.
# Entrada : entero que representa el tiempo de rotación de los servos.
#           Cuanto mayor sea el valor de tiempo, más lenta será la rotación.
# Salida  : no retorna datos de salida.
def arm_extended(s_time = 500):
    Arm.Arm_serial_servo_write(2, 22, s_time)
    time.sleep(.01)
    Arm.Arm_serial_servo_write(3, 64, s_time)
    time.sleep(.01)
    Arm.Arm_serial_servo_write(4, 56, s_time)
    time.sleep(.01)
    Arm.Arm_serial_servo_write(5, 270, int(s_time*1.2))
    time.sleep(s_time/1000)

# Función utilizada para girar completamente a la derecha el brazo robótico.
# El servo manipulado con esta función es S1.
# Ángulo del servo S1=0°.
# Entrada : entero que representa el tiempo de rotación del servo.
#           Cuanto mayor sea el valor de tiempo, más lenta será la rotación.
# Salida  : no retorna datos de salida.
def arm_turn_right(s_time = 500):
    Arm.Arm_serial_servo_write(1, 0, s_time)
    time.sleep(s_time/1000)

# Función utilizada para girar al centro el brazo robótico.
# El servo manipulado con esta función es S1.
# Ángulo del servo S1=90°.
# Entrada : entero que representa el tiempo de rotación del servo.
#           Cuanto mayor sea el valor de tiempo, más lenta será la rotación.
# Salida  : no retorna datos de salida.
def arm_turn_center(s_time = 500):
    Arm.Arm_serial_servo_write(1, 90, s_time)
    time.sleep(s_time/1000)

# Función utilizada para girar completamente a la izquierda el brazo robótico.
# El servo manipulado con esta función es S1.
# Ángulo del servo S1=180°.
# Entrada : entero que representa el tiempo de rotación del servo.
#           Cuanto mayor sea el valor de tiempo, más lenta será la rotación.
# Salida  : no retorna datos de salida.
def arm_turn_left(s_time = 500):
    Arm.Arm_serial_servo_write(1, 180, s_time)
    time.sleep(s_time/1000)

# Función utilizada para manipular la pinza y la muñeca de la mano.
# Los servos manipulados con esta función son S5 (muñeca), S6 (pinza).
# Entradas: entero que representa el ángulo de giro de la pinza. S5=0° a 360°.
#           entero que representa el ángulo de giro de la muñeca. S6=0° a 180°.
#           entero que representa el tiempo de rotación del servo.
#           Cuanto mayor sea el valor de tiempo, más lenta será la rotación.
# Salida  : no retorna datos de salida.
def arm_gripper(pos_gripper = 60, pos_wrist = 270, s_time = 400 ):
    Arm.Arm_serial_servo_write(5,pos_wrist, s_time)
    time.sleep(.01)
    Arm.Arm_serial_servo_write(6, pos_gripper, s_time)
    time.sleep(s_time/1000)

# Función utilizada mover el brazo robótico a su posición de calibración.
# Los servos manipulados con esta función son S1, S2, S3, S4, S5 y S6.
# Ángulo de los servos S1=90°, S2=90°,S3=90°,S4=90° ,S5=90°, S6=180°.
# Entrada :
# Salida  : no retorna datos de salida.
def arm_calibration(s_time = 500):
    Arm.Arm_serial_servo_write6(90, 90, 90, 90, 90, 180, s_time)
    time.sleep(s_time/1000)

# Función utilizada para mover el brazo robótico a su posición inicial.
# Los servos manipulados con esta función son S1, S2, S3, S4, S5 y S6.
# Ángulo de los servos S1=90, S2=130°,S3=0°,S4=0° ,S5=90°, S6=90°.
# Entrada :
# Salida  : no retorna datos de salida.
def arm_pos_initial(s_time = 500):
    Arm.Arm_serial_servo_write6(90, 130, 0, 0, 90, 90, s_time)
    time.sleep(s_time/1000)

# Función utilizada para hacer pruebas de las funciones con los distintos
# movimientos del brazo robótico.
# Entrada : sin datos de entrada.
# Salida  : no retorna datos de salida.
def menu():
    while True:
        os.system('clear')
        text = '''
Para manipular el brazo robótico debe elegir una de las siguientes ópciones:

   1 Retraer el brazo.
   2 Extender al centro el brazo.
   3 Extender completamente el brazo.     
   4 Girar el brazo a la derecha.
   5 Girar el brazo al centro.
   6 Girar el brazo a la izquierda.
   7 Manipular la pinza.
   8 Posición de calibración.
   9 Posición inicial.
   s Salir.
'''
        print(text)
        option = input("Selecciona una opción: ")

        if option == "1":
            arm_retracted()
        elif option == "2":
            arm_center()
        elif option == "3":
            arm_extended()
        elif option == "4":
            arm_turn_right()
        elif option == "5":
            arm_turn_center()
        elif option == "6":
            arm_turn_left()
        elif option == "7":
            while True:
                pos_gripper = int(input("Ingrese el ángulo de la pinza: "))
                if pos_gripper >= 0 and pos_gripper <181:
                    while True:
                        pos_wrist = int(input("Ingrese el ángulo de la muñeca: "))
                        if pos_wrist >= 0 and pos_wrist <361:
                            arm_gripper(pos_gripper,pos_wrist)
                            break
                        else:
                            print("Ingrese un ángulo correcto para la muñeca.")
                    break
                else:
                    print("Ingrese un ángulo correcto para la pinza.")
        elif option == "8":
            arm_calibration()
        elif option == "9":
            arm_pos_initial()
        elif option == "s":
            break
        else:
            print("Opción inválida.")

if __name__ == '__main__':
    menu()






