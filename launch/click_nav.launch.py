from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, RegisterEventHandler
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    turtle = Node(package='turtlesim', executable='turtlesim_node',
                  name='turtlesim', output='screen')
    clicker = Node(package='turtle_click_nav', executable='goal_clicker',
                   name='goal_clicker', output='screen')
    controller = Node(package='turtle_click_nav', executable='go_to_goal',
                      name='go_to_goal', output='screen')
    # 필수 노드의 창이나 프로세스가 종료되면 전체 시스템도 종료한다.
    handlers = [RegisterEventHandler(OnProcessExit(
        target_action=process,
        on_exit=[EmitEvent(event=Shutdown(reason='Required navigation node exited'))],
    )) for process in (turtle, clicker, controller)]
    return LaunchDescription([
        DeclareLaunchArgument('show_graph', default_value='true',
                              description='Open rqt_graph alongside navigation'),
        *handlers, turtle, controller, clicker,
        Node(package='rqt_graph', executable='rqt_graph', name='navigation_graph',
             condition=IfCondition(LaunchConfiguration('show_graph')),
             output='screen'),
    ])
