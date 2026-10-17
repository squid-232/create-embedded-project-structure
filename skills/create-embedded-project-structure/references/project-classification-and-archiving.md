# 项目类型判断与资料归档规则

自动判断项目类型、输出方式，以及把用户已有的资料（文档、硬件文件、源码、工具、固件）归到标准目录的规则。**第 1 节**在每次收集输入时使用；**第 2、3 节**在用户提供了现有文件、压缩包、文件清单或已有工程时使用。
## 1. 项目类型判断
### 1.1 判断流程
按顺序执行，命中即停：
1. **用户明确指定**（“MCU 项目”“Linux 项目”“跑 FreeRTOS”）→ 直接采用。与下面的信号冲突时（如“Linux 项目，芯片 STM32F407”），用 当前环境可用的提问工具或直接向用户提问 确认一次。
2. **用户提供了现有资料** → 先按第 3 节扫描文件，文件里的信号（工程文件、启动文件、设备树、defconfig）优先于文字描述。
3. **收集信号**：从用户的文字、文件名和文件内容中，按 1.2 和 1.3 的表找出所有强信号和弱信号。
4. **按 1.4 的规则得出结论**。
5. 在最终回复第一行写明结论和依据，例如：`项目类型：mcu-rtos（依据：STM32F407、FreeRTOS、startup_stm32f407xx.s）`，方便用户纠正。
### 1.2 强信号：MCU + RTOS（`mcu-rtos`）
<table header-row="true">
<tr>
<td>类别</td>
<td>判断条件（出现任一即命中）</td>
</tr>
<tr>
<td>ST</td>
<td>STM32 C0 / F0 / F1 / F2 / F3 / F4 / F7 / G0 / G4 / H5 / H7 / L0 / L1 / L4 / L5 / U0 / U5 / WB / WBA / WL 系列（STM32MP 除外，见 1.5）</td>
</tr>
<tr>
<td>国产 MCU</td>
<td>GD32（含 GD32V RISC-V）、AT32、HC32、MM32、CH32（含 CH32V）、N32、APM32、FM33、HK32、CKS32、BK72xx、BL602 / BL616 / BL702、W800 / W801、ASR、LKS32</td>
</tr>
<tr>
<td>无线 SoC</td>
<td>ESP32 全系列（ESP32、S2、S3、C2、C3、C5、C6、H2、P4）、ESP8266、nRF51 / nRF52 / nRF53 / nRF54 / nRF91、CC13xx / CC26xx / CC32xx、EFR32 / EFM32、PHY62xx、TLSR82xx、CYW43xxx 配 MCU 使用</td>
</tr>
<tr>
<td>其他厂商</td>
<td>NXP LPC / Kinetis / MCX / i.MX RT（RT1050、RT1060、RT1170 等）/ S32K；Microchip SAMD / SAME / SAML / PIC / dsPIC / AVR / ATmega / ATtiny；TI MSP430 / MSP432 / MSPM0 / TM4C / C2000（TMS320F28xxx）；Renesas RA / RX / RL78 / RH850；Infineon XMC / PSoC / AURIX（TC2xx、TC3xx）/ TRAVEO；RP2040 / RP2350；K210；Silicon Labs、Holtek、Nuvoton（M0 / M4 / NUC 系列）、Artery</td>
</tr>
<tr>
<td>RTOS / 裸机</td>
<td>FreeRTOS、RT-Thread（标准版、Nano）、Zephyr、ThreadX / Azure RTOS / Eclipse ThreadX、uC/OS-II / uC/OS-III、embOS、Keil RTX / CMSIS-RTOS、NuttX、LiteOS-M、TencentOS tiny、AliOS Things、Mbed OS、SafeRTOS、“裸机”“超级循环”“前后台”</td>
</tr>
<tr>
<td>工具链 / IDE</td>
<td>Keil MDK（`*.uvprojx`、`*.uvproj`）、IAR EWARM（`*.ewp`、`*.eww`）、STM32CubeIDE / CubeMX（`*.ioc`）、MCUXpresso、e² studio、Code Composer Studio、MounRiver、ESP-IDF（`idf.py`、`sdkconfig`）、PlatformIO（`platformio.ini`）、Arduino（`*.ino`）、`arm-none-eabi-gcc`、`riscv-none-elf-gcc`、J-Link / ST-Link / DAP-Link / OpenOCD 烧录</td>
</tr>
<tr>
<td>文件</td>
<td>`startup_*.s` / `startup_*.S`、`system_*.c`、含 `MEMORY { FLASH ... RAM ... }` 的 `*.ld`、`*.sct`、`*.icf`、`*_hal_conf.h`、`FreeRTOSConfig.h`、`rtconfig.h`、`tx_user.h`、`os_cfg.h`、`prj.conf`（Zephyr）、`*.svd`、`*.FLM`</td>
</tr>
<tr>
<td>描述</td>
<td>单片机、MCU、Cortex-M0 / M3 / M4 / M7 / M33 / M55、RISC-V MCU、KB 级 RAM / Flash、寄存器、中断服务函数、低功耗传感器节点、按键 / LED / 串口小板</td>
</tr>
</table>
### 1.3 强信号：嵌入式 Linux（`linux`）
<table header-row="true">
<tr>
<td>类别</td>
<td>判断条件（出现任一即命中）</td>
</tr>
<tr>
<td>Rockchip</td>
<td>RK3036 / RK3128 / RK3188 / RK3288 / RK3308 / RK3326 / RK3328 / RK3399 / RK3528 / RK3562 / RK3566 / RK3568 / RK3576 / RK3588、RV1103 / RV1106 / RV1109 / RV1126</td>
</tr>
<tr>
<td>全志</td>
<td>H2+ / H3 / H5 / H6 / H616 / H618、A33 / A40i / A64 / A133、T113 / T507 / T527、V3s / V851 / V853、F1C100s / F1C200s、D1 / D1s、R528 / R818</td>
</tr>
<tr>
<td>NXP / TI / ST / Microchip</td>
<td>i.MX 6 / 7 / 8 / 8M / 8M Mini / 8M Plus / 9 / 93（i.MX RT 除外）、Layerscape；TI AM335x / AM437x / AM57x / AM62x / AM64x / AM62A；STM32MP13 / MP15 / MP2（见 1.5）；SAMA5 / SAMA7 / SAM9X</td>
</tr>
<tr>
<td>其他 SoC</td>
<td>海思 Hi3516 / Hi3518 / Hi3519 / Hi3559、SigmaStar SSD20x / SSD22x、君正 X1000 / X2000 / T31、Amlogic S905 / A311D、MediaTek MT76xx / MT7621 / MT7628（OpenWrt）、Broadcom BCM2711 / BCM2712（树莓派）、NVIDIA Jetson、晶晨、瑞芯微、星宸、Cortex-A7 / A9 / A35 / A53 / A55 / A72 / A76</td>
</tr>
<tr>
<td>系统 / 构建</td>
<td>Buildroot、Yocto / Poky / OpenEmbedded / bitbake、PetaLinux、OpenWrt、Debian / Ubuntu / Armbian 根文件系统、U-Boot、Linux 内核、设备树、rootfs、BusyBox、systemd、init.d、内核模块 `*.ko`、交叉编译器 `aarch64-linux-gnu-`、`arm-linux-gnueabihf-`</td>
</tr>
<tr>
<td>文件</td>
<td>`*.dts` / `*.dtsi` / `*.dtso`、`*_defconfig`（内容含 `CONFIG_ARM64`、`CONFIG_SYS_`、`BR2_`）、`Kconfig`、`external.desc`、`*.bb` / `*.bbappend` / `layer.conf`、`*.service`、`etc/init.d/S*`、`update.img` / `*.wic` / `*.ext4` / `zImage` / `Image` / `*.dtb`、含 `module_init` / `MODULE_LICENSE` 的 `.c`</td>
</tr>
<tr>
<td>描述</td>
<td>网关跑 Linux、工控 HMI 屏（Qt / LVGL on framebuffer）、AI 摄像头、NPU、DDR / eMMC / GB 级内存、Docker、多进程、Python / Node.js 应用</td>
</tr>
</table>
### 1.4 结论规则
<table header-row="true">
<tr>
<td>信号情况</td>
<td>结论</td>
</tr>
<tr>
<td>只有 MCU 强信号</td>
<td>`mcu-rtos`；出现“裸机”“超级循环”时按特殊情况“MCU 裸机”处理</td>
</tr>
<tr>
<td>只有 Linux 强信号</td>
<td>`linux`</td>
</tr>
<tr>
<td>两类强信号都有，且是两颗芯片（如 RK3568 主控 + STM32 协处理器）</td>
<td>多固件：`03_Firmware/linux/` 和 `03_Firmware/mcu/` 分别按两种结构组织，见 skill 的“特殊情况”</td>
</tr>
<tr>
<td>两类强信号来自同一颗异构 SoC（STM32MP1、i.MX 8M 的 M4 / M7 核、AM62x 的 M4F 核）</td>
<td>`linux` 为主；用户提到 M 核固件时，加 `03_Firmware/mcu/` 按多固件处理</td>
</tr>
<tr>
<td>只有文档和硬件资料（原理图、PCB、3D、BOM、Gerber、手册），用户只要求归档</td>
<td>不判断类型，也不提问：`01_Docs/`、`02_Hardware/`、`04_Tools/` 在两种类型中结构相同。要生成骨架或资料中出现固件文件时再判断</td>
</tr>
<tr>
<td>只有弱信号（见 1.6）或没有信号</td>
<td>例程模式：默认 `mcu-rtos`；否则用 当前环境可用的提问工具或直接向用户提问 问一次，选项为“MCU + RTOS / 嵌入式 Linux / 两者都有”</td>
</tr>
</table>
### 1.5 容易判错的芯片
<table header-row="true">
<tr>
<td>芯片</td>
<td>正确类型</td>
<td>说明</td>
</tr>
<tr>
<td>STM32MP13 / MP15 / MP2</td>
<td>`linux`</td>
<td>名字带 STM32，但主核是 Cortex-A，跑 Linux；MP15 的 M4 核固件按多固件处理</td>
</tr>
<tr>
<td>i.MX RT 系列</td>
<td>`mcu-rtos`</td>
<td>跨界 MCU，没有 MMU，跑 FreeRTOS 或裸机</td>
</tr>
<tr>
<td>i.MX 6 / 8 / 9</td>
<td>`linux`</td>
<td>应用处理器</td>
</tr>
<tr>
<td>ESP32-P4 / ESP32-S3</td>
<td>`mcu-rtos`</td>
<td>主频高、带屏幕，但仍是 ESP-IDF（FreeRTOS）</td>
</tr>
<tr>
<td>Xilinx Zynq / ZynqMP / Versal</td>
<td>看系统</td>
<td>用 PetaLinux 为 `linux`；只在 R5 / A9 上跑 standalone 或 FreeRTOS 为 `mcu-rtos`；两者都有按多固件</td>
</tr>
<tr>
<td>全志 F1C100s / V3s</td>
<td>`linux`</td>
<td>内存小，但通常跑 Linux；用户明确说跑 RT-Thread 时为 `mcu-rtos`</td>
</tr>
<tr>
<td>K210、BL808</td>
<td>看系统</td>
<td>K210 通常为 `mcu-rtos`；BL808 的 D0 核跑 Linux、M0 核跑 RTOS，两者都有按多固件</td>
</tr>
<tr>
<td>RT-Thread Smart、NuttX on MPU</td>
<td>用 当前环境可用的提问工具或直接向用户提问 确认</td>
<td>带 MMU 的 RTOS，按 `mcu-rtos` 结构组织更常见</td>
</tr>
<tr>
<td>Android 设备</td>
<td>`linux`（参考）</td>
<td>本 skill 不覆盖 AOSP 结构，按 Linux 结构给出 BSP 部分，并在回复中说明</td>
</tr>
</table>
### 1.6 弱信号（单独出现时不能定类型）
网关、控制器、物联网设备、智能硬件、Wi-Fi、BLE、4G、MQTT、OTA、LVGL、GUI、触摸屏、CMake、Makefile、C / C++、GCC、Modbus、CAN、“嵌入式”。弱信号只用于在 1.4 中辅助判断（例如“Qt”“Python”“Docker”偏向 Linux，“KB 级 RAM”“电池供电几年”偏向 MCU），不能单独作为结论。
## 2. 输出方式判断
用户可以同时命中多项，按 skill 第 3 节逐项执行。
<table header-row="true">
<tr>
<td>用户的说法</td>
<td>输出方式</td>
</tr>
<tr>
<td>目录结构、工程结构、怎么分层、项目怎么组织</td>
<td>A. 目录树 + 说明</td>
</tr>
<tr>
<td>zip、骨架、模板、脚手架、下载、直接能用、生成工程</td>
<td>B. 项目骨架 zip</td>
</tr>
<tr>
<td>Notion、写成页面、文档、规范页、放到知识库</td>
<td>C. Notion 规范页面</td>
</tr>
<tr>
<td>研发流程、开发规范、工作流、CI、代码检查、EVT / DVT / PVT、发布流程</td>
<td>D. 研发工作流规范</td>
</tr>
<tr>
<td>上传了文件或压缩包、给出文件清单；整理、归类、归档、这些资料放哪、已有工程规范化、迁移</td>
<td>E. 资料归档</td>
</tr>
<tr>
<td>都没命中</td>
<td>A；例程模式为 A + B</td>
</tr>
</table>
## 3. 资料归档规则
### 3.1 获取文件清单
<table header-row="true">
<tr>
<td>来源</td>
<td>做法</td>
</tr>
<tr>
<td>对话里上传的文件或压缩包</td>
<td>下载到工作目录；压缩包先安全检查，用 `unzip -l` 列出路径；本地目录用 `rg --files` 或文件系统工具枚举</td>
</tr>
<tr>
<td>Notion 页面中的附件</td>
<td>通过当前 Notion MCP 加载页面并取得附件下载地址，下载到工作目录</td>
</tr>
<tr>
<td>用户贴出的文件清单或目录截图</td>
<td>直接按清单分类，内容判断项写“按文件名判断”</td>
</tr>
<tr>
<td>只口头描述</td>
<td>按描述列出“建议存放位置”表，不做内容判断</td>
</tr>
</table>
文件超过 200 个时，先按 3.3 的目录规则整目录归类，映射表只列目录，不逐个列文件。
### 3.2 匹配顺序
每个文件按下面顺序匹配，命中即停：
1. **不入库规则**（3.9）：编译输出、IDE 临时文件、密钥 → 标记“不入库”。
2. **整目录规则**（3.3）：厂商 SDK、RTOS、CubeMX 目录等整体归类，保持内部结构不变。
3. **文件名和扩展名规则**（3.4–3.8）。
4. **内容规则**（3.10）：扩展名不足以判断时（`.pdf`、`.docx`、`.xlsx`、`.c`、`.h`、`.bin`、图片），读取内容判断。
5. 都没命中 → 放入“待确认”列表，给出最可能的两个位置供用户选择。
### 3.3 整目录规则
<table header-row="true">
<tr>
<td>原目录特征</td>
<td>目标位置</td>
</tr>
<tr>
<td>`Drivers/CMSIS/`、含 `core_cm*.h`、`cmsis_*.h` 的目录</td>
<td>`03_Firmware/cmsis/`</td>
</tr>
<tr>
<td>`Drivers/STM32*_HAL_Driver/`、`Libraries/*StdPeriph_Driver/`、`GD32*_Firmware_Library/`、`nrfx/`、厂商 `SDK/`</td>
<td>`03_Firmware/hal/`（只读，保留原目录名）</td>
</tr>
<tr>
<td>`Middlewares/Third_Party/FreeRTOS/`、`FreeRTOS/Source/`、RT-Thread 的 `src/`、`libcpu/`、`include/`，ThreadX 的 `common/`、`ports/`</td>
<td>`03_Firmware/os/`</td>
</tr>
<tr>
<td>`Middlewares/Third_Party/FatFs/`、`littlefs/`</td>
<td>`03_Firmware/middleware/fs/fatfs/`、`middleware/fs/littlefs/`</td>
</tr>
<tr>
<td>`Middlewares/Third_Party/LwIP/`、`LWIP/`</td>
<td>`03_Firmware/middleware/net/lwip/`</td>
</tr>
<tr>
<td>`Middlewares/ST/STM32_USB_*_Library/`、TinyUSB、CherryUSB</td>
<td>`03_Firmware/middleware/usb/`（只读）</td>
</tr>
<tr>
<td>`lvgl/`</td>
<td>`03_Firmware/middleware/gui/lvgl/`（只读）</td>
</tr>
<tr>
<td>带 LICENSE 或 COPYING 的其他第三方库（cJSON、mbedTLS、Paho MQTT、nanopb、SEGGER RTT、letter-shell、EasyLogger 等）</td>
<td>协议类放 `middleware/protocol/<lib>/`，其余放 `03_Firmware/third_party/<lib>/`；保留 LICENSE</td>
</tr>
<tr>
<td>`MDK-ARM/`、`EWARM/`、`.cproject` 和 `.project`（CubeIDE）</td>
<td>`03_Firmware/project/`；其中的启动文件放 `cmsis/`，`Objects/`、`Listings/`、`Debug/`、`Release/` 不入库</td>
</tr>
<tr>
<td>Keil 的 `RTE/`</td>
<td>`03_Firmware/project/RTE/`（由 Keil 管理）</td>
</tr>
<tr>
<td>完整的 U-Boot 源码树（含 `arch/`、`board/`、`cmd/`、`include/configs/`）</td>
<td>不入库：在 `scripts/fetch_sources.sh` 中记录仓库地址和版本，`03_Firmware/uboot/src/`（git 忽略）；已有修改导出 patch 放 `uboot/patches/`</td>
</tr>
<tr>
<td>完整的内核源码树（含 `arch/`、`drivers/`、`kernel/`、`mm/`，`Makefile` 有 `VERSION =`）</td>
<td>同上，放 `03_Firmware/kernel/src/`（git 忽略），修改导出到 `kernel/patches/`</td>
</tr>
<tr>
<td>Buildroot 源码树（含 `package/`、`boot/`、`Config.in` 和 `support/`）</td>
<td>不入库，在 `fetch_sources.sh` 中记录版本；用户自己的 package 和配置按 3.7 归类</td>
</tr>
<tr>
<td>Yocto 层（含 `conf/layer.conf`）</td>
<td>厂商层不入库，在文档中记录；自己的层放 `03_Firmware/rootfs/meta-<board>/`</td>
</tr>
</table>
### 3.4 文档 → `01_Docs/`
<table header-row="true">
<tr>
<td>判断条件（文件名关键词或内容）</td>
<td>目标</td>
</tr>
<tr>
<td>需求、PRD、SRS、MRD、需求规格、产品规格书、功能清单、立项书；内容含 `REQ-` 编号、“功能需求”“非功能需求”</td>
<td>`01_Docs/Requirements/`</td>
</tr>
<tr>
<td>选型报告、方案、竞品分析、系统框图、架构、概要设计、详细设计、接口文档、通信协议（自定义）、状态机、时序图、流程图、Flash / 内存分区、引脚分配表、`*.drawio`、`*.vsdx`、`*.puml`、`*.mmd`、`*.xmind`</td>
<td>`01_Docs/Design/`</td>
</tr>
<tr>
<td>datasheet、DS、Reference Manual（RM）、Programming Manual（PM）、User Manual（UM）、Application Note（AN）、Errata（ES）、勘误、器件规格书；文件名以芯片或器件型号开头（`stm32f407vg.pdf`、`BMP280-DS001.pdf`）</td>
<td>`01_Docs/Datasheets/`；超过 20 份时按器件建子目录 `Datasheets/<器件>/`</td>
</tr>
<tr>
<td>测试计划、测试用例、测试报告、TC-、老化、高低温、EMC、ESD、功耗测试、可靠性、问题单、Bug 列表、调试记录</td>
<td>`01_Docs/Test/`</td>
</tr>
<tr>
<td>CE、FCC、SRRC、CCC、RoHS、REACH 等认证或检测报告</td>
<td>`01_Docs/Test/Certification/`</td>
</tr>
<tr>
<td>SOP、作业指导书、量产、烧录说明、产测说明、校准、工装说明、包装、出货检验</td>
<td>`01_Docs/Production/`</td>
</tr>
<tr>
<td>会议纪要、评审记录、周报、minutes、文件名以日期开头的纪要</td>
<td>`01_Docs/Meeting/`</td>
</tr>
<tr>
<td>产品说明书、用户手册（面向客户）</td>
<td>`01_Docs/Manual/`（新增子目录）</td>
</tr>
</table>
### 3.5 硬件 → `02_Hardware/`
<table header-row="true">
<tr>
<td>判断条件</td>
<td>目标</td>
</tr>
<tr>
<td>`*.SchDoc`、`*.kicad_sch`、`*.sch`、`*.DSN`（OrCAD Capture）、`*.opj`；文件名含“原理图”、SCH、Schematic 的 PDF</td>
<td>`02_Hardware/Schematic/`</td>
</tr>
<tr>
<td>`*.PcbDoc`、`*.PrjPcb`、`*.kicad_pcb`、`*.kicad_pro`、`*.brd`（Allegro / Eagle）、`*.pcb`（PADS）、`*.epro` / `*.eprj`（嘉立创 EDA）</td>
<td>`02_Hardware/PCB/`</td>
</tr>
<tr>
<td>封装库和元件库：`*.SchLib`、`*.PcbLib`、`*.IntLib`、`*.olb`、`*.dra`、`*.psm`、`*.pretty/`、`*.kicad_sym`</td>
<td>`02_Hardware/PCB/Library/`</td>
</tr>
<tr>
<td>文件名含 BOM、物料清单；或 `.xlsx` / `.csv` 表头含“位号 / Designator”“料号 / Part Number”“数量 / Quantity”“封装 / Footprint”</td>
<td>`02_Hardware/BOM/`</td>
</tr>
<tr>
<td>`*.gbr`、`*.gtl` / `*.gbl` / `*.gto` / `*.gbo` / `*.gts` / `*.gbs` / `*.gtp` / `*.gbp` / `*.gko` / `*.gm1`、钻孔文件 `*.drl` / `*.xln`、`*.ipc`、坐标文件（`*.pos`、文件名含 CPL、坐标、Pick Place）；只含这些文件的压缩包</td>
<td>`02_Hardware/Gerber/`</td>
</tr>
<tr>
<td>PCB 整板 3D 模型：EDA 导出的 `*.step`、`*.stp`、`*.wrl`、`*.x_t`，文件名与 PCB 工程同名，或含 PCB、板、board、3D、装配；文件名看不出来时按 3.5.1 读取文件头</td>
<td>`02_Hardware/PCB/3D/`（新增子目录）</td>
</tr>
<tr>
<td>元件 3D 模型：位于封装库目录（`*.pretty/`、`*.3dshapes/`、`Library/`、`3D/models/`），或文件名是封装名、器件型号（`SOT-23.step`、`QFN-48_7x7mm.wrl`、`USB_C_Receptacle.step`）</td>
<td>`02_Hardware/PCB/Library/3D/`（新增子目录）</td>
</tr>
<tr>
<td>外壳和结构件：文件名含外壳、壳体、上盖、下盖、面板、支架、结构、enclosure、housing、case、cover、bracket；或结构软件格式 `*.SLDPRT`、`*.SLDASM`、`*.SLDDRW`、`*.ipt`、`*.iam`、`*.idw`、`*.prt`、`*.asm`（Creo / NX，见 3.5.1）、`*.f3d`、`*.f3z`、`*.CATPart`、`*.CATProduct`、`*.3dm`、`*.igs`、`*.iges`；工程图 `*.dwg`、`*.dxf`</td>
<td>`02_Hardware/Mechanical/`（新增子目录）</td>
</tr>
<tr>
<td>3D 打印文件：`*.stl`、`*.3mf`、文本格式的 `*.obj`（见 3.5.1）</td>
<td>`02_Hardware/Mechanical/print/`</td>
</tr>
<tr>
<td>3D 渲染图、装配图、爆炸图（`*.png`、`*.jpg`、`*.pdf`），文件名含渲染、render、3D、装配、爆炸、assembly</td>
<td>跟随对应的 3D 模型：整板 → `02_Hardware/PCB/3D/`；外壳或整机 → `02_Hardware/Mechanical/`</td>
</tr>
<tr>
<td>3D PDF（PDF 中嵌入 U3D 或 PRC 模型）</td>
<td>按文件名跟随对应的 3D 模型；无法判断 → 待确认</td>
</tr>
<tr>
<td>整机装配体（同时包含 PCB 和外壳）</td>
<td>`02_Hardware/Mechanical/`，备注“含 PCB 模型”</td>
</tr>
</table>
硬件文件名没有版本号时，在映射表备注里建议重命名（如 `Main_V1.2.SchDoc`）。
#### 3.5.1 文件名无法判断的 3D 文件
STEP 是文本格式，先读取文件头和产品名称：`head -c 3000 <文件>` 查看 `FILE_NAME` 中的生成软件，`grep -ao "PRODUCT('[^']*'" <文件> | sort -u | head -40` 查看零件名称。
<table header-row="true">
<tr>
<td>特征</td>
<td>判断</td>
</tr>
<tr>
<td>生成软件是 Altium、KiCad、Cadence Allegro / OrCAD、PADS、嘉立创 EDA、Eagle / Fusion Electronics，且零件名称大量是位号（R1、C12、U3）或封装名</td>
<td>PCB 整板 3D 模型 → `02_Hardware/PCB/3D/`</td>
</tr>
<tr>
<td>生成软件是 EDA，零件只有一两个，名称是封装名或器件型号</td>
<td>元件 3D 模型 → `02_Hardware/PCB/Library/3D/`</td>
</tr>
<tr>
<td>生成软件是 SolidWorks、Inventor、Creo、NX、Fusion 360、CATIA、FreeCAD，零件名称是外壳、零件名</td>
<td>结构件 → `02_Hardware/Mechanical/`</td>
</tr>
<tr>
<td>结构软件生成，但零件中也有大量位号或 PCB 名称</td>
<td>整机装配 → `02_Hardware/Mechanical/`，备注“含 PCB 模型”</td>
</tr>
<tr>
<td>仍无法判断</td>
<td>待确认，给出 `PCB/3D/` 和 `Mechanical/` 两个选项</td>
</tr>
</table>
扩展名有歧义的文件，先用 `file <文件>` 判断是文本还是二进制：
- `.obj`：文本，且以 `v `、`vn `、`mtllib` 或 `# Blender` 等开头 → 3D 模型，放 `Mechanical/print/`；二进制 → 编译输出，不入库。
- `.asm`：文本，且含汇编指令（`AREA`、`SECTION`、`PUBLIC`、`.section`）→ 汇编源码，按 3.6 处理（启动文件放 `cmsis/`）；二进制 → Creo 装配体，放 `Mechanical/`。
- `.prt`：Creo 或 NX 零件，放 `Mechanical/`。
#### 3.5.2 大文件
3D 模型、整机装配和高清渲染图经常超过 50 MB：
- 单个文件超过 50 MB：放在规定目录，用 Git LFS 跟踪，在映射表备注“Git LFS”。回复中给出 `.gitattributes` 规则，例如 `*.step filter=lfs diff=lfs merge=lfs -text`，同样适用于 `*.stp`、`*.wrl`、`*.stl`、`*.SLDPRT`、`*.SLDASM`、`*.f3d`。
- 单个文件超过 500 MB，或团队不用 Git LFS：放网盘或 PLM 系统，在所在目录的 `README.md` 中记录文件名、版本、链接和 sha256。
- 打包交付 zip 时，超过对话附件大小上限的文件不放进 zip，在回复中列出这些文件和它们的目标位置。
### 3.6 MCU 固件源码 → `03_Firmware/`（`mcu-rtos`）
<table header-row="true">
<tr>
<td>判断条件</td>
<td>目标</td>
</tr>
<tr>
<td>`startup_*.s` / `*.S`、`system_*.c` / `.h`、`*.ld` / `*.lds` / `*.sct` / `*.icf`、器件头文件（`stm32f407xx.h`、`gd32f4xx.h`）、`*.svd`</td>
<td>`cmsis/`</td>
</tr>
<tr>
<td>厂商外设库单文件：`stm32*_hal_*.c`、`stm32*_ll_*.c`、`gd32*_<外设>.c`、`at32*_<外设>.c`、`n32*_<外设>.c`、`fsl_*.c`、`nrf_*.c`（SDK）；头注释有厂商版权</td>
<td>`hal/`</td>
</tr>
<tr>
<td>FreeRTOS：`tasks.c`、`queue.c`、`list.c`、`timers.c`、`event_groups.c`、`stream_buffer.c`、`croutine.c`、`port.c`、`portmacro.h`、`heap_1.c`–`heap_5.c`；RT-Thread、ThreadX、uC/OS 内核文件</td>
<td>`os/`</td>
</tr>
<tr>
<td>配置文件：`FreeRTOSConfig.h`、`rtconfig.h`、`tx_user.h`、`os_cfg.h`、`*_hal_conf.h`、`lwipopts.h`、`ffconf.h`、`lv_conf.h`、`sdkconfig`</td>
<td>`config/`</td>
</tr>
<tr>
<td>`version.h` 或含版本号宏的头文件；功能开关头文件（`config.h`、`app_cfg.h`）</td>
<td>合并到 `config/version.h` 和 `config/app_config.h`（版本号只保留一处）</td>
</tr>
<tr>
<td>`main.c`；`freertos.c`、`*_task.c`、`task_*.c`、`app_*.c`；含任务创建（`xTaskCreate`、`osThreadNew`、`rt_thread_create`、`tx_thread_create`、`k_thread_create`）或业务状态机</td>
<td>`app/`</td>
</tr>
<tr>
<td>界面代码：调用 `lv_` 接口创建控件的 `ui_*.c`、`screens/`、SquareLine Studio 导出文件</td>
<td>`app/ui/`</td>
</tr>
<tr>
<td>CubeMX 外设初始化：`gpio.c`、`usart.c`、`i2c.c`、`spi.c`、`tim.c`、`dma.c`、`adc.c`、`can.c`、`rtc.c`；`*_it.c`（中断服务函数）、`*_hal_msp.c`；`board.c`、`board_*.c`、`bsp_*.c`；`syscalls.c`、`sysmem.c`、`retarget.c`</td>
<td>`bsp/`</td>
</tr>
<tr>
<td>以外部器件型号命名（`bmp280.c`、`sht30.c`、`w25qxx.c`、`st7789.c`、`ssd1306.c`、`mpu6050.c`、`at24cxx.c`、`ds18b20.c`、`ws2812.c`），或内容有器件寄存器地址宏、芯片 ID、I²C 从机地址</td>
<td>`drivers/<器件名>/`（目录和文件名转成 snake_case）</td>
</tr>
<tr>
<td>与硬件无关的通用组件：`ring_buffer`、`fifo`、`crc`、`log`、`list`、`soft_timer`、`shell`、`json` 封装；内容不 include 任何 HAL、BSP 头文件</td>
<td>`middleware/utils/`</td>
</tr>
<tr>
<td>自己实现的协议解析：Modbus、自定义帧、AT 指令、MQTT 封装</td>
<td>`middleware/protocol/<协议>/`</td>
</tr>
<tr>
<td>文件名含 boot、iap、ota、bootloader；内容有跳转应用的代码（`__set_MSP`、`SCB->VTOR`、`jump_to_app`）</td>
<td>独立 Bootloader 工程放 `bootloader/`；应用侧的升级逻辑放 `middleware/ota/`</td>
</tr>
<tr>
<td>`test_*.c`、`*_test.c`、引用 `unity.h` 或 `assert.h` 且有 `main()` 的主机测试</td>
<td>`test/`</td>
</tr>
<tr>
<td>`*.uvprojx`、`*.uvproj`、`*.ewp`、`*.eww`、`*.ewd`、`*.ioc`、`.cproject`、`.project`、`platformio.ini`</td>
<td>`project/`（CMake 工程不需要）</td>
</tr>
<tr>
<td>`CMakeLists.txt`、`Makefile`</td>
<td>`03_Firmware/` 根目录（多个时合并或放对应子目录）</td>
</tr>
<tr>
<td>工具链文件 `*.cmake`；构建、烧录、调试脚本（含 `cmake`、`make`、`JLink`、`openocd`、`st-flash`、`STM32_Programmer_CLI`、`esptool`）；`*.jlink`、OpenOCD `*.cfg`</td>
<td>`scripts/`</td>
</tr>
</table>
### 3.7 Linux 固件源码 → `03_Firmware/`（`linux`）
<table header-row="true">
<tr>
<td>判断条件</td>
<td>目标</td>
</tr>
<tr>
<td>`*.patch` / `*.diff`，diff 路径含 `board/`、`cmd/`、`include/configs/`、`arch/arm/mach-` 或 `u-boot`</td>
<td>`uboot/patches/`</td>
</tr>
<tr>
<td>`*.patch` / `*.diff`，diff 路径含 `arch/arm64/boot/dts/`、`arch/arm/boot/dts/`、`drivers/`、`kernel/`、`sound/`、`net/`</td>
<td>`kernel/patches/`</td>
</tr>
<tr>
<td>Buildroot 软件包补丁（路径为 `package/<pkg>/`）</td>
<td>`rootfs/package/<pkg>/`</td>
</tr>
<tr>
<td>`*_defconfig` 或 `.config`，内容含 `CONFIG_SYS_`、`CONFIG_SPL`、`CONFIG_TARGET_`</td>
<td>`uboot/configs/<board>_defconfig`</td>
</tr>
<tr>
<td>`*_defconfig` 或 `.config`，内容含 `CONFIG_ARM64=`、`CONFIG_LOCALVERSION`、`CONFIG_MODULES=`</td>
<td>`kernel/configs/<board>_defconfig`（完整 `.config` 先用 `make savedefconfig` 精简）</td>
</tr>
<tr>
<td>`*_defconfig`，内容以 `BR2_` 开头</td>
<td>`rootfs/configs/<board>_defconfig`</td>
</tr>
<tr>
<td>`*.dts`、`*.dtsi`、`*.dtso`、设备树 overlay</td>
<td>`kernel/dts/`；U-Boot 专用的 `*-u-boot.dtsi` 做成 patch 放 `uboot/patches/`</td>
</tr>
<tr>
<td>`external.desc`、`external.mk`、顶层 `Config.in`</td>
<td>`rootfs/`</td>
</tr>
<tr>
<td>软件包目录：`Config.in`、`<pkg>.mk`、`<pkg>.hash`</td>
<td>`rootfs/package/<pkg>/`</td>
</tr>
<tr>
<td>`post-build.sh`、`post-image.sh`、`genimage.cfg`、`*.its`、分区表 `parameter.txt`</td>
<td>`rootfs/board/<board>/`（新增子目录）</td>
</tr>
<tr>
<td>`*.bb`、`*.bbappend`、`*.bbclass`、`*.inc`、`layer.conf`</td>
<td>`rootfs/meta-<board>/` 下对应的 `recipes-*/`、`classes/`、`conf/`</td>
</tr>
<tr>
<td>根文件系统里的文件：`etc/init.d/S*`、`*.service`、`*.rules`（udev）、`fstab`、`inittab`、`profile`、应用默认配置</td>
<td>`rootfs/overlay/<原路径>`</td>
</tr>
<tr>
<td>含 `module_init`、`MODULE_LICENSE` 的 `.c`，以及 `obj-m` 的 `Makefile` 或 `Kbuild`</td>
<td>`drivers/<驱动名>/`</td>
</tr>
<tr>
<td>用户态程序：有 `main()` 且使用 Linux 接口（`pthread`、`socket`、`epoll`、`open("/dev/...")`、`ioctl`、`mmap`）；Qt 工程（`*.pro`、`*.qml`）；Python / Shell 应用</td>
<td>`apps/<应用名>/src/`、`include/`；多个应用共用的头文件放 `apps/common/include/`</td>
</tr>
<tr>
<td>交叉编译的 `toolchain.cmake`、环境脚本（导出 `ARCH`、`CROSS_COMPILE`）、整机构建和打包脚本</td>
<td>`scripts/`（合并进 `env.sh`、`build_all.sh`、`pack_image.sh`）</td>
</tr>
</table>
### 3.8 工具和发布物 → `04_Tools/`、`05_Release/`
<table header-row="true">
<tr>
<td>判断条件</td>
<td>目标</td>
</tr>
<tr>
<td>烧录软件和配置：J-Flash 工程、`*.FLM`、`*.stldr`、STM32CubeProgrammer 脚本、RKDevTool、`upgrade_tool`、PhoenixSuit / LiveSuit、`uuu` / mfgtool、批量烧录脚本</td>
<td>`04_Tools/flash/`；安装包大于 10 MB 时不入 Git，在 `04_Tools/flash/README.md` 记录名称、版本和下载地址</td>
</tr>
<tr>
<td>产测程序、工装脚本、产测上位机、测试序列配置</td>
<td>`04_Tools/factory_test/`</td>
</tr>
<tr>
<td>PC 端上位机源码（`*.sln`、`*.csproj`、PC 端 Qt 工程、Python GUI）、串口助手配置</td>
<td>`04_Tools/host/`</td>
</tr>
<tr>
<td>已发布的固件或镜像：文件名带版本号（`v1.2.0`、`V1.2`、`_1_2_0`），或用户说明是正式版本；`*.bin`、`*.hex`、`*.elf`、`*.axf`、`update.img`、`*.wic`</td>
<td>`05_Release/vX.Y.Z/`；镜像大于 50 MB 用 Git LFS 或制品库</td>
</tr>
<tr>
<td>发布说明、更新日志</td>
<td>各版本说明放 `05_Release/vX.Y.Z/release_note.md`；汇总合并进 `05_Release/CHANGELOG.md`</td>
</tr>
<tr>
<td>没有版本号、来源不明的 `.bin` / `.hex`</td>
<td>待确认（问用户是正式版本、测试版本还是可以丢弃）</td>
</tr>
</table>
### 3.9 不入库
<table header-row="true">
<tr>
<td>类型</td>
<td>判断条件</td>
<td>处理</td>
</tr>
<tr>
<td>编译输出</td>
<td>`build/`、`output/`、`Objects/`、`Listings/`、`Debug/`、`Release/` 目录；`*.o`、`*.obj`（文本格式的 3D 模型除外，见 3.5.1）、`*.d`、`*.crf`、`*.lst`、`*.dep`、`*.map`（非发布版本）</td>
<td>不入库，`.gitignore` 已覆盖</td>
</tr>
<tr>
<td>IDE 和工具临时文件</td>
<td>`*.uvguix.*`、`*.uvoptx`、`JLinkLog.txt`、`JLinkSettings.ini`、`.idea/`、`.vscode/`（`settings.json` 除外）、Altium 的 `History/`、`__Previews/`、`Project Logs for */`、`*.bak`、`*-backups/`、`~$*`（Office 锁文件）、`.DS_Store`、`Thumbs.db`</td>
<td>不入库</td>
</tr>
<tr>
<td>大体积源码包和安装包</td>
<td>厂商 SDK 压缩包、内核 / Buildroot 源码包、IDE 安装包</td>
<td>不入 Git，记录下载地址和版本（`scripts/fetch_sources.sh` 或对应 `README.md`）</td>
</tr>
<tr>
<td>机密</td>
<td>`*.pem`、`*.key`、`*.p12`、签名私钥、含密码或 Token 的配置</td>
<td>不入库，提醒用户改用密钥管理或 CI 变量</td>
</tr>
</table>
### 3.10 按内容判断
扩展名不足以判断时，用沙盒工具读取内容：
<table header-row="true">
<tr>
<td>文件类型</td>
<td>读取方式</td>
<td>判断依据</td>
</tr>
<tr>
<td>PDF</td>
<td>`pdftotext -l 2 <文件> -`，看前 80 行</td>
<td>有 Datasheet、Electrical Characteristics、Ordering Information、Pin Description → Datasheets；有标题栏（Title、Rev、Sheet x of y）和大量网络名、位号（R1、C3、U2）→ Schematic；有“测试报告 / Test Report / 结论 / Pass / Fail”→ Test；有 SOP、作业步骤 → Production；有需求编号或“功能需求”→ Requirements</td>
</tr>
<tr>
<td>Word / Markdown</td>
<td>`markitdown <文件>`，看前 80 行</td>
<td>按 3.4 的关键词匹配标题和前几段</td>
</tr>
<tr>
<td>Excel / CSV</td>
<td>用 openpyxl 读取前 3 行表头</td>
<td>位号、料号、数量 → BOM；用例编号、预期结果、实际结果 → Test；引脚、GPIO、复用功能、网络名 → Design（引脚分配表）；需求编号、优先级 → Requirements</td>
</tr>
<tr>
<td>`.c` / `.h`</td>
<td>读取 `#include`、版权头和函数调用</td>
<td>按下面的分层判断顺序</td>
</tr>
<tr>
<td>`.bin` / `.hex` / `.img`</td>
<td>看文件名、大小和所在目录</td>
<td>带版本号且在发布目录 → `05_Release/`；在编译输出目录 → 不入库；其余待确认</td>
</tr>
<tr>
<td>图片</td>
<td>看文件名和所在目录</td>
<td>框图、架构、流程 → Design；测试截图、波形 → Test；实物照片 → `02_Hardware/Photos/`（新增子目录）；PCB 渲染、3D 装配图 → 按 3.5 跟随对应的 3D 模型；无法判断 → 待确认</td>
</tr>
<tr>
<td>`*.step`、`*.stp`</td>
<td>读取文件头和零件名称</td>
<td>按 3.5.1 区分整板、元件和结构件</td>
</tr>
<tr>
<td>压缩包</td>
<td>解压后按本节规则逐个判断</td>
<td>内容全部属于同一类（如 Gerber）时整体放入该目录</td>
</tr>
</table>
`.c` / `.h` 分层判断顺序（MCU）：
1. 有厂商或第三方版权头，或文件名符合 3.6 的厂商规则 → `hal/`、`cmsis/`、`os/` 或第三方目录。
2. 有 `main()` → `app/`。
3. 创建任务、处理业务流程或状态机 → `app/`。
4. 直接调用 `HAL_`、`LL_`、寄存器（`GPIOA->`、`RCC->`），或定义引脚、`MX_*_Init`、`*_IRQHandler` → `bsp/`。
5. 有器件寄存器表、器件 ID，通过总线读写器件 → `drivers/<器件名>/`。如果直接调用 `HAL_I2C_*` 等接口，备注“改为通过 bsp 提供的总线接口访问”。
6. 不 include 任何硬件相关头文件 → `middleware/`。
7. 一个文件同时承担多层职责（如 CubeMX 生成的 `main.c` 包含时钟配置、外设初始化和主循环）→ 放主要职责所在层，备注“需拆分”并写出拆分方式（如 `SystemClock_Config` 和 `MX_*_Init` 移到 `bsp/board.c`）。
### 3.11 CubeMX 工程对照表
STM32 用户的已有工程多数是 CubeMX 生成的，可以直接按下表归类：
<table header-row="true">
<tr>
<td>CubeMX 路径</td>
<td>目标</td>
<td>备注</td>
</tr>
<tr>
<td>`Core/Src/main.c`</td>
<td>`app/main.c`</td>
<td>`SystemClock_Config`、`MX_*_Init` 移到 `bsp/board.c` 的 `board_init()`</td>
</tr>
<tr>
<td>`Core/Inc/main.h`</td>
<td>`app/`</td>
<td>引脚宏移到 `bsp/board.h`</td>
</tr>
<tr>
<td>`Core/Src/freertos.c`、`app_freertos.c`</td>
<td>`app/app_tasks.c`</td>
<td>任务创建和任务函数</td>
</tr>
<tr>
<td>`Core/Src/gpio.c`、`usart.c`、`i2c.c`、`spi.c`、`tim.c`、`dma.c`、`adc.c` 等</td>
<td>`bsp/`</td>
<td></td>
</tr>
<tr>
<td>`Core/Src/stm32*_it.c`、`stm32*_hal_msp.c`</td>
<td>`bsp/`</td>
<td></td>
</tr>
<tr>
<td>`Core/Src/system_stm32*.c`</td>
<td>`cmsis/`</td>
<td></td>
</tr>
<tr>
<td>`Core/Src/syscalls.c`、`sysmem.c`</td>
<td>`bsp/`</td>
<td></td>
</tr>
<tr>
<td>`Core/Inc/stm32*_hal_conf.h`、`FreeRTOSConfig.h`</td>
<td>`config/`</td>
<td></td>
</tr>
<tr>
<td>`Core/Startup/startup_stm32*.s`、`MDK-ARM/startup_stm32*.s`</td>
<td>`cmsis/`</td>
<td></td>
</tr>
<tr>
<td>`STM32*_FLASH.ld`、`*.sct`</td>
<td>`cmsis/`</td>
<td></td>
</tr>
<tr>
<td>`Drivers/CMSIS/`</td>
<td>`cmsis/`</td>
<td>只读</td>
</tr>
<tr>
<td>`Drivers/STM32*_HAL_Driver/`</td>
<td>`hal/`</td>
<td>只读</td>
</tr>
<tr>
<td>`Middlewares/Third_Party/FreeRTOS/`</td>
<td>`os/`</td>
<td>只读</td>
</tr>
<tr>
<td>`Middlewares/Third_Party/FatFs/`、`LwIP/`</td>
<td>`middleware/fs/fatfs/`、`middleware/net/lwip/`</td>
<td>只读</td>
</tr>
<tr>
<td>`*.ioc`</td>
<td>`project/`</td>
<td>保留，用于以后重新生成初始化代码</td>
</tr>
<tr>
<td>`MDK-ARM/*.uvprojx`、`EWARM/*.ewp`</td>
<td>`project/`</td>
<td></td>
</tr>
<tr>
<td>`Debug/`、`Release/`、`MDK-ARM/Objects/`</td>
<td>不入库</td>
<td></td>
</tr>
</table>
以后还要用 CubeMX 重新生成代码时，生成结果会回到 CubeMX 的原布局。在回复中提醒用户二选一：把 CubeMX 当作参考生成器，生成后手动同步到 `bsp/`；或保留 CubeMX 工程，在 `CMakeLists.txt` 中引用它的生成目录。
### 3.12 执行原则
- 使用当前环境可用的等效读取工具；Windows 无 `head`、`file` 等命令时可用 Python 或 PowerShell 读取文件头，保持同样的判断依据。
- 只复制，不移动、不删除用户的原文件；原文件位置保持不变。
- 厂商代码和第三方库保持原文件名和内部目录结构，整目录放入目标位置。
- 用户代码的目录名和文件名转成 snake_case；文档和硬件文件保留原名。
- 目标位置已有同名文件时，不覆盖，放入“待确认”列表。
- 不在标准结构中的子目录（如 `Manual/`、`Mechanical/`、`Certification/`、`rootfs/board/`）按需新增，并在映射表备注“新增子目录”。
- 用户要求实际整理时：先用脚本生成骨架，再把文件复制到骨架中的目标位置，按 skill B.4 验证、B.5 打包。代码拆分（“需拆分”的文件）只在备注中给出建议，不擅自修改代码。
### 3.13 输出格式
1. **判断结论**：项目类型和依据（第 1 节）。
2. **统计**：每个顶层目录归入多少个文件，待确认和不入库各多少个。
3. **映射表**：按目标顶层目录分组。
<table header-row="true">
<tr>
<td>原路径</td>
<td>目标路径</td>
<td>依据</td>
<td>备注</td>
</tr>
<tr>
<td>`资料/STM32F407 数据手册.pdf`</td>
<td>`01_Docs/Datasheets/`</td>
<td>文件名含“数据手册”和芯片型号</td>
<td></td>
</tr>
<tr>
<td>`Core/Src/main.c`</td>
<td>`03_Firmware/app/main.c`</td>
<td>有 `main()`</td>
<td>含 `MX_GPIO_Init`，需拆分到 `bsp/`</td>
</tr>
<tr>
<td>`Core/Src/bmp280.c`</td>
<td>`03_Firmware/drivers/bmp280/bmp280.c`</td>
<td>以器件型号命名，有寄存器地址宏</td>
<td>直接调用 `HAL_I2C_Mem_Read`，改为通过 bsp 接口</td>
</tr>
<tr>
<td>`硬件/MainBoard_V1.2.step`</td>
<td>`02_Hardware/PCB/3D/MainBoard_V1.2.step`</td>
<td>与 PCB 工程同名，文件头生成软件为 Altium</td>
<td>120 MB，用 Git LFS</td>
</tr>
<tr>
<td>`结构/上盖.SLDPRT`</td>
<td>`02_Hardware/Mechanical/上盖.SLDPRT`</td>
<td>文件名含“上盖”，SolidWorks 格式</td>
<td></td>
</tr>
<tr>
<td>`MDK-ARM/Objects/`</td>
<td>不入库</td>
<td>编译输出</td>
<td></td>
</tr>
</table>
1. **待确认**：每项给出最可能的两个位置，用 当前环境可用的提问工具或直接向用户提问 一次问完。
2. **不入库清单**：文件和原因。
3. **后续建议**：需要拆分的文件、建议重命名的硬件文件、需要记录下载地址的大文件。
