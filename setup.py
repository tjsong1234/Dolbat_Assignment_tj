from glob import glob
from setuptools import find_packages, setup

setup(
    name='turtle_click_nav',
    version='0.1.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/turtle_click_nav']),
        ('share/turtle_click_nav', ['package.xml']),
        ('share/turtle_click_nav/screenshots', glob('screenshots/*.png')),
        ('share/turtle_click_nav/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='tjsong12',
    maintainer_email='tjsong12@example.com',
    description='Educational turtlesim click navigation',
    license='Apache-2.0',
    entry_points={'console_scripts': [
        'goal_clicker = turtle_click_nav.goal_clicker:main',
        'go_to_goal = turtle_click_nav.go_to_goal:main',
    ]},
)
