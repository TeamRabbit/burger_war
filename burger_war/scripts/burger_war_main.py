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

rospy.init_node('burger_war_main_node')#smath_filesでtfを使用するため,init_nodeする前にtf_listerner()があるとエラー
from smach_files          import *

# Global変数
target_location_global = ''


class Commander(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=['move', 'fight', 'commander', 'game_finish'])

        #Northは敵陣なので現状は行かない.
        self.check_points     = ['south_center', 'south_left', 'south_right', 'west_center', 'west_left', 'west_right', 'east_left', 'east_center', 'east_right']
        self.last_notice_time = rospy.Time.now()
        self.is_enemy_close   = False

        self.tf_listener = tf.TransformListener()
        self.sub_enemy   = rospy.Subscriber('robot2enemy', Float32, self.enemy_callback)

        rospy.sleep(1)
        move_base.pub_initialpose_for_burger_war()
        rospy.sleep(1)

    def execute(self, userdata):
        global target_location_global

        try:
            trans, rot = self.tf_listener.lookupTransform('/base_footprint', '/enemy_closest', rospy.Time(0))
            length = math.sqrt(pow(trans[0], 2) + pow(trans[1], 2))
            self.is_enemy_close = True if length < 0.90 else False
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            rospy.logerr('TF lookup error [base_footprint -> enemy_closest]')
            self.is_enemy_close = False

        #各状況に合わせて状態遷移
        if self.is_enemy_close == True:
            return 'fight'
        elif len(self.check_points) > 0:
            target_location_global = self.check_points[0]
            self.check_points.pop(0)
            return 'move'
        else:
            rospy.sleep(0.1)
            return 'commander'

    def enemy_callback(self, msg):
        notice_length = 0.90

        if msg.data <= notice_length and self.is_enemy_close == False:
            self.check_points.insert(0, target_location_global)#中断する目標値を再度格納
            move_base.cancel_goal()
            self.last_notice_time = rospy.Time.now() #最後に敵を確認した時刻
            self.is_enemy_close   = True
        elif msg.data > notice_length and self.is_enemy_close == True:
            self.is_enemy_close == False


class Move(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=['finish'])

    def execute(self, userdata):
        global target_location_global

        goal = json_util.generate_movebasegoal_from_locationname(target_location_global)
        overlaytext.publish('Move to ' + target_location_global)

        #移動開始
        result = move_base.send_goal_and_wait_result(goal)

        if result == True:
            rospy.loginfo('Turtlebot reached at [' + target_location_global + '].')
            overlaytext.publish('Turtlebot reached at [' + target_location_global + '].')
        else:
            rospy.loginfo('Moving Failed [' + target_location_global + '].')
            overlaytext.publish('Moving Failed [' + target_location_global + '].')
            #self.check_points.append(target_location_global)

        return 'finish'

class Fight(smach.State):#敵が付近に存在する場合は、敵のマーカーをとりに行く。（実装予定）

    def __init__(self):
        smach.State.__init__(self, outcomes=['finish'])
        self.tf_listener = tf.TransformListener()
        self.pub_twist   = rospy.Publisher('cmd_vel', Twist, queue_size=10)

    def execute(self, userdata):

        overlaytext.publish('STATE: Fight')

        while True:
            try:
                trans, rot = self.tf_listener.lookupTransform('/base_footprint', '/enemy_closest', rospy.Time(0))
            except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
                rospy.logerr('TF lookup error [base_footprint -> enemy_closest]')
                rospy.sleep(1)
                break

            len = math.sqrt(pow(trans[0], 2) + pow(trans[1], 2))
            if len > 0.90:
                break

            send_data = Twist()
            send_data.angular.z = math.atan2(trans[1], trans[0]) * 1.5
            if math.degrees(send_data.angular.z) > 100:
                send_data.angular.z = math.radians(100)
            elif math.degrees(send_data.angular.z) < -100:
                send_data.angular.z = math.radians(-100)

            self.pub_twist.publish(send_data)
            rospy.sleep(0.3)
            self.pub_twist.publish(Twist())

        rospy.sleep(1)
        return 'finish'


if __name__ == '__main__':

    rospy.init_node('burger_war_main_node')
    rospy.loginfo('Start burger war main program.')

    sm = smach.StateMachine(outcomes=['Game_finish'])
    with sm:
        smach.StateMachine.add('Commander', Commander(), transitions={'move': 'Move', 'fight': 'Fight', 'commander': 'Commander', 'game_finish': 'Game_finish'})
        smach.StateMachine.add('Move',  Move(),  transitions={'finish': 'Commander'})
        smach.StateMachine.add('Fight', Fight(), transitions={'finish': 'Commander'})

    sis = smach_ros.IntrospectionServer('server', sm, '/BURGER_WAR_TASK')
    sis.start()
    sm.execute()
    sis.stop()
