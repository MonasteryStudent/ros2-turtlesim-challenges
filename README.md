# ROS 2 Turtlesim Challenges

A collection of independently implemented ROS 2 challenges built around the `turtlesim` package.

The Topic and Service challenges are based on the book *ROS 2 from Scratch* by Edouard Renard. The Action challenge was designed independently to apply and deepen the concepts introduced in the book.

## Learning Goals

This project aims to gain hands-on experience with ROS 2 software development by implementing practical applications in both **Python** (`rclpy`) and **C++** (`rclcpp`).

The challenges cover core ROS 2 concepts such as:

- Nodes
- Topics
- Services
- Actions
- Parameters
- Launch Files
- Custom Interfaces

The challenges build upon previously introduced ROS 2 concepts, resulting in progressively more capable applications.

## Challenges

### 1. Topic Challenge

A closed-loop turtle controller that subscribes to the turtle's pose and publishes velocity commands to move the turtle in a circle.

Behavior:

- If `x < 5.5`:
  - `linear.x = 1.0`
  - `angular.z = 1.0`
- Otherwise:
  - `linear.x = 2.0`
  - `angular.z = 2.0`

### 2. Service Challenge

#### 2.1 Service Client

The turtle controller is extended with a service client that changes the turtle's pen color using the `SetPen` service.

Behavior:

- Green pen while the turtle is on the left side of the screen.
- Red pen while the turtle is on the right side of the screen.

#### 2.2 Custom Interface and Service Server

The turtle controller is extended with a custom service interface and a service server that allows external clients to activate or deactivate the turtle.

When the controller is deactivated, it stops publishing new velocity commands. When reactivated, it resumes controlling the turtle.

### 3. Action Challenge

This self-designed challenge introduces ROS 2 actions by implementing a navigation Action Server and Action Client for `turtlesim`.

The server accepts a target position and controls the turtle until the destination is reached. The client sends the navigation goal, processes feedback and the final result, and provides a service for canceling the goal.

Features:

- Uses a custom `NavigateToPosition` action with goal, result, and feedback data.
- Accepts target coordinates through ROS 2 parameters or terminal input.
- Rejects targets outside the valid `turtlesim` area.
- Rejects new goals while another goal is active.
- Publishes the remaining distance as feedback at regular intervals.
- Processes successful, aborted, and canceled goal states.
- Exposes a `/cancel_navigation` service using `std_srvs/srv/Trigger`.
- Allows the active goal to be canceled through a ROS 2 service.
- Returns the final turtle position and whether the navigation completed successfully.
- Uses a closed-loop controller based on the current turtle pose.
- Uses a `MultiThreadedExecutor` and a `ReentrantCallbackGroup` so pose updates and Action callbacks can be processed concurrently.
- Allows feedback logging to be enabled through the `show_feedback` parameter.

Unlike the previous challenges, this challenge was designed independently to apply the ROS 2 Action concepts introduced in the book.

### 4. Parameters Challenge

This challenge extends the turtle controller by introducing configurable ROS 2 parameters.

The controller can be customized through command-line arguments or a YAML parameter file.

Features:

- Configures the left and right pen colors through ROS 2 parameters.
- Configures the turtle's movement speed through a ROS 2 parameter.
- Validates all parameter values during startup.
- Reports invalid parameter values together with the list of supported colors.
- Supports loading parameter sets from a YAML configuration file.

## Requirements

- Ubuntu 24.04
- ROS 2 Jazzy Jalisco

## Build

```bash
colcon build
```

Source the workspace:

```bash
source install/setup.bash
```

Alternatively, you can use the provided helper script, which sources both the ROS 2 installation and the workspace:

```bash
source scripts/setup.sh
```

## Run

Start `turtlesim`:

```bash
ros2 run turtlesim turtlesim_node
```

Then run the desired node from one of the packages, for example:

```bash
ros2 run <package_name> <executable_name>
```

## Acknowledgement

The Topic and Service challenges are based on the book *ROS 2 from Scratch* by Edouard Renard.

The Action challenge was designed independently to explore ROS 2 actions, feedback, cancellation, and concurrency.

All implementations in this repository are my own solutions developed as part of my learning process.