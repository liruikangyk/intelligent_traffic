#!/usr/bin/python
# -*- coding:utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import sys
import caffe
import os
import cv2
import glob
from caffe.proto import caffe_pb2
from google.protobuf import text_format
import rospy
from cv_bridge import CvBridge
from lrkmsg.msg import obj_info
from sensor_msgs.msg import Image
from std_msgs.msg import String
from lrk_server import myVehicleObject
import time

vehicleList = []


class carDetector:
    def __init__(self):
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber("lrk/image_with_car", Image, self.callback)
        self.image_sub = rospy.Subscriber("lrk/plate_single_car", String, self.plateCallback)
        self.pubobj = rospy.Publisher('/lrk/obj_info', obj_info, queue_size=10)
        self.pub = rospy.Publisher("lrk/image_single_car", Image, queue_size=10)
        self.blockFlag = 1
        self.waitCount = 0

    def blockClear(self):
        self.blockFlag = 1
        self.waitCount = 0

    def get_labelname(self, labelmap, labels):
        num_labels = len(labelmap.item)
        labelnames = []
        if type(labels) is not list:
            labels = [labels]
        for label in labels:
            found = False
            for i in xrange(0, num_labels):
                if label == labelmap.item[i].label:
                    found = True
                    labelnames.append(labelmap.item[i].display_name)
                    break
            assert found == True
        return labelnames

    def plateCallback(self, data):
        """
        @type data:String
        """
        tmpstr = data.data[7:]
        platestr = tmpstr.split(':')[0]
        # print tmpstr,platestr,len(platestr)
        if len(platestr) == 9:
            print platestr
            self.tmpVehicle.setPlateRoi(11, 12, 13, 14, 15, 16, 17, 18)
            self.tmpVehicle.setPlateRoiConf(-1)
            self.tmpVehicle.setPlateNum(platestr)
            self.tmpVehicle.setPlateNumConf(-1)
        else:
            print "Detection FAILED"
            self.tmpVehicle.setPlateRoi(11, 12, 13, 14, 15, 16, 17, 18)
            self.tmpVehicle.setPlateRoiConf(-1)
            self.tmpVehicle.setPlateNum("@@@@@@@@@")
            self.tmpVehicle.setPlateNumConf(-1)
        self.blockFlag = 1

    def callback(self, data):
        """
        @type data: Image
        """
        print "!!!getpic"

        image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        # image1 = cv2.resize(image, (1920, 1080))
        im_input = cv2.resize(image - np.array([104, 117, 123], dtype=np.float64),
                              (image_resize, image_resize)).transpose(2, 0, 1)
        im_input = im_input[np.newaxis, :, :, :]
        net.blobs['data'].data[...] = im_input
        detections = net.forward()['detection_out']
        det_label = detections[0, 0, :, 1]
        det_conf = detections[0, 0, :, 2]
        det_xmin = detections[0, 0, :, 3]
        det_ymin = detections[0, 0, :, 4]
        det_xmax = detections[0, 0, :, 5]
        det_ymax = detections[0, 0, :, 6]
        label_conf = zip(det_label, det_conf)
        top_indices = [i for i, conf in enumerate(label_conf) if conf[1] >= 0.3 and conf[0] in [2, 6, 7, 14]]
        top_conf = det_conf[top_indices]
        top_label_indices = det_label[top_indices].tolist()
        top_labels = self.get_labelname(labelmap, top_label_indices)
        # print top_labels
        top_xmin = det_xmin[top_indices]
        top_ymin = det_ymin[top_indices]
        top_xmax = det_xmax[top_indices]
        top_ymax = det_ymax[top_indices]
        # cv2.imshow('detection', image1)
        global vehicleList
        vehicleList = []
        for i in xrange(top_conf.shape[0]):
            xmin = int(round(top_xmin[i] * image.shape[1]))
            ymin = int(round(top_ymin[i] * image.shape[0]))
            xmax = int(round(top_xmax[i] * image.shape[1]))
            ymax = int(round(top_ymax[i] * image.shape[0]))
            score = top_conf[i]
            y0 = ymin - int(0.15 * (ymax - ymin))
            y0 = max(0, y0)
            xmin = max(0, xmin)
            if y0 >= ymax or xmin >= xmax:
                continue
            car_region = image[y0: ymax, xmin: xmax]

            self.tmpVehicle = myVehicleObject()
            if top_label_indices[i] == 2:
                self.tmpVehicle.setObjType(myVehicleObject.VEHICLE_TYPE_NONE_MOTORIZED)
            elif top_label_indices[i] == 6:
                self.tmpVehicle.setObjType(myVehicleObject.VEHICLE_TYPE_BUS)
            elif top_label_indices[i] == 7:
                self.tmpVehicle.setObjType(myVehicleObject.VEHICLE_TYPE_CAR)
            elif top_label_indices[i] == 14:
                self.tmpVehicle.setObjType(myVehicleObject.VEHICLE_TYPE_MOTORBIKE)
            else:
                self.tmpVehicle.setObjType(myVehicleObject.VEHICLE_TYPE_UNKNOWN)
            self.tmpVehicle.setObjDirection(20)
            self.tmpVehicle.setObjState(-1)
            self.tmpVehicle.setObjRoi(xmin, y0, xmax, y0, xmin, ymax, xmax, ymax)
            print score
            self.tmpVehicle.setObjRoiConf(score)

            self.pub.publish(self.bridge.cv2_to_imgmsg(car_region, "bgr8"))

            self.blockFlag = 0
            while self.blockFlag == 0:
                time.sleep(1)
                print "blocking...", self.blockFlag, self.waitCount
                self.waitCount = self.waitCount + 1
            print "block over"
            self.blockClear()
            vehicleList.append(self.tmpVehicle)
            print i
        print "last phase"
        abc = obj_info()
        tmpstrobj = ""
        for item in vehicleList:
            tmpstrobj = tmpstrobj + item.getPack()
        print len(tmpstrobj)
        abc.obj_info = tmpstrobj
        self.pubobj.publish(abc)
        print "obj info published"


if __name__ == "__main__":
    rospy.init_node('lrk_cardetect')
    caffe_root = '/home/lrk/caffe/'
    sys.path.insert(0, caffe_root + 'python')
    num_classes = 20
    colorshsv = plt.cm.hsv(np.linspace(0, 1, num_classes)).tolist()
    colorsh = np.array([i[0:3] for i in colorshsv]) * 255
    colors = np.array(colorsh, dtype='uint8')
    font = cv2.FONT_HERSHEY_SIMPLEX
    os.chdir(caffe_root)
    labelmap_file = caffe_root + 'models/VGGNet/labelmap_voc.prototxt'
    file = open(labelmap_file, 'r')
    labelmap = caffe_pb2.LabelMap()
    text_format.Merge(str(file.read()), labelmap)
    model_def = caffe_root + 'models/VGGNet/VOC0712/SSD_300x300/deploy.prototxt'
    model_weights = caffe_root + 'models/VGGNet/VOC0712/SSD_300x300/VGG_VOC0712_SSD_300x300_iter_120000.caffemodel'
    net = caffe.Net(model_def, model_weights, caffe.TEST)
    image_resize = 300
    net.blobs['data'].reshape(1, 3, image_resize, image_resize)
    picname = glob.glob('/home/lrk/caffetest/*.jpg')
    testcardetector = carDetector()
    rospy.spin()
