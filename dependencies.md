# burger_war

Rabbitのリポジトリについて

## インストール

### 1. このリポジトリをクローン

```
$ cd ~/catkin_ws/src
$ git clone -b develop https://github.com/TeamRabbit/burger_war.git
```

### 2. 追加のライブラリのインストール

```
$ sudo apt install ros-kinetic-dwa-local-planner
$ sudo apt install ros-kinetic-jsk-rviz-plugins
$ sudo apt install ros-kinetic-smach*
$ sudo apt install -y libarmadillo-dev libarmadillo6 
```

> NOTE: **roswiki**  
> http://wiki.ros.org/dwa_local_planner  
> http://wiki.ros.org/jsk_rviz_plugins  
> http://wiki.ros.org/smach


### 3. 環境変数を追加

```
$ export GAZEBO_MODEL_PATH=$HOME/catkin_ws/src/burger_war/burger_war/models/
$ export TURTLEBOT3_MODEL=burger
```

### 4. make

```
$ cd ~/catkin_ws
$ catkin_make
```

## 実行手順
### シミュレータ

ターミナルを起動

```
$ cd ~/catkin_ws/src/burger_war
# シミュレーションを起動
$ bash scripts/sim_with_judge.sh
```
フィールドとロボットが立ち上がったら別のターミナルを起動

```
$ cd ~/catkin_ws/src/burger_war
# ロボット動作スクリプトを実行
$ bash scripts/start.sh
```
