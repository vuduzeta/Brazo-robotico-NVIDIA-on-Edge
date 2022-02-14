import os
import time as tt
import argparse
import sys
import numpy as np
import json
import Jetson.GPIO as GPIO
from datetime import datetime

from Arm_Lib import Arm_Device
import cv2
import pycuda.autoinit  # This is needed for initializing CUDA driver
from utils.yolo_classes import get_cls_dict
from utils.camera import add_camera_args, Camera
from utils.display import open_window, set_display, show_fps
from utils.visualization import BBoxVisualization
from utils.yolo_with_plugins import TrtYOLO
import position_dict


Arm = Arm_Device()
tt.sleep(.1)

switch = 12
solenoid = 22
pump = 19
GPIO.setmode(GPIO.BOARD)
GPIO.setup(switch, GPIO.IN)
GPIO.setup(solenoid, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(pump, GPIO.OUT, initial=GPIO.LOW)

def arm_retracted(t_servo=500):
    t_delay = .01
    Arm.Arm_serial_servo_write(2, 71, t_servo)
    tt.sleep(t_delay)
    Arm.Arm_serial_servo_write(3, 75, t_servo)
    tt.sleep(t_delay)
    Arm.Arm_serial_servo_write(4, 72, t_servo)
    tt.sleep(t_delay)
    Arm.Arm_serial_servo_write(5, 2, t_servo)
    tt.sleep(t_servo/1000)

def arm_center(s_time = 500):
    Arm.Arm_serial_servo_write(2, 66, s_time)
    tt.sleep(.01)
    Arm.Arm_serial_servo_write(3, 20, s_time)
    tt.sleep(.01)
    Arm.Arm_serial_servo_write(4, 29, s_time)
    tt.sleep(.01)
    Arm.Arm_serial_servo_write(5, 90, int(s_time*1.2))
    tt.sleep(s_time/1000)

def arm_extended(s_time = 500):
    Arm.Arm_serial_servo_write(2, 22, s_time)
    tt.sleep(.01)
    Arm.Arm_serial_servo_write(3, 64, s_time)
    tt.sleep(.01)
    Arm.Arm_serial_servo_write(4, 56, s_time)
    tt.sleep(.01)
    Arm.Arm_serial_servo_write(5, 90, int(s_time*1.2))
    tt.sleep(s_time/1000)

def arm_turn_right(s_time = 500):
    Arm.Arm_serial_servo_write(1, 0, s_time)
    tt.sleep(s_time/1000)

def arm_turn_center(s_time = 500):
    Arm.Arm_serial_servo_write(1, 90, s_time)
    tt.sleep(s_time/1000)

def arm_turn_left(s_time = 500):
    Arm.Arm_serial_servo_write(1, 180, s_time)
    tt.sleep(s_time/1000)


def arm_gripper(pos_gripper = 60, pos_wrist = 270, s_time = 400 ):
    Arm.Arm_serial_servo_write(5,pos_wrist, s_time)
    tt.sleep(.01)
    Arm.Arm_serial_servo_write(6, pos_gripper, s_time)
    tt.sleep(s_time/1000)


def arm_calibration(s_time = 1000):
    Arm.Arm_serial_servo_write6(90, 90, 90, 90, 90, 180, s_time)
    tt.sleep(s_time/1000)

def arm_pos_initial(s_time = 500):
    Arm.Arm_serial_servo_write(5,160, s_time)
    tt.sleep(1)
    Arm.Arm_serial_servo_write6(0, 92, 37, 2, 91, 10, s_time)
    tt.sleep(s_time/1000)

def arm_pos_capture(angle_s1, s_time = 500):
    Arm.Arm_serial_servo_write(5,160, s_time)
    tt.sleep(1)
    Arm.Arm_serial_servo_write6(angle_s1, 92, 37, 3, 91, 10, s_time)
    tt.sleep(s_time/500)

def parse_args():
    parser = argparse.ArgumentParser()
    parser = add_camera_args(parser)
    parser.add_argument('-c', '--category_num', type=int, default=5)
    parser.add_argument('-m', '--model', type=str, default='yolov4-416')
    parser.add_argument('-l', '--letter_box', action='store_true', default=True)
    args = parser.parse_args()
    return args

class result_file():
    def __init__(self,**kwargs):
        self._data = {}

    def create_json(self, _list):
        self._data[_list[0]] = {}

        self._data[_list[0]]["date"] = _list[1]
        self._data[_list[0]]["start_time"] = _list[2]
        self._data[_list[0]]["finished_time"] = _list[3]
        self._data[_list[0]]["number_items"] = _list[4][0]
        bagged = []
        for i in range(len(_list[4])):
            item = {}
            if i != 0:
                item["id_item"] = _list[4][i][0]
                item["confidentiality"] = _list[4][i][1]
                bagged.append(item)
        self._data[_list[0]]["bagged_items"] = bagged
    #    self._data[_list[0]] = [self._data[_list[0]]]
        return

    def get_data(self):
        return self._data

class trt_scan():
    def __init__(self,**kwargs):
        if not hasattr(type(self),'_current_args'):
            type(self)._current_args=parse_args()
        if not hasattr(type(self),'trt_yolo'):
            type(self).trt_yolo=TrtYOLO(type(self)._current_args.model, type(self)._current_args.category_num, type(self)._current_args.letter_box)
        if not hasattr(type(self),'cls_dict'):
            type(self).cls_dict=get_cls_dict(type(self)._current_args.category_num)
        #print(type(self).cls_dict)
        #self.WINDOW_NAME=kwargs.get('name','TrtYOLODemo')
        self.conf_th=kwargs.get('conf_th',0.6)
        self.vis=BBoxVisualization(type(self).cls_dict)
        return
    
    def run(self):
        cam = Camera(type(self)._current_args)
        img = cam.read()
        #cv2.namedWindow(self.WINDOW_NAME, cv2.WINDOW_NORMAL)
        #cv2.setWindowTitle(self.WINDOW_NAME, self.WINDOW_NAME)
        #cv2.resizeWindow(self.WINDOW_NAME, cam.img_width, cam.img_height)
        #######open_window(WINDOW_NAME, 'Camera TensorRT YOLO Demo',cam.img_width, cam.img_height)
        if img is not None:
            boxes, confs, clss = type(self).trt_yolo.detect(img, self.conf_th)
        #    img =  self.vis.draw_bboxes(img, boxes, confs, clss)
        #    cv2.imshow(self.WINDOW_NAME, img)
        #    cv2.waitKey()
        cam.release()
        #cv2.destroyAllWindows()
        return clss.tolist(), confs.tolist(), boxes.tolist()
    
    def __del__(self):
        return

def detect_items():
    return trt_scan().run()

def position_servo(values, t_servo):
    for i in range(len(values)):
        #print("Paso: ", i)
        if values[i] != False:
            tt.sleep(.01)
            read = Arm.Arm_serial_servo_read(i+1)
            #print("Lectura: ", read)
            tt.sleep(.01)
            while (read == None) or not (read >= values[i]-5 and read <= values[i]+5):
                Arm.Arm_serial_servo_write(i+1, values[i], t_servo)
                tt.sleep(.01)
                read = Arm.Arm_serial_servo_read(i+1)
                tt.sleep(.01)
    tt.sleep(.2)
    return

def touch_item():
    if(GPIO.input(switch) == 1):
        tt.sleep(0.020)
        if(GPIO.input(switch) == 1):
            return True
    if(GPIO.input(switch) == 0):
        tt.sleep(0.020)
        if(GPIO.input(switch) == 0):
            return False

def vacuum():
    t_suction = 3.5
    GPIO.output(pump, GPIO.HIGH)
    tt.sleep(t_suction)
    return

def drop_item():
    t_solenoid = 1.5
    GPIO.output(pump, GPIO.LOW)
    GPIO.output(solenoid, GPIO.HIGH)
    tt.sleep(t_solenoid)
    GPIO.output(solenoid, GPIO.LOW)
    return

def put_item_bag():
    t_servo = 600
    t_spin = 2000
    arm_retracted(2000)
    Arm.Arm_serial_servo_write(1, 245, t_spin)
    tt.sleep(.01)
    position_servo([245, False, False, False, False, False], t_spin)
    #print("Posss...")
    for value in position_dict.put_in_bag0.values():
            Arm.Arm_serial_servo_write(5, value[0], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(4, value[1], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(3, value[2], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(2, value[3], t_servo)
            tt.sleep(.01)
            position_servo([False, value[3],value[2],value[1],value[0],False], t_servo)
    drop_item()
    for value in position_dict.put_in_bag1.values():
            Arm.Arm_serial_servo_write(5, value[0], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(4, value[1], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(3, value[2], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(2, value[3], t_servo)
            tt.sleep(.01)
            position_servo([False, value[3],value[2],value[1],value[0],False], t_servo)
    return

def polar_coord(box):
    adj_error_x = 0
    adj_error_y = 0
    cord_item_x = (box[2] - box[0])/2 + box[0]
    cord_item_y = (box[3] - box[1])/2 + box[1]
    cord_x = cord_item_x - (640/2) + adj_error_x
    cord_y = 480 - cord_item_y + adj_error_y
    radio = np.sqrt(cord_x**2 + cord_y**2)
    theta = np.degrees(np.arctan2(cord_y, cord_x))
    return radio, theta

def take_item(box, angle):
    t_servo = 500
    t_rotate = 500
    radio, theta = polar_coord(box)
    #print("RADIO: ",radio)
    #print("TETHA: ",theta)
    ## 2.9 pixeles por mm aprox.
    ## 14.5 pixeles cada 5 mm
    ## 29 pixeles cada 10 mm
    ## 109.5 ---> 138.5

    if (radio >= 0) and (radio <= 185.875):
        angle_s1 = angle - 90 + theta
        Arm.Arm_serial_servo_write(1, angle_s1, t_rotate)
        for value in position_dict.radio13.values():
            Arm.Arm_serial_servo_write(5, value[0], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(4, value[1], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(3, value[2], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(2, value[3], t_servo)
            tt.sleep(.01)
#            tt.sleep(.7)
            position_servo([False, value[3],value[2],value[1],value[0],False], t_servo)
            if touch_item():
                vacuum()
                put_item_bag()
                return True
        return False

    if (radio > 185.875) and (radio <= 209.405):
        angle_s1 = angle - 90 + theta
        Arm.Arm_serial_servo_write(1, angle_s1, t_rotate)
        for value in position_dict.radio12.values():
            Arm.Arm_serial_servo_write(5, value[0], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(4, value[1], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(3, value[2], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(2, value[3], t_servo)
            tt.sleep(.01)
#            tt.sleep(.7)
            position_servo([False, value[3],value[2],value[1],value[0],False], t_servo)
            if touch_item():
                vacuum()
                put_item_bag()
                return True
        return False

    if (radio > 209.405) and (radio <= 232.935):
        angle_s1 = angle - 90 + theta
        Arm.Arm_serial_servo_write(1, angle_s1, t_rotate)
        for value in position_dict.radio11.values():
            Arm.Arm_serial_servo_write(5, value[0], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(4, value[1], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(3, value[2], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(2, value[3], t_servo)
            tt.sleep(.01)
            position_servo([False, value[3],value[2],value[1],value[0],False], t_servo)
            if touch_item():
                vacuum()
                put_item_bag()
                return True
        return False

    if (radio > 232.935) and (radio <= 256.465):
 
        angle_s1 = angle - 90 + theta
        Arm.Arm_serial_servo_write(1, angle_s1, t_rotate)
        for value in position_dict.radio10.values():
            Arm.Arm_serial_servo_write(5, value[0], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(4, value[1], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(3, value[2], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(2, value[3], t_servo)
            tt.sleep(.01)
            position_servo([False, value[3],value[2],value[1],value[0],False], t_servo)
            if touch_item():
                vacuum()
                put_item_bag()
                return True
        return False

    if (radio > 256.465) and (radio <= 279.995):
        angle_s1 = angle - 90 + theta
        Arm.Arm_serial_servo_write(1, angle_s1, t_rotate)
        for value in position_dict.radio9.values():
            Arm.Arm_serial_servo_write(5, value[0], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(4, value[1], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(3, value[2], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(2, value[3], t_servo)
            tt.sleep(.01)
            position_servo([False, value[3],value[2],value[1],value[0],False], t_servo)
            if touch_item():
                vacuum()
                put_item_bag()
                return True
        return False

    if (radio > 279.995) and (radio <= 303.525):
        angle_s1 = angle - 90 + theta
        Arm.Arm_serial_servo_write(1, angle_s1, t_rotate)
        for value in position_dict.radio8.values():
            Arm.Arm_serial_servo_write(5, value[0], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(4, value[1], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(3, value[2], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(2, value[3], t_servo)
            tt.sleep(.01)
            position_servo([False, value[3],value[2],value[1],value[0],False], t_servo)
            if touch_item():
                vacuum()
                put_item_bag()
                return True
        return False

    if (radio > 303.525) and (radio <= 327.055):
        angle_s1 = angle - 90 + theta
        Arm.Arm_serial_servo_write(1, angle_s1, t_rotate)
        for value in position_dict.radio7.values():
            #print(value)
            Arm.Arm_serial_servo_write(5, value[0], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(4, value[1], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(3, value[2], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(2, value[3], t_servo)
            tt.sleep(.01)
            position_servo([False, value[3],value[2],value[1],value[0],False], t_servo)
            if touch_item():
                vacuum()
                put_item_bag()
                return True
        return False

    if (radio > 327.055) and (radio <= 350.585):
        angle_s1 = angle - 90 + theta
        Arm.Arm_serial_servo_write(1, angle_s1, t_rotate)
        for value in position_dict.radio6.values():
            Arm.Arm_serial_servo_write(5, value[0], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(4, value[1], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(3, value[2], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(2, value[3], t_servo)
            tt.sleep(.01)
            position_servo([False, value[3],value[2],value[1],value[0],False], t_servo)
            if touch_item():
                vacuum()
                put_item_bag()
                return True
        return False

    if (radio > 350.585) and (radio <= 374.115):
        angle_s1 = angle - 90 + theta
        Arm.Arm_serial_servo_write(1, angle_s1, t_rotate)
        for value in position_dict.radio5.values():
            Arm.Arm_serial_servo_write(5, value[0], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(4, value[1], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(3, value[2], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(2, value[3], t_servo)
            tt.sleep(.01)
            position_servo([False, value[3],value[2],value[1],value[0],False], t_servo)
            if touch_item():
                vacuum()
                put_item_bag()
                return True
        return False

    if (radio > 374.115) and (radio <= 397.645):
        angle_s1 = angle - 90 + theta
        Arm.Arm_serial_servo_write(1, angle_s1, t_rotate)
        for value in position_dict.radio4.values():
            Arm.Arm_serial_servo_write(5, value[0], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(4, value[1], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(3, value[2], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(2, value[3], t_servo)
            tt.sleep(.01)
            position_servo([False, value[3],value[2],value[1],value[0],False], t_servo)
            if touch_item():
                vacuum()
                put_item_bag()
                return True
        return False

    if (radio > 397.645) and (radio <= 421.175):
        angle_s1 = angle - 90 + theta
        Arm.Arm_serial_servo_write(1, angle_s1, t_rotate)
        for value in position_dict.radio3.values():
            Arm.Arm_serial_servo_write(5, value[0], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(4, value[1], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(3, value[2], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(2, value[3], t_servo)
            tt.sleep(.01)
            position_servo([False, value[3],value[2],value[1],value[0],False], t_servo)
            if touch_item():
                vacuum()
                put_item_bag()
                return True
        return False

    if (radio > 421.175) and (radio <= 444.705):
        angle_s1 = angle - 90 + theta
        Arm.Arm_serial_servo_write(1, angle_s1, t_rotate)
        for value in position_dict.radio2.values():
            Arm.Arm_serial_servo_write(5, value[0], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(4, value[1], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(3, value[2], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(2, value[3], t_servo)
            tt.sleep(.01)
            position_servo([False, value[3],value[2],value[1],value[0],False], t_servo)
            if touch_item():
                vacuum()
                put_item_bag()
                return True
        return False

    if (radio > 444.705) and (radio <= 468.235):
        angle_s1 = angle - 90 + theta
        Arm.Arm_serial_servo_write(1, angle_s1, t_rotate)
        for value in position_dict.radio1.values():
            Arm.Arm_serial_servo_write(5, value[0], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(4, value[1], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(3, value[2], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(2, value[3], t_servo)
            tt.sleep(.01)
            position_servo([False, value[3],value[2],value[1],value[0],False], t_servo)
            if touch_item():
                vacuum()
                put_item_bag()
                return True
        return False

    if (radio > 468.235) and (radio <= 480.0):
        angle_s1 = angle - 90 + theta
        Arm.Arm_serial_servo_write(1, angle_s1, t_rotate)
        for value in position_dict.radio0.values():
            Arm.Arm_serial_servo_write(5, value[0], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(4, value[1], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(3, value[2], t_servo)
            tt.sleep(.01)
            Arm.Arm_serial_servo_write(2, value[3], t_servo)
            tt.sleep(.01)
            position_servo([False, value[3],value[2],value[1],value[0],False], t_servo)
            if touch_item():
                vacuum()
                put_item_bag()
                return True
        return False

def search_items(current_items):
    t_servo1 = 500
    t_servo = 1000
    list_items = current_items
    list_angles = [20, 80, 140]
    list_items_bagged = []
    number_bagged = 0
    arm_pos_initial(t_servo)
    for angle_s1 in list_angles:
        Arm.Arm_serial_servo_write(1, angle_s1, t_servo1)
        tt.sleep(.01)
        list_clss, list_confs, list_boxes = detect_items()
        for clss, confs, boxes in zip(list_clss, list_confs, list_boxes):
            for current_item in list_items:
                if (clss == current_item["id_item"]) and (current_item["quantity"] > 0):
                    bagged = take_item(boxes, angle_s1)
                    if bagged == True:
                        list_items_bagged.append([clss, confs])
                        current_item["quantity"] -= 1
                        number_bagged += 1
                        arm_pos_capture(angle_s1, t_servo)
                    else:
                        arm_pos_capture(angle_s1, t_servo)
    list_items_bagged.insert(0,number_bagged)
    return list_items_bagged

def main():
    os.system('clear')
    output_file = []
    input_file = open("bag.json")
    bag_list = json.load(input_file)
    object_result_file = result_file()

    for current_bag in bag_list:
        print("Embolsado N°: %d"%current_bag["id_bag"])
        output_file.append(current_bag["id_bag"])
        dateTime = datetime.now()
        date = dateTime.strftime("%d-%b-%Y")
        time = dateTime.strftime("%H:%M:%S")
        output_file.append(date)
        output_file.append(time)
        out_items = search_items(current_bag["items"])
        dateTime = datetime.now()
        time = dateTime.strftime("%H:%M:%S")
        output_file.append(time)
        output_file.append(out_items)
        object_result_file.create_json(output_file)
        print("Embolsado %d finalizado."%current_bag["id_bag"])
        output_file = []
        tt.sleep(20.0)
    with open('/home/jetson/Desktop/bagged.json', 'w') as json_file:
        json.dump(object_result_file.get_data(), json_file)
    input_file.close()
    print("Creado el archivo de salida.")
    GPIO.cleanup()
    return

if __name__ == '__main__':
    main()
 




