#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
import tf
import math

tf_listener = tf.TransformListener()

def get_the_length_to_enemy():
    try:
        trans,rot = tf_listener.lookupTransform('/base_footprint', '/enemy_closest', rospy.Time(0))
    except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
        rospy.logerr('TF lookup error [base_footprint -> enemy_closest]')
        return 1.0 #敵が検出されない場合
        
    return math.sqrt(pow(trans[0],2)+pow(trans[1],2))


def get_the_radian_to_enemy():
    try:
        trans,rot = tf_listener.lookupTransform('/base_footprint', '/enemy_closest', rospy.Time(0))
    except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
        rospy.logerr('TF lookup error [base_footprint -> enemy_closest]')
        return 0.0 #敵が検出されない場合

    return math.atan2(trans[1],trans[0])