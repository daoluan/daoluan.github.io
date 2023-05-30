---
layout: post
title: webrtc-source-gcc
date: 2023-06-25 10:27:32
author: daoluan
comments: true
typora-root-url: ../
---

# gcc 算法核心

- twcc 反馈获取延迟梯度
- trendline (窗口，平滑系数，增益 =>  最小二乘法计算斜率)，得出网络状态
- 网络状态 aimd 变更码率，得到估算当前码率

# twcc 反馈路径

gcc 拥塞控制算法核心控制入口，想要实现自己的算法，继承`NetworkControllerInterface`类即可。

```c++
class NetworkControllerInterface {
 public:
  virtual ~NetworkControllerInterface() = default;
  // ...
  // Called when remotely calculated bitrate is received.
  ABSL_MUST_USE_RESULT virtual NetworkControlUpdate OnRemoteBitrateReport(
  // ...
  // Called when a protocol specific calculation of packet loss has been made.
  ABSL_MUST_USE_RESULT virtual NetworkControlUpdate OnTransportLossReport(
      TransportLossReport) = 0;
  // Called with per packet feedback regarding receive time.
  ABSL_MUST_USE_RESULT virtual NetworkControlUpdate OnTransportPacketsFeedback(
      TransportPacketsFeedback) = 0;
  // Called with network state estimate updates.
  ABSL_MUST_USE_RESULT virtual NetworkControlUpdate OnNetworkStateEstimate(
      NetworkStateEstimate) = 0;
};
```

webrtc 源代码中，pcc 和 goog_cc 都实现了该接口。下面 twcc 反馈的传导路径

- void Port::OnReadPacket(const char* data,
                          size_t size,
                          const rtc::SocketAddress& addr,
                          ProtocolType proto) {
- void P2PTransportChannel::OnReadPacket(Connection* connection,
                                         const char* data,
                                         size_t len,
                                         int64_t packet_time_us) {
- void DtlsTransport::OnReadPacket(rtc::PacketTransportInternal* transport,
                                   const char* data,
                                   size_t size,
                                   const int64_t& packet_time_us,
                                   int flags) {
- bool DtlsTransport::HandleDtlsPacket(const char* data, size_t size) {
- void WebRtcVideoChannel::OnPacketReceived(rtc::CopyOnWriteBuffer packet,
                                            int64_t packet_time_us)
- PacketReceiver::DeliveryStatus Call::DeliverPacket(
      MediaType media_type,
      rtc::CopyOnWriteBuffer packet,
      int64_t packet_time_us)
- bool RtpVideoStreamReceiver2::DeliverRtcp(const uint8_t* rtcp_packet,
  size_t rtcp_packet_length) - 音频和视频都有对应的处理，这里指列举视频的处理
- void ModuleRtpRtcpImpl2::IncomingRtcpPacket(const uint8_t* rtcp_packet, const size_t length) {
- void RTCPReceiver::IncomingPacket(rtc::ArrayView<const uint8_t>packet)
- void RTCPReceiver::TriggerCallbacksFromRtcpPacket
- void RtpTransportControllerSend::OnTransportFeedback
- NetworkControllerInterface::OnTransportPacketsFeedback

几点提示

- Twcc 反馈的载体是 rtcp，所以自然处理的入口在 RTCPReceiver 里面
- webrtc 存在一个较为复杂上下层协议栈交互的系统

```c++
PacketReceiver::DeliveryStatus Call::DeliverPacket(
    MediaType media_type,
    rtc::CopyOnWriteBuffer packet,
    int64_t packet_time_us) {
  if (IsRtcpPacket(packet)) {
    RTC_DCHECK_RUN_ON(network_thread_);
    DeliverRtcp(media_type, std::move(packet));
    return DELIVERY_OK;
  }

  RTC_DCHECK_RUN_ON(worker_thread_);
  return DeliverRtp(media_type, std::move(packet), packet_time_us);
}
```

# 其他

- modules/remote_bitrate_estimator 基于 REMB 的旧版本，基本已经废弃了，其中几个类在新版本中也有使用 remb
- modules/congestion_controller/receive_side_congestion_controller.cc remb 使用入口
- modules/remote_bitrate_estimator remb 核心实现
- modules/congestion_controller  基于 Transport Wide CC 的新版本，新旧版本中接收端的估算逻辑移到了发送端，其中的卡尔曼滤波算法也改成了线性回归算法
- modules/congestion_controller/pcc Probe-based Congestion Control
