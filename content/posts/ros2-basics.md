# ROS2 入门笔记：节点、话题、服务与动作

机器人分类的第一篇，先把 ROS2 的通信骨架理清楚，后面再谈感知、控制与导航。

## 四种通信方式

- **Topic（话题）**：发布订阅，适合作高频数据流（传感器、里程计）
- **Service（服务）**：请求响应，适合短小的确定性调用
- **Action（动作）**：长任务 + 进度反馈 + 可取消，适合导航这类耗时操作
- **Parameter（参数）**：节点运行时可调配置

## 几个基础概念

- **Node（节点）**：最小功能单元，职责尽量单一
- **DDS 与 QoS**：ROS2 的底层通信中间件；可靠性、历史深度、丢弃策略都会影响实际行为
- **工作空间与 colcon**：`colcon build` 构建，`source install/setup.bash` 后使用
- **launch 文件**：把多节点、参数、命名空间组织成一次启动
- **tf2**：坐标系之间的变换树，机器人开发里绕不开
- **rosbag2**：录制与回放数据，调试和复现问题的利器

## 最小验证方式

```bash
ros2 run demo_nodes_cpp talker
ros2 run demo_nodes_py listener
ros2 topic list
ros2 topic echo /chatter
```

能跑通一组 talker / listener，再去看具体的传感器驱动与算法包。

## 后续记录方向

- 传感器接入（相机、激光雷达、IMU）
- 坐标变换与建图定位
- 导航栈配置与调参
- 多节点架构与工程化
