# intelligent_traffic
structrue of the project(5 processes):
1.	image publisher
2.	plate detector
3.	main
4.	tcp server
5.	neural network

preparations-environment:
1.	install CLIENT simulator on a computer running Windows
2.	install opencv
3.	install "libPR.so" and "train XMLs" of senior Tse
4.	install caffe(branch ssd;pycaffe)
5.	install VGGNet of brother Hung-Heoi (copy VGGNet to some folder and change the settings in lrk_detectcar.py)

preparations-project deployment:
1.	copy "lrkmsg" folder to ~/catkin_ws/src
2.	catkin_make
3.	copy "tcpTest" folder to anywhere you like (do not delete the "pics" folder inside it)

run:
1.	connect camera to the computer(default:/dev/video0)
2.	rosrun lrkmsg image_publisher
3.	rosrun lrkmsg plate_detector  
move to "tcpTest" folder and:
4.	python lrk_detectcar.py
5.	python lrk_tcpserver.py
6.	python lrk_main.py
7.	trigger the whole system with CLIENT on Windows and see if it works(pls make sure that ip/port/firewall settings are correct)
