import rospy
import rosbag
import argparse
import tqdm
import numpy as np
from sensor_msgs.msg import PointCloud2, PointField
import std_msgs.msg
from sensor_msgs import point_cloud2

def create_pointcloud2_msg(data, frame_id="livox_frame"):
    """
    Converts the custom point data into a PointCloud2 message.

    Args:
    - data: List of dictionaries containing point information.
    - frame_id: Frame ID for the PointCloud2 message.

    Returns:
    - PointCloud2 message
    """
    # Create list for PointCloud data
    point_cloud = []

    for item in data:
        # Each point consists of (x, y, z, reflectivity, tag, line)
        point = (item['x'], item['y'], item['z'], item['reflectivity'], item['tag'], item['line'])
        point_cloud.append(point)

    # Create list of PointFields for each field in PointCloud2
    fields = [
        PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
        PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
        PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
        PointField(name='reflectivity', offset=12, datatype=PointField.UINT8, count=1),
        PointField(name='tag', offset=13, datatype=PointField.UINT8, count=1),
        PointField(name='line', offset=14, datatype=PointField.UINT8, count=1),
    ]
    
    # Create PointCloud2 message header
    header = std_msgs.msg.Header()
    header.frame_id = frame_id
    header.stamp = rospy.Time.now()
    
    # Create PointCloud2 message
    pc2_msg = point_cloud2.create_cloud(header, fields, point_cloud)
    
    return pc2_msg


def publish_pointcloud(bag, output_bag_file, topics=['/livox/lidar'], end_time = float('inf')):
    rospy.init_node("pointcloud_publisher")
    pc_pub = rospy.Publisher("/livox/lidar_pointcloud", PointCloud2, queue_size=10)
    rate = rospy.Rate(10)  # 10 Hz

    circle_iter = 0
    with rosbag.Bag(output_bag_file, 'w') as output_bag:
        for topic, msg, t in bag.read_messages(topics=topics):
            if circle_iter > end_time:
                break  # Skip messages outside the time range
            circle_iter += 1

            # Process and write the message as usual
            point_data = [
                {
                    'offset_time': p.offset_time,
                    'x': p.x,
                    'y': p.y,
                    'z': p.z,
                    'reflectivity': p.reflectivity,
                    'tag': p.tag,
                    'line': p.line
                }
                for p in msg.points
            ]

            pc2_msg = create_pointcloud2_msg(point_data)
            pc_pub.publish(pc2_msg)
            output_bag.write("/livox/lidar_pointcloud", pc2_msg, t)
            rate.sleep()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_name', required=True, help="path to the rosbag file")
    parser.add_argument('--output_bag', required=True, help="path to save the new rosbag file")
    parser.add_argument('--topic', required=False, default="/livox/lidar", help="name of the point cloud topic used in the rosbag")
    args = parser.parse_args()

    topics = [args.topic]
    with rosbag.Bag(args.file_name, 'r') as bag:
        publish_pointcloud(bag, args.output_bag, topics=topics, end_time=float('inf'))
