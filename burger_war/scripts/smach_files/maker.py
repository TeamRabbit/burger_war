#!/usr/bin/env python
# coding: utf-8
import sys
import rospy
import copy
import math
from burger_war.msg     import MarkerList

my_side    = rospy.get_param("/send_id_to_judge/side")
enemy_side = "b" if my_side == "r" else "r"

#location_listの読み込み
file_path = roslib.packages.get_pkg_dir('burger_war') + "/location_list/target_list.json"
file = open(file_path, 'r')
location_list_dict = json.load(file)

my_last_get_maker_name           = ""#何かで初期化すべき
enemy_last_get_maker_name        = ""
previous_my_markers_name_list    = []
previous_enemy_markers_name_list = []
next_target_location = ""

def get_next_location_name():
    return next_target_location


def get_erea_name(location_name):
    return location_list_dict[location_name]["option"]


def get_location_point(location_name):
    x = location_list_dict[location_name]["translation"]["x"]
    y = location_list_dict[location_name]["translation"]["y"]
    return (x, y)

def get_location_weight(target_location, enemy_location):
    target_erea = get_erea_name(target_location)
    enemy_erea  = get_erea_name(enemy_location)

    if enemy_erea == "north":
        if target_erea   == "north":
            return 1
        elif target_erea == "west" or target_erea == "east":
            return 0.5
        else:#south
            return 0
    elif enemy_erea == "west":
        if target_erea   == "west":
            return 1
        elif target_erea == "north" or target_erea == "south":
            return 0.5
        else:#east
            return 0
    elif enemy_erea == "east":
        if target_erea   == "east":
            return 1
        elif target_erea == "north" or target_erea == "south":
            return 0.5
        else:#west
            return 0
    else:#south
        if target_erea   == "south":
            return 1
        elif target_erea == "west" or target_erea == "east":
            return 0.5
        else:#north
            return 0


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

    #保存
    previous_my_markers_name_list    = copy.copy(my_markers_name_list)
    previous_enemy_markers_name_list = copy.copy(enemy_markers_name_list)

    #敵のいる領域を推定
    enemy_zone = get_erea_name(enemy_last_get_maker_name)
    my_zone    = get_erea_name(my_last_get_maker_name)

    #各マーカーの優先度を評価
    location_value_dict = {}
    for name in previous_enemy_markers_name_list:
        evaluation_value = 1.0 if name in none_markers_name_list else 2.0 #noneのマーカは1点、敵のマーカは2点の評価
        evaluation_value -= get_location_weight(name, enemy_last_get_maker_name)#敵に近いマーカーは評価を下げる
        evaluation_value += get_location_weight(name, my_last_get_maker_name)#自分に近いマーカーは評価を上げる
        location_value_dict[name] = {evaluation_value}

    max_value = max(location_value_dict.values())
    for element_key, element_value in location_value_dict.items():
        if element_value == max_value:
            next_target_location = element_key
            print ("next_target_location = {}".format(next_target_location))
            break
    #評価値が最も高い場所をリストアップ
    """
    max_value = max(location_value_dict.values())
    candidate_location_name = []
    for element_key, element_value in location_value_dict.items():
        if element_value == max_value:
            candidate_location_name.append(element_key)
    
    my_location_x, my_location_y = tf_util.get_the_my_point()
    for name in candidate_location_name:
        location_x, location_y = get_location_point(name)
        length = sqrt(pow(location_x-my_location_x,2) + pow(location_y-my_location_y,2))
    """

    #各waypointの価値評価
    #評価が高いものから順に回る


#sub_move_base_dummy_path   = rospy.Subscriber('move_base/DWAPlannerROS/global_plan', Path, cb_global_path)
sub_makers_states          = rospy.Subscriber('/marker_status', GoalStatusArray, cb_marker_status)
