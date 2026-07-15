#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "turtlesim/msg/pose.hpp"

using namespace std::placeholders;
using Pose = turtlesim::msg::Pose;
using Twist = geometry_msgs::msg::Twist;

class TurtleControllerNode : public rclcpp::Node
{
public:
    TurtleControllerNode() : Node("turtle_controller")
    {
        pose_sub_ = this->create_subscription<Pose>(
            "/turtle1/pose",
            10,
            std::bind(&TurtleControllerNode::pose_callback, this, _1)
        );
        cmd_vel_pub_ = this->create_publisher<Twist>("/turtle1/cmd_vel", 10);
        RCLCPP_INFO(this->get_logger(), "Turtle Controller has been started.");
    }
    
private:
    void pose_callback(const Pose::SharedPtr pose)
    {
        float screen_middle = 5.5;
        auto cmd = Twist();
        if (pose->x < screen_middle) {
            cmd.linear.x = 1.0;
            cmd.angular.z = 1.0;
        } else {
            cmd.linear.x = 2.0;
            cmd.angular.z = 2.0;
        }
        cmd_vel_pub_->publish(cmd);
        
    }

    rclcpp::Subscription<Pose>::SharedPtr pose_sub_;
    rclcpp::Publisher<Twist>::SharedPtr cmd_vel_pub_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<TurtleControllerNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}