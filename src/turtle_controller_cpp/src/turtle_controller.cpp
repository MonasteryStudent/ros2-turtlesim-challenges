#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "turtlesim/msg/pose.hpp"
#include "turtlesim/srv/set_pen.hpp"
#include <map>
#include <string>

using namespace std::placeholders;
using namespace std::chrono_literals;
using Pose = turtlesim::msg::Pose;
using Twist = geometry_msgs::msg::Twist;
using Pen = turtlesim::srv::SetPen;

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
        set_pen_client_ = this->create_client<Pen>("/turtle1/set_pen");

        init_pen_color_settings();

        RCLCPP_INFO(this->get_logger(), "Turtle Controller has been started.");
    }
    
private:

    enum class PenColor
    {
        Green,
        Red
    };

    struct Color
    {
        uint8_t r;
        uint8_t g;
        uint8_t b;
    };

    std::string pen_color_to_string(PenColor color) 
    {
        switch (color) {
            case PenColor::Green:
                return "green";
            case PenColor::Red:
                return "red";
        }
        return "unkown";
    }

    void init_pen_color_settings()
    {   
        pen_cur_color_ = PenColor::Green;
        pen_request_pending_ = false;
        pen_colors_ = {
            {PenColor::Green, {0, 255, 0}},
            {PenColor::Red, {255, 0, 0}}
        };
    }

    void call_set_pen(PenColor color_name) 
    {
        if (pen_request_pending_) {
            return;
        }

        while (!set_pen_client_->wait_for_service(1s)) {
            RCLCPP_WARN(this->get_logger(), "Waiting for the server...");
        }

        auto request = std::make_shared<Pen::Request>();
        Color color =  pen_colors_.at(color_name);
        request->r = color.r;
        request->g = color.g;
        request->b = color.b;

        pen_request_pending_ = true;
        set_pen_client_->async_send_request(
            request,
            [this, color_name](rclcpp::Client<Pen>::SharedFuture future)
            {
                set_pen_callback(future, color_name);
            }
        );
    }

    void set_pen_callback(rclcpp::Client<Pen>::SharedFuture future, PenColor color_name)
    {
        auto response = future.get();
        pen_cur_color_ = color_name;
        pen_request_pending_ = false;
        std::string color = pen_color_to_string(color_name);
        RCLCPP_INFO(this->get_logger(), "Pen color has changed to %s.", color.c_str());
    }

    void pose_callback(const Pose::SharedPtr pose)
    {
        float screen_middle = 5.5;
        auto cmd = Twist();
        if (pose->x < screen_middle) {
            cmd.linear.x = 1.0;
            cmd.angular.z = 1.0;
            if (pen_cur_color_ == PenColor::Red){
                call_set_pen(PenColor::Green);
            }
        } else {
            cmd.linear.x = 2.0;
            cmd.angular.z = 2.0;
            if (pen_cur_color_ == PenColor::Green) {
                call_set_pen(PenColor::Red);
            }
        }
        cmd_vel_pub_->publish(cmd);
        
    }

    PenColor pen_cur_color_;
    bool pen_request_pending_;
    std::map<PenColor, Color> pen_colors_;

    rclcpp::Subscription<Pose>::SharedPtr pose_sub_;
    rclcpp::Publisher<Twist>::SharedPtr cmd_vel_pub_;
    rclcpp::Client<Pen>::SharedPtr set_pen_client_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<TurtleControllerNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}