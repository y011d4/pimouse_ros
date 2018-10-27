#!/usr/bin/env python
#encoding: utf8
import rospy, unittest, rostest, actionlib
import rosnode
import time
from std_msgs.msg import UInt16
from pimouse_ros.msg import MusicAction, MusicResult, MusicFeedback, MusicGoal

class BuzzerTest(unittest.TestCase):
    def setUp(self):
        self.client = actionlib.SimpleActionClient("music", MusicAction)
        self.device_values = []

    def test_node_exist(self):
        nodes = rosnode.get_node_names()
        self.assertIn('/buzzer', nodes, "node does not exist")

    def test_put_value(self):
        pub = rospy.Publisher('/buzzer', UInt16)
        for i in range(10):
            pub.publish(1234)
            time.sleep(0.1)

        dev = "rtbuzzer0"
        try:
            with open("/dev/"+dev, "r") as f:
                data = f.readline()
                self.assertEqual(data, "1234\n", "value is not written to rtbuzzer0")
        except IOError:
            rospy.logerr("cannot open file: /dev/"+dev)

    def test_music(self):
        goal = MusicGoal()
        goal.freqs = [100, 200, 300, 0]
        goal.durations = [1, 1, 1, 1]

        self.client.wait_for_server()
        self.client.send_goal(goal, feedback_cb=self.feedback_cb)
        self.client.wait_for_result()

        rospy.loginfo("test")
        rospy.loginfo(goal.freqs)
        self.assertTrue(self.client.get_result(), "invalid result")
        #self.assertEqual(goal.freqs, self.device_values, "invalid feedback: "
        #    + ", ".join([str(e) for e in self.device_values]))
        self.assertTrue(goal.freqs == self.device_values, "invalid feedback: ")

        ###preemption###
        self.device_values = []
        self.client.send_goal(goal, feedback_cb=self.feedback_cb)
        self.client.wait_for_result(rospy.Duration.from_sec(0.5))

        self.assertFalse(self.client.get_result(), "stop is requested but return true")
        self.assertFalse(goal.freqs == self.device_values, "not stopped")

    def feedback_cb(self, feedback):
        dev = "rtbuzzer0"
        try:
            with open("/dev/"+dev, "r") as f:
                data = f.readline()
                self.device_values.append(int(data.rstrip()))
        except IOError:
            rospy.logerr("cannot open file: /dev/rtbuzzer0")
            self.assertTrue(False, "open error")

if __name__ == '__main__':
    time.sleep(3)
    rospy.init_node('travis_test_buzzer')
    rostest.rosrun('pimouse_ros', 'travis_test_buzzer', BuzzerTest)
