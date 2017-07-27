#include "ros/ros.h"
#include "std_msgs/String.h"
#include "image_transport/image_transport.h"
#include "opencv2/opencv.hpp"
#include "cv_bridge/cv_bridge.h"
#include <iostream>
#include <sstream>
#include "PR.h"
using namespace std;
using namespace cv;

class xxpr {
	private:
		Mat image;
		int cnt;
		ros::NodeHandle nh;
		image_transport::ImageTransport it;
		image_transport::Subscriber sub;
		ros::Publisher plate_msg;
	public : 
		void imageCallback(const sensor_msgs::ImageConstPtr& msg)
		{
			try
			{
				Mat frame = cv_bridge::toCvShare(msg, "bgr8")->image;
				frame.copyTo(image);
				//Mat ft = frame;
				cout << "frame : "<<cnt++<<endl;
				vector<string> plate;
				if(mypr(frame,plate) == 0)
				{
					std_msgs::String msg;
					std::stringstream ss;
					//for(int i = 0; i < plate.size(); i++)
					//{
						//ss << plate[i] << ",";
					//}
					if(plate.size()>0)
					{
					    ss << plate[0];
					}
					msg.data = ss.str();
					plate_msg.publish(msg);
						for(int i = 0; i < plate.size(); i++)
					{
							cout<<"plate"<<i+1<<": "<<plate[i]<<endl;
					//ROS_INFO(plate[i]);
					}
				}
				//cv::imshow("view_subscriber", cv_bridge::toCvShare(msg, "bgr8")->image);
				//	Mat ft;
				//		resize(frame, ft, cv::Size(640, 360));
				// imshow("view",ft);
				// cv::waitKey(1);
			}
			catch (cv_bridge::Exception& e)
			{
				ROS_ERROR("Could not convert from '%s' to 'bgr8'.", msg->encoding.c_str());
			}
		}

		xxpr():
			it(nh)
	{
		sub = it.subscribe("lrk/image_single_car", 1, &xxpr::imageCallback, this);
		cnt = 0;
		plate_msg = nh.advertise<std_msgs::String>("lrk/plate_single_car", 1000);
	}
};

int main(int argc, char **argv)
{
	ros::init(argc, argv, "testcv");
	xxpr obj;
	ros::spin();
	//cv::destroyWindow("view");
}

