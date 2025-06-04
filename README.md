# AI示波器控制系统

## 项目简介

本项目是一个基于人工智能的示波器控制系统，通过AI模型来智能化控制示波器设备。系统采用模块化设计，支持插件扩展，包含时序图分析等功能。

## 技术架构

### 核心技术栈
- **AI框架**: LangChain - 用于AI模型调用和处理
- **UI界面**: PyQt6 - 现代化桌面应用界面
- **并发处理**: Pykka - Actor模型实现多线程消息交互
- **数据处理**: NumPy, Matplotlib - 数据分析和可视化
- **日志系统**: Python原生logging模块

### 系统架构
系统采用Actor模式，每个功能模块都是独立的Actor：
- UI Actor：负责用户界面交互
- AI Actor：处理AI模型调用和推理
- 示波器控制Actor：设备通信和控制
- 数据处理Actor：数据分析和处理
- 日志Actor：系统日志管理

## 项目结构

```
pank_ins/
├── src/                    # 源代码目录
│   ├── actors/            # Actor模块
│   ├── core/              # 核心功能模块
│   ├── ui/                # 用户界面模块
│   ├── utils/             # 工具函数
│   └── config/            # 配置文件
├── plugins/               # 插件目录
├── docs/                  # 文档目录
├── tests/                 # 测试目录
├── logs/                  # 日志目录
├── requirements.txt       # 依赖列表
└── main.py               # 主程序入口
```

## 安装说明

1. 克隆项目
```bash
git clone <repository-url>
cd pank_ins
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行程序
```bash
python main.py
```

## 功能特性

- ✅ AI智能控制示波器
- ✅ 模块化Actor架构
- ✅ 现代化UI界面
- ✅ 插件系统支持
- ✅ 时序图分析
- ✅ 完整的日志系统

## 开发规范

项目遵循以下开发规范：
- SOLID设计原则
- DRY（Don't Repeat Yourself）原则
- 模块化设计
- 完善的异常处理
- 完整的文档注释

## 许可证

待定 