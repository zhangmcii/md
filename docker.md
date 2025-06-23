docker四种网络模式

1.Bridge(桥接)模式

此模式为每个容器分配和设置ip，并且将容器连接到一个docker0的虚拟网桥，通过docker0虚拟网桥以及iptable net表等与宿主机通信

docker inspect flasky_backend

查看3个不同的容器，ip都与主机不同

<img src="file:///Users/v/Library/Application%20Support/marktext/images/2025-06-13-17-52-31-image.png" title="" alt="" width="301">



> d当创建一个容器时，同时会创建一对veth pair对接口。这对接口一端在容器内，即eth0;另一端在本地并被挂载到docker0网桥，名称以veth开头。通过这种方式，主机可以和容器通信，容器之间也可以相互通信。



2.HOST模式

与宿主机在同一网络中，使用主机的IP和端口



3.Container模式

指定和已经存在的某个容器共享同于个network namespace，此时这两个容器共同使用同一个网卡,主机名，IP地址。



4.None模式

容器有自己的网络命名空间，但不做任何配置，它与宿主机，其他容器不连通。







组合compose文件怎么使用网络？

使用networks创建网络，在各服务networks字段中使用


