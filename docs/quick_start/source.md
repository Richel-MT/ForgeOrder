
[README](/README.md)
[返回](../index.md)

# 快速开始——Python 源代码运行
## 1. 克隆项目
使用Git克隆项目到本地：
```bash
git clone https://github.com/computer-drive/ForgeOrder.git
```

### 2. 后端操作
在`server`目录下，使用Poetry安装依赖：
```bash
poetry install
```

### 3. 前端操作
在`web`目录下，使用npm安装依赖：
```bash
npm install
```
运行编译命令：
```bash
npm run build
```
注意：编译后的文件将自动放在`/server/static/`目录下。

### 4. 运行后端
在`server`目录下，使用Poetry运行后端：
```bash
poetry run python app.py
```