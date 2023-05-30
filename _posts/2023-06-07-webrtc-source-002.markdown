---
layout: post
title: webrtc-source-002
date: 2023-06-07 17:26:27
author: daoluan
comments: true
typora-root-url: ../
---

webrtc 的延迟组成：按键触发，网络上行，输入云端设备，云端设备响应（很难精确统计，不算入延迟），视频采集，视频编码，视频网络传输，视频组帧，音视频延迟（TODO），视频解码，播放延迟，视频播放。

因网络环境的不稳定性，因此接收端都需 buffer 抗网络抖动，buffer 根据网络的情况，可大可小，这里根据场景需要做不同的策略，比如注重实时的场景云游戏，buffer 不能过大。比如直播场景注重流畅性，buffer 可以大一些。

