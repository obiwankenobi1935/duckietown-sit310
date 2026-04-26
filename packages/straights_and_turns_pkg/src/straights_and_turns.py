#!/usr/bin/env python3
import rospy 
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
from turtlesim.msg import Pose
import math

class TurtlesimStraightsAndTurns:
    def __init__(self):
        self.goal_distance = 0
        self.dist_goal_active = False
        self.forward_movement = True
        self.start_x = None
        self.start_y = None
        self.current_x = 0.0
        self.current_y = 0.0
        
        self.current_angle = 0.0
        self.goal_angle = 0.0
        self.angle_goal_active = False
        self.start_angle = None
        self.total_angle_turned = 0.0  # NEW: accumulate total rotation
        self.last_angle = None          # NEW: track previous angle

        rospy.init_node('turtlesim_straights_and_turns_node', anonymous=True)

        rospy.Subscriber("/goal_angle", Float64, self.goal_angle_callback)
        rospy.Subscriber("/goal_distance", Float64, self.goal_distance_callback)
        rospy.Subscriber("/turtle1/pose", Pose, self.pose_callback)

        self.velocity_publisher = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10)

        timer_period = 0.01
        rospy.Timer(rospy.Duration(timer_period), self.timer_callback)

        rospy.loginfo("Initialized node!")
        rospy.spin()

    def pose_callback(self, msg):
        # NEW: accumulate angle incrementally each pose update
        if self.angle_goal_active and self.last_angle is not None:
            delta = self.angle_diff(msg.theta, self.last_angle)
            self.total_angle_turned += delta

        self.last_angle = msg.theta
        self.current_angle = msg.theta
        self.current_x = msg.x
        self.current_y = msg.y

    def goal_angle_callback(self, msg):
        if msg.data == 0.0:
            return
        self.goal_angle = msg.data
        self.angle_goal_active = True
        self.dist_goal_active = False
        self.start_angle = self.current_angle
        self.last_angle = self.current_angle
        self.total_angle_turned = 0.0  # reset accumulator
        rospy.loginfo("New angle goal: %.4f", self.goal_angle)

    def goal_distance_callback(self, msg):
        if msg.data == 0.0:
            return
        self.goal_distance = abs(msg.data)
        self.forward_movement = msg.data > 0
        self.dist_goal_active = True
        self.angle_goal_active = False
        self.start_x = self.current_x
        self.start_y = self.current_y
        rospy.loginfo("New distance goal: %.4f from (%.2f, %.2f)", msg.data, self.start_x, self.start_y)

    def timer_callback(self, msg):
        cmd = Twist()

        if self.dist_goal_active:
            if self.start_x is None:
                return
            dx = self.current_x - self.start_x
            dy = self.current_y - self.start_y
            travelled = math.sqrt(dx**2 + dy**2)
            rospy.loginfo("Travelled: %.4f / Goal: %.4f", travelled, self.goal_distance)

            if travelled >= self.goal_distance:
                self.dist_goal_active = False
                cmd.linear.x = 0.0
                rospy.loginfo("Distance goal reached!")
            else:
                cmd.linear.x = 1.5 if self.forward_movement else -1.5

        elif self.angle_goal_active:
            rospy.loginfo("Angle turned: %.4f / Goal: %.4f", self.total_angle_turned, self.goal_angle)

            if abs(self.total_angle_turned) >= abs(self.goal_angle):
                self.angle_goal_active = False
                cmd.angular.z = 0.0
                rospy.loginfo("Angle goal reached!")
            else:
                cmd.angular.z = 1.5 if self.goal_angle > 0 else -1.5

        self.velocity_publisher.publish(cmd)

    def angle_diff(self, current, start):
        diff = current - start
        if diff > math.pi:
            diff -= 2 * math.pi
        elif diff < -math.pi:
            diff += 2 * math.pi
        return diff

if __name__ == '__main__': 
    try: 
        turtlesim_straights_and_turns_class_instance = TurtlesimStraightsAndTurns()
    except rospy.ROSInterruptException: 
        pass