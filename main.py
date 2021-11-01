import os
import time
import argparse
import sys
import numpy as np

from Arm_Lib import Arm_Device
import cv2
import pycuda.autoinit  # This is needed for initializing CUDA driver
from utils.yolo_classes import get_cls_dict
from utils.camera import add_camera_args, Camera
from utils.display import open_window, set_display, show_fps
from utils.visualization import BBoxVisualization
from utils.yolo_with_plugins import TrtYOLO

Arm = Arm_Device()
time.sleep(.1)

#Función utilizada para retraer el brazo robótico.
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
    Arm.Arm_serial_servo_write(5, 270, int(s_time*1.2))
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
    Arm.Arm_serial_servo_write(1, 90, s_time)
    time.sleep(s_time/1000)

# Función utilizada para girar al centro el brazo robótico.
# El servo manipulado con esta función es S1.
# Ángulo del servo S1=90°.
# Entrada : entero que representa el tiempo de rotación del servo.
#           Cuanto mayor sea el valor de tiempo, más lenta será la rotación.
# Salida  : no retorna datos de salida.
def arm_turn_center(s_time = 500):
    Arm.Arm_serial_servo_write(1, 180, s_time)
    time.sleep(s_time/1000)

# Función utilizada para girar completamente a la izquierda el brazo robótico.
# El servo manipulado con esta función es S1.
# Ángulo del servo S1=180°.
# Entrada : entero que representa el tiempo de rotación del servo.
#           Cuanto mayor sea el valor de tiempo, más lenta será la rotación.
# Salida  : no retorna datos de salida.
def arm_turn_left(s_time = 500):
    Arm.Arm_serial_servo_write(1, 270, s_time)
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
    Arm.Arm_serial_servo_write6(180, 90, 90, 90, 90, 180, s_time)
    time.sleep(s_time/1000)

# Función utilizada para mover el brazo robótico a su posición inicial.
# Los servos manipulados con esta función son S1, S2, S3, S4, S5 y S6.
# Ángulo de los servos S1=90, S2=130°,S3=0°,S4=0° ,S5=90°, S6=90°.
# Entrada :
# Salida  : no retorna datos de salida.
def arm_pos_initial(s_time = 500):
    Arm.Arm_serial_servo_write6(180, 95, 0, 0, 90, 10, s_time)
    time.sleep(s_time/1000)

def parse_args():
    parser = argparse.ArgumentParser()
    parser = add_camera_args(parser)
    parser.add_argument('-c', '--category_num', type=int, default=80)
    parser.add_argument('-m', '--model', type=str, default='yolov4-416')
    parser.add_argument('-l', '--letter_box', action='store_true', default=True)
    args = parser.parse_args()
    return args

#**{'a':1,'b':2} -> 'a'=1, 'b'=2
#a=trt_scan(model='hola')
#{**dict1,**dict2}
#{'a':1,'b':2}, {'b':1,'c':2}
#{'a'=1, 'b'=1, 'c'=2}
#type(self)._current_model
#self._current_model

class trt_scan:
    def __init__(self,**kwargs):
        if not hasattr(type(self),'_current_args'):
            type(self)._current_args=parse_args()
        if not hasattr(type(self),'trt_yolo'):
            type(self).trt_yolo=TrtYOLO(type(self)._current_args.model, type(self)._current_args.category_num, type(self)._current_args.letter_box)
        if not hasattr(type(self),'cls_dict'):
            type(self).cls_dict=get_cls_dict(type(self)._current_args.category_num)
        self.WINDOW_NAME=kwargs.get('name','TrtYOLODemo')
        self.conf_th=kwargs.get('conf_th',0.3)
        self.vis=BBoxVisualization(type(self).cls_dict)
        return
    
    def run(self):
        cam = Camera(type(self)._current_args)
        img = cam.read()
        cv2.namedWindow(self.WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.setWindowTitle(self.WINDOW_NAME, self.WINDOW_NAME)
        cv2.resizeWindow(self.WINDOW_NAME, cam.img_width, cam.img_height)
        #open_window(WINDOW_NAME, 'Camera TensorRT YOLO Demo',cam.img_width, cam.img_height)
        if img is not None:
            boxes, confs, clss = type(self).trt_yolo.detect(img, self.conf_th)
            img =  self.vis.draw_bboxes(img, boxes, confs, clss)
            cv2.imshow(self.WINDOW_NAME, img)
            cv2.waitKey()
        cam.release()
        cv2.destroyAllWindows()
        return [clss.tolist(), confs.tolist(), boxes.tolist()]
    
    def __del__(self):
        return
        
def detect():
    return trt_scan().run()

def scan_objects(s_time = 500):
    items = []
    arm_pos_initial()
    arm_turn_right()
    for angle in range(45, 246, 40):
        Arm.Arm_serial_servo_write(1, angle, s_time)
        items.append(detect())
        items[len(items)-1].append(angle)
#        print('\n', angle)
#        print('\n', items)
    arm_pos_initial()
    time.sleep(s_time/1000)
    return items

def find_object(obj):
    det_objects = scan_objects()
    length = len(det_objects)
    for i in range(length):
        len_obj = len(det_objects[i][0])
        for j in range(len_obj):
            if det_objects[i][0][j] == obj:
                return [det_objects[i][2][j], det_objects[i][3]]
            else:
                return [[],-1]

def take_object(obj, s_time = 500):
    found_obj = find_object(obj)
    print('\n',found_obj,'\n')
    c_obj_x = (found_obj[0][2] - found_obj[0][0])/2+found_obj[0][0]
    c_obj_y = (found_obj[0][3] - found_obj[0][1])/2+found_obj[0][1]
    a_obj = found_obj[1]
    print(c_obj_x, c_obj_y, a_obj,'\n')
    crd_x = c_obj_x - (640/2)
    crd_y = 480 - c_obj_y
    radio = np.sqrt(crd_x**2 + crd_y**2)
    theta = np.degrees(np.arctan2(crd_y, crd_x))
    print(crd_x, crd_y, radio, theta,'\n')
    if (radio >= 0) and (radio < 146):
        a_servo = a_obj - 90 + theta
        Arm.Arm_serial_servo_write(5, 270, int(s_time*1.2))
        time.sleep(.01)
        Arm.Arm_serial_servo_write(4, 70, s_time)
        time.sleep(.01)
        Arm.Arm_serial_servo_write(1, a_servo, s_time)
        time.sleep(.5)
        Arm.Arm_serial_servo_write(2, 10, s_time)
        time.sleep(.01)
        Arm.Arm_serial_servo_write(3, 68, s_time)
        time.sleep(.01)
        Arm.Arm_serial_servo_write(4, 0, s_time)
        time.sleep(.01)
        time.sleep(s_time/1000)
    elif (radio > 145) and (radio < 243):
        a_servo = a_obj - 90 + theta
        Arm.Arm_serial_servo_write(5, 270, int(s_time*1.2))
        time.sleep(.01)
        Arm.Arm_serial_servo_write(4, 70, s_time)
        time.sleep(.01)
        Arm.Arm_serial_servo_write(1, a_servo, s_time)
        time.sleep(.5)
        Arm.Arm_serial_servo_write(2, 0, s_time)
        time.sleep(.01)
        Arm.Arm_serial_servo_write(3, 90, s_time)
        time.sleep(.01)
        Arm.Arm_serial_servo_write(4, 0, s_time)
        time.sleep(.01)
        time.sleep(s_time/1000)
    elif (radio > 242) and (radio < 340):
        a_servo = a_obj - 90 + theta
        Arm.Arm_serial_servo_write(5, 270, int(s_time*1.2))
        time.sleep(.01)
        Arm.Arm_serial_servo_write(4, 70, s_time)
        time.sleep(.01)
        Arm.Arm_serial_servo_write(1, a_servo, s_time)
        time.sleep(.5)
        Arm.Arm_serial_servo_write(2, 0, s_time)
        time.sleep(.01)
        Arm.Arm_serial_servo_write(3, 83, s_time)
        time.sleep(.01)
        Arm.Arm_serial_servo_write(4, 15, s_time)
        time.sleep(.01)
        time.sleep(s_time/1000)
    elif (radio > 339) and (radio < 434):
        a_servo = a_obj - 90 + theta
        Arm.Arm_serial_servo_write(5, 270, int(s_time*1.2))
        time.sleep(.01)
        Arm.Arm_serial_servo_write(4, 70, s_time)
        time.sleep(.01)
        Arm.Arm_serial_servo_write(1, a_servo, s_time)
        time.sleep(.5)
        Arm.Arm_serial_servo_write(2, 0, s_time)
        time.sleep(.01)
        Arm.Arm_serial_servo_write(3, 76, s_time)
        time.sleep(.01)
        Arm.Arm_serial_servo_write(4, 33, s_time)
        time.sleep(.01)
        time.sleep(s_time/1000)
    elif (radio > 433) and (radio < 481):
        a_servo = a_obj - 90 + theta
        Arm.Arm_serial_servo_write(5, 270, int(s_time*1.2))
        time.sleep(.01)
        Arm.Arm_serial_servo_write(4, 70, s_time)
        time.sleep(.01)
        Arm.Arm_serial_servo_write(1, a_servo, s_time)
        time.sleep(.5)
        Arm.Arm_serial_servo_write(2, 0, s_time)
        time.sleep(.01)
        Arm.Arm_serial_servo_write(3, 65, s_time)
        time.sleep(.01)
        Arm.Arm_serial_servo_write(4, 55, s_time)
        time.sleep(.01)
        time.sleep(s_time/1000)

# Función utilizada para hacer pruebas de las funciones con los distintos
# movimientos del brazo robótico.
# Entrada : sin datos de entrada.
# Salida  : no retorna datos de salida.
def menu():
    while True:
       # os.system('clear')
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
   10 Escanear.
   11 Servo 1 (Girar brazo).
   12 Servo 2.
   13 Servo 3.
   14 Servo 4.
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
        elif option == "10":
            take_object(39., 1000)              #39. corresponde a clase botella.
        elif option == "11":
            angle = int(input("Ingrese el ángulo: "))
            Arm.Arm_serial_servo_write(1, angle, 2000)
            time.sleep(2000/1000)
        elif option == "12":
            angle = int(input("Ingrese el ángulo: "))
            Arm.Arm_serial_servo_write(2, angle, 2000)
            time.sleep(2000/1000)
        elif option == "13":
            angle = int(input("Ingrese el ángulo: "))
            Arm.Arm_serial_servo_write(3, angle, 2000)
            time.sleep(2000/1000)
        elif option == "14":
            angle = int(input("Ingrese el ángulo: "))
            Arm.Arm_serial_servo_write(4, angle, 2000)
            time.sleep(2000/1000)
        elif option == "s":
            break
        elif option == "20":
            arm_turn_left(2000)
            time.sleep(2)
            arm_turn_right(2000)
        else:
            print("Opción inválida.")

if __name__ == '__main__':
    menu()






