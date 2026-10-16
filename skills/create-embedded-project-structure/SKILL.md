---
name: create-embedded-project-structure
description: "为嵌入式项目（MCU + RTOS、嵌入式 Linux）设计标准化的项目结构、工程结构和研发工作流。可以：(1) 根据项目信息生成定制化目录树和说明；(2) 用脚本生成可直接使用的项目骨架 zip：分层模板代码、CMake 或 Buildroot / Yocto 配置、debug / release / factory 构建脚本、主机端单元测试、cppcheck 和 clang-format 检查脚本、GitLab 或 GitHub CI、开发协作规范以及需求和测试报告模板；(3) 在 Notion 中生成项目结构规范页面；(4) 输出研发工作流规范：项目阶段与交付物、EVT / DVT / PVT、日常开发闭环、分支与提交规范、发布流程。用户提到嵌入式、单片机、STM32 / ESP32 / GD32、FreeRTOS / RT-Thread、嵌入式 Linux、RK / 全志 / NXP iMX6 / iMX8、Buildroot / Yocto 项目的目录结构、工程结构、项目模板、项目骨架、代码分层、新建工程、工程规范化、研发流程、开发规范、CI、代码检查、单元测试、版本发布或项目规范文档时使用。"
---


为嵌入式项目生成标准化的项目结构、工程结构和研发工作流。支持两种项目类型：**MCU + RTOS**、**嵌入式 Linux**；支持四种输出：定制化目录树 + 说明、项目骨架 zip、Notion 规范页面、研发工作流规范。
## 参考子页面（按需读取）
- [MCU + RTOS 结构参考](references/mcu-rtos.md)：项目类型为 MCU / 单片机 / RTOS 时必读。
- [嵌入式 Linux 结构参考](references/embedded-linux.md)：项目类型为 Linux / SoC / BSP 时必读。
- [研发工作流参考](references/development-workflow.md)：输出研发工作流规范，回答研发流程、开发规范、CI、代码检查、EVT / DVT / PVT 相关问题，或 Notion 页面需要“研发流程与交付物”章节时读取。
- [Notion 规范页面模板](references/notion-page-template.md)：输出 Notion 页面时读取。
参考资料已随本技能安装在 `references/`，按需读取对应的本地文件。
## 1. 收集输入
缺少的必要信息用当前环境可用的提问工具或直接向用户一次问完；有默认值的不要追问，直接使用并在最终回复里说明。
<table header-row="true">
<tr>
<td>输入</td>
<td>说明</td>
<td>默认值</td>
</tr>
<tr>
<td>项目名</td>
<td>英文 PascalCase，只能用字母、数字、`_`、`-`；中文名称写进描述</td>
<td>必填（例程模式除外）</td>
</tr>
<tr>
<td>一句话描述</td>
<td>写进 README</td>
<td>空</td>
</tr>
<tr>
<td>项目类型</td>
<td>`mcu-rtos` / `linux`</td>
<td>必填（例程模式默认 `mcu-rtos`）</td>
</tr>
<tr>
<td>输出方式</td>
<td>目录树说明 / zip / Notion 页面 / 研发工作流规范，可多选</td>
<td>目录树说明</td>
</tr>
<tr>
<td>MCU：芯片 / RTOS / 构建方式</td>
<td>构建方式 `cmake` / `keil` / `iar`</td>
<td>STM32F407 / FreeRTOS / cmake</td>
</tr>
<tr>
<td>MCU：是否需要 Bootloader / OTA</td>
<td>需要时加 `bootloader/` 和 Flash 分区文档</td>
<td>否</td>
</tr>
<tr>
<td>MCU：外部器件驱动</td>
<td>如 bmp280, st7789, w25qxx</td>
<td>无</td>
</tr>
<tr>
<td>Linux：SoC / rootfs</td>
<td>rootfs `buildroot` / `yocto`</td>
<td>RK3568 / buildroot</td>
</tr>
<tr>
<td>Linux：用户态应用、内核驱动</td>
<td>逗号分隔的名称</td>
<td>`main_app` / 无</td>
</tr>
<tr>
<td>功能特性</td>
<td>如 BLE、MQTT、LVGL、文件系统、Modbus</td>
<td>无</td>
</tr>
<tr>
<td>代码托管 / CI</td>
<td>GitLab / GitHub / 不需要</td>
<td>GitLab</td>
</tr>
<tr>
<td>文档语言</td>
<td>中文 / 英文；代码注释始终用英文</td>
<td>跟随用户的语言</td>
</tr>
</table>
**例程模式**：用户说“没有项目”“仅作例程 / 模板 / 示例”时，不要追问项目信息，直接使用默认值：没指定类型时用 `mcu-rtos`；项目名 `McuRtosTemplate`（mcu-rtos）或 `LinuxBspTemplate`（linux）；不加 Bootloader 和驱动；其余参数取上表默认值。回复里列出这些默认值，说明换成真实项目时用户需要提供哪些信息，并告诉用户也可以生成另一种类型的例程。
## 2. 核心规则（所有输出都必须遵守）
- 顶层固定为 `01_Docs/ 02_Hardware/ 03_Firmware/ 04_Tools/ 05_Release/ README.md .gitignore`，编号前缀保持顺序；研发工作流文件 `CONTRIBUTING.md`、CI 配置（`.gitlab-ci.yml` + `.gitlab/` MR 模板；GitHub 为 `.github/`）、`.editorconfig` 也放在根目录。
- 分层调用只能自上而下：`app → middleware → drivers → bsp → hal/cmsis`。下层通知上层只用回调，禁止 include 上层头文件。
- 只有 `bsp/` 知道板级细节（引脚、时钟）。换板只改 bsp；换芯片只改 bsp + hal。
- 厂商代码（`hal/`、`cmsis/`、`os/`）只读。Linux 的 U-Boot / 内核源码不进仓库，只提交 `patches/`、`configs/`、`dts/`。
- 版本号只在 `version.h` 定义一次；Git tag 用 `vX.Y.Z`；正式固件用 `pack.sh` 归档到 `05_Release/vX.Y.Z/`，并更新 `CHANGELOG.md`。
- 编译输出（`build/`、`output/`）加入 `.gitignore`。
- 命名：文件和函数用 snake_case（`模块_动作()`），宏全大写，全局变量加 `g_` 前缀，静态变量加 `s_` 前缀；每个模块一对 `.c/.h`，内部函数加 `static`。
- 只放与需求相关的目录：没有 OTA 就不要 `bootloader/`；有 MQTT 就加 `middleware/protocol/mqtt/`。功能特性和目录的对应关系见参考子页面。
研发工作流规则：
- 本地和 CI 运行同一套脚本：`scripts/check.sh`（静态检查 + 格式检查）、`scripts/run_tests.sh`（主机端单元测试）、`scripts/build.sh`（构建）。不要在 CI 里另写一套命令。
- 静态检查和格式化只覆盖自己的代码，跳过 `hal/`、`cmsis/`、`os/` 和带 LICENSE 的第三方目录。
- 固件分 debug / release / factory 三种构建变体，用 `app_config.h` 中的 `CFG_FACTORY_MODE` 和 `CFG_LOG_LEVEL` 区分。
- 需求编号 REQ-xxx 贯穿分支名、提交信息、测试用例和测试报告。
## 3. 按输出方式执行
### A. 定制化目录树 + 说明
1. 读取对应类型的参考子页面。
2. 输出一个代码块目录树，每个目录后用 `# 注释` 说明用途；只展开到有意义的层级。
3. 目录树后依次给出：分层调用示意图、本项目定制点（新增或删除了哪些目录、原因）、命名与 Git 规范（简表）。
4. 不要贴模板代码全文。
### B. 项目骨架 zip
1. 使用随技能安装的 `scripts/gen_embedded_skeleton.py`（v2.0，只依赖 Python 标准库，需要 Python 3.12 或更新版本）。将下文 `/data/skill/gen_embedded_skeleton.py` 替换为本技能脚本的实际绝对路径，将 `/data/out` 替换为用户指定的项目输出目录；Windows 可通过 `load_workspace_dependencies` 查找随 Codex 提供的 Python 3.12，执行 `.sh` 检查需使用可用的 Bash / WSL 环境。
1. 运行脚本：
```bash
# MCU + RTOS（中文文档，GitLab CI）
python3 /data/skill/gen_embedded_skeleton.py --name SmartSensor --type mcu-rtos \
  --desc "温湿度采集节点" --chip STM32F407 --rtos FreeRTOS --build cmake \
  --drivers bmp280,st7789 --bootloader --out /data/out

# 嵌入式 Linux（GitHub Actions）
python3 /data/skill/gen_embedded_skeleton.py --name EdgeGateway --type linux \
  --soc RK3568 --rootfs buildroot --apps gateway,webui --drivers mydev --ci github --out /data/out
```
<table header-row="true">
<tr>
<td>参数</td>
<td>适用类型</td>
<td>说明</td>
</tr>
<tr>
<td>`--name` `--type`</td>
<td>全部</td>
<td>必填；`--type` 取 `mcu-rtos` 或 `linux`</td>
</tr>
<tr>
<td>`--desc` `--out` `--drivers`</td>
<td>全部</td>
<td>描述、输出目录、驱动列表（名称自动转成 snake_case）</td>
</tr>
<tr>
<td>`--lang`</td>
<td>全部</td>
<td>文档语言：`zh`（默认）或 `en`</td>
</tr>
<tr>
<td>`--ci`</td>
<td>全部</td>
<td>`gitlab`（默认）、`github` 或 `none`</td>
</tr>
<tr>
<td>`--minimal`</td>
<td>全部</td>
<td>不生成下表前五行的研发工作流文件（包括 `check.sh`、`.clang-format` 和文档模板）；`run_tests.sh`、构建和打包脚本、构建变体保留</td>
</tr>
<tr>
<td>`--chip` `--rtos` `--build` `--bootloader`</td>
<td>mcu-rtos</td>
<td>`--build` 取 cmake / keil / iar；keil、iar 生成 `project/`，没有 CMakeLists 和 `build.sh`</td>
</tr>
<tr>
<td>`--soc` `--rootfs` `--apps`</td>
<td>linux</td>
<td>`--rootfs` 取 buildroot（BR2_EXTERNAL 树）或 yocto（meta 层）</td>
</tr>
<tr>
<td>`--no-zip`</td>
<td>全部</td>
<td>只生成文件夹，不打包</td>
</tr>
<tr>
<td>`--selftest`</td>
<td>维护脚本</td>
<td>修改脚本模板后运行：生成所有参数组合，并执行测试和检查</td>
</tr>
</table>
除了目录和模板代码，脚本还会生成以下研发工作流文件：
<table header-row="true">
<tr>
<td>文件</td>
<td>作用</td>
</tr>
<tr>
<td>`CONTRIBUTING.md`</td>
<td>日常开发闭环、分支模型、提交格式、MR 自检清单、构建变体、发布流程、可追溯性</td>
</tr>
<tr>
<td>CI 配置：`.gitlab-ci.yml` 或 `.github/workflows/ci.yml`</td>
<td>static-check → unit-test → firmware-build；`cmsis/` 中有链接脚本后才启用固件构建；打 tag 时校验 tag 与 `version.h` 一致</td>
</tr>
<tr>
<td>MR / PR 模板</td>
<td>关联需求 + 自检清单</td>
</tr>
<tr>
<td>`SRS_template.md`、`test_report_template.md`</td>
<td>需求和测试报告模板，REQ 与 TC 一一对应</td>
</tr>
<tr>
<td>`.editorconfig`、`.clang-format`、`scripts/check.sh`</td>
<td>编码和缩进、代码格式、cppcheck + clang-format 检查；厂商目录关闭格式化</td>
</tr>
<tr>
<td>`scripts/run_tests.sh`、`build.sh`、`pack.sh`（Linux 为 `pack_image.sh`）</td>
<td>主机端单元测试、三种变体构建、归档到 `05_Release/vX.Y.Z/`</td>
</tr>
</table>
1. 脚本只生成通用骨架。用户的功能特性需要的额外目录或文件（如 `middleware/protocol/mqtt/`），在生成的文件夹里补上；先不打包，验证通过后按第 5 步重新打包。
2. 验证（必须做）。先确认工具：`command -v gcc cppcheck clang-format`（Linux 项目再加 `cmake`），缺少的先安装：`sudo dnf install -y cppcheck cmake`、`pip install 'clang-format==18.1.*'`（与 CI 镜像 ubuntu:24.04 的 clang-format 18 一致）。然后运行：
```bash
cd /data/out/<Name>/03_Firmware
./scripts/check.sh --fix     # 只在第 3 步补过或改过 .c/.h 时运行
./scripts/run_tests.sh       # 必须通过
CI=1 ./scripts/check.sh      # 必须通过；CI=1 时缺工具直接报错，不会跳过
```
不加 `CI=1` 时，缺工具只输出 `WARN … skipped`，最后仍显示 `[check] OK`，不能算通过。用了 `--minimal` 时没有 `check.sh`，只运行 `run_tests.sh`。工具确实装不上时，在回复里写明哪项没有检查。沙盒没有 arm-none-eabi-gcc，不要尝试交叉编译固件。
1. 打包：第 3 步改过文件时重新打包，并排除测试生成的构建输出（`-D` 不写目录条目，与脚本生成的 zip 一致）。没改过文件时直接用脚本生成的 zip：它在测试之前生成，不含构建输出。
```bash
cd /data/out && rm -f <Name>.zip
zip -rqD <Name>.zip <Name> -x '*/03_Firmware/build/*' '*/03_Firmware/output/host-test/*'
```
1. 将 zip 保存到用户可访问的位置，并用当前环境支持的本地文件链接或附件交付给用户，回复内容见第 4 节。下一步写给用户：把厂商 HAL 放进 `hal/`，RTOS 源码放进 `os/`，RTOS 配置文件（如 `FreeRTOSConfig.h`、`rtconfig.h`）放进 `config/`，启动文件和链接脚本放进 `cmsis/`（之后 CI 的固件构建会自动启用）；Linux 项目补全 `fetch_sources.sh` 和 `build_all.sh`。
### C. Notion 规范页面
1. 读取“Notion 规范页面模板”子页面，按其章节结构生成页面。
2. 用户没指定位置时，用当前环境可用的提问工具或直接询问父页面或 teamspace。用户跳过或拒绝时，建在用户的私有页面顶层（parent 类型为 `user`），并在回复里说明可以移动。
3. 同时生成了 zip 时，使用当前 Notion MCP 支持的上传和 file 块接口把 zip 附在页面里；若不支持本地文件上传，交付本地 zip 链接并说明页面附件尚未上传，并在开头的 callout 注明骨架版本。创建后重新加载页面，确认附件存在。
4. 文件名、路径、命令一律用行内代码（如 `SmartSensor.zip`），否则 Notion 会把它们自动识别成网址。
### D. 研发工作流规范
1. 读取“研发工作流参考”子页面。
2. 按用户项目裁剪，以下两项完整给出：项目阶段与交付物（标出项目当前所处阶段；例程模式标为“从阶段 1 开始”）、硬件阶段与固件就绪（EVT / DVT / PVT / MP）。
3. 日常开发闭环、分支与提交规范、构建变体、CI 流水线、发布流程：同时生成了 zip 时，这些已经写在骨架的 `CONTRIBUTING.md` 和 CI 文件里，只给出文件位置和关键命令，不要重复贴全文；没有 zip 时按参考子页面完整给出，命令换成本项目的。
4. 同时生成 Notion 页面时，把以上内容写成页面的“研发流程与交付物”章节，回复里只给出页面位置。
## 4. 最终回复格式
按输出方式依次分节，用户没选的输出不写：
1. **标准目录结构**：目录树代码块、分层调用、本项目定制点、命名与 Git 简表。
2. **项目骨架 zip**：zip 文件块、包含的内容、验证结果（`run_tests.sh` 和 `check.sh` 是否通过、zip 文件数）、下一步。已经输出第 1 节目录树时不再附树，只列出目录树之外的关键文件；没有第 1 节时附两层目录树（根目录 + 一级子目录）。
3. **Notion 页面**：页面链接、所在位置、包含的章节。
4. **研发工作流**：按 D 的第 2–4 步输出。
最后用一个简短列表说明用了哪些默认值，以及换成真实项目时用户需要提供哪些信息（如项目名、芯片或 SoC、构建方式、外部器件、功能特性）。
## 5. 特殊情况
- **MCU 裸机**：按 mcu-rtos 生成，然后删除 `os/`，把 `app_tasks.c` 改成超级循环（`while(1)` + 定时器、状态机），并删掉 `app_config.h` 里的任务栈和优先级配置。
- **多固件（Bootloader + App、主从 MCU、Linux + MCU 协处理器）**：在 `03_Firmware/` 下按固件并列放置（如 `03_Firmware/boot/`、`03_Firmware/app/`，或 `03_Firmware/linux/`、`03_Firmware/mcu/`），共享代码放 `03_Firmware/common/`。可以分别运行脚本再手动合并，合并后同步修改 CI 和 `CONTRIBUTING.md` 中的路径。
- **Keil / IAR**：没有 `build.sh`，在 IDE 中建 Debug / Release / Factory 三个 Target；CI 的固件构建需要装了 IDE 的 Windows runner（CI 文件里有注释模板）；归档用 `scripts/pack.sh release <IDE 输出目录>`。
- **已有工程要规范化**：先列出现有结构，输出“旧路径 → 新路径”的迁移映射表和迁移步骤，不要直接删除用户文件。
- **用户已有团队规范或 CI**：用户的规范优先，本 skill 的规则只补充未覆盖的部分；生成骨架时用 `--minimal` 或 `--ci none`，避免和现有流程冲突。
