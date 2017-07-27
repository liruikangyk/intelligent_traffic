# intelligent_traffic
### structrue of the project(5 processes):
1.	image publisher
2.	plate detector
3.	main
4.	tcp server
5.	neural network

### preparations-environment:
1.	install CLIENT simulator on a computer running Windows
2.	install opencv
3.	install "libPR.so" and "train XMLs" of senior Tse
4.	install caffe(branch ssd;pycaffe)
5.	install VGGNet of brother Hung-Heoi (copy VGGNet to some folder and change the settings in lrk_detectcar.py)

### run:
##### 0. connect camera to the computer(default:/dev/video0)
1.	git clone https://github.com/liruikangyk/intelligent_traffic.git
2.	cd intelligent_traffic
3.	catkin_make
4.	source devel/setup.bash
5.	roslaunch lrkmsg lrk_start_all.launch
6.	trigger the whole system with CLIENT on Windows and see if it works(pls make sure that ip/port/firewall settings are correct)
##### you can use "rosrun rqt_graph rqt_graph" to see if all 5 processes started and established the communication 
##### you can use "rqt" and use plugins-visualization-image_view to see the topics of type "Image"
##### you can use "rostopic list";"rostopic echo \<topicname>" to see the topics of type "String" 


