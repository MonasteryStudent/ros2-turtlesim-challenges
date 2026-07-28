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

This self-designed challenge introduces ROS 2 actions by implementing a navigation Action Server for `turtlesim`.

The server accepts a target position and controls the turtle until the destination is reached.

Features:

- Accepts target coordinates through a custom `NavigateToPosition` action.
- Rejects targets outside the valid `turtlesim` area.
- Rejects new goals while another goal is active.
- Continuously publishes the remaining distance as feedback.
- Supports cancel requests.
- Returns the final turtle position and whether the goal was completed successfully.
- Uses a closed-loop controller based on the current turtle pose.
- Uses a `MultiThreadedExecutor` and a `ReentrantCallbackGroup` so pose updates and Action callbacks can be processed concurrently.

Unlike the previous challenges, this challenge was designed independently to apply the ROS 2 Action concepts introduced in the book.

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

Start the Python controller:

```bash
ros2 run turtle_controller_py turtle_controller
```

Start the C++ controller:

```bash
ros2 run turtle_controller_cpp turtle_controller
```

## Acknowledgement

The Topic and Service challenges are based on the book *ROS 2 from Scratch* by Edouard Renard.

The Action challenge was designed independently to explore ROS 2 actions, feedback, cancellation, and concurrency.

All implementations in this repository are my own solutions developed as part of my learning process.