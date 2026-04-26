#!/usr/bin/env python3
# Import Dependencies
import rospy 
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
from turtlesim.msg import Pose
import math

class DistanceReader:
    def __init__(self):
        # Initialize the node
        rospy.init_node('turtlesim_distance_node', anonymous=True)

        # Store previous position
        self.prev_x = None
        self.prev_y = None
        self.total_distance = 0.0

        # Initialize subscriber
        rospy.Subscriber("/turtle1/pose", Pose, self.callback)

        # Initialize publisher
        self.distance_publisher = rospy.Publisher('/turtle_dist', Float64, queue_size=10)

        rospy.loginfo("Initialized node!")
        rospy.spin()

    def callback(self, msg):
        rospy.loginfo("Turtle Position: %s %s", msg.x, msg.y)

        ########## YOUR CODE GOES HERE ##########
        if self.prev_x is not None and self.prev_y is not None:
            # Calculate distance between previous and current position
            dx = msg.x - self.prev_x
            dy = msg.y - self.prev_y
            distance = math.sqrt(dx**2 + dy**2)

            # Add to total distance
            self.total_distance += distance

            # Publish total distance
            self.distance_publisher.publish(self.total_distance)
            rospy.loginfo("Total Distance Travelled: %.4f", self.total_distance)

        # Update previous position
        self.prev_x = msg.x
        self.prev_y = msg.y
        ###########################################

if __name__ == '__main__': 
    try: 
        distance_reader_class_instance = DistanceReader()
    except rospy.ROSInterruptException: 
        pass