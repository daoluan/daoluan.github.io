---
layout: post
title: webrtc-source-001
date: 2023-05-29 12:57:18.000+00:00
author: daoluan
comments: true
typora-root-url: ../
---

api 定义了 WebRTC 的抽象组件和 WebRTC 的使用基础接口。

在里面找不到和网络相关的代码，看 WebRTC 的处理流程，一般看当收到第一个包的时候，做了什么逻辑

Socket/socketserver

定义一个 Server，在 OnReadEvent 里面实现对客户端的处理（创建 pc） -- 但是每个服务都需要一个线程？

没有 RTP 打包的逻辑，包括 h264 等分片逻辑https://github.com/aisouard/libwebrtc.git 

NOTE：尝试编译 rtc_base.a 库，熟悉一下 base 使用。编译过程，发现依赖盘根错节，不适合拿出来独立使用。

我本来一开始的目的，是能否独立一个 libwebrtc 的库，能在构建相关后台服务的时候，直接拿出来用。



### 目标：写一个基于 libwebrtc 的后台服务

NOTE：编译好 webrtc.a 后，使用库各种问题，WebRTC 默认使用 clang 作为编译器

基本步骤：https://github.com/webrtc-sdk/libwebrtc m104_release

```Bash
apt-get install -y libxext-dev libxrandr-dev libxdamage1 libgbm1 software-properties-common gcc-9 g++-9 libxtst-dev libpulse-dev

# ubuntu 编译很坑，g++ 需要比较新的版本，clang 等要默认关闭，不然其他程序引用库时报各种符号问题
#!/bin/sh

export ARCH=x64
gn gen out/linux-$ARCH --args="target_os=\"linux\" target_cpu=\"$ARCH\" is_clang=false use_lld=false treat_warnings_as_errors=false rtc_include_tests=false is_debug=true rtc_include_tests=false rtc_use_h264=true ffmpeg_branding=\"Chrome\" is_component_build=false use_rtti=true use_custom_libcxx=false use_custom_libcxx_for_host=false rtc_enable_protobuf=false proprietary_codecs=true"

# 列出所有的编译选项，如果编译可以在这里寻找方法
gn args out/linux-x64 --list
```

Google WebRTC 的编译需要一个音频和视频的采集源，还是作为一个客户端来使用的。

- VideoCapturer 负责采集视频，收到帧的时候，广播出去，注意这里可以有多个接受者
- AudioDeviceImpl/RTCVideoDeviceImpl
- VideoCapturer 一般是摄像头或者桌面 https://zhuanlan.zhihu.com/p/549327174

> 然而我们大多数情况下，并不需要用到VCMCapturer或者DesktopCapturer ，我们的数据源是自定义的，行为也想自定义。此时就需要用到自定义的视频源捕获器了。

- AdaptedVideoTrackSource WebRTC 里面自带的类，对应一个视频源，如果想实现自己获取视频源并广播给 WebRTC，可以继承该类
  - public: VideoSourceInterface 对应视频源
- RTCVideoRenderer 用于渲染， 在后台服务里面一般不需要用到
- VideoSinkInterface WebRTC 自带，视频流管理？
- pc.AddTrack rtc_track() -> VideoTrackInterface(public: VideoSourceInterface)

### source 和 sink 的关系

![image-20230616154947384](/images/blog/image-20230616154947384.png)

source 一般提供 AddOrUpdateSink, RemoveSink，sink  一般提供 OnFrame 方法。

一个 source 应该是包含 AddOrUpdateSink, RemoveSink 两个方法，而且会调用  sinks  的 OnFrame 方法

![image-20230530193130507](/images/blog/image-20230530193130507.png)

- 如何实现一次编码，多个 peerconnection 使用？
- AudioProcessingImpl 音频的处理：https://blog.csdn.net/boywgw/article/details/46790955，后台服务应该不需要。默认创建：webrtc::AudioDeviceModule::Create

![image-20230530193201838](/images/blog/image-20230530193201838.png)

- CreateBuiltinVideoEncoderFactory 获取内建的编码器生成器，也可以自己按 VideoEncoderFactory 实现。`引申一个问题：当需要对接多路  webrtc 链接的时候，不可能每一路都做一个编码。`；
  - 手游 intel
  - 端游 英伟达
- 研究 PC 接口的时候，什么时候要 AddTrack,什么时候要 AddTransceiver，什么时候要 AddStream。AddStream 已经被废弃，看资料最好是不要使用。AddTrack 和 AddTransceiver 都是单独添加一个媒体轨道。
- VideoCapturer -> VcmCapturer
- RTCVideoDevice -> RTCVideoDeviceImpl 可以创建返回 RTCVideoCapture <- RefCountInterface（有点奇怪的实现）
- RTCVideoSrouce -> RTCVideoSourceImpl
- VideoTrack -> VideoTrackImpl
- 一开始以为 libwebrtc 是没什么用，很多代码（比如工具组件）照搬 webrtc 里面的代码。但是我尝试只依赖源代码来写一个 demo  的时候，发现并不是这样。比如构建一个 PC 的时候需要填写很多的依赖，了解这些结构需要花费很多的时间。所以 lib  还是有一定的价值。
- 5 月 24 日  libwebrtc  调试极其困难，翻阅了 webrtc/examples 刚好有一个  PCFactory->Create AddTrack 的流程，放弃 libwebrtc  的使用。
- VideoTrack 更想一个连接器，连接  source  和 sink，当调用  VideoTrack.AddOrUpdateSink 时，就是更新原来 source 的 sink 数组。

### CreatePeerConnectionFactory

我们看看一个新建 PC 工厂，需要哪些资料，部分资料后台开发是不需要的。

```C++
# 看 WebRTC 的代码，可以领略到好代码的魅力，这里接口无处不在。

RTC_EXPORT rtc::scoped_refptr<PeerConnectionFactoryInterface>
CreatePeerConnectionFactory(
    rtc::Thread* network_thread, // 网络收发包处理
    rtc::Thread* worker_thread,  // 其他任务处理
    rtc::Thread* signaling_thread, // ？
    rtc::scoped_refptr<AudioDeviceModule> default_adm, // 后台里面不一定需要，音频设备连接管理
    rtc::scoped_refptr<AudioEncoderFactory> audio_encoder_factory, // 音频编码创建工厂
    rtc::scoped_refptr<AudioDecoderFactory> audio_decoder_factory, // 音频解码创建工厂
    std::unique_ptr<VideoEncoderFactory> video_encoder_factory,    // 视频编码创建工厂
    std::unique_ptr<VideoDecoderFactory> video_decoder_factory,    // 视频解码创建工厂。注意我们来设计这个函数的时候，一般设计一个 EncoderInterface 即可，这里为什么需要搞一个工厂呢
    rtc::scoped_refptr<AudioMixer> audio_mixer, // 混音相关
    rtc::scoped_refptr<AudioProcessing> audio_processing, // 音频处理，用于实现音频处理功能，例如回声消除、噪声抑制、自动增益控制等。可见音频处理一个很复杂的模块：https://blog.csdn.net/netease_im/article/details/107048860
    AudioFrameProcessor* audio_frame_processor = nullptr,
    std::unique_ptr<FieldTrialsView> field_trials = nullptr);
```

### Sigslot 如何理解

一个对象，声明自己的信号，我把我的信号对象公开访问，我的对象给你，你需要的话往我信号里面取注册即可（connect(your_callback_function)）。当我需要广播某个信号的时候，我们通过的信号函数广播出去。

- 只要一个对象有需要广播的事件，都声明自己的信号。
- 只要想接受信号，处理类应该继承 has_slot
- 每个对象想要关注信号，需要自己主动去注册

![image-20230530193249192](/images/blog/image-20230530193249192.png)

Ref

- https://blog.csdn.net/xiaxiaojing/article/details/82224921 写的很形象



sigslot webrtc 源码中被大量使用。其中网络包处理方面： udp -> p2ptransport -> dtlstransport -> rtptransport(sctptransport)，在初始化 webrtc 会话时，这些信号和信号槽都会被初始化和连接好。当 udp 收包时，数据被一层层解析和传递。

### 媒体流是如何流转的

好奇 webrtc 里面媒体流是如何流转的，这里用从视频流入手。

从 webrtc  双人对话场景里面，视频流从摄像头采集后，经过 webrtc  的处理，经由网络，传输到对端。

这里面视频数据，是怎么流转的，rtc 里面存在很多的结构，这些结构错综复杂，用作视频流转使用。看源代码时，如不停下来好好整理一番，很难摸清里面的秩序。

提到流转，在媒体流里面，涉及  source  和 sink  概念。关于两者的关系，可以看：[媒体流 source 和 sink](https://blog.csdn.net/boywgw/article/details/46790955)

source  一般管理这一个或者多个 sink，在实现里面一般 sinks  会用一个数组来表示。

一个 source  对象，可以增加 sink：AddOrUpdateSink，可以移除  sink：RemoveSink。当视频数据采集到是，可以调用  sink.OnFrame 方法，从而驱动视频数据的流转。

代表 source 的接口类 VideoSourceInterface，代表  sink 的接口类 VideoSinkInterface。

在源码的 examples 里面，有一些 demo，从这些  demo  里面，可以挖掘更全面的视频流流转路径。

在 webrtc 里面，有 track 概念，就是轨道的意思，里面可以跑音频，也可以跑视频。比如  PC.AddTrack 增加一个媒体流轨道，当我们想在一个 PC 上传送一个视频流的时候，就需调用此方法。

没错，按理应该是这样的。但是看  AddTrack，其只输入一个没有 AddOrUpdateSink 方法的 MediaStreamTrackInterface。

```C++
RTCErrorOr<rtc::scoped_refptr<RtpSenderInterface>> PeerConnection::AddTrack(
    rtc::scoped_refptr<MediaStreamTrackInterface> track,
    const std::vector<std::string>& stream_ids) {
```

PCFactory 里面有一个 CreateVideoTrack 方法：好理解一下，他返回了一个 VideoTrackInterface，视频流可以流转。它需要一个 VideoTrackSourceInterface 作为参数，它也是一个视频源。

```C++
rtc::scoped_refptr<VideoTrackInterface> PeerConnectionFactory::CreateVideoTrack(
    const std::string& id,
    VideoTrackSourceInterface* source) {
```

那么，视频流是如何被编码的，如果编码器也是一个 sink。而这个问题，就是 webrtc 代码里面很有意思的地方。

关于这一点，我看了一篇关于视频流如何流转的文章：https://juejin.cn/post/6844904150849814542。

看了这篇文章，突然理解了 webrtc：本地轨道和远端轨道，而  webrtc 需要连接通信，那么本地轨道和远端轨道就要连接起来。OfferSdp 里面描述了一端支持哪些媒体，另一端收到后也描述支持哪些媒体。当前者收到 AnaswerSdp 后，选取其中的一个作为轨道的通信协议（媒体协议），而正是此时，webrtc 内部把上面说的  VideoTrack 和 EncoderSink 链接起来了。这么说也合理，因为无法确认哪个媒体时，EncoderSink 对象也是未知的，而只有 EncoderSink 被创建时，VideoTrack 和 EncoderSink 才能被链接起来。

到这里，还有一个细节没有弄明白。注意上面  PC::AddTrack 的声明，入参类型为 MediaStreamTrackInterface，这是一个很基础的接口（虚基类），但它并没有 AddOrUpdateSink 等管理 sink 的方法。如果传入的结构，需要调用 AddOrUpdateSink 等管理 sink 的方法，一定要做强制的转换才行，但这是蹩脚的做法。

![image-20230530193318236](/images/blog/image-20230530193318236.png)

直到翻阅 RtpSender 的实现，发现有一个基类到子类的强制转换，实现略显别扭。

```C++
  rtc::scoped_refptr<VideoTrackInterface> video_track() const {
    return rtc::scoped_refptr<VideoTrackInterface>(
        static_cast<VideoTrackInterface*>(track_.get()));
  }
  
  // track_ 的声明
  rtc::scoped_refptr<MediaStreamTrackInterface> track_;
```

![image-20230530193337297](/images/blog/image-20230530193337297.png)

webrtc 媒体流流转路径，和我原始设想的不太一样。本意是在采集后立即编码，然后才通过  VideoTrack 去分发，也就是说它拿到的是编码后的数据。

编码主要的是设备硬件的编码，编码前置的好处是可以一次编码多路分发。

那么是否可以在当前数据流转流程的框架中，达到这个目的呢？

### 一个数据包收到后，在 webrtc 里面是如何流转的 TODO

开发的同学，喜欢弄清楚，数据的流转的过程，流转弄清楚了，业务也就明白了。

当  webrtc 收到第一个网络包，其在 webrtc  内部是如何流转的呢？


### WebRTC 视频发送过程

疑问：当取得一个音视频帧时，WebRTC native 代码是如何发送到网络上的？

参考文章：https://blog.csdn.net/freeabc/article/details/106000923

![image-20230625195541662](/images/blog/image-20230625195541662.png)

 流程整理

- VideoCaptureModule: 视频采集编码分发
- VideoStreamEncoder: 视频编码
- VideoSendStream: 
- RtpVideoSender: OnEncodedImage 似乎是将编码好的视频帧及其相关宽高等
- RTPSender: 发送 RTP 数据
- PacedSender: RTPSender 包含了 PacedSender，发送的时候会投递给 PacedSender
- WebRTCVideoChannel: 对接 WebRTC 传输层的地方

###   webrtc  源码类图

![uml](/images/blog/webrtc-uml.png)

### nack  机制
作为接收端，发现丢包时，请求发送端重发丢失的包。接收端的机制：

- 定时检查 nack_list_ 队列，发现丢包满足申请重传条件，立即触发发送 NACK 报文。
- nack_list_ 如果过长，强制触发 I 帧
- TODO：这里有优化的空间，仅仅这两个条件对弱网的考虑太少了。



调用栈（转）

![image-20230531152124425](/images/blog/image-20230531152124425.png)

核心函数：SendNack, RequestKeyFrame。

当丢包过多等一些极端的情况，会触发  RequestKeyFrame。*注意*，接收端为了响应 nack 会重发数据，这里如果重发的数据过多的情况，会挤压下行的带宽，恶化业务体验，音视频直接卡死。接收端，更聪明的做法，是放弃过多的 nack。

做了一些测试，本意是：可以防止突发的弱网情况，视频卡死的问题

方向：

*   看是不是 pli 太多导致的
*   流量突发是哪里来，主要是什么流量，为什么 nackqueue  调小了还是这么多流量

nack 直接不响应是不行的因为丢包在持续，陆续会有一些 nack

如果是以下突发的网络拥塞，那么优化的难度很大：所在线路可能真的拥塞了（比如路径上的路由故障等），此时无法发送端和接受端如何调整，最终都是需要重连（重选路由）来解决，所以这个情况，调整 nack 的策略行不通

*假设线路没问题*，不可持续的突发的网络拥塞，突发的较大的丢包，那么导致的突发 nack 流量有可能达到下行带宽的瓶颈，从而导致画面卡死。

如果从服务端的角度来思考的话，那么可以监控下行流量 DBW，结合带宽探测结果 DDBW：

- 注重延时的场景（比如云游戏）：当 *DBW<DDBW* 时，那么 nack 流量可以发出；当 *DBW >> DDBW* 时，那么应该放弃超出的 nack 流量，并合理触发 pli，如此可以“稳住”画面

![控制 nack 流量](/images/blog/image-20230607115337723.png)

![未控制 nack 流量](/images/blog/image-20230607115413934.png)

可以看到 nack 流量的占比有一个明显的下降，播放端卡死次数减少。

为什么修改之前，有这么高的突发流量，答案是 I 帧出现的重传，视频流里面 I 帧的带宽占比较高。

- 注重流畅的场景（比如直播）：nack 流量做合理的平滑处理（未实验）

#### 客户端处理 nack 的机制总结

- 一个 rtp 包最多触发 10 次重传（重传如此多次是为了抗一定的网络丢包等网络波动，特定情况下这里触发的 10 次重传会导致下行流量被打满）
- 每隔一段时间（动态调整，和探测的 rtt 相关）触发 nack
- 不到一个 rtt 不会继续发送 nack 请求
- nack_list 有一个长度限制：1000，超过触发 pli（实时场景，这里有调整的空间）
- nack_list 里面的续航最大最小 diff 不能超过 10000，超过触发 pli
