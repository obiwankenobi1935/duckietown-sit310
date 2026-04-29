#!/usr/bin/env python3
import rospy
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import AprilTagDetectionArray

class Target_Follower:
    def __init__(self):
        rospy.init_node('target_follower_node', anonymous=True)
        rospy.on_shutdown(self.clean_shutdown)
        self.seeking = True
        self.cmd_vel_pub = rospy.Publisher('/myboty002833/car_cmd_switch_node/cmd', Twist2DStamped, queue_size=1)
        rospy.Subscriber('/myboty002833/apriltag_detector_node/detections', AprilTagDetectionArray, self.tag_callback, queue_size=1)
        rospy.spin()

    def tag_callback(self, msg):
        self.move_robot(msg.detections)

    def clean_shutdown(self):
        rospy.loginfo("System shutting down. Stopping robot...")
        self.stop_robot()

    def stop_robot(self):
        cmd_msg = Twist2DStamped()
        cmd_msg.header.stamp = rospy.Time.now()
        cmd_msg.v = 0.0
        cmd_msg.omega = 0.0
        self.cmd_vel_pub.publish(cmd_msg)

    def move_robot(self, detections):
        cmd_msg = Twist2DStamped()
        cmd_msg.header.stamp = rospy.Time.now()
        cmd_msg.v = 0.0
        if len(detections) == 0:
            if not self.seeking:
                rospy.loginfo("No tag detected. Seeking...")
                self.seeking = True
            cmd_msg.omega = 1.5
        else:
            x = detections[0].transform.translation.x
            y = detections[0].transform.translation.y
            z = detections[0].transform.translation.z
            rospy.loginfo("Tag detected! x,y,z: %f %f %f", x, y, z)
            if self.seeking:
                rospy.loginfo("Tag found! Switching to tracking mode.")
                self.seeking = False
            Kp = 3.0
            omega = -Kp * x
            if 0 < omega < 0.5:
                omega = 0.5
            elif -0.5 < omega < 0:
                omega = -0.5
            omega = max(-3.0, min(3.0, omega))
            cmd_msg.omega = omega
        self.cmd_vel_pub.publish(cmd_msg)

if __name__ == '__main__':
    try:
        target_follower = Target_Follower()
    except rospy.ROSInterruptException:
        pass
