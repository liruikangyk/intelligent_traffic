#include <ros/ros.h>
#include <image_transport/image_transport.h>
#include "opencv2/opencv.hpp"
#include <cv_bridge/cv_bridge.h>
#include <iostream>

using namespace std;
using namespace cv;

int main(int argc, char** argv)
{
  // Check if video source has been passed as a parameter
  //if(argv[1] == NULL) return 1;

  ros::init(argc, argv, "cam_image_publisher");
  ros::NodeHandle nh;
  image_transport::ImageTransport it(nh);
  image_transport::Publisher pub = it.advertise("lrk/image_raw", 1);

  cv::VideoCapture cap("/dev/video0");
  // Check if video device can be opened with the given index
  if(!cap.isOpened())
  { cout << "open cam error"<<endl;return 1;}
  cv::Mat frame;
  sensor_msgs::ImagePtr msg;

  int cnt = 0;
  ros::Rate loop_rate(10);
  while (nh.ok()) {
    cap >> frame;
    // Check if grabbed frame is actually full with some content
    if(!frame.empty()) {
      msg = cv_bridge::CvImage(std_msgs::Header(), "bgr8", frame).toImageMsg();
      pub.publish(msg);
      cout << "frame : "<<cnt++ <<endl;
      imshow("view_publisher",frame);
      cv::waitKey(1);
    }

    ros::spinOnce();
    loop_rate.sleep();
  }
}
