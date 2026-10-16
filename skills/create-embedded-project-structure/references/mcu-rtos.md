# MCU + RTOS 结构参考


MCU + RTOS 项目的完整结构、分层职责，以及功能特性和目录的对应关系。
## 完整目录树
```plain text
ProjectName/
├── 01_Docs/
│   ├── Requirements/        # 需求规格书 SRS（SRS_template.md），需求编号 REQ-xxx
│   ├── Design/              # 架构图、接口文档、flash_layout.md、状态机图
│   ├── Datasheets/          # 芯片 / 器件手册
│   ├── Test/                # 测试用例、测试报告（test_report_template.md）
│   ├── Production/          # 量产 SOP、烧录和产测说明
│   └── Meeting/             # 会议纪要、评审记录
├── 02_Hardware/
│   ├── Schematic/  PCB/  BOM/  Gerber/
├── 03_Firmware/
│   ├── app/                 # 业务逻辑、任务、状态机；main.c
│   ├── middleware/
│   │   ├── protocol/        # 通信协议（自定义帧、Modbus、MQTT…）
│   │   ├── fs/              # FatFS / LittleFS
│   │   └── utils/           # log、ring_buffer、crc、软件定时器
│   ├── os/                  # RTOS 内核 + port（只读）
│   ├── drivers/<device>/    # 外部器件驱动，每个器件一个目录
│   ├── bsp/                 # board.c/.h：时钟、GPIO 映射、板载外设初始化
│   ├── hal/                 # 厂商 HAL / LL / SDK（只读）
│   ├── cmsis/               # 启动文件、system_xxx.c、链接脚本
│   ├── config/              # version.h、app_config.h；RTOS 配置（FreeRTOSConfig.h 等）由用户放入
│   ├── bootloader/          # 可选：独立 Bootloader 工程
│   ├── test/                # 主机端单元测试 test_*.c（run_tests.sh 编译运行）
│   ├── scripts/             # build.sh、flash.sh、run_tests.sh、check.sh、pack.sh、toolchain
│   ├── project/             # 仅 Keil / IAR：工程文件，只引用源码，不拷贝
│   ├── build/               # 编译输出 build/debug|release|factory/（git 忽略）
│   ├── .clang-format        # 代码格式；hal/ cmsis/ os/ 内放 DisableFormat
│   ├── CMakeLists.txt
│   └── README.md
├── 04_Tools/
│   ├── flash/               # 烧录工具、批量烧录脚本
│   ├── factory_test/        # 产测固件、工装脚本
│   └── host/                # 上位机
├── 05_Release/
│   ├── v1.0.0/              # pack.sh 输出：bin / hex / elf / map、sha256sum.txt、release_note.md
│   └── CHANGELOG.md         # 开发中的变更先写在 Unreleased 下
├── .gitlab/                 # MR 模板（GitHub：.github/pull_request_template.md）
├── .gitlab-ci.yml           # CI：static-check → unit-test → firmware-build（GitHub：.github/workflows/ci.yml）
├── .editorconfig
├── .gitignore
├── CONTRIBUTING.md          # 开发闭环、分支与提交、MR 自检清单、构建变体、发布流程
└── README.md
```
## 分层职责
<table header-row="true">
<tr>
<td>层</td>
<td>职责</td>
<td>禁止</td>
</tr>
<tr>
<td>app</td>
<td>任务划分、业务流程、状态机</td>
<td>直接操作寄存器或 HAL</td>
</tr>
<tr>
<td>middleware</td>
<td>与硬件无关、可复用的组件</td>
<td>include bsp 或 hal</td>
</tr>
<tr>
<td>drivers</td>
<td>器件协议（寄存器表、时序），通过 bsp 提供的总线接口收发</td>
<td>写死引脚号</td>
</tr>
<tr>
<td>bsp</td>
<td>引脚映射、时钟、总线实例，向上提供 `board_xxx()` 接口</td>
<td>包含业务逻辑</td>
</tr>
<tr>
<td>hal / cmsis / os</td>
<td>厂商和第三方代码</td>
<td>修改源码（配置放 config/）</td>
</tr>
</table>
RTOS 任务间通信用队列、信号量、事件组，禁止用全局变量传递数据；中断里只发通知，不做耗时处理。
## 功能特性 → 目录
<table header-row="true">
<tr>
<td>功能</td>
<td>新增目录或文件</td>
</tr>
<tr>
<td>OTA / IAP</td>
<td>`bootloader/`、`01_Docs/Design/flash_layout.md`、`middleware/ota/`</td>
</tr>
<tr>
<td>BLE / Wi-Fi</td>
<td>`middleware/protocol/ble/` 或 `wifi/`；SDK 协议栈放 `hal/` 或 `third_party/`</td>
</tr>
<tr>
<td>MQTT / HTTP</td>
<td>`middleware/protocol/mqtt/`；lwIP 放 `middleware/net/lwip/`</td>
</tr>
<tr>
<td>Modbus / CAN</td>
<td>`middleware/protocol/modbus/`、`drivers/can_xxx/`</td>
</tr>
<tr>
<td>GUI（LVGL）</td>
<td>`middleware/gui/lvgl/`（只读）+ `app/ui/`（界面代码）</td>
</tr>
<tr>
<td>文件系统</td>
<td>`middleware/fs/littlefs/` 或 `fatfs/`</td>
</tr>
<tr>
<td>参数存储</td>
<td>`middleware/param/`（KV + CRC 校验）</td>
</tr>
<tr>
<td>低功耗</td>
<td>`bsp/board_pm.c`、`app/pm_manager.c`</td>
</tr>
<tr>
<td>第三方库较多</td>
<td>`03_Firmware/third_party/`，每个库保留 LICENSE；`check.sh` 自动跳过含 LICENSE / COPYING 的目录</td>
</tr>
</table>
## config 约定
- `version.h`：`FW_VERSION_MAJOR / MINOR / PATCH / STR`，构建时间用 `__DATE__` 和 `__TIME__`。
- `app_config.h`：`CFG_ENABLE_xxx` 功能开关、任务栈和优先级；`CFG_FACTORY_MODE`（factory 构建传入 1）；`CFG_LOG_LEVEL` 按构建变体自动选择：debug 4、release 2（定义了 `NDEBUG`）、factory 3。
- RTOS 配置文件（如 `FreeRTOSConfig.h`、`rtconfig.h`）放 `config/`，不要放进 `os/`。
## 构建变体
<table header-row="true">
<tr>
<td>变体</td>
<td>CMake</td>
<td>Keil / IAR</td>
</tr>
<tr>
<td>debug</td>
<td>`scripts/build.sh debug`：-O0 -g</td>
<td>Debug Target</td>
</tr>
<tr>
<td>release</td>
<td>`scripts/build.sh release`：-Os，定义 `NDEBUG`</td>
<td>Release Target，定义 `NDEBUG`</td>
</tr>
<tr>
<td>factory</td>
<td>`scripts/build.sh factory`：release + `CFG_FACTORY_MODE=1`</td>
<td>Factory Target，定义 `NDEBUG` 和 `CFG_FACTORY_MODE=1`</td>
</tr>
</table>
CMake 产物在 `build/<变体>/`（elf、bin、hex、map），用 `scripts/pack.sh <变体>` 归档到 `05_Release/vX.Y.Z/`；Keil / IAR 用 `scripts/pack.sh release <IDE 输出目录>`。
