#!/usr/bin/env python3
import rospy
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import AprilTagDetectionArray

class Target_Follower:
    def __init__(self):
        rospy.init_node('target_follower_node', anonymous=True)
        rospy.on_shutdown(self.clean_shutdown)

        self.goal_distance = 0.3
        self.Kp_omega = 1.5
        self.Kp_v = 0.8

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

        if len(detections) == 0:
            rospy.loginfo("No tag detected. Staying still.")
            cmd_msg.v = 0.0
            cmd_msg.omega = 0.0
        else:
            x = detections[0].transform.translation.x
            y = detections[0].transform.translation.y
            z = detections[0].transform.translation.z
            rospy.loginfo("Tag detected! x,y,z: %f %f %f", x, y, z)

            if abs(x) < 0.05:
                omega = 0.0
            else:
                omega = -self.Kp_omega * x
                omega = max(-2.0, min(2.0, omega))

            distance_error = z - self.goal_distance
            if abs(distance_error) < 0.05:
                v = 0.0
            else:
                v = self.Kp_v * distance_error
                v = max(-0.3, min(0.3, v))

            cmd_msg.v = v
            cmd_msg.omega = omega

        self.cmd_vel_pub.publish(cmd_msg)

if __name__ == '__main__':
    try:
        target_follower = Target_Follower()
    except rospy.ROSInterruptException:
        pass