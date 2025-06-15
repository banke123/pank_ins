# AI示波器控制系统

一个基于AI技术的智能示波器控制和数据分析系统，集成了现代化的用户界面、智能工作流程生成和实时数据分析功能。

## 🌟 项目特色

### 核心功能
- **🤖 AI智能助手**: 基于LangChain框架的智能对话和分析系统
- **📊 实时波形显示**: 高性能的时域和频域波形可视化
- **🔄 智能工作流程**: AI自动生成测试流程和操作指导
- **📈 数据分析**: 自动信号特征提取和智能诊断
- **💬 自然语言交互**: 支持中文对话的AI助手
- **🔐 用户认证**: 现代化登录界面，支持用户管理

### 技术架构
- **UI框架**: PySide6 (现代化界面设计)
- **并发处理**: Pykka Actor模型 (高性能多线程)
- **AI引擎**: LangChain (可扩展的AI集成)
- **数据处理**: NumPy + Matplotlib (科学计算)
- **日志系统**: Python原生logging (完整的调试支持)

## 🚀 快速开始

### 系统要求
- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **Python版本**: 3.8 或更高版本
- **内存**: 建议 4GB 以上
- **存储空间**: 至少 1GB 可用空间

### 一键启动 (Windows)
```bash
# 双击运行批处理文件，选择启动模式
start.bat

# 启动模式选项:
# 1. 标准启动 (登录窗口)
# 2. 直接启动主窗口 (跳过登录)  
# 3. 快速启动 (跳过检查和登录)
# 4. 开发模式 (跳过检查，显示登录)
```

### 命令行启动
```bash
# 标准启动 (带环境检查和登录窗口)
python run.py

# 跳过登录直接启动主窗口
python run.py --skip-login

# 跳过环境检查快速启动
python run.py --skip-checks --skip-login

# 开发模式 (跳过检查但显示登录)
python run.py --skip-checks

# 直接使用main.py启动
python main.py --mode main
```

### 手动安装
```bash
# 1. 克隆项目
git clone <repository-url>
cd pank_ins

# 2. 创建虚拟环境
python -m venv .venv

# 3. 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 运行程序
python run.py
# 或直接运行
python main.py
```

### 启动参数说明
- `--skip-login`: 跳过登录窗口，直接启动主界面
- `--mode login|main`: 指定启动模式 (login=登录窗口, main=主窗口)
- `--skip-checks`: 跳过环境检查 (仅run.py支持)

### 登录说明
- **用户名**: 至少3个字符
- **密码**: 至少6个字符
- **记住密码**: 可选择保存登录凭证
- **演示模式**: 当前为演示版本，满足长度要求即可登录

## 📁 项目结构

```
pank_ins/
├── main.py                 # 主程序入口
├── run.py                  # 启动脚本(带环境检查)
├── start.bat              # Windows一键启动脚本
├── requirements.txt       # 依赖库列表
├── README.md              # 项目说明文档
├── .gitignore            # Git忽略文件
│
├── src/                   # 源代码目录
│   ├── __init__.py
│   ├── actors/           # Actor系统模块
│   │   ├── __init__.py
│   │   ├── base_actor.py      # Actor基类
│   │   ├── ui_actor.py        # UI处理Actor
│   │   ├── ai_actor.py        # AI处理Actor
│   │   ├── oscilloscope_actor.py  # 示波器控制Actor
│   │   ├── data_processor_actor.py # 数据处理Actor
│   │   └── logger_actor.py    # 日志管理Actor
│   │
│   ├── core/             # 核心功能模块
│   │   ├── __init__.py
│   │   └── system_manager.py  # 系统管理器
│   │
│   ├── ui/               # 用户界面模块
│   │   ├── __init__.py
│   │   ├── login_window.py    # 登录窗口
│   │   ├── main_window.py     # 主窗口(含左右侧边栏、工作区、日志区)
│   │   ├── app_launcher.py    # 应用启动器
│   │   ├── test_login.py      # 登录窗口测试
│   │   ├── test_main.py       # 主窗口测试
│   │   └── README.md          # UI模块说明
│   │
│   ├── utils/            # 工具函数模块
│   │   ├── __init__.py
│   │   └── logger_config.py   # 日志配置
│   │
│   └── config/           # 配置模块
│       ├── __init__.py
│       └── system_config.py   # 系统配置
│
├── config/               # 配置文件目录
├── logs/                 # 日志文件目录
├── plugins/              # 插件目录(时序图等功能)
├── tests/                # 测试文件目录
└── docs/                 # 文档目录
```

## 🎯 功能模块

### 1. 用户认证系统
- **现代化登录界面**: 左右分栏设计，动漫风格UI
- **用户验证**: 支持用户名密码验证
- **记住密码**: 可选择保存登录凭证
- **无边框窗口**: 支持拖拽移动，自定义控制按钮
- **动画效果**: 窗口淡入动画，提升用户体验

### 2. 主窗口系统
- **模块化设计**: 左侧边栏、右侧边栏、工作区、日志区独立组件
- **可拖拽布局**: 支持拖动分割线调整各区域大小
- **功能导航**: 左侧树形结构显示AI控制、插件管理、设备管理等模块
- **属性面板**: 右侧显示设备信息、任务状态等实时信息
- **实时日志**: 底部日志区域显示系统运行状态，支持颜色分级
- **完整界面**: 包含菜单栏、工具栏、状态栏的完整桌面应用

### 3. AI智能助手
- **自然语言对话**: 支持中文问答和技术咨询
- **智能分析**: 自动分析波形特征和信号质量
- **故障诊断**: 基于症状描述提供诊断建议
- **工作流程生成**: 根据测试目标自动生成操作步骤

### 4. 示波器控制
- **设备连接**: 支持USB/网络连接多种示波器
- **参数配置**: 智能参数推荐和自动配置
- **实时采集**: 高速数据采集和实时显示
- **自动测量**: 幅度、频率、相位等参数自动测量

### 5. 数据分析
- **时域分析**: 波形统计、趋势分析
- **频域分析**: FFT频谱分析、谐波检测
- **信号处理**: 滤波、去噪、信号增强
- **报告生成**: 自动生成测试报告和分析结果

### 6. Actor系统架构
- **BaseActor**: 提供通用Actor功能和消息处理
- **UIActor**: 处理用户界面相关消息和事件
- **AIActor**: 处理AI对话和智能分析请求
- **OscilloscopeActor**: 管理示波器设备连接和控制
- **DataProcessorActor**: 处理数据分析和信号处理
- **LoggerActor**: 统一日志管理和记录

## 🔧 配置说明

### 系统配置
系统使用JSON格式的配置文件，支持以下配置项：
- **系统信息**: 名称、版本、调试模式
- **日志配置**: 日志级别、输出格式
- **UI设置**: 主题、语言、窗口大小
- **AI配置**: 模型选择、API设置

### 日志配置
- **控制台输出**: 实时显示系统状态和错误信息
- **文件记录**: 按日期轮转的详细日志文件
- **级别控制**: DEBUG、INFO、WARNING、ERROR四个级别
- **格式化输出**: 时间戳、模块名、级别、消息内容

## 🔌 插件系统

系统支持插件扩展，预留了以下插件接口：
- **时序图功能**: 数字信号时序分析
- **高级分析**: 复杂信号处理算法
- **自定义测量**: 用户定义的测量项目
- **报告模板**: 自定义报告格式

## 🐛 故障排除

### 常见问题

**1. 程序无法启动**
```bash
# 检查Python版本
python --version

# 检查依赖库
pip list | grep PySide6

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

**2. 登录窗口显示异常**
- 检查显示器DPI设置
- 确保PySide6正确安装
- 尝试以管理员权限运行

**3. PowerShell执行策略问题**
```powershell
# 临时允许脚本执行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 或者直接运行Python
python main.py
```

**4. 示波器连接失败**
- 检查设备驱动程序
- 验证连接线缆
- 确认设备权限设置

### 日志查看
```bash
# 查看最新日志
tail -f logs/app_YYYYMMDD.log

# 查看错误日志
grep ERROR logs/app_YYYYMMDD.log
```

## 🤝 开发指南

### 代码规范
- 遵循PEP 8 Python代码规范
- 使用类型注解增强代码可读性
- 编写详细的文档字符串
- 保持模块化和低耦合设计

### 添加新功能
1. 在相应模块中创建新的Actor类
2. 实现必要的消息处理方法
3. 在系统管理器中注册新Actor
4. 添加相应的UI组件和交互逻辑
5. 编写单元测试和文档

### 测试
```bash
# 运行单元测试
python -m pytest tests/

# 代码格式检查
black src/
flake8 src/
```

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 👥 贡献者

- **PankIns Team** - 项目开发和维护

## 📞 支持

如果您遇到问题或有建议，请：
1. 查看[故障排除](#故障排除)部分
2. 检查[Issues](../../issues)中的已知问题
3. 创建新的Issue描述您的问题
4. 联系开发团队获取技术支持

## 🔄 更新日志

### v1.0.0 (2024-01-01)
- ✨ 初始版本发布
- 🎨 现代化Fluent Design界面
- 🤖 AI智能助手集成
- 📊 实时波形显示功能
- 🔄 Actor并发处理系统
- 📝 完整的日志和配置系统

---

**感谢使用AI示波器控制系统！** 🎉 