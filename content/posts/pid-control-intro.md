# PID 控制入门笔记：从公式到代码

自动化分类开篇。PID 是最基础也最常被低估的控制器，理解每一项的作用比背公式更重要。

## 三项分别做什么

- **P（比例）**：按当前误差出力，越大响应越快，但过大容易振荡
- **I（积分）**：累积历史误差，消除稳态误差，过大容易超调
- **D（微分）**：按误差变化率抑制突变，能改善稳定度，但对噪声敏感

## 离散实现

```python
# 位置式 PID 伪代码：注意采样周期 dt 必须固定
integral = 0.0
prev_error = 0.0

def pid(setpoint, measured, dt, kp, ki, kd):
    global integral, prev_error
    error = setpoint - measured
    integral += error * dt
    derivative = (error - prev_error) / dt
    prev_error = error
    return kp * error + ki * integral + kd * derivative
```

## 调参顺序

1. 先把 I 和 D 置零，只调 P 到"响应够快但不持续振荡"
2. 加 I 消除稳态误差，注意积分饱和
3. 最后微调 D 抑制超调，同时注意引入的噪声

## 工程上的关键细节

- **采样周期**要稳定，抖动会让微分项失真
- 加**抗积分饱和**（积分限幅或条件积分）
- 输出要**限幅**，并和保护逻辑配合
- 记录阶跃响应曲线：超调量、上升时间、稳态误差，调参才有依据

> 调参不是玄学，是记录与对比。
