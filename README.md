# ROS 2 Turtlesim Challenges

A collection of independently implemented ROS 2 challenges built around the `turtlesim` package.

The challenges are based on the book *ROS 2 from Scratch* by Edouard Renard and are implemented as part of my personal learning journey.

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

Each challenge extends the previous one, resulting in a progressively more capable ROS 2 application.

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

*Coming soon.*

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

The challenge descriptions are based on the book *ROS 2 from Scratch* by Edouard Renard.

The implementations in this repository are my own solutions developed as part of my learning process.