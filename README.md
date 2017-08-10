# intelligent_traffic
### structrue of the project(5 working processes and 1 daemon process):
1.	image publisher
2.	plate detector
3.	main
4.	tcp server
5.	neural network
6.  daemon_test

### preparations-environmen:
1.  "cd ~"
2.  "git clone git@10.92.13.175:~/intraffic.git"   (passwd: single space--> " ")
3.	install CLIENT simulator on a computer running Windows (\share\users\李睿康\智慧交通0727\仿真器V0.52.rar)
4.	install ros (http://wiki.ros.org/kinetic/Installation/Ubuntu)
5.	install caffe [branch ssd;pycaffe] (http://blog.csdn.net/humble_thumber/article/details/54135923)
6.  copy all the caffe model file to caffe model folder("cp -r ~/intraffic/VGGNet ~/caffe/models/")
7.	copy all the library files in ~/intraffic/opencv3-3-arm64lib to /usr/local/lib ("sudo cp ~/intraffic/opencv3-3-arm64lib/* /usr/local/lib")
8.  copy train folder and all the files inside it to system root path ("sudo cp -r ~/intraffic/train /")
9.  "sudo ldconfig"

### installation:
1.	"mkdir ~/catkin_ws"
2.  "cd ~/catkin_ws"
3.  "ln -s ~/intraffic/src ."
4.	"catkin_make"
5.  append all the lines in txtfile ~/intraffic/bashrc_example to ~/.bashrc 
6.  open a new bash terminal, type "lrk" then enter, you will see the system works

### test:
1.	connect camera to the computer(default:/dev/video0)
2.	"lrk"
3.	connect and trigger the whole system with CLIENT on Windows and see if it works(pls make sure that ip/port/firewall settings are correct)
##### you can use "rosrun rqt_graph rqt_graph" to see if all 5 processes started and established the communication 
##### you can use "rqt" and use plugins-visualization-image_view to see the topics of type "Image"
##### you can use "rostopic list";"rostopic echo \<topicname>" to see the topics of type "String" 
##### you can add [~/intraffic/autorun.sh] to operation system's startup applications list, then the programs will automatically run at system startup

