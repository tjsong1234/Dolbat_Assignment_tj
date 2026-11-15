# turtle_click_nav

마우스로 선택한 목표 좌표까지 turtlesim의 거북이를 이동시키는 ROS 2 패키지입니다.

## 파일 설명

| 파일 | 역할 |
|---|---|
| `turtle_click_nav/goal_clicker.py` | 목표 지도 창에서 클릭한 위치를 `/goal_point`로 발행하고, `/turtle1/pose`를 구독해 현재 위치를 표시합니다. |
| `turtle_click_nav/go_to_goal.py` | `/goal_point`와 `/turtle1/pose`를 구독하고, 위치·방향 오차에 비례하는 속도를 계산해 `/turtle1/cmd_vel`로 발행합니다. 목표에 도착하면 정지합니다. |
| `turtle_click_nav/__init__.py` | Python 패키지를 구성하는 초기화 파일입니다. |
| `launch/click_nav.launch.py` | `turtlesim`, `goal_clicker`, `go_to_goal`과 rqt_graph를 함께 실행합니다. `show_graph:=false`로 rqt_graph 실행을 생략할 수 있습니다. |
| `package.xml` | 패키지 정보와 ROS 2 실행 의존성을 정의합니다. |
| `setup.py` | Python 패키지, 실행 프로그램, launch 파일의 설치 구성을 정의합니다. |
| `setup.cfg` | ROS 2가 실행 프로그램을 찾을 수 있도록 설치 경로를 지정합니다. |
| `resource/turtle_click_nav` | ament 인덱스에 패키지를 등록하기 위한 리소스 파일입니다. |
| `.gitignore` | 빌드 결과, 로그, Python 캐시 등을 Git 관리 대상에서 제외합니다. |
