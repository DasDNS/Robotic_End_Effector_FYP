# ROS2 Jazzy Beginner Setup
## Python Publisher–Subscriber Test (Foundation for STM32 Serial Bridge)

---

## 📌 Project Goal

This project demonstrates **basic ROS2 communication** using a **Python publisher and subscriber**.

It is designed as a **foundation** for later connecting:
- Vision system (Computer B)
- Serial bridge (Computer A)
- STM32 microcontroller via USB-to-TTL

Before connecting hardware, we **verify ROS2 message passing between two nodes**.

---

## 🖥 System Requirements

- Ubuntu Linux (22.04 or newer)
- Python 3.12
- ROS2 Jazzy Jalisco

---

## 1️⃣ Install ROS2 Jazzy

### Install ROS2 Jazzy Desktop

```bash
sudo apt update
sudo apt install ros-jazzy-desktop
```

**Why this is needed:**  
Installs ROS2 core, DDS middleware, Python tools, and demo packages.

---

### Source ROS2 Environment

```bash
source /opt/ros/jazzy/setup.bash
```

**Why this is needed:**  
Makes `ros2`, `colcon`, and ROS libraries available in the current terminal.

Make it permanent:

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

### Verify Installation

```bash
ros2 doctor
```

**Why this is needed:**  
Checks if ROS2 is installed correctly. Version warnings are safe to ignore.

---

## 2️⃣ Create a ROS2 Workspace

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
```

**Why this is needed:**  
ROS2 uses workspaces to organize and build packages.

Initial build:

```bash
colcon build
source install/setup.bash
```

---

## 3️⃣ Create a Python ROS2 Package

```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python my_py_pkg --dependencies rclpy std_msgs
```

**Why this is needed:**  
Creates a Python-based ROS2 package with required dependencies.

---

## 📁 Folder Structure

```
ros2_ws/
 └── src/
     └── my_py_pkg/
         ├── my_py_pkg/
         │   ├── __init__.py
         │   ├── publisher_node.py
         │   └── subscriber_node.py
         ├── setup.py
         ├── setup.cfg
         └── package.xml
```

---

## 4️⃣ Publisher Node

Create the file:

```bash
nano ~/ros2_ws/src/my_py_pkg/my_py_pkg/publisher_node.py
```

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class SimplePublisher(Node):
    def __init__(self):
        super().__init__(node_name='simple_publisher')
        self.publisher_ = self.create_publisher(String, 'chatter', 10)
        self.timer = self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        msg = String()
        msg.data = "Hello from Publisher!"
        self.publisher_.publish(msg)
        self.get_logger().info(f"Published: {msg.data}")

def main(args=None):
    rclpy.init(args=args)
    node = SimplePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

Make executable:

```bash
chmod +x ~/ros2_ws/src/my_py_pkg/my_py_pkg/publisher_node.py
```

---

## 5️⃣ Subscriber Node

Create the file:

```bash
nano ~/ros2_ws/src/my_py_pkg/my_py_pkg/subscriber_node.py
```

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class SimpleSubscriber(Node):
    def __init__(self):
        super().__init__(node_name='simple_subscriber')
        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.listener_callback,
            10
        )

    def listener_callback(self, msg):
        self.get_logger().info(f"Received: {msg.data}")

def main(args=None):
    rclpy.init(args=args)
    node = SimpleSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

Make executable:

```bash
chmod +x ~/ros2_ws/src/my_py_pkg/my_py_pkg/subscriber_node.py
```

---

## 6️⃣ Register Nodes in setup.py

Edit:

```bash
nano ~/ros2_ws/src/my_py_pkg/setup.py
```

Add:

```python
entry_points={
    'console_scripts': [
        'publisher_node = my_py_pkg.publisher_node:main',
        'subscriber_node = my_py_pkg.subscriber_node:main',
    ],
},
```

**Why this is needed:**  
Allows nodes to be executed using `ros2 run`.

---

## 7️⃣ Clean, Build, and Source

```bash
cd ~/ros2_ws
rm -rf build install log
colcon build
source install/setup.bash
```

**Why this is needed:**  
ROS2 executes code from the `install/` directory. Cleaning prevents old code issues.

---

## 8️⃣ Run the Nodes

### Terminal 1 – Subscriber

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run my_py_pkg subscriber_node
```

### Terminal 2 – Publisher

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run my_py_pkg publisher_node
```

---

## ✅ Expected Output

Subscriber terminal:
```
[INFO] [simple_subscriber]: Received: Hello from Publisher!
```

Publisher terminal:
```
[INFO] [simple_publisher]: Published: Hello from Publisher!
```

---

## 9️⃣ Useful ROS2 Commands

```bash
ros2 topic list
ros2 topic echo /chatter
ros2 node list
```

---

## 🔜 Next Steps

- Replace publisher with vision system output
- Add ROS2 → Serial bridge
- Connect STM32 via USB-TTL
- Enable bidirectional communication

---

## 📌 Key Notes

- Always source setup files
- Always rebuild after code changes
- ROS2 Jazzy requires explicit `node_name=`
- `install/` directory is what ROS2 executes

