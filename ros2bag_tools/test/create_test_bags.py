# Copyright 2023 AIT Austrian Institute of Technology GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Sequence, Tuple

from diagnostic_msgs.msg import DiagnosticArray
from example_interfaces.msg import String

from rclpy.serialization import serialize_message
CONVERSION_CONSTANT = 10 ** 9
from rclpy.time import Time

from ros2bag_tools.filter import BagMessageTuple

from rosbag2_py import SequentialWriter
from rosbag2_py import TopicMetadata

from rosbag2_tools import default_rosbag_options

from sensor_msgs.msg import Image


def create_string_bag(path):
    writer = SequentialWriter()
    storage_options, converter_options = default_rosbag_options(path)
    writer.open(storage_options, converter_options)

    topic = TopicMetadata('/data', 'example_interfaces/msg/String', 'cdr')
    writer.create_topic(topic)

    msg = String()
    msg.data = 'test_start'
    writer.write('/data', serialize_message(msg), 1000)
    msg.data = 'test_end'
    writer.write('/data', serialize_message(msg), CONVERSION_CONSTANT + 2000)


def create_diagnostics_bag(path):
    writer = SequentialWriter()
    storage_options, converter_options = default_rosbag_options(path)
    writer.open(storage_options, converter_options)

    topic = TopicMetadata(
        '/diagnostics', 'diagnostic_msgs/msg/DiagnosticArray', 'cdr')
    writer.create_topic(topic)

    msg = DiagnosticArray()
    writer.write('/diagnostics', serialize_message(msg), 1000)


def create_day_time_bag(path):
    writer = SequentialWriter()
    storage_options, converter_options = default_rosbag_options(path)
    writer.open(storage_options, converter_options)

    topic = TopicMetadata('/data', 'example_interfaces/msg/String', 'cdr')
    writer.create_topic(topic)

    HOUR_TO_NS = 60 * 60 * CONVERSION_CONSTANT

    msg = String()
    msg.data = 'msg0'
    writer.write('/data', serialize_message(msg), 13 * HOUR_TO_NS - 1000)
    msg.data = 'msg1'
    writer.write('/data', serialize_message(msg), 13 * HOUR_TO_NS)
    msg.data = 'msg2'
    writer.write('/data', serialize_message(msg), 14 * HOUR_TO_NS)
    msg.data = 'msg2'
    writer.write('/data', serialize_message(msg), 14 * HOUR_TO_NS + 1000)


def create_images_bag(path):
    writer = SequentialWriter()
    storage_options, converter_options = default_rosbag_options(path)
    writer.open(storage_options, converter_options)

    topic = TopicMetadata('/image', 'sensor_msgs/msg/Image', 'cdr')
    writer.create_topic(topic)
    for i in range(3):
        msg = Image()
        t = 1000 * 1000 * 1000 * i
        msg.header.frame_id = 'camera_optical_frame'
        msg.header.stamp.nanosec = t
        msg.width = 2
        msg.height = 2
        msg.step = 2
        msg.encoding = 'mono8'
        msg.data = [0, 128, 128, 255]
        writer.write('/image', serialize_message(msg), t)


def create_synced_bag(path) -> Tuple[TopicMetadata, Sequence[BagMessageTuple]]:
    writer = SequentialWriter()
    storage_options, converter_options = default_rosbag_options(path)
    writer.open(storage_options, converter_options)

    topics = [TopicMetadata(topic, 'diagnostic_msgs/msg/DiagnosticArray', 'cdr')
              for topic in ['/sync0', '/sync1', '/offsync0']]
    for topic in topics:
        writer.create_topic(topic)
    entries = {
        # times in ms (match between /syncN = m, no match = x)
        # assumes 10ms match tolerance (exclusive)
        #             m    m    x    x
        '/sync0':    [0, 100, 200, 300],
        '/sync1':    [0, 109, 210, 311],
        '/offsync0': [20]
    }
    for topic, ts in entries.items():
        for ms in ts:
            ns = int(ms*1e6)
            t = Time(nanoseconds=ns)
            msg = DiagnosticArray()
            msg.header.stamp = t.to_msg()
            writer.write(topic, serialize_message(msg), ns)
