#include <cstdint>
#include <map>
#include <vector>
#include <string>
#include <stdexcept>

#include "rclcpp/rclcpp.hpp"
#include "rcl_interfaces/msg/set_parameters_result.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "turtlesim/msg/pose.hpp"
#include "turtlesim/srv/set_pen.hpp"
#include "turtle_controller_interfaces/srv/switch_activation.hpp"

using namespace std::placeholders;
using namespace std::chrono_literals;
using Pose = turtlesim::msg::Pose;
using Twist = geometry_msgs::msg::Twist;
using Pen = turtlesim::srv::SetPen;
using SwitchActivation = turtle_controller_interfaces::srv::SwitchActivation;

class TurtleControllerNode : public rclcpp::Node
{
public:

    TurtleControllerNode() : Node("turtle_controller")
    {
        is_active_ = true;

        this->declare_parameter("color_left", "green");
        this->declare_parameter("color_right", "red");
        this->declare_parameter("turtle_velocity", 1.0);

        color_left_ = this->get_parameter("color_left").as_string();
        color_right_ = this->get_parameter("color_right").as_string();
        turtle_velocity_ = this->get_parameter("turtle_velocity").as_double();

        init_pen_color_settings();

        validate_params();

        pen_cur_color_ = color_left_;
        pending_pen_color_ = "";
        pen_request_pending_ = false;

        pose_sub_ = this->create_subscription<Pose>(
            "/turtle1/pose",
            10,
            std::bind(&TurtleControllerNode::pose_callback, this, _1)
        );
        cmd_vel_pub_ = this->create_publisher<Twist>("/turtle1/cmd_vel", 10);
        set_pen_client_ = this->create_client<Pen>("/turtle1/set_pen");
        switch_activation_service_ = this->create_service<SwitchActivation>(
            "switch_activation",
            std::bind(&TurtleControllerNode::switch_activation_service_callback, this, _1, _2)
        );
        param_callback_handle_ = this->add_on_set_parameters_callback(
            std::bind(
                &TurtleControllerNode::parameters_callback,
                this,
                _1
            )
        );

        RCLCPP_INFO(this->get_logger(), "Turtle Controller has been started.");
    }
    
private:

    struct Color
    {
        uint8_t r;
        uint8_t g;
        uint8_t b;
    };

    void init_pen_color_settings()
    {   
        pen_colors_ = {
            {"green", {0, 255, 0}},
            {"red", {255, 0, 0}},
            {"yellow", {255, 255, 0}},
            {"purple", {128, 0, 128}},
            {"orange", {255, 165, 0}},
            {"cyan", {0, 255, 255}}
        };
    }

    void validate_color_param(
        const std::string color,
        const std::string side,
        std::vector<std::string>& errors)
    {
        if (pen_colors_.find(color) == pen_colors_.end()) {
            errors.push_back(
                "Invalid value for '" + side + "': '" + color + "'."
            );
        }
    }

    void validate_velocity_param(
        double velocity,
        std::vector<std::string>& errors)
    {
        const double min_velocity = 0.0;
        const double max_velocity = 3.0;

        if (!(min_velocity < velocity && velocity <= max_velocity)) {
            errors.push_back(
                "Invalid value for 'turtle_velocity': '" +
                std::to_string(velocity) +
                "'.\nValid range is (0.0, 3.0]."
            );
        }
    }

    /// Validate all configurable node parameters.
    void validate_params()
    {
        std::vector<std::string> color_errors;
        std::vector<std::string> velocity_errors;

        validate_color_param(color_left_, "color_left", color_errors);
        validate_color_param(color_right_, "color_right", color_errors);
        validate_velocity_param(turtle_velocity_, velocity_errors);

        if (!color_errors.empty()) {
            std::string valid_colors = "Valid colors are: ";
            bool first = true;

            for (const auto& entry : pen_colors_) {
                if (!first) {
                    valid_colors += ", ";
                }

                valid_colors += entry.first;
                first = false;
            }

            valid_colors += ".";
            color_errors.push_back(valid_colors);
        }

        std::vector<std::string> errors = color_errors;

        errors.insert(
            errors.end(),
            velocity_errors.begin(),
            velocity_errors.end()
        );

        if (!errors.empty()) {
            std::string message;

            for (std::size_t i = 0; i < errors.size(); ++i) {
                if (i > 0) {
                    message += "\n";
                }

                message += errors[i];
            }

            throw std::invalid_argument(message);
        }
    }

    /// Send a request to change the turtle's pen color.
    void call_set_pen(std::string color_name) 
    {
        if (pen_request_pending_) {
            // Keep only the most recently requested color.
            pending_pen_color_ = color_name;
            return;
        }

        while (!set_pen_client_->wait_for_service(1s)) {
            RCLCPP_WARN(this->get_logger(), "Waiting for the server...");
        }

        auto request = std::make_shared<Pen::Request>();
        const Color color = pen_colors_.at(color_name);
        request->r = color.r;
        request->g = color.g;
        request->b = color.b;

        pen_request_pending_ = true;

        set_pen_client_->async_send_request(
            request,
            // Capture the requested color so the confirmed state can be updated
            // when the asynchronous service call completes.
            [this, color_name](rclcpp::Client<Pen>::SharedFuture future)
            {
                set_pen_callback(future, color_name);
            }
        );
    }

    /// Porcess the result of a pen color change request.
    void set_pen_callback(rclcpp::Client<Pen>::SharedFuture future, std::string color_name)
    {
        future.get();
        pen_cur_color_ = color_name;
        pen_request_pending_ = false;
        RCLCPP_INFO(this->get_logger(), "Pen color has changed to %s.", pen_cur_color_.c_str());
        
        if (!pending_pen_color_.empty()) {
            std::string next_color = pending_pen_color_;
            pending_pen_color_.clear();

            if (next_color != pen_cur_color_) {
                call_set_pen(next_color);
            }
        }
    }

    void pose_callback(const Pose::SharedPtr pose)
    {
        if (!is_active_) {
            return;
        }

        const double screen_middle = 5.5;
        auto cmd = Twist();

        if (pose->x < screen_middle) {
            cmd.linear.x = turtle_velocity_;
            cmd.angular.z = turtle_velocity_;
            if (pen_cur_color_ == color_right_) {
                call_set_pen(color_left_);
            }
        } else {
            cmd.linear.x = turtle_velocity_ * 2.0;
            cmd.angular.z = turtle_velocity_ * 2.0;
            if (pen_cur_color_ == color_left_) {
                call_set_pen(color_right_);
            }
        }
        cmd_vel_pub_->publish(cmd);
    }

    void switch_activation_service_callback(
        const SwitchActivation::Request::SharedPtr request,
        const SwitchActivation::Response::SharedPtr response)
    {
        if (request->activate == is_active_) {
            response->success = false;
            response->message = is_active_
                ? "Turtle already activated."
                : "Turtle already deactivated.";
            return;
        }

        is_active_ = request->activate;
        response->success = true;
        response->message = is_active_
            ? "Turtle activated."
            : "Turtle deactivated.";
    }

    /// Validate and apply parameter changes at runtime.
    rcl_interfaces::msg::SetParametersResult parameters_callback(
        const std::vector<rclcpp::Parameter>& params)
    {
        std::vector<std::string> color_errors;
        std::vector<std::string> velocity_errors;

        for (const auto& param : params) {
            if (param.get_name() == "color_left" ||
                param.get_name() == "color_right"
            ) {
                validate_color_param(
                    param.as_string(), 
                    param.get_name(), 
                    color_errors
                );
            }
            else if (param.get_name() == "turtle_velocity") {
                validate_velocity_param(
                    param.as_double(),
                    velocity_errors
                );
            }
        }

        if (!color_errors.empty()) {
            std::string valid_colors = "Valid colors are: ";
            bool first = true;

            for (const auto& entry : pen_colors_) {
                if (!first) {
                    valid_colors += ", ";
                }

                valid_colors += entry.first;
                first = false;
            }

            valid_colors += ".";
            color_errors.push_back(valid_colors);
        }

        std::vector<std::string> errors = color_errors;
        
        errors.insert(
            errors.end(),
            velocity_errors.begin(),
            velocity_errors.end()
        );
        
        rcl_interfaces::msg::SetParametersResult result;

        if (!errors.empty()) {
            std::string message;

            for (std::size_t i = 0; i < errors.size(); ++i) {
                if (i > 0) {
                    message += "\n";
                }
                message += errors[i];
            }

            result.successful = false;
            result.reason = message;
            return result;
        }

        for (const auto& param : params) {
            if (param.get_name() == "color_left") {
                if (pen_cur_color_ == color_left_) {
                    call_set_pen(param.as_string());
                }
                color_left_ = param.as_string();
            }
            else if (param.get_name() == "color_right") {
                if (pen_cur_color_ == color_right_) {
                    call_set_pen(param.as_string());
                }
                color_right_ = param.as_string();
            }
            else if (param.get_name() == "turtle_velocity") {
                turtle_velocity_ = param.as_double();
            }
        }

        result.successful = true;
        return result;
    }

    std::string pen_cur_color_;
    std::string pending_pen_color_;
    std::map<std::string, Color> pen_colors_;
    std::string color_left_;
    std::string color_right_;
    bool is_active_;
    bool pen_request_pending_;
    double turtle_velocity_;

    rclcpp::Subscription<Pose>::SharedPtr pose_sub_;
    rclcpp::Publisher<Twist>::SharedPtr cmd_vel_pub_;
    rclcpp::Client<Pen>::SharedPtr set_pen_client_;
    rclcpp::Service<SwitchActivation>::SharedPtr switch_activation_service_;
    rclcpp::node_interfaces::OnSetParametersCallbackHandle::SharedPtr param_callback_handle_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<TurtleControllerNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}