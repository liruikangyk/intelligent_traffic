#!/usr/bin/python
# -*- coding:utf-8 -*-
import socket
from struct import pack, unpack
import time, signal
from PIL import Image as pilImage
from lrkmsg.msg import cmd_info, image_info
import rospy
from cv_bridge import CvBridge
import cv2
import os

basepath=os.path.dirname(__file__)
print basepath
port = 6342
localip = '10.92.13.175'


class mySoundSource():
    def __init__(self, row=0, column=0):
        self.row = row
        self.column = column

    def getRow(self):
        return pack(">i", self.row)

    def getColumn(self):
        return pack(">i", self.column)


class myVehicleObject():
    VEHICLE_TYPE_CAR = 20
    VEHICLE_TYPE_BUS = 21
    VEHICLE_TYPE_MOTORBIKE = 22
    VEHICLE_TYPE_UNKNOWN = -1
    VEHICLE_TYPE_NONE_MOTORIZED = 0

    def __init__(self, inpack=None):
        if inpack:
            self.decodePack(inpack, isprint=0)
        else:
            self.objType = None
            self.objRoi = None
            self.objRoiConf = None
            self.objDirection = None
            self.objState = None
            self.plateRoi = None
            self.plateRoiConf = None
            self.plateNum = None
            self.plateNumConf = None

    def printHex(self, myByteArray, nline=1):
        for i in myByteArray:
            tmp = hex(ord(i))[-2:]
            if tmp[0] == 'x':
                tmp = '0' + tmp[1]
            print tmp,
        if (nline == 1):
            print("")
        return ""

    def getPack(self):
        objType_pack = pack(">i", self.objType)
        objRoi_pack = pack(">8i", self.objRoi[0], self.objRoi[1], self.objRoi[2], self.objRoi[3], self.objRoi[4],
                           self.objRoi[5], self.objRoi[6], self.objRoi[7])
        objRoiConf_pack = pack(">i", self.objRoiConf)
        objDirection_pack = pack(">i", self.objDirection)
        objState_pack = pack(">i", self.objState)
        plateRoi_pack = pack(">8i", self.plateRoi[0], self.plateRoi[1], self.plateRoi[2], self.plateRoi[3],
                             self.plateRoi[4], self.plateRoi[5], self.plateRoi[6], self.plateRoi[7])
        plateRoiConf_pack = pack(">i", self.plateRoiConf)
        plateNum_pack = self.plateNum + "@@@"
        plateNumConf_pack = pack(">i", self.plateNumConf)
        return objType_pack + objRoi_pack + objRoiConf_pack + objDirection_pack + objState_pack + plateRoi_pack + plateRoiConf_pack + plateNum_pack + plateNumConf_pack

    def setObjType(self, intype):
        self.objType = intype

    def setObjRoi(self, x0, y0, x1, y1, x2, y2, x3, y3):
        self.objRoi = [x0, y0, x1, y1, x2, y2, x3, y3]

    def setObjRoiConf(self, conf):
        self.objRoiConf = conf

    def setObjDirection(self, dire):
        self.objDirection = dire

    def setObjState(self, state):
        self.objState = state

    def setPlateRoi(self, x0, y0, x1, y1, x2, y2, x3, y3):
        self.plateRoi = [x0, y0, x1, y1, x2, y2, x3, y3]

    def setPlateRoiConf(self, conf):
        self.plateRoiConf = conf

    def setPlateNum(self, instr):
        self.plateNum = instr

    def setPlateNumConf(self, conf):
        self.plateNumConf = conf

    def SETTESTVALUE(self):
        self.setObjType(1)
        self.setObjRoi(1, 2, 3, 4, 5, 6, 7, 8)
        self.setObjRoiConf(98)
        self.setObjDirection(5)
        self.setObjState(0)
        self.setPlateRoi(8, 7, 6, 5, 4, 3, 2, 1)
        self.setPlateRoiConf(76)
        self.setPlateNum("沪D12345")
        self.setPlateNumConf(54)

    def decodePack(self, tmp1, isprint=0):
        tmp2 = unpack(">iiiiiiiiiiiiiiiiiiiiiiiii", tmp1[:100])
        self.setObjType(tmp2[0])
        self.setObjRoi(tmp2[1], tmp2[2], tmp2[3], tmp2[4], tmp2[5], tmp2[6], tmp2[7], tmp2[8])
        self.setObjRoiConf(tmp2[9])
        self.setObjDirection(tmp2[10])
        self.setObjState(tmp2[11])
        self.setPlateRoi(tmp2[12], tmp2[13], tmp2[14], tmp2[15], tmp2[16], tmp2[17], tmp2[18], tmp2[19])
        self.setPlateRoiConf(tmp2[20])
        self.setPlateNum(pack(">iii", tmp2[21], tmp2[22], tmp2[23])[-9:])
        self.setPlateNumConf(tmp2[24])
        if (isprint == 1):
            print("objType:"), self.objType,
            print "(", self.printHex(pack(">i", tmp2[0]), 0), ")"
            print("objRoi:"), self.objRoi,
            print "(", self.printHex(
                pack(">8i", tmp2[1], tmp2[2], tmp2[3], tmp2[4], tmp2[5], tmp2[6], tmp2[7], tmp2[8]), 0), ")"
            print("objRoiConf:"), self.objRoiConf,
            print "(", self.printHex(pack(">i", tmp2[9]), 0), ")"
            print("objDirection:"), self.objDirection,
            print "(", self.printHex(pack(">i", tmp2[10]), 0), ")"
            print("objState:"), self.objState,
            print "(", self.printHex(pack(">i", tmp2[11]), 0), ")"
            print("plateRoi:"), self.plateRoi,
            print "(", self.printHex(
                pack(">8i", tmp2[12], tmp2[13], tmp2[14], tmp2[15], tmp2[16], tmp2[17], tmp2[18], tmp2[19]), 0), ")"
            print("plateRoiConf:"), self.plateRoiConf,
            print "(", self.printHex(pack(">i", tmp2[20]), 0), ")"
            print("plateNum:"), self.plateNum,
            print "(", self.printHex(pack(">3i", tmp2[21], tmp2[22], tmp2[23]), 0), ")"
            print("plateNumConf:"), self.plateNumConf,
            print "(", self.printHex(pack(">i", tmp2[24]), 0), ")"


class myTcp():
    MSG_TYPE_C_CONNECT_TEST = pack(">i", 1)
    MSG_TYPE_C_SEND_TIME = pack(">i", 3)
    MSG_TYPE_C_SEND_TRIGGER = pack(">i", 4)
    MSG_TYPE_C_GET_PIC = pack(">i", 6)
    MSG_TYPE_C_RTN = pack(">i", 9)

    MSG_TYPE_S_RTN = pack(">i", 255)
    MSG_TYPE_S_SEND_TIME = pack(">i", 250)
    MSG_TYPE_S_SEND_PIC = pack(">i", 249)
    MSG_TYPE_S_SEND_OBJECT_INFO = pack(">i", 248)

    def msgNum(self, inmsg):
        return unpack(">i", inmsg)[0]

    def __init__(self, insock=None, indebug=1):
        self.Head = pack(">BBBB", 0x77, 0xdd, 0xee, 0xaa)  # FIXED
        self.SN = pack(">BBBB", 0x12, 0x34, 0x56, 0x78)  # Serial Number of CLIENT
        self.Index = 0  # Serial Number of CLIENT
        self.Type = pack(">i", 0)
        self.Spare = pack(">i", 0)  # BeiYong
        self.lastRecvType = 0
        self.lastState = 0
        self.trigLabel = 0
        self.secTrigLabel = 0
        self.testObject = myVehicleObject()
        self.testObject.SETTESTVALUE()
        self.sock = insock
        self.debug = indebug

    def setLast(self, intype):
        self.lastState = 1
        self.lastRecvType = intype

    def clearLast(self):
        self.lastState = 0
        self.lastRecvType = 0

    def printHex(self, myByteArray, nline=1):
        for i in myByteArray:
            tmp = hex(ord(i))[-2:]
            if tmp[0] == 'x':
                tmp = '0' + tmp[1]
            print tmp,
        if (nline == 1):
            print("")
        return ""

    def getTrigLabel(self, isnew=1):
        if isnew == 1:
            self.trigLabel = self.trigLabel + 1
            self.secTrigLabel = 0
        else:
            self.secTrigLabel = self.secTrigLabel + 1
        return pack(">i", self.trigLabel)

    def getSecTrigLabel(self):
        return pack(">i", self.secTrigLabel)

    def getTime(self, needpack=1, intime=None):
        if intime == None:
            tmp = time.time() + 2082844800.0
        else:
            tmp = intime + 2082844800.0
        if needpack == 1:
            return pack(">d", tmp)
        else:
            return tmp

    def getLastState(self):
        return pack(">i", self.lastState)

    def getIdx(self):
        self.Index = self.Index + 1
        return pack(">i", self.Index)

    def getLastRecvType(self):
        return pack(">i", self.lastRecvType)

    def setPicType(self, typenum):
        return pack(">i", typenum)

    def send_ALL(self, data, isTEST=0):
        if isTEST == 0:
            tmp = self.Head + \
                  self.SN + \
                  self.getIdx() + \
                  data
        else:
            tmp = self.Head + \
                  self.SN + \
                  self.Spare + \
                  data
        self.sock.send(pack(">i", len(tmp)) + tmp)
        return 0

    def C_sendTime(self):
        data = self.MSG_TYPE_C_SEND_TIME + \
               self.getTime() + \
               self.Spare + \
               self.Spare
        # print("C_sendTime", len(data))
        if self.debug > 0:
            print("C_SEND_TIME("), self.msgNum(self.MSG_TYPE_C_SEND_TIME), (") ---->>> remote ")
        return self.send_ALL(data)

    def S_sendTime(self):
        data = self.MSG_TYPE_S_SEND_TIME + \
               self.getTime() + \
               self.Spare + \
               self.Spare
        # print("C_sendTime", len(data))
        if self.debug > 0:
            print("S_SEND_TIME("), self.msgNum(self.MSG_TYPE_S_SEND_TIME), (") ---->>> remote ")
        return self.send_ALL(data)

    def C_getPic(self):
        data = self.MSG_TYPE_C_GET_PIC + \
               self.getTime() + \
               self.Spare + \
               self.Spare
        # print("C_getPic", len(data))
        if self.debug > 0:
            print("C_GET_PIC("), self.msgNum(self.MSG_TYPE_C_GET_PIC), (") ---->>> remote ")
        return self.send_ALL(data)

    def S_sendPic(self, intime, intrig, intype, filename):
        binfile = open(filename, 'rb')
        tmpPicData = binfile.read()
        data = self.MSG_TYPE_S_SEND_PIC + \
               pack(">d", intime) + \
               pack(">i", intrig) + \
               pack(">i", intype) + \
               tmpPicData
        # self.testPicData
        # print("C_sendPic", len(data))
        if self.debug > 0:
            print("S_SEND_PIC("), self.msgNum(self.MSG_TYPE_S_SEND_PIC), (") ---->>> remote ")
        return self.send_ALL(data)

    def C_sendTrigger(self, isnew=1):
        if isnew == 1:
            tmp = self.getTrigLabel()
        else:
            tmp = self.getTrigLabel(0)
        data = self.MSG_TYPE_C_SEND_TRIGGER + \
               self.getTime() + \
               tmp + \
               self.getSecTrigLabel() + \
               pack(">i", 0) + \
               self.Spare + \
               self.Spare
        if self.debug > 0:
            print("C_SEND_TRIGGER("), self.msgNum(self.MSG_TYPE_C_SEND_TRIGGER), (") ---->>> remote ")
        return self.send_ALL(data)

    def C_TEST(self):
        data = self.MSG_TYPE_C_CONNECT_TEST
        if self.debug > 0:
            print("C_CONNECT_TEST("), self.msgNum(self.MSG_TYPE_C_CONNECT_TEST), (") ---->>> remote ")
        return self.send_ALL(data, 1)

    def C_RTN(self):
        data = self.MSG_TYPE_C_RTN + \
               self.getLastRecvType() + \
               self.getLastState()
        if self.debug > 0:
            print("C_RTN("), self.msgNum(self.MSG_TYPE_C_RTN), "type=", self.lastRecvType, (") ---->>> remote ")
        return self.send_ALL(data, 1)

    def S_RTN(self, istest=0):
        data = self.MSG_TYPE_S_RTN + \
               self.getLastRecvType() + \
               self.getLastState()
        if self.debug == 2:
            print("S_RTN("), self.msgNum(self.MSG_TYPE_S_RTN), "type=", self.lastRecvType, (") ---->>> remote ")
        if self.debug == 1 and istest == 0:
            print("S_RTN("), self.msgNum(self.MSG_TYPE_S_RTN), "type=", self.lastRecvType, (") ---->>> remote ")
        return self.send_ALL(data, 1)

    def S_sendObjInfo(self, intime, intrig, inobj):
        data = self.MSG_TYPE_S_SEND_OBJECT_INFO + \
               pack(">d", intime) + \
               pack(">i", intrig) + \
               inobj + \
               self.Spare + \
               self.Spare
        if self.debug > 0:
            print("S_SEND_OBJECT_INFO("), self.msgNum(self.MSG_TYPE_S_SEND_OBJECT_INFO), (") ---->>> remote ")
        return self.send_ALL(data)

    def myRecvDecode(self, data):
        tmp = unpack(">5i", data[0:20])
        realData = data[20:]
        if self.debug == 1 and tmp[4] != 1:
            print("[***msg received***]"),
        if self.debug == 2:
            print "msg length:", tmp[0], "(", self.printHex(data[0:4], 0), ")"
            print "exact length:", len(data)
            print "HEAD: ",
            self.printHex(data[4:8])
            print "SN: ",
            self.printHex(data[8:12])
            print "msg index:", tmp[3], "(", self.printHex(data[12:16], 0), ")"
            print "msg type:", tmp[4], "(", self.printHex(data[16:20], 0), ")"
            print "data length:", len(data[20:])
            print "DATA: ",
            if len(realData) < 140:
                self.printHex(realData)
            else:
                self.printHex(realData[:140], 0)
                print "...(too long to show)"
            print("**********data decoding phase**********")

        if tmp[4] == 1:
            if self.debug > 1:
                print("local <<<---- C_CONNECT_TEST"), "(", self.msgNum(self.MSG_TYPE_C_CONNECT_TEST), ")"
            if self.debug == 2:
                print("No data.")
            self.setLast(0x01)
            self.S_RTN(1)
            self.clearLast()

        elif tmp[4] == 3:
            nowtime = unpack(">d", realData[0:8])[0]
            if self.debug > 0:
                print("local <<<---- C_SEND_TIME"), "(", self.msgNum(self.MSG_TYPE_C_SEND_TIME), ")"
            if self.debug == 2:
                print("timestamp:"),
                print(nowtime), time.ctime(nowtime), "(", self.printHex(realData[0:8], 0), ")"
                print("spare1:"), "(", self.printHex(realData[8:12], 0), ")"
                print("spare2:"), "(", self.printHex(realData[12:16], 0), ")"
            self.setLast(0x03)
            self.S_RTN()
            self.clearLast()

        elif tmp[4] == 4:
            tmp = unpack(">diii", realData[0:20])
            nowtime = tmp[0]
            if self.debug > 0:
                print("local <<<---- C_SEND_TRIGGER"), "(", self.msgNum(self.MSG_TYPE_C_SEND_TRIGGER), ")"
            if self.debug == 2:
                print("timestamp:"),
                print(nowtime), time.ctime(nowtime), "(", self.printHex(realData[0:8], 0), ")"
                print("triggerFlag:"), tmp[1], "(", self.printHex(realData[8:12], 0), ")"
                print("secondaryTriggerFlag:"), tmp[2], "(", self.printHex(realData[12:16], 0), ")"
                print("soundSourceNum:"), tmp[3], "(", self.printHex(realData[16:20], 0), ")"
            self.setLast(0x04)
            self.S_RTN()
            self.clearLast()
            myCmdPub.pubcmd("get_picture_and_objInfo" + realData[0:12])

        elif tmp[4] == 6:
            tmp = unpack(">d", realData[0:8])
            nowtime = tmp[0]
            if self.debug > 0:
                print("local <<<---- C_GET_PIC"), "(", self.msgNum(self.MSG_TYPE_C_GET_PIC), ")"
                print("timestamp:"),
                print(nowtime)
            if self.debug == 2:
                print("timestamp:"),
                print(nowtime), time.ctime(nowtime), "(", self.printHex(realData[0:8], 0), ")"
                print("spare1:"), "(", self.printHex(realData[8:12], 0), ")"
                print("spare2:"), "(", self.printHex(realData[12:16], 0), ")"
            self.setLast(0x06)
            self.S_RTN()
            self.clearLast()
            # self.S_sendPic()
            myCmdPub.pubcmd("get_picture_only" + realData[0:8])

        elif tmp[4] == 9:
            tmp = unpack(">II", realData[0:8])
            if self.debug > 0:
                print("local <<<---- C_RTN"), "(", self.msgNum(self.MSG_TYPE_C_RTN), "type=", tmp[0], ")"
            if self.debug == 2:
                print("RTN_Type:"), tmp[0], "(", self.printHex(realData[0:4], 0), ")"
                print("RTN_State:"), tmp[1], "(", self.printHex(realData[4:8], 0), ")"

        elif tmp[4] == 0xff:
            tmp = unpack(">II", realData[0:8])
            if self.debug > 0:
                print("local <<<---- S_RTN"), "(", self.msgNum(self.MSG_TYPE_S_RTN), "type=", tmp[0], ")"
            if self.debug == 2:
                print("RTN_Type:"), tmp[0], "(", self.printHex(realData[0:4], 0), ")"
                print("RTN_State:"), tmp[1], "(", self.printHex(realData[4:8], 0), ")"

        elif tmp[4] == 0xf9:
            tmp = unpack(">dii", realData[0:16])
            nowtime = tmp[0]
            picData = realData[16:]
            tmpfile = open("tmp.jpg", 'wb')
            tmpfile.write(picData)
            lena = pilImage.open("tmp.jpg")
            if self.debug > 0:
                print("local <<<---- S_SEND_PIC"), "(", self.msgNum(self.MSG_TYPE_S_SEND_PIC), ")"
            if self.debug == 2:
                print("timestamp:"),
                print(nowtime), time.ctime(nowtime), "(", self.printHex(realData[0:8], 0), ")"
                print("triggerFlag:"), tmp[1], "(", self.printHex(realData[8:12], 0), ")"
                print("pictureType:"), tmp[2], "(", self.printHex(realData[12:16], 0), ")"
                print(lena.mode)
            self.setLast(0xf9)
            self.C_RTN()
            self.clearLast()

        elif tmp[4] == 0xfa:
            nowtime = unpack(">d", realData[0:8])[0]
            if self.debug > 0:
                print("local <<<---- S_SEND_TIME"), "(", self.msgNum(self.MSG_TYPE_S_SEND_TIME), ")"
            if self.debug == 2:
                print("timestamp:"),
                print(nowtime), time.ctime(nowtime), "(", self.printHex(realData[0:8], 0), ")"
                print("spare1:"), "(", self.printHex(realData[8:12], 0), ")"
                print("spare2:"), "(", self.printHex(realData[12:16], 0), ")"
            self.setLast(0xfa)
            self.C_RTN()
            self.clearLast()
            self.C_sendTime()

        elif tmp[4] == 0xf8:
            tmp = unpack(">di", realData[0:12])
            nowtime = tmp[0]
            tmp2 = realData[12:112]
            if self.debug > 0:
                print("local <<<---- S_SEND_OBJECT_INFO"), "(", self.msgNum(self.MSG_TYPE_S_SEND_OBJECT_INFO), ")"
            tmpVehicle = myVehicleObject()
            tmpVehicle.decodePack(tmp2, 1)
            if self.debug == 2:
                print("timestamp:"),
                print(nowtime), time.ctime(nowtime), "(", self.printHex(realData[0:8], 0), ")"
                print("triggerFlag:"), tmp[1], "(", self.printHex(realData[8:12], 0), ")"
                print("spare1:"), "(", self.printHex(realData[112:116], 0), ")"
                print("spare2:"), "(", self.printHex(realData[116:120], 0), ")"
            self.setLast(0xf8)
            self.C_RTN()
            self.clearLast()

        return 0


def TCP(sock, addr):  # TCP服务器端处理逻辑
    print('Accept new connection from %s:%s.' % addr)  # 接受新的连接请求
    mytcpTest.sock = sock
    while True:
        data = sock.recv(1024000)  # 接受其数据
        time.sleep(0.5)  # 延迟
        if not data:  # 如果数据为空或者'quit'，则退出
            break
        if mytcpTest.debug == 2:
            print("**********msg received**********")
            if len(data) < 140:
                mytcpTest.printHex(data)
            else:
                mytcpTest.printHex(data[:140], 0)
                print "...(too long to show)"
        mytcpTest.myRecvDecode(data)

    sock.close()  # 关闭连接
    print('Connection from %s:%s closed.' % addr)


class cmdInfo_publisher:
    def __init__(self):
        self.pub = rospy.Publisher("/lrk/cmd_info", cmd_info, queue_size=10)

    def pubcmd(self, incmd):
        tmp = cmd_info()
        tmp.cmd = incmd
        self.pub.publish(tmp)


class imgInfo_subscriber:
    def __init__(self):
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber("lrk/image_info", image_info, self.callback)
        self.ifSendObj = 0

    def callback(self, data):
        """
        @type data: image_info
        """
        xtrig = []
        if len(data.trigInfo) > 0:
            print("trig info:"),
            xtrig = unpack(">i", data.trigInfo[0:4])[0]
            print xtrig
            self.ifSendObj = self.ifSendObj + 1
        else:
            print("no trig info")
        if len(data.objInfo) > 0:
            print("recv obj info")
            try:
                obj_list = []
                if len(data.objInfo) % 100 != 0:
                    print("obj Len ERROR!")
                    return 1
                objnum = len(data.objInfo) / 100
                for i in range(objnum):
                    obj_list.append(myVehicleObject(data.objInfo[i * 100:i * 100 + 100]))  # type:myVehicleObject
                print "obj num:", len(obj_list)
                self.ifSendObj = self.ifSendObj + 1

            except Exception, e:
                print(e)
        else:
            print("no obj info")
        xtime = unpack(">d", data.timeInfo[8:16])[0]
        ytime = unpack(">d", data.timeInfo[0:8])[0]
        print("timestamp:"),
        print(xtime)
        print("realtime:"),
        print(ytime)
        ximage = self.bridge.imgmsg_to_cv2(data.image, "rgb8")
        filename = basepath+"/pics/" + str(xtime) + ".jpg"
        cv2.imwrite(filename, ximage)
        mytcpTest.S_sendPic(xtime, 0, 0, filename)

        if self.ifSendObj == 2:
            mytcpTest.S_sendObjInfo(xtime, xtrig, data.objInfo)
            print("OBJ info SENT")
            self.ifSendObj = 0


if __name__ == "__main__":
    def exit(signum, frame):
        print('You choose to stop me.')
        sock.close()
        s.close()


    signal.signal(signal.SIGINT, exit)
    signal.signal(signal.SIGTERM, exit)

    rospy.init_node('lrk_server')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((localip, port))
    s.listen(1)
    print('Server is running...')
    myCmdPub = cmdInfo_publisher()
    myImgSub = imgInfo_subscriber()
    mytcpTest = myTcp(indebug=1)

    sock, addr = s.accept()
    TCP(sock, addr)
