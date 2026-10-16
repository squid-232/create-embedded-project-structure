# 研发工作流参考


研发流程的阶段、交付物、日常开发闭环和发布流程。生成的骨架已经内置这些约定（`CONTRIBUTING.md`、CI 配置、文档模板、`scripts/`）；输出规范时引用骨架里的文件和命令，不要另起一套。
## 项目阶段与交付物
<table header-row="true">
<tr>
<td>阶段</td>
<td>主要工作</td>
<td>交付物</td>
<td>存放位置</td>
</tr>
<tr>
<td>1. 需求分析</td>
<td>功能、性能、功耗、成本、认证和环境约束；每条需求编号 REQ-xxx</td>
<td>SRS、需求评审记录</td>
<td>`01_Docs/Requirements/`（`SRS_template.md`）、`01_Docs/Meeting/`</td>
</tr>
<tr>
<td>2. 方案与选型</td>
<td>芯片或平台对比、RTOS / Linux 选型、系统框图、风险评估</td>
<td>选型报告、系统框图</td>
<td>`01_Docs/Design/`、`01_Docs/Datasheets/`</td>
</tr>
<tr>
<td>3. 软硬件协同设计</td>
<td>引脚分配、电源和时钟树、通信接口；软件参加原理图评审</td>
<td>引脚分配表、接口定义、评审意见</td>
<td>`01_Docs/Design/`、`02_Hardware/`</td>
</tr>
<tr>
<td>4. 软件架构</td>
<td>分层、任务划分、Flash / RAM 分区、启动流程、OTA 方案</td>
<td>架构文档、`flash_layout.md`、任务列表</td>
<td>`01_Docs/Design/`</td>
</tr>
<tr>
<td>5. 驱动与 BSP</td>
<td>时钟、GPIO、调试串口、外设驱动、Bootloader；Linux 为 U-Boot、内核、设备树</td>
<td>`bsp/`、`drivers/` 代码和驱动测试记录</td>
<td>`03_Firmware/`</td>
</tr>
<tr>
<td>6. 中间件与业务</td>
<td>协议栈、文件系统、状态机、业务任务</td>
<td>`middleware/`、`app/` 代码和单元测试</td>
<td>`03_Firmware/`</td>
</tr>
<tr>
<td>7. 调试与验证</td>
<td>板级调试、功能验证、问题定位（J-Link、逻辑分析仪、示波器）</td>
<td>调试记录、问题单</td>
<td>`01_Docs/Test/`</td>
</tr>
<tr>
<td>8. 集成与系统测试</td>
<td>功能、稳定性、压力、老化、功耗、EMC 预测试，随 EVT / DVT / PVT 推进</td>
<td>测试报告（`test_report_template.md`）</td>
<td>`01_Docs/Test/`</td>
</tr>
<tr>
<td>9. 量产与发布</td>
<td>产测固件、烧录方案、量产 SOP、发布包归档</td>
<td>factory 固件、烧录工具、SOP、发布包</td>
<td>`04_Tools/`、`01_Docs/Production/`、`05_Release/vX.Y.Z/`</td>
</tr>
<tr>
<td>10. 维护迭代</td>
<td>现场问题、OTA 升级、需求变更</td>
<td>补丁版本、CHANGELOG</td>
<td>`hotfix/*` 分支、`05_Release/CHANGELOG.md`</td>
</tr>
</table>
## 硬件阶段与固件就绪
<table header-row="true">
<tr>
<td>硬件阶段</td>
<td>目标</td>
<td>固件需要具备</td>
</tr>
<tr>
<td>EVT（工程验证）</td>
<td>验证原理图和关键器件</td>
<td>板级 bring-up：时钟、调试串口、各外设驱动可用；硬件测试固件</td>
</tr>
<tr>
<td>DVT（设计验证）</td>
<td>验证完整功能和可靠性</td>
<td>功能完整，能跑系统测试、老化和 EMC 预测试；严重问题清零</td>
</tr>
<tr>
<td>PVT（生产验证）</td>
<td>验证产线和良率</td>
<td>冻结的 release 固件、factory 产测固件、烧录和校准流程</td>
</tr>
<tr>
<td>MP（量产）</td>
<td>批量生产</td>
<td>`05_Release/vX.Y.Z/` 中带 `sha256sum.txt` 的发布包；OTA 和返修方案</td>
</tr>
</table>
## 日常开发闭环
每个任务按以下顺序完成。命令在 `03_Firmware/` 下执行，骨架的 `CONTRIBUTING.md` 有同样的表。
1. 拆解任务：每个任务对应 REQ-xxx 或 Issue。
2. 拉分支：`git checkout -b feature/REQ-012-uart-dma develop`。
3. 设计：接口、数据流、时序；改接口前先改 `01_Docs/Design/` 中的文档。
4. 编码：遵守分层规则和命名规范。
5. 静态检查：`scripts/check.sh`（cppcheck + clang-format，跳过厂商代码；`--fix` 自动格式化）。要求 MISRA 时，在 CI 中增加 MISRA 检查工具，如 PC-lint Plus、Polyspace 或 cppcheck 的 misra 插件。
6. 单元测试：`scripts/run_tests.sh`。MCU 用主机 gcc 编译运行 `test/test_*.c`；Linux 在主机上编译 apps 并运行 ctest。
7. 板级验证：`scripts/build.sh debug && scripts/flash.sh`；Keil / IAR 在 IDE 中编译 Debug 目标并下载。
8. 合并请求：按 MR / PR 模板自检，至少一人 Code Review。
9. 合并：CI 全部通过后合并到 develop。
10. 文档：更新 README、接口文档和 CHANGELOG 的 Unreleased 部分。
## 贯穿始终的工程实践
<table header-row="true">
<tr>
<td>实践</td>
<td>约定</td>
<td>骨架中的位置</td>
</tr>
<tr>
<td>分支模型</td>
<td>main 只放发布版本；develop 用于集成；另有 feature/REQ-xxx-desc、release/vX.Y.Z、hotfix/vX.Y.Z</td>
<td>`CONTRIBUTING.md`</td>
</tr>
<tr>
<td>提交信息</td>
<td>`<type>(<scope>): <subject> [REQ-xxx]`；type 取 feat、fix、docs、refactor、test、perf、build、ci、chore</td>
<td>`CONTRIBUTING.md`</td>
</tr>
<tr>
<td>版本号</td>
<td>MAJOR.MINOR.PATCH 只在 `version.h` 定义；tag 用 `vX.Y.Z`，CI 校验 tag 与 `version.h` 一致</td>
<td>`version.h`、CI 的 version-tag-check</td>
</tr>
<tr>
<td>配置</td>
<td>功能开关、日志等级、构建变体集中在 `app_config.h`</td>
<td>`config/app_config.h`</td>
</tr>
<tr>
<td>构建变体</td>
<td>debug：-O0 -g，日志等级 4；release：-Os、NDEBUG，日志等级 2；factory：release + `CFG_FACTORY_MODE=1`，日志等级 3</td>
<td>`scripts/build.sh`；Keil / IAR 建三个 Target</td>
</tr>
<tr>
<td>代码质量</td>
<td>本地和 CI 运行同一套脚本；`.clang-format` 统一格式，厂商目录关闭格式化</td>
<td>`scripts/check.sh`、`.clang-format`、`.editorconfig`</td>
</tr>
<tr>
<td>CI</td>
<td>static-check → unit-test → firmware-build；`cmsis/` 中有链接脚本后自动启用构建。Keil / IAR 和 Linux 整机构建需要专用 runner</td>
<td>`.gitlab-ci.yml` 或 `.github/workflows/ci.yml`</td>
</tr>
<tr>
<td>文档体系</td>
<td>需求、设计、测试、生产文档分目录存放，模板随骨架生成</td>
<td>`01_Docs/`</td>
</tr>
<tr>
<td>可追溯性</td>
<td>REQ-xxx → 分支名和提交信息 → 测试用例 TC-xxx → 测试报告；每条需求至少一个用例</td>
<td>SRS 和测试报告模板</td>
</tr>
</table>
## 发布流程
1. 从 develop 拉 `release/vX.Y.Z`，只做 bug 修复和版本号修改。
2. 修改 `version.h`；把 CHANGELOG 中 Unreleased 的内容移到新版本标题下。
3. 构建并归档到 `05_Release/vX.Y.Z/`（产物、`sha256sum.txt`、`release_note.md`），命令见下表。
4. 完成发布测试，测试报告放 `01_Docs/Test/`。
5. 合并到 main 并打 tag `vX.Y.Z`，再合并回 develop。
<table header-row="true">
<tr>
<td>项目类型</td>
<td>构建并归档</td>
</tr>
<tr>
<td>MCU（CMake）</td>
<td>`scripts/build.sh release && scripts/pack.sh release`；产测固件再运行 `scripts/build.sh factory && scripts/pack.sh factory`</td>
</tr>
<tr>
<td>MCU（Keil / IAR）</td>
<td>在 IDE 中编译 Release 目标，再运行 `scripts/pack.sh release <IDE 输出目录>`</td>
</tr>
<tr>
<td>Linux</td>
<td>`scripts/build_all.sh && scripts/pack_image.sh`；镜像体积大，用 Git LFS 或制品库保存</td>
</tr>
</table>
