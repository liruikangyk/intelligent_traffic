# -*- coding:utf-8 -*-
import time
from struct import pack, unpack
import rospy
from cv_bridge import CvBridge, CvBridgeError
from lrkmsg.msg import obj_info, cmd_info, image_info, blk_info
from sensor_msgs.msg import Image
from lrk_server import myVehicleObject

imageFIFO = []


class signalWaiter():
    def __init__(self):
        self.blockSigName = ""
        self.blockSigFlag = 1
        self.waitCount = 0

    def waitForSig(self, insigname):
        self.blockSigFlag = 0
        self.blockSigName = insigname
        self.waitCount = 0
        while self.blockSigFlag == 0:
            time.sleep(1)
            print "Waiting for signal ::", self.blockSigName, self.blockSigFlag, self.waitCount
            self.waitCount = self.waitCount + 1
        print "Block Signal Received!"
        self.__init__()


class blkInfo_subscriber:
    def __init__(self):
        self.sub = rospy.Subscriber("/lrk/blk_info", blk_info, self.callback)
        self.signalWaiter = signalWaiter()

    def callback(self, data):
        """
        @type data: blk_info
        """
        if data.blockString == self.signalWaiter.blockSigName:
            self.signalWaiter.blockSigFlag = 1


def showFIFOcontents():
    for item in imageFIFO:
        print str(item.timeStamp).split('.')[0][-2:] + '.' + str(item.timeStamp).split('.')[1][:2],
        # print item.timeStamp


def getMostNearImage(intime):
    delta_prev = 500
    delta = 500
    tmp = []
    for item in imageFIFO:
        delta = abs(item.timeStamp - intime)
        if delta > delta_prev:
            tmp = item
            print(imageFIFO.index(item))
            break
        delta_prev = delta
    if tmp != []:
        return tmp
    else:
        return imageFIFO[-1]


class cmdInfo_subscriber:
    def __init__(self):
        self.bridge = CvBridge()
        self.sub = rospy.Subscriber("/lrk/cmd_info", cmd_info, self.callback)
        self.pub = rospy.Publisher("/lrk/image_with_car", Image, queue_size=10)
        self.subobj = rospy.Subscriber("/lrk/obj_info", obj_info, self.objCallback)
        self.objpack=""
        self.blockFlag = 1
        self.waitCount = 0

    def blockClear(self):
        self.blockFlag = 1
        self.waitCount = 0

    def objCallback(self, data):
        """
        @type data: obj_info
        """
        try:
            if len(data.obj_info) % 100 != 0:
                print("objmsg Len ERROR!")
            else:
                self.objpack=data.obj_info
            self.blockFlag=1
            print("recv objMSG"),len(data.obj_info)
        except Exception, e:
            print(e)
            self.blockFlag = 1

    def printHex(self, myByteArray, nline=1):
        for i in myByteArray:
            tmp = hex(ord(i))[-2:]
            if tmp[0] == 'x':
                tmp = '0' + tmp[1]
            print tmp,
        if (nline == 1):
            print("")
        return ""

    def callback(self, data):
        """
        @type data: cmd_info
        """
        if data.cmd == "getPic":
            testobjPub.pubobjTest()
        if data.cmd[:16] == "get_picture_only":
            print "recvGetPicRequest"
            tmp = data.cmd[16:]
            tmp1 = unpack(">d", tmp[0:8])
            nowtime = tmp1[0]
            tmpimagewithtime = getMostNearImage(nowtime)  # type:imageWithTime
            testImagePublish.publish(tmpimagewithtime.image, tmpimagewithtime.timeStamp, nowtime)
        if data.cmd[:23] == "get_picture_and_objInfo":
            print "recvGetPicAndInfoRequest"
            tmp = data.cmd[23:]
            nowtime = unpack(">d", tmp[0:8])[0]
            nowtrig = unpack(">i", tmp[8:12])[0]
            print("nowtrig"), nowtrig
            tmpimagewithtime = getMostNearImage(nowtime)  # type:imageWithTime
            cvModeImg = tmpimagewithtime.image
            # ************HERE: getObjInfo(cvModeImg)************#
            self.pub.publish(self.bridge.cv2_to_imgmsg(cvModeImg, "rgb8"))
            self.blockFlag = 0
            self.objpack=""
            while self.blockFlag == 0:
                time.sleep(1)
                print "blocking...", self.blockFlag, self.waitCount
                self.waitCount = self.waitCount + 1
            print "block over"
            self.blockClear()
            testImagePublish.publish(tmpimagewithtime.image, tmpimagewithtime.timeStamp, nowtime, nowtrig, self.objpack)


class imgInfo_publisher:
    def __init__(self):
        self.bridge = CvBridge()
        self.image_pub = rospy.Publisher("lrk/image_info", image_info, queue_size=1)

    def publish(self, inimage, imgtime, intime, intrig=None, inobj=None):
        try:
            tmp = image_info()
            tmpimg = self.bridge.cv2_to_imgmsg(inimage, "bgr8")
            tmp.image = tmpimg
            tmp.timeInfo = pack(">d", imgtime) + pack(">d", intime)

            if intrig != None:
                tmp.trigInfo = pack(">i", intrig)
            if inobj != None:
                tmp.objInfo = inobj

            self.image_pub.publish(tmp)
            print "imgInfo published"
        except CvBridgeError as e:
            print(e)


class objInfo_publisher:
    def __init__(self):
        self.pub = rospy.Publisher('/lrk/obj_info', obj_info, queue_size=10)

    def pubobjTest(self):
        testobj1 = myVehicleObject()
        testobj1.SETTESTVALUE()
        abc = obj_info()
        tmp = testobj1.getPack()
        abc.obj_info = tmp + tmp + tmp + tmp + tmp
        self.pub.publish(abc)


class imageWithTime:
    def __init__(self, inimage):
        self.image = inimage
        self.timeStamp = time.time() + 2082844800.0


class image_converter:
    def __init__(self):
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber("/lrk/image_raw", Image, self.callback)
        self.drone_image = []

    def callback(self, data):
        """
        @type data: Image
        """
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "rgb8")
            if len(imageFIFO) < 50:
                imageFIFO.append(imageWithTime(cv_image))
            else:
                imageFIFO.pop(0)
                imageFIFO.append(imageWithTime(cv_image))
                # showFIFOcontents()
        except CvBridgeError as e:
            print(e)


if __name__ == "__main__":
    rospy.init_node('lrk_commandInfo_publish')
    #testobjPub = objInfo_publisher()
    testsub = cmdInfo_subscriber()
    testImage = image_converter()
    testImagePublish = imgInfo_publisher()
    blockTester = blkInfo_subscriber()
    rospy.spin()
