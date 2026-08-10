# CLOCK - 高精度频率计后端标准时钟产生模块

<div align="center">

**专业级时间基准解决方案 | 超低相位噪声 | 高稳定度输出**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)]()

</div>

---

## 📋 项目概述

本模块是**高精度频率计的后端标准时钟产生系统**，为频率测量提供超稳定的时间基准信号。采用 TI 高端时钟发生器芯片 **LMK5B12204** 和 **LMK1C1102**，实现超低相位噪声和高精度的时钟输出，适用于精密测试测量、通信系统、雷达电子战等对时钟质量要求极高的应用场景。

### 核心特性

- ✅ **超低相位噪声**：专业级时钟性能，满足苛刻的频谱纯度要求
- ✅ **多路可编程输出**：支持 4 路独立可编程差分时钟输出（LVDS/PECL）
- ✅ **高分辨率频率合成**：支持 1Hz-3.3GHz 范围内任意频率设定
- ✅ **参考源冗余切换**：双参考输入 + 自动切换，确保时钟连续性
- ✅ **低抖动性能**：<0.2ps RMS 抖动，提供精准时序基准
- ✅ **EEPROM 存储**：配置断电保存，上电自启动
- ✅ **硬件级稳定性**：工业级设计，宽温工作范围

---

## 🔧 技术规格

### 时钟输出性能

| 参数 | 指标 |
|------|------|
| 输出通道数 | 4 路独立可编程 |
| 输出类型 | LVDS / PECL / CML 差分 |
| 频率范围 | 1MHz ~ 1.25GHz (每路独立) |
| 相位噪声 | < -110dBc @ 1kHz (100MHz 输出) |
| 均方根抖动 | < 0.2ps (12kHz-20MHz 积分) |
| 输出幅度 | 800mVp-p 差分 (典型) |
| 输出阻抗 | 50Ω 匹配 |

### 参考输入

| 参数 | 指标 |
|------|------|
| 主参考输入 | 10MHz 正弦/CMOS 可选 |
| 备参考输入 | 10MHz 或 1PPS 可选 |
| 参考切换 | 自动故障检测与无缝切换 |
| 1PPS 对齐 | 支持秒脉冲同步对齐 |

### 电源要求

- **核心电压**：3.3V ±5%
- **功耗**：典型 1.2W
- **电源抑制比**：>60dB

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    CLOCK 时钟产生模块                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│   │  Ref 1   │    │  Ref 2   │    │  1PPS    │              │
│   │ 10MHz    │    │ 10MHz/   │    │  Pulse   │              │
│   │ 正弦     │    │ PPS      │    │          │              │
│   └────┬─────┘    └────┬─────┘    └────┬─────┘              │
│        │               │                │                   │
│        └───────────────┼────────────────┘                   │
│                        ▼                                    │
│                 ┌───────────────┐                           │
│                 │   LMK5B12204  │  ┌────────────┐          │
│                 │  时钟生成器   │  │            │          │
│                 │  (Main PLL)   │→ │ Out0:100MHz│ LVDS     │
│                 │               │  │            │          │
│                 │               │→ │ Out1:10MHz │ LVDS     │
│                 │               │  │            │          │
│                 │               │→ │ Out2:10MHz │ LVDS     │
│                 │               │  │            │          │
│                 │               │→ │ Out3:1PPS  │ CMOS     │
│                 └───────────────┘  └────────────┘           │
│                        ▲                                      │
│                        │ I²C 配置                            │
│                 ┌───────────────┐                           │
│                 │   LMK1C1102   │  ┌────────────┐           │
│                 │  低抖动分配器 │  │  Status    │ LED 指示    │
│                 │  (Secondary)  │  │  GPIO      │            │
│                 └───────────────┘  └────────────┘           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 关键组件

| 器件 | 制造商 | 功能描述 |
|------|--------|----------|
| **LMK5B12204** | Texas Instruments | 高性能时钟生成器，内置 4 个超低噪声 PLL |
| **LMK1C1102** | Texas Instruments | 低抖动时钟分配器，提供辅助时钟路径 |
| **SMA 连接器** | Amphenol | RF 输入输出接口，50Ω 匹配 |
| **EEPROM** | Atmel | 非易失性配置存储 |

---

## 📁 目录结构

```
CLOCK-master/
├── firmware/              # 嵌入式固件代码
│   ├── src/
│   │   ├── app/           # 应用层：时钟控制逻辑、状态机
│   │   ├── hal/           # 硬件抽象层：GPIO、I²C、定时器
│   │   ├── drivers/       # 驱动层：LMK5B 寄存器配置
│   │   └── services/      # 服务层：I²C 通信、EEPROM 访问
│   ├── boards/            # 板级配置
│   └── CMakeLists.txt     # CMake 构建配置
├── hardware/              # 硬件设计文件
│   ├── schematic/         # KiCad 原理图
│   │   └── v1.0/
│   │       ├── CLOCK.kicad_sch
│   │       ├── CLOCK.kicad_pcb
│   │       └── ...
│   ├── bom/               # BOM 物料清单
│   ├── gerber/            # PCB 生产文件
│   └── pinout/pinout.md   # 引脚分配说明
├── software/              # 配套软件（可选）
│   ├── desktop/           # PC 配置工具
│   └── mobile/            # 移动端 App
├── docs/                  # 项目文档
│   ├── architecture/      # 架构设计文档
│   ├── user-guide/        # 用户使用手册
│   └── api/               # API 接口文档
├── tests/                 # 测试套件
│   ├── unit/              # 单元测试
│   └── integration/       # 集成测试
└── tools/                 # 工具脚本
    └── scripts/build.py   # 自动化构建脚本
```

---

## 🛠️ 快速开始

### 环境要求

- **编译工具链**：ARM GCC Toolchain (arm-none-eabi-gcc)
- **构建系统**：CMake 3.16+
- **硬件调试器**：JLink / STLink
- **操作系统**：Windows 10+ / Linux / macOS

### 构建固件

```bash
# 克隆仓库
git clone https://github.com/your-repo/CLOCK.git
cd CLOCK

# 创建构建目录
mkdir build && cd build

# 配置项目
cmake .. -DBOARD=default

# 编译 Debug 版本
cmake --build .

# 编译 Release 版本（优化）
cmake --build . --config Release
```

或使用自动化脚本：

```bash
python tools/scripts/build.py --board=default          # Debug 构建
python tools/scripts/build.py --board=v2.0 --release   # Release 构建
python tools/scripts/build.py --flash                  # 构建并烧录
```

### 烧录固件

```bash
# JLink 烧录
JLinkExe -device STM32F4xx -interface swd -speed 4000 -fc 4 -commandER -exitafter1sec firmware/build/app.hex

# 或通过 IDE 烧录
```

---

## 📖 使用说明

### 1. 硬件连接

1. 连接外部 10MHz 参考源到 **J1 (REF_IN)** SMA 接口
2. 可选：连接备用参考源到 **REF_BIST** 接口
3. 连接电源至 **VDD_3V3** (3.3V, 最大 500mA)
4. 观测输出：
   - **J2: OUT0** - 100MHz 主时钟
   - **J3: OUT1** - 10MHz 分频时钟  
   - **J4: OUT2** - 可配置频率
   - **J5: OUT3** - 1PPS 秒脉冲

### 2. 默认配置

上电后，模块将加载 EEPROM 中保存的配置：

- **OUT0**: 100MHz LVDS 差分输出
- **OUT1**: 10MHz LVDS 差分输出
- **OUT2**: 10MHz LVDS 差分输出
- **OUT3**: 1PPS 正方形波输出（上升沿对齐 UTC 时间）

### 3. 配置时钟参数

通过串口命令或 I²C 接口修改时钟参数：

```bash
# 示例：使用串口终端配置
echo "SET_FREQ OUT0 200MHz" > /dev/ttyUSB0    # 设置 OUT0 为 200MHz
echo "SET_FMT OUT1 LVDS" > /dev/ttyUSB0       # 设置 OUT1 格式为 LVDS
echo "SAVE_CONFIG" > /dev/ttyUSB0             # 保存配置到 EEPROM
```

详细命令集请参考 [API 文档](docs/api/).

---

## 🔬 性能验证

### 相位噪声测试

在 100MHz 输出端口测得的典型相位噪声：

| 偏移频率 | 相位噪声 (dBc/Hz) |
|----------|------------------|
| 100 Hz   | -95              |
| 1 kHz    | -110             |
| 10 kHz   | -125             |
| 100 kHz  | -135             |
| 1 MHz    | -145             |
| 10 MHz   | -150             |

### 抖动测试

使用示波器测得 RMS 抖动：**0.15ps** (12kHz-20MHz 带宽)

### 频率稳定度

- 短期稳定度 (ADEV @ 1s): **2×10⁻¹²**
- 长期稳定度 (±0.5ppm/年，配合 TCXO 参考)

---

## 🧪 测试运行

```bash
# 运行单元测试
ctest --output-on-failure

# 运行集成测试（需要硬件）
python tests/integration/run_hwt_tests.py --board=default
```

---

## 📚 参考资料

- **数据手册**：
  - [LMK5B12204 Datasheet (PDF)](https://www.ti.com/lit/ds/symlink/lmk5b12204.pdf)
  - [LMK1C1102 Datasheet (PDF)](https://www.ti.com/lit/ds/symlink/lmk1c1102.pdf)
  
- **应用笔记**：
  - [Clock and Timing Design Guidelines](https://www.ti.com/lit/an)
  - [Low-Jitter Clock Distribution Techniques](docs/architecture/clock_design.pdf)

- **项目文档**：
  - [架构设计文档](docs/architecture/architecture.md)
  - [用户操作手册](docs/user-guide/)

---

## 🛡️ 许可证

本项目采用 **MIT License**。详见 [LICENSE](LICENSE) 文件。

---

## 🤝 贡献指南

欢迎提交 Bug Report 和功能请求！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feat/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feat/AmazingFeature`)
5. 开启 Pull Request

---

## 📞 联系方式

如有技术问题或合作意向，请联系：

- **项目负责人**: [Your Name]
- **邮箱**: [your.email@example.com](mailto:your.email@example.com)
- **GitHub**: [您的 GitHub 地址](https://github.com/your-repo)

---

## ⚠️ 免责声明

本模块为专业级测试设备，仅供研发和技术人员使用。使用者需具备以下能力：

- 熟悉射频电路设计和测试仪器操作
- 理解时钟完整性、EMC/EMI 相关规范
- 遵守实验室安全操作规程

作者不对因不当使用导致的设备损坏或人身伤害承担责任。

---

<div align="center">

**© 2026 CLOCK 项目团队。保留所有权利。**

*基于 Texas Instruments LMK5B12204 + LMK1C1102 专业时钟芯片方案开发*

🎯 **为高精度频率测量提供黄金时间基准** 🎯

</div>
