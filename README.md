# SiiWay/DDNS

累了 不改了()

*如果有好的**强制**使用指定协议(ipv4/ipv6)请求url的方法可提issue，无奖~~*

<!--
这是 [NewFuture/DDNS] 的修改版本

## Original

原 README: [README_original.md](./README_original.md)

## Changes

### 1.

- [...](./util/ip.py#L69-L86)

更改了 api 获取地址的方式

> [!WARNING]
> 为了能使用双栈 api 获取指定协议的地址，修改后使用了 dns 后直接请求 ip 的方式，因此需要安装 `dnspython`

```sh
pip install dnspython
# or APT:
sudo apt install python3-dnspython
```
-->
- Cloudflare Workers Script: [_worker.js](./_worker.js)