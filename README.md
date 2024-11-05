# ROS-CustomMsgToPCD2
Type of custom message converts to pointcloud2

# Usage
run the script and you can set `end_time` to convert part of your bag to test first.

```bash
python livox_topic_transfer.py --file_name {FILENAME} --output_bag {OUTPUT_BAG_DIR&NAME}
```
For example   

```bash
eg. python livox_topic_transfer.py --file_name 2024-03-29-12-42-59.bag --output_bag odom.bag
```
