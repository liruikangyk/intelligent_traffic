# intelligent_traffic
### structrue of the project(5 processes):
1.	image publisher
2.	plate detector
3.	main
4.	tcp server
5.	neural network

### preparations-environment:
1.	install CLIENT simulator on a computer running Windows (\share\users\李睿康\智慧交通0727\仿真器V0.52.rar)
2.	install opencv	(sudo apt-get install libopencv-dev ; http://www.cnblogs.com/dragonyo/p/6754599.html)
3.	install "libPR.so" and "train XMLs" of senior Tse (\share\users\李睿康\智慧交通0727\PR.tar)
4.	install caffe [branch ssd;pycaffe] (http://blog.csdn.net/humble_thumber/article/details/54135923)
5.	install VGGNet of brother Hung-Heoi (unzip \share\users\李睿康\智慧交通0727\VGGNet.zip and copy VGGNet to some folder and change the settings in lrk_detectcar.py)
6.  install ros (http://wiki.ros.org/kinetic/Installation/Ubuntu)

### installation:
1.	git clone git@10.92.13.175:~/repo/intelligent_traffic.git   (passwd: single space--> " ")
2.	cd intelligent_traffic
3.	catkin_make

### run:
##### 0. connect camera to the computer(default:/dev/video0)
1.	cd intelligent_traffic
2.	source devel/setup.bash
3.	roslaunch lrkmsg lrk_start_all.launch
4.	connect and trigger the whole system with CLIENT on Windows and see if it works(pls make sure that ip/port/firewall settings are correct)
##### you can use "rosrun rqt_graph rqt_graph" to see if all 5 processes started and established the communication 
##### you can use "rqt" and use plugins-visualization-image_view to see the topics of type "Image"
##### you can use "rostopic list";"rostopic echo \<topicname>" to see the topics of type "String" 


