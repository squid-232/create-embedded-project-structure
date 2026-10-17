# 嵌入式项目结构生成 Skill

简体中文 | [English](README.md)

为 **MCU + RTOS** 和 **嵌入式 Linux** 项目提供可复用的 Codex 技能与独立 Python 生成器。根据项目需求生成统一的目录结构、分层固件骨架和研发工作流。

## 功能

- 支持 MCU 的 CMake、Keil、IAR 工程结构，以及 FreeRTOS、RT-Thread 约定。
- 支持 Linux 的 Buildroot、Yocto 结构，包含用户态应用和树外驱动模板。
- 输出项目文件夹与 ZIP，生成的项目文档支持中文和英文。
- 提供 debug / release / factory 构建约定、主机端测试和代码检查脚本。
- 提供 GitHub Actions / GitLab CI 模板、协作规范、需求和测试报告模板。
- 提供架构分层、EVT / DVT / PVT / MP 就绪要求、发布归档流程，可选生成 Notion 规范页面。

骨架需要补充厂商源码、板级配置和业务实现才能用于硬件。Linux 的源码获取和整机镜像构建脚本需要按厂商 BSP 补全。

## v2 新增能力

本次 skill 包版本为 **2.0.0**。Python 骨架生成器仍为 **v2.0**，与上一版完全相同；以下新增能力由技能指令和参考规则提供，不是新增的 Python 自动分类命令。

- **自动识别项目类型**：结合芯片、RTOS、工程文件、启动文件、设备树和 defconfig 判断 MCU / Linux；支持多固件和异构 SoC，避免把 ESP32-P4 当成 Linux、把 STM32MP 当成普通 MCU。
- **识别所需输出**：在目录树、骨架 ZIP、Notion 规范、研发流程之外，增加已有资料归档模式。
- **资料归档与迁移映射**：为文档、硬件、源码、工具和发布文件输出“原路径 → 目标路径 → 判断依据 → 备注”，支持 CubeMX 工程和厂商 SDK 整目录处理。
- **更细的硬件分类**：原理图进入 `02_Hardware/Schematic/`；整板 3D 进入 `PCB/3D/`；元件模型进入 `PCB/Library/3D/`；外壳和整机装配进入 `Mechanical/`；3D 打印模型进入 `Mechanical/print/`（后四项均位于 `02_Hardware/` 下）。
- **内容辅助识别**：名称不清楚时读取 STEP 文件头、生成软件和零件名，区分 `.obj` 的模型与编译产物、`.asm` 的汇编源码与 CAD 装配。
- **归档保护与大文件约定**：默认给映射表；用户明确要求实际整理时只复制，保留原文件、不覆盖冲突文件、保留厂商目录结构。超过 50 MB 建议 Git LFS，超过 500 MB 或不用 LFS 时建议外部存储并记录链接和 SHA-256。仅归档文档和硬件时无需先确定 MCU / Linux 类型。

这些是代理执行时的判断规则，不保证仅凭扩展名就能确定所有文件；无法确认的项目会列入待确认清单。生成器本身仍只生成工程骨架。

示例：

```text
$create-embedded-project-structure
分析当前文件夹中的原理图、PCB、STEP 模型、手册和示例工程，
先给出分类映射表和待确认清单。
```

需要实际复制整理时，在请求中明确写明目标目录和“按映射表复制整理，保留原文件”。

## 环境要求

- **Python 3.12+**；生成器仅依赖标准库。
- 对话式技能需要 Codex；Python 生成器可以独立使用。
- MCU 主机端检查需要 Bash、GCC、cppcheck、clang-format 18；Linux 主机测试还需要 CMake。
- Windows 可以直接用 Python 生成文件；生成的 Shell 检查脚本需在合适的 Bash / WSL 环境运行。
- Notion MCP 仅在需要写入 Notion 页面时使用。

当前技能正文和参考文档使用中文；仓库介绍和生成的项目文档支持中英文。

## 安装技能

```bash
git clone https://github.com/squid-232/create-embedded-project-structure.git
```

将仓库内 `skills/create-embedded-project-structure/` 完整复制到目标项目的 `.agents/skills/`，保留其中的 `scripts/` 和 `references/`。

在仓库根目录执行 PowerShell 示例：

```powershell
New-Item -ItemType Directory -Force 'C:\path\to\project\.agents\skills'
Copy-Item -Recurse 'skills\create-embedded-project-structure' 'C:\path\to\project\.agents\skills\'
```

下一轮 Codex 对话中调用：

```text
$create-embedded-project-structure
为 SmartSensor 创建 STM32F407 + FreeRTOS 工程，使用 CMake，
包含 BMP280 驱动、GitHub CI 和中文文档，输出骨架 ZIP。
```

## 独立运行生成器

在仓库根目录执行：

```bash
# MCU + RTOS
python skills/create-embedded-project-structure/scripts/gen_embedded_skeleton.py --name SmartSensor --type mcu-rtos --chip STM32F407 --rtos FreeRTOS --build cmake --drivers bmp280,st7789 --bootloader --ci github --lang zh --out ./out

# 嵌入式 Linux
python skills/create-embedded-project-structure/scripts/gen_embedded_skeleton.py --name EdgeGateway --type linux --soc RK3568 --rootfs buildroot --apps gateway,webui --ci github --lang zh --out ./out
```

生成结果为 `out/<Name>/` 和 `out/<Name>.zip`。建议使用新项目名或空输出目录，避免覆盖同名模板文件。

| 参数 | 用途 |
| --- | --- |
| `--name`、`--type` | 必填；类型为 `mcu-rtos` 或 `linux` |
| `--lang zh\|en` | 生成文档语言，默认中文 |
| `--ci gitlab\|github\|none` | CI 类型，默认 GitLab |
| `--build cmake\|keil\|iar` | MCU 构建结构，默认 CMake |
| `--rootfs buildroot\|yocto` | Linux 根文件系统结构 |
| `--minimal` | 跳过研发工作流文件，保留测试和适用的构建、打包脚本 |
| `--no-zip` | 仅生成文件夹 |
| `--help` | 查看全部参数 |

## 生成目录

```text
ProjectName/
├── 01_Docs/
├── 02_Hardware/
├── 03_Firmware/
├── 04_Tools/
├── 05_Release/
├── CONTRIBUTING.md
└── README.md
```

MCU 分层遵循 `app → middleware → drivers → bsp → hal/cmsis`，厂商代码与应用代码分开。Linux 工程保存配置、补丁和设备树，通过获取脚本引入完整厂商源码。

## 验证

在 Linux 环境运行生成器内置的六组配置检查：

```bash
CI=1 python skills/create-embedded-project-structure/scripts/gen_embedded_skeleton.py --selftest
```

先安装所需工具。`CI=1` 会使质量检查在工具缺失时报错，避免把跳过当作通过。这些检查在主机端运行；交叉编译、烧录和板级验证需另行完成。

## 参与贡献

见 [CONTRIBUTING.md](CONTRIBUTING.md)。修改时保持生成路径、参考文档和技能行为一致；提交问题请附 Python 版本、执行命令和可复现的错误。

## 许可证

采用 [MIT 许可证](LICENSE)。加入生成项目的第三方 SDK、RTOS 内核和库遵循各自的许可证。
