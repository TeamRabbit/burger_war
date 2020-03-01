#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
import random
import tf
import json
import math
import actionlib
import actionlib_msgs
import smach
import smach_ros
import roslib.packages
from geometry_msgs.msg    import Twist
from std_msgs.msg         import Float32

rospy.init_node("burger_war_main_node")#smath_filesでtfを使用するため,init_nodeする前にtf_listerner()があるとエラー
from smach_files          import *

# Global変数
target_location_global = ""


class Setup(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=["finish"])

    def execute(self, userdata):

        overlaytext.publish("Setup now ...")
        rospy.sleep(1)

        if rospy.get_param("/send_id_to_judge/side") == "r":
            move_base.pub_initialpose_for_burger_war()
        else:
            move_base.pub_initialpose_for_burger_war()
        
        rospy.sleep(1)
        return "finish"


class Commander(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=["move", "fight", "commander", "game_finish"])

        #Northは敵陣なので現状は行かない.
        self.check_points     = ["south_center", "south_left", "south_right", "west_center", "west_left", "west_right", "east_left", "east_center", "east_right"]
        self.is_enemy_close   = False

    def execute(self, userdata):
        global target_location_global

        self.is_enemy_close = True if tf_util.get_the_length_to_enemy() < 0.90 else False

        #各状況に合わせて状態遷移
        if self.is_enemy_close == True:
            return "fight"
        elif len(self.check_points) > 0:
            target_location_global = self.check_points[0]
            self.check_points.pop(0)
            return "move"
        else:
            rospy.sleep(0.1)
            return "commander"


class Move(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=["finish"])

    def execute(self, userdata):
        global target_location_global

        goal = json_util.generate_movebasegoal_from_locationname(target_location_global)
        overlaytext.publish("Move to " + target_location_global)

        #移動開始
        result = move_base.send_goal_and_wait_result(goal)

        if result == True:
            overlaytext.publish("Turtlebot reached at [" + target_location_global + "].")
        else:
            overlaytext.publish("Moving Failed [" + target_location_global + "].")

        return "finish"


class Fight(smach.State):#敵が付近に存在する場合は、敵のマーカーをトラッキング

    def __init__(self):
        smach.State.__init__(self, outcomes=["finish"])
        self.angular_weight = 1.50
        self.notice_length  = 0.90

    def execute(self, userdata):

        while True:

            overlaytext.publish("STATE: Fight\nlength = " + str(tf_util.get_the_length_to_enemy())[:6])
            if tf_util.get_the_length_to_enemy() > self.notice_length:
                break

            # Twistのpublish
            target_angular = tf_util.get_the_radian_to_enemy() * self.angular_weight
            twist.publish_rotate_twist(target_angular)

        return "finish"


if __name__ == "__main__":

    rospy.init_node("burger_war_main_node")
    rospy.loginfo("Start burger war main program.")

    sm = smach.StateMachine(outcomes=["Game_finish"])
    with sm:
        smach.StateMachine.add("Setup",     Setup(),     transitions={"finish": "Commander"})
        smach.StateMachine.add("Commander", Commander(), transitions={"move": "Move", "fight": "Fight", "commander": "Commander", "game_finish": "Game_finish"})
        smach.StateMachine.add("Move",      Move(),      transitions={"finish": "Commander"})
        smach.StateMachine.add("Fight",     Fight(),     transitions={"finish": "Commander"})

    sis = smach_ros.IntrospectionServer("server", sm, "/BURGER_WAR_TASK")
    sis.start()
    sm.execute()
    sis.stop()
