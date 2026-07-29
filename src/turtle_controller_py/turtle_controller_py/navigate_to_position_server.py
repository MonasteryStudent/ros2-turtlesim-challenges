#!/usr/bin/env python3

import math
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.action.server import ServerGoalHandle
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from turtlesim.msg import Pose

from turtle_controller_interfaces.action import NavigateToPosition


class NavigateToPositionServerNode(Node):
    def __init__(self):
        super().__init__("navigate_to_position_server")

        self.pose_received = False
        self.goal_active = False

        self.pose_sub = self.create_subscription(
            Pose,
            "/turtle1/pose",
            self.pose_callback,
            10
        )
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            "/turtle1/cmd_vel",
            10
        )
        self.navigate_to_position_server = ActionServer(
            self,
            NavigateToPosition,
            "navigate_to_position",
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            execute_callback=self.execute_callback,
            callback_group=ReentrantCallbackGroup()
        )

        self.get_logger().info("Navigate to position action server started.")

    def cancel_callback(self, goal_handle: ServerGoalHandle) -> CancelResponse:
        """Accept an incoming goal cancellation request."""
        self.get_logger().info("Received a cancel request.")
        return CancelResponse.ACCEPT

    def pose_callback(self, pose_msg: Pose) -> None:
        """Update the turtle's current pose."""
        self.current_x = pose_msg.x
        self.current_y = pose_msg.y
        self.current_theta = pose_msg.theta
        self.pose_received = True

    def goal_callback(
        self, 
        goal_request: NavigateToPosition.Goal
    ) -> GoalResponse:
        """Validate and accept or reject an incoming goal request."""
        self.get_logger().info("Received a goal.")

        if self.goal_active:
            self.get_logger().warning(
                "Rejecting goal because another goal is already being executed."
            )
            return GoalResponse.REJECT

        if not self.pose_received:
            self.get_logger().warning(
                "Rejecting goal because no turtle pose has been received yet."
            )
            return GoalResponse.REJECT

        min_pos = 0.5
        max_pos = 10.5

        position_is_valid = (
            min_pos <= goal_request.target_x <= max_pos
            and min_pos <= goal_request.target_y <= max_pos
        )

        if not position_is_valid:
            self.get_logger().warning(
                "Rejecting the goal, target position is outside the turtlesim area."
            )
            return GoalResponse.REJECT

        self.goal_active = True

        self.get_logger().info("Accepting the goal.")
        return GoalResponse.ACCEPT

    def compute_distance(self) -> float:
        """Compute the Euclidean distance to the target position."""
        dx = self.target_x - self.current_x
        dy = self.target_y - self.current_y
        return math.sqrt(dx ** 2 + dy ** 2)
   
    def compute_target_angle(self) -> float:
        """Compute the heading from the current position to the target."""
        dx = self.target_x - self.current_x
        dy = self.target_y - self.current_y
        return math.atan2(dy, dx)

    def compute_angle_error(self) -> float:
        """Compute the difference between the current and desired heading."""
        target_angle = self.compute_target_angle()
        return target_angle - self.current_theta

    def execute_callback(
        self,
        goal_handle: ServerGoalHandle
    ) -> NavigateToPosition.Result:
        """Execute an accepted navigation goal until completion or cancellation."""
        self.target_x = goal_handle.request.target_x
        self.target_y = goal_handle.request.target_y

        angle_tolerance = 0.05
        distance_tolerance = 0.5
        angular_speed = 1.0
        linear_speed = 1.0
        feedback_interval = 0.5
        last_feedback_time = time.monotonic()

        cmd_vel = Twist()
        result = NavigateToPosition.Result()
        feedback = NavigateToPosition.Feedback()

        self.get_logger().info("Executing the goal.")

        while True:

            if goal_handle.is_cancel_requested:
                self.get_logger().info("Canceling goal.")

                cmd_vel.linear.x = 0.0
                cmd_vel.angular.z = 0.0
                self.cmd_vel_pub.publish(cmd_vel)

                goal_handle.canceled()

                result.success = False
                result.final_x = self.current_x
                result.final_y = self.current_y

                self.goal_active = False

                return result

            angle_error = self.compute_angle_error()
            distance = self.compute_distance()

            current_time = time.monotonic()

            if current_time - last_feedback_time >= feedback_interval:
                feedback.distance_remaining = distance
                goal_handle.publish_feedback(feedback)
                last_feedback_time = current_time

            if distance < distance_tolerance:
                cmd_vel.linear.x = 0.0
                cmd_vel.angular.z = 0.0
                self.cmd_vel_pub.publish(cmd_vel)
                break
            elif angle_error > angle_tolerance:
                cmd_vel.angular.z = angular_speed
                cmd_vel.linear.x = 0.0
            elif angle_error < -angle_tolerance:
                cmd_vel.angular.z = -angular_speed
                cmd_vel.linear.x = 0.0  
            else:
                cmd_vel.linear.x = linear_speed
                cmd_vel.angular.z = 0.0

            self.cmd_vel_pub.publish(cmd_vel)
            time.sleep(0.05)

        goal_handle.succeed()
        result.success = True
        result.final_x = self.current_x
        result.final_y = self.current_y

        self.goal_active = False

        return result


def main(args=None) -> None:
    rclpy.init(args=args)
    node = NavigateToPositionServerNode()
    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor=executor)
    rclpy.shutdown()


if __name__ == "__main__":
    main()