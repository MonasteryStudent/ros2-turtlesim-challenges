# ROS 2 Turtlesim Challenges

A collection of independently implemented ROS 2 challenges built around the `turtlesim` package.

This repository documents my progress in learning ROS 2 by solving the challenge exercises from the book *ROS 2 from Scratch* by Edouard Renard.

## Learning Goals

The goal of this project is to strengthen my understanding of ROS 2 by implementing practical applications using concepts such as:

- Nodes
- Topics
- Services
- Actions
- Parameters
- Launch Files
- Custom Interfaces

Each challenge builds upon the previous one, resulting in a progressively more capable ROS 2 application.

## Current Challenge

### Closed-Loop Turtle Controller

The controller subscribes to the turtle's pose and publishes velocity commands to move the turtle in a circle.

Behavior:

- If `x < 5.5`, the turtle moves with:
  - `linear.x = 1.0`
  - `angular.z = 1.0`
- Otherwise:
  - `linear.x = 2.0`
  - `angular.z = 2.0`

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

Start the controller:

```bash
ros2 run turtle_controller_py turtle_controller
```

## Acknowledgement

The challenge descriptions are based on the book *ROS 2 from Scratch* by Edouard Renard.

The implementations in this repository are my own solutions developed as part of my learning process.