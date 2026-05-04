#!/usr/bin/env python3
import rospy
from duckietown_msgs.msg import Twist2DStamped, WheelEncoderStamped

class ClosedLoopSquare:
    def __init__(self):
        rospy.init_node('closed_loop_square_node', anonymous=True)
        rospy.on_shutdown(self.clean_shutdown)

        # Encoder tick thresholds based on measurements
        self.TICKS_PER_METER = 460
        self.TICKS_PER_90_DEG = 50  # average of left and right turns

        # Encoder state
        self.left_ticks = 0
        self.right_ticks = 0
        self.left_start = 0
        self.right_start = 0

        # Publisher and Subscribers
        self.cmd_pub = rospy.Publisher('/myboty002833/car_cmd_switch_node/cmd', Twist2DStamped, queue_size=1)
        rospy.Subscriber('/myboty002833/left_wheel_encoder_node/tick', WheelEncoderStamped, self.left_encoder_callback)
        rospy.Subscriber('/myboty002833/right_wheel_encoder_node/tick', WheelEncoderStamped, self.right_encoder_callback)

        rospy.sleep(1)  # wait for subscribers to connect
        self.run_square()
        rospy.spin()

    def left_encoder_callback(self, msg):
        self.left_ticks = msg.data

    def right_encoder_callback(self, msg):
        self.right_ticks = msg.data

    def stop_robot(self):
        cmd = Twist2DStamped()
        cmd.header.stamp = rospy.Time.now()
        cmd.v = 0.0
        cmd.omega = 0.0
        self.cmd_pub.publish(cmd)
        rospy.sleep(0.5)

    def move_straight(self, distance, speed=0.3):
        ticks_needed = int(abs(distance) * self.TICKS_PER_METER)
        v = speed if distance > 0 else -speed

        self.left_start = self.left_ticks
        self.right_start = self.right_ticks

        rospy.loginfo("Moving %.2fm at speed %.2f (%d ticks needed)", distance, speed, ticks_needed)

        rate = rospy.Rate(20)
        while not rospy.is_shutdown():
            left_moved = abs(self.left_ticks - self.left_start)
            right_moved = abs(self.right_ticks - self.right_start)
            avg_moved = (left_moved + right_moved) / 2.0

            if avg_moved >= ticks_needed:
                break

            cmd = Twist2DStamped()
            cmd.header.stamp = rospy.Time.now()
            cmd.v = v
            cmd.omega = 0.0
            self.cmd_pub.publish(cmd)
            rate.sleep()

        self.stop_robot()
        rospy.loginfo("Straight done!")

    def rotate(self, angle_deg, speed=2.0):
        ticks_needed = int(abs(angle_deg) / 90.0 * self.TICKS_PER_90_DEG)
        omega = speed if angle_deg > 0 else -speed  # positive = left, negative = right

        self.left_start = self.left_ticks
        self.right_start = self.right_ticks

        rospy.loginfo("Rotating %.1f degrees (%d ticks needed)", angle_deg, ticks_needed)

        rate = rospy.Rate(20)
        while not rospy.is_shutdown():
            left_moved = abs(self.left_ticks - self.left_start)
            right_moved = abs(self.right_ticks - self.right_start)
            avg_moved = (left_moved + right_moved) / 2.0

            if avg_moved >= ticks_needed:
                break

            cmd = Twist2DStamped()
            cmd.header.stamp = rospy.Time.now()
            cmd.v = 0.0
            cmd.omega = omega
            self.cmd_pub.publish(cmd)
            rate.sleep()

        self.stop_robot()
        rospy.loginfo("Rotation done!")

    def run_square(self):
        rospy.loginfo("Starting closed loop square!")
        for i in range(4):
            rospy.loginfo("Side %d", i + 1)
            self.move_straight(1.0, speed=0.3)
            rospy.sleep(0.5)
            self.rotate(90, speed=2.0)
            rospy.sleep(0.5)
        rospy.loginfo("Square complete!")

    def clean_shutdown(self):
        rospy.loginfo("Shutting down...")
        self.stop_robot()

if __name__ == '__main__':
    try:
        ClosedLoopSquare()
    except rospy.ROSInterruptException:
        pass