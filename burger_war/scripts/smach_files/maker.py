#!/usr/bin/env python
# coding: utf-8
import sys
import rospy
import copy
import math
from burger_war.msg     import MarkerList

my_side    = rospy.get_param("/send_id_to_judge/side")
enemy_side = "b" if my_side == "r" else "r"

my_last_get_maker_name           = ""
enemy_last_get_maker_name        = ""
previous_my_markers_name_list    = []
previous_enemy_markers_name_list = []


def cb_marker_status(msg):

    enemy_markers_name_list = []
    none_markers_name_list  = []
    my_markers_name_list    = []

    #誰がどのマーカーを確保しているか情報整理
    for marker in msg.markers:
        if marker.owner == enemy_side:
            enemy_markers_name_list.append(marker.marker_name)
        elif marker.owner == "n":
            none_markers_name_list.append(marker.marker_name)
        elif marker.owner == my_side:
            my_markers_name_list.append(marker.marker_name)

    #最後に取得したマーカー情報を獲得
    for location_name in enemy_markers_name_list:
        if location_name not in previous_enemy_markers_name_list
            enemy_last_get_maker_name = location_name
            break
    for location_name in my_markers_name_list:
        if location_name not in previous_my_markers_name_list
            my_last_get_maker_name = location_name
            break

    previous_my_markers_name_list    = copy.copy(my_markers_name_list)
    previous_enemy_markers_name_list = copy.copy(enemy_markers_name_list)

    #敵のいる領域を推定
    #各waypointの価値評価
    #評価が高いものから順に回る


#sub_move_base_dummy_path   = rospy.Subscriber('move_base/DWAPlannerROS/global_plan', Path, cb_global_path)
sub_makers_states          = rospy.Subscriber('/marker_status', GoalStatusArray, cb_marker_status)
