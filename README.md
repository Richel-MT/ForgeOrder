# ForgeOrder 在线点单系统
一个运行于局域网的轻量级在线点单系统。

ForgeOrder 面向餐厅、小吃店、奶茶店等小型商户，支持顾客扫码点单、订单管理以及后台管理。

本系统仍处于开发阶段，仅用于学习和测试。

开发环境主要基于Windows，Linux尚未经过充分测试。

## 项目结构
```
├─docs
├─scripts
├─server
│  ├─app
│  │  ├─app_settings
│  │  ├─cli
│  │  ├─config
│  │  ├─db
│  │  ├─init_app
│  │  ├─models
│  │  ├─printer
│  │  │  ├─receipt
│  │  │  ├─renderer
│  │  ├─routes
│  ├─core
│  │  ├─auth
│  │  ├─config
│  │  ├─db
│  │  ├─error_handler
│  │  ├─log
│  │  ├─utils
│  │  ├─validation
│  │  │  ├─validators
│  ├─res
└─web
    ├─public
    └─src
        ├─assets
        ├─components
        ├─composables
        ├─locales
        ├─utils
        └─views
            ├─main
            │  └─components
            ├─shop
            └─system
```
其中，`web`目录为前端代码；`server`目录为后端代码。

## 技术架构
前端：
 - Vue3；
 - Vue Router；
 - Axios；
 - [mdui2](https://mdui.org)。

后端：
 - Python 3.14；
 - Flask；
 - SQLite3。

## 快速开始

- [Python 源代码运行](docs/quick_start/source.md)；
- [构建版本运行](docs/quick_start/release.md)。

## 文档
[目录](docs/index.md)。


## Todo
- [ ] Server：所有接口的详细日志输出
- [ ] Server：配置项验证功能对于自定义验证器的支持
- [ ] Server：类型转换器的扩展支持
- [ ] Web：统一的响应状态码的处理




## 协议
[MIT License](LICENSE)








