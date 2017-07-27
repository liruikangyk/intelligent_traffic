cmake_minimum_required(VERSION 2.8.3)
project(lrkmsg)


find_package(catkin REQUIRED COMPONENTS
  cv_bridge
  image_transport
  roscpp
  rospy
  std_msgs
  message_generation
)

add_message_files(
  FILES
  cmd_info.msg
  obj_info.msg
  image_info.msg
  blk_info.msg
)

generate_messages(
  DEPENDENCIES
  std_msgs
  sensor_msgs
)



catkin_package(
  #CATKIN_DEPENDS message_runtime
)

include_directories(
  ${catkin_INCLUDE_DIRS}
  include
)

add_executable(image_publisher src/image_publisher.cpp)
target_link_libraries(image_publisher
   ${catkin_LIBRARIES}
   ${OpenCV_LIBRARIES}
 )


add_executable(plate_detector src/test.cpp)
target_link_libraries(plate_detector
    ${catkin_LIBRARIES}
		PR
  )

#############
## Install ##
#############

 install(PROGRAMS
   DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
 )

## Mark executables and/or libraries for installation
# install(TARGETS lrkmsg lrkmsg_node
#   ARCHIVE DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
#   LIBRARY DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
#   RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
# )

## Mark cpp header files for installation
# install(DIRECTORY include/${PROJECT_NAME}/
#   DESTINATION ${CATKIN_PACKAGE_INCLUDE_DESTINATION}
#   FILES_MATCHING PATTERN "*.h"
#   PATTERN ".svn" EXCLUDE
# )


