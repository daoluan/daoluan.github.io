---
author: daoluan
layout: post
title: 如何书写高性能高效率的业务框架
categories:
- 编程小记
tags:
- tinyco
---


做后台业务，设计一个系统时，并发是需重点考虑的，当然依据业务的不同，情况会有所不同。

一谈到并发，就会听到很多专业名词，譬如 qps，阻塞，多线程，多进程，协程，多核，异步同步等等，前人在业务的驱使下也发展出了一套套支持高并发的架构。

多进程。这个很好理解，因为多核服务器已经非常普遍，为了充分机器计算资源，多进程也是自然而然的事情。譬如比较火的 nginx，多个 worker在处理客户端过来的连接，每个进程都是独立工作的，所以性能高，吞吐量大。

多线程。特别是在较新版本的 linux下面，多线程和多进程除了在共享资源上有区别，他们两个实际上很相似。多线程也很好理解，譬如 memcached，一个主线程负责监听请求，其余的线程负责服务请求。在我工作团队里面，极力不推荐使用多线程，原因是多线程在共享资源上面会有比较多的坑；代码出问题，可能导致单机整个服务垮掉。

协程。协程的诞生，是程序猿的福音。举一个例，业务处理的时候经常需要请求其他模块的数据，非协程的处理模式：

	build request;
	send request;
	bind(HandleRespone)
	...
	// event loop invoke HandleResponse

可以看到请求发出后和处理请求两个阶段是完全分开的，如果业务简单可以接受，但只要有稍微复杂点，在业务逻辑多请求几个其他模块，这很痛苦。协程的处理模式：

	build request0;
	send requset0;
	recv response0;
	handle response0;
	
	build request1;
	send requset1;
	recv response1;
	handle response1;

这样的代码使用简单，可维护性好，性能上会比非协程模式稍差，但综合权衡还是协程模块适合业务开发。所以协程能体现出开发的**高效率**

类似 nginx以及 memcached 都是基于非协程异步事件框架来做的，所以你会看到像 memcached 里面代码很难读懂，得多抠几行才能理解，而且里面还涉及较为复杂的状态机来处理请求（[decode-memcached](https://github.com/daoluan/decode-memcached)）。

提了这些背景，那怎么来写**高性能**的业务框架。最主要的核心是你的框架要使得当前一个请求的业务处理流程不要阻塞导致其他共存的业务处理流程被阻塞。举例子，当请求发出后，不能死等，得让进程继续处理其他请求，比如继续处理新进来的请求，比如继续处理上一个请求的响应。简而言之，要想高性能，就别阻塞。

如果直接照搬 memcached以及 nginx 这样的模型来做业务框架，这样会让开发人员很痛苦，试想如果让他们和协程结合是不是可以诞生一个同时具备高性能以及高开发效率的开发框架？ [tinyco](https://github.com/daoluan/tinyco) 就是依据这样的目标来设计的，在多次使用了部门的公共组件后，发现它并不完美，所以才诞生了 tinyco，可以看看下面的 snippets：

http 服务器：

	#include <assert.h>
	
	#include "http_server.h"
	
	using namespace tinyco;
	
	class TestWork : public http::HttpSrvWork {
	 public:
	  virtual int Serve() {
	    LOG("ready to reply");
	    hrsp_.SetStatus(200);
	    hrsp_.SetContent("hello world!");
	    Reply();
	
	    return 0;
	  }
	};
	
	int main() {
	  assert(Frame::Init());
	  Frame::TcpSrv<TestWork>(0, 8080);
	  Frame::Fini();
	  return 0;
	}

udp 服务器：

	#include <assert.h>
	
	#include "frame.h"
	
	using namespace tinyco;
	
	class TestWork : public UdpReqWork {
	 public:
	  TestWork() {}
	  virtual ~TestWork() {}
	
	  int Run() {
	    LOG("new udp req: %s|response after 10s", req_.reqpkg.c_str());
	
	    Frame::Sleep(10000);
	
	    LOG("rsp to client");
	    Reply(req_.reqpkg);
	  }
	};
	
	int main(int argc, char **argv) {
	  assert(Frame::Init());
	  Frame::UdpSrv<TestWork>(0, 32000);
	  Frame::Fini();
	  return 0;
	}

tinyco 借鉴了 nginx的特性，多个 worker 都监听了一个端口（通过 fork），但他们竞争一个文件锁，在拿到文件锁后的 worker 才有权利去 accept 一个新的请求，这样可以利用多核优势，大大提供吞吐量。曾经使用过一个业务框架，只有一个进程在 accept 请求，实际上这样不能利用多核优势，吞吐量上不来。另外，tinyco 引入了协程，有很高的开发效率，支持 http/dns 等。

实际测试简单的 echo服务，nginx 和 tinyco 的表现很接近。这个框架还有很多待完善的地方以及待增加的功能，后面会持续跟进。