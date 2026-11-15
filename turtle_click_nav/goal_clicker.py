"""Tk 지도에서 클릭한 지점을 ROS 메시지의 목표 좌표로 발행한다."""

import math
import tkinter as tk

import rclpy
from geometry_msgs.msg import PointStamped
from rclpy.node import Node
from turtlesim.msg import Pose


class GoalClicker(Node):
    SIZE = 550
    WORLD = 11.088889  # turtlesim 화면에 보이는 좌표 영역의 대략적인 가로·세로 길이

    def __init__(self):
        super().__init__('goal_clicker')
        self.pub = self.create_publisher(PointStamped, '/goal_point', 10)
        self.create_subscription(Pose, '/turtle1/pose', self.on_pose, 10)
        self.root = tk.Tk()
        self.root.title('Turtle Goal Map - Click to move')
        self.root.protocol('WM_DELETE_WINDOW', self.root.quit)
        tk.Label(self.root, text='Click a target. Orange = goal, green = turtle.').pack()
        self.canvas = tk.Canvas(self.root, width=self.SIZE, height=self.SIZE,
                                bg='#192b40', highlightthickness=0)
        self.canvas.pack()
        self.status = tk.StringVar(value='Waiting for turtlesim pose...')
        tk.Label(self.root, textvariable=self.status).pack()
        for value in range(1, 12):
            pixel = value / self.WORLD * self.SIZE
            self.canvas.create_line(pixel, 0, pixel, self.SIZE, fill='#30445c')
            self.canvas.create_line(0, self.SIZE - pixel, self.SIZE,
                                    self.SIZE - pixel, fill='#30445c')
        self.canvas.create_text(6, self.SIZE - 8, text='(0,0)',
                                anchor='sw', fill='white')
        self.canvas.create_text(self.SIZE - 8, 8, text='x right / y up',
                                anchor='ne', fill='white')
        self.canvas.bind('<Button-1>', self.on_click)

    def on_click(self, event):
        # 화면은 아래쪽으로 y가 커지고, ROS 좌표는 위쪽으로 y가 커지므로 뒤집는다.
        x = max(0.5, min(10.5, event.x / self.SIZE * self.WORLD))
        y = max(0.5, min(10.5, (self.SIZE - event.y) / self.SIZE * self.WORLD))
        msg = PointStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'world'
        msg.point.x, msg.point.y = x, y
        self.pub.publish(msg)
        px, py = x / self.WORLD * self.SIZE, self.SIZE - y / self.WORLD * self.SIZE
        self.canvas.delete('goal')
        self.canvas.create_oval(px - 7, py - 7, px + 7, py + 7,
                                outline='#ffb347', width=3, tags='goal')
        self.status.set(f'Goal: x={x:.2f}, y={y:.2f} (world)')
        self.get_logger().info(f'Published goal: ({x:.2f}, {y:.2f})')

    def on_pose(self, pose):
        px = pose.x / self.WORLD * self.SIZE
        py = self.SIZE - pose.y / self.WORLD * self.SIZE
        self.canvas.delete('turtle')
        self.canvas.create_oval(px - 6, py - 6, px + 6, py + 6,
                                fill='#73e5a1', tags='turtle')
        self.canvas.create_line(px, py, px + 20 * math.cos(pose.theta),
                                py - 20 * math.sin(pose.theta),
                                fill='#73e5a1', width=3, arrow=tk.LAST, tags='turtle')

    def poll_ros(self):
        if rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.0)
            self.root.after(20, self.poll_ros)
        else:
            self.root.quit()


def main(args=None):
    rclpy.init(args=args)
    node = GoalClicker()
    try:
        node.poll_ros()
        node.root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        node.root.destroy()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
