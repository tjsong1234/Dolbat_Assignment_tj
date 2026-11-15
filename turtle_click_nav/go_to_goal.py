"""현재 위치를 받아 목표와의 오차에 비례하는 속도 명령을 만드는 제어 노드."""

import math
import time

import rclpy
from geometry_msgs.msg import PointStamped, Twist
from rclpy.node import Node
from turtlesim.msg import Pose


def compute_velocity(x, y, theta, goal_x, goal_y, tolerance, k_linear,
                     k_angular, max_linear, max_angular):
    """(선속도, 각속도, 도착 여부)를 반환한다. 속도 단위는 m/s와 rad/s다."""
    dx, dy = goal_x - x, goal_y - y
    distance = math.hypot(dx, dy)
    if distance <= tolerance:
        return 0.0, 0.0, True
    desired_heading = math.atan2(dy, dx)
    # 방향 오차를 [-π, π] 범위로 바꿔 더 짧은 방향으로 회전하게 한다.
    heading_error = math.atan2(math.sin(desired_heading - theta),
                               math.cos(desired_heading - theta))
    angular = max(-max_angular, min(max_angular, k_angular * heading_error))
    # 목표 방향과 잘 맞을수록 전진 속도를 높인다.
    alignment = max(0.0, math.cos(heading_error))
    linear = min(max_linear, k_linear * distance) * alignment
    if abs(heading_error) > math.pi / 3:
        linear = 0.0
    return linear, angular, False


class GoToGoal(Node):
    def __init__(self):
        super().__init__('go_to_goal')
        defaults = {'goal_tolerance': 0.12, 'k_linear': 1.2,
                    'k_angular': 5.0, 'max_linear_speed': 2.0,
                    'max_angular_speed': 4.0, 'pose_timeout': 1.0}
        for name, value in defaults.items():
            self.declare_parameter(name, value)
        self.settings = {name: float(self.get_parameter(name).value)
                         for name in defaults}
        if any(not math.isfinite(value) or value <= 0
               for value in self.settings.values()):
            raise ValueError('All controller parameters must be finite and positive')
        self.pose = None
        self.pose_time = None
        self.goal = None
        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.create_subscription(Pose, '/turtle1/pose', self.on_pose, 10)
        self.create_subscription(PointStamped, '/goal_point', self.on_goal, 10)
        self.create_timer(0.05, self.control_step)  # 0.05초마다 제어 수행: 20 Hz
        self.get_logger().info('Ready: waiting for a click on the goal map.')

    def on_pose(self, msg):
        self.pose = msg
        self.pose_time = time.monotonic()

    def on_goal(self, msg):
        x, y = msg.point.x, msg.point.y
        if msg.header.frame_id != 'world' or not all(
                math.isfinite(v) and 0.5 <= v <= 10.5 for v in (x, y)):
            self.get_logger().warning('Rejected goal: use world frame, x/y in [0.5, 10.5].')
            return
        self.goal = (x, y)
        self.get_logger().info(f'New goal: ({x:.2f}, {y:.2f})')

    def control_step(self):
        cmd = Twist()  # 기본 속도는 0: 목표가 없거나 위치 정보가 오래됐으면 정지한다.
        if (self.goal is not None and self.pose is not None
                and time.monotonic() - self.pose_time <= self.settings['pose_timeout']):
            s = self.settings
            linear, angular, arrived = compute_velocity(
                self.pose.x, self.pose.y, self.pose.theta, *self.goal,
                s['goal_tolerance'], s['k_linear'], s['k_angular'],
                s['max_linear_speed'], s['max_angular_speed'])
            cmd.linear.x, cmd.angular.z = linear, angular
            if arrived:
                self.get_logger().info('Goal reached. Stopping.')
                self.goal = None
        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = GoToGoal()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.cmd_pub.publish(Twist())
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
