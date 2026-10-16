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
