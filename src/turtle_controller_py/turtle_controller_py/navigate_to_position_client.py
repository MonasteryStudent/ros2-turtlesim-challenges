#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.action.client import GoalStatus
from rclpy.parameter import Parameter

from turtle_controller_interfaces.action import NavigateToPosition
from std_srvs.srv import Trigger


class NavigateToPositionClientNode(Node):
    def __init__(self):
        super().__init__("navigate_to_position_client_node")

        self.navigate_to_position_client = ActionClient(
            self,
            NavigateToPosition,
            "navigate_to_position"
        )
        self.cancel_service = self.create_service(
            Trigger,
            "cancel_navigation",
            self.cancel_service_callback
        )

        target_x_parameter = self.declare_parameter(
            "target_x", Parameter.Type.DOUBLE
        )
        target_y_parameter = self.declare_parameter(
            "target_y", Parameter.Type.DOUBLE
        )

        self.target_x = (
            target_x_parameter.value
            if target_x_parameter.type_ != Parameter.Type.NOT_SET
            else None
        )
        self.target_y = (
            target_y_parameter.value
            if target_y_parameter.type_ != Parameter.Type.NOT_SET
            else None
        )

        self.show_feedback = self.declare_parameter(
            "show_feedback", False
        ).value

        self.goal_handle = None

        self.get_logger().info("Navigate to position action client started.")

    def get_target_position(self) -> tuple[float, float] | None:
        while True:
            user_input = input(
                "Enter target coordinates as 'x y' or 'q' to quit: "
            ).strip()

            if user_input.lower() in {"q", "quit"}:
                return None

            try:
                target_x, target_y = map(float, user_input.split())
            except ValueError:
                print("Please enter two numbers, for example: 6.0 1.25")
                continue

            return (target_x, target_y)

    def ensure_target_position(self) -> bool:
        if self.target_x is not None and self.target_y is not None:
            return True

        target = self.get_target_position()

        if target is None:
            return False
        
        self.target_x, self.target_y = target

        return True

    def send_goal(self) -> None:
        """Send a navigation goal and register response and feedback callbacks."""
        self.navigate_to_position_client.wait_for_server()

        goal = NavigateToPosition.Goal()
        goal.target_x = self.target_x
        goal.target_y = self.target_y

        self.navigate_to_position_client.send_goal_async(
            goal, feedback_callback=self.goal_feedback_callback
        ).add_done_callback(self.goal_response_callback)

    def cancel_service_callback(
        self,
        request: Trigger.Request,
        response: Trigger.Response
    ) -> Trigger.Response:
        """Cancel the active goal when a service request is received."""
        if self.goal_handle is None:
            response.success = False
            response.message = "No active goal."
            return response

        self.get_logger().info(
            "Received cancel service request."
        )

        # The service only sends the cancel request.
        # Acceptance is processed asynchronously in cancel_response_callback().
        self.goal_handle.cancel_goal_async().add_done_callback(
            self.cancel_response_callback
        )

        response.success = True
        response.message = "Cancel request sent."
        return response

    def cancel_response_callback(self, future) -> None:
        cancel_response = future.result()

        if cancel_response.goals_canceling:
            self.get_logger().info("Cancel request was accepted.")
        else:
            self.get_logger().warning("Cancel request was rejected.")

    def goal_feedback_callback(self, feedback_msg) -> None:
        if not self.show_feedback:
            return

        distance_remaining = feedback_msg.feedback.distance_remaining
        self.get_logger().info(f"Got feedback: {distance_remaining}.")

    def goal_response_callback(self, future) -> None:
        """Process whether the server accepted or rejected the goal."""
        self.goal_handle = future.result()

        if not self.goal_handle.accepted:
            self.get_logger().warning("Goal got rejected.")
            self.goal_handle = None
            rclpy.shutdown()
            return

        self.get_logger().info("Goal got accepted.")

        self.goal_handle.get_result_async().add_done_callback(
            self.goal_result_callback
        )
        
    def goal_result_callback(self, future) -> None:
        """Process the final action status and result."""
        response = future.result()
        status = response.status
        result = response.result

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info("Goal succeeded.")
        elif status == GoalStatus.STATUS_ABORTED:
            self.get_logger().error("Goal was aborted.")
        elif status == GoalStatus.STATUS_CANCELED:
            self.get_logger().warning("Goal was canceled.")
        else:
            self.get_logger().warning(
                f"Unexpected goal status: {status}"
            )

        self.get_logger().info(
            f"Result:\n"
            f"x: {result.final_x}\n"
            f"y: {result.final_y}"
        )

        self.goal_handle = None

        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)

    node = NavigateToPositionClientNode()

    if node.ensure_target_position():
        node.send_goal()
        rclpy.spin(node)

    if rclpy.ok():
        rclpy.shutdown()


if __name__ == "__main__":
    main()