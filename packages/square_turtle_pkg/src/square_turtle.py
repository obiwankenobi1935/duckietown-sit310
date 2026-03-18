#!/usr/bin/env python3

# Import Dependencies
import rospy 
from geometry_msgs.msg import Twist 
import time 

def move_turtle_square(): 
    rospy.init_node('turtlesim_square_node', anonymous=True)
    
    # Init publisher
    velocity_publisher = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10) 
    rospy.loginfo("Drawing a square!")

    rospy.sleep(1)  # Allow publisher to connect

    rate = rospy.Rate(10)

    while not rospy.is_shutdown():  # 4 sides of square
        
        # ---- Move Forward ----
        cmd_vel_msg = Twist()
        cmd_vel_msg.linear.x = 2.0
        cmd_vel_msg.angular.z = 0.0

        t0 = time.time()
        while time.time() - t0 < 2:  # move for 2 seconds
            velocity_publisher.publish(cmd_vel_msg)
            rate.sleep()

        # ---- Stop ----
        cmd_vel_msg.linear.x = 0.0
        velocity_publisher.publish(cmd_vel_msg)
        rospy.sleep(1)

        # ---- Turn 90 degrees ----
        cmd_vel_msg = Twist()
        cmd_vel_msg.angular.z = 1.57  # ~90 deg/sec

        t0 = time.time()
        while time.time() - t0 < 1:  # rotate for 1 second
            velocity_publisher.publish(cmd_vel_msg)
            rate.sleep()

        # ---- Stop after turn ----
        cmd_vel_msg.angular.z = 0.0
        velocity_publisher.publish(cmd_vel_msg)
        rospy.sleep(1)


if __name__ == '__main__': 
    try: 
        move_turtle_square() 
    except rospy.ROSInterruptException: 
        pass