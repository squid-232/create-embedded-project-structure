#!/usr/bin/env python3
"""Generate a standardized embedded project skeleton (MCU+RTOS or embedded Linux) and zip it.

Usage examples:
  python3 gen_embedded_skeleton.py --name SmartSensor --type mcu-rtos \\
      --chip STM32F407 --rtos FreeRTOS --drivers bmp280,st7789 --bootloader --out /data/out
  python3 gen_embedded_skeleton.py --name EdgeGateway --type linux \\
      --soc RK3568 --rootfs buildroot --apps gateway,webui --drivers mydev --ci github --out /data/out

Besides directories and code templates it generates the R&D workflow files: CONTRIBUTING.md,
CI config (GitLab / GitHub), MR/PR template, SRS and test report templates, .editorconfig,
.clang-format and scripts/check.sh. --minimal skips these workflow files.
scripts/run_tests.sh and (MCU) scripts/pack.sh plus debug/release/factory builds are always generated.
Docs are Chinese by default (--lang en for English); code comments are always English.

Only uses the Python standard library. Prints the generated tree and the zip path.
After editing any template run:  python3 gen_embedded_skeleton.py --selftest
"""
import argparse, datetime, os, re, shutil, subprocess, sys, tempfile, zipfile

GENERATOR_VERSION = "2.0"
TODAY = datetime.date.today().isoformat()


def ident(s):
    s = re.sub(r"[^0-9a-zA-Z_]", "_", s.strip()).lower()
    return ("m_" + s) if s[:1].isdigit() else s


def split_list(v):
    return [ident(x) for x in (v or "").split(",") if x.strip()]


def L(a, zh, en):
    """Doc text in the --lang language."""
    return zh if a.lang == "zh" else en


def ide_name(a):
    return {"keil": "Keil MDK", "iar": "IAR EWARM"}.get(a.build, a.build)


def fill(text, **kw):
    """Replace @KEY@ placeholders (shell / YAML templates; avoids f-string brace escaping)."""
    for k, v in kw.items():
        text = text.replace(f"@{k}@", str(v))
    return text


class Tree:
    def __init__(self, root):
        self.root = root
        self.files = {}
        self.dirs = set()

    def d(self, *paths):
        for p in paths:
            self.dirs.add(p)

    def f(self, path, content):
        # exactly one trailing newline, no double blank lines (keeps clang-format / linters quiet)
        self.files[path] = re.sub(r"\n{3,}", "\n\n", content.strip("\n")) + "\n"

    def write(self):
        if os.path.exists(self.root):
            shutil.rmtree(self.root)
        for p in self.dirs:
            os.makedirs(os.path.join(self.root, p), exist_ok=True)
        for p, c in self.files.items():
            full = os.path.join(self.root, p)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(c)
            if p.endswith(".sh"):
                os.chmod(full, 0o755)
        # .gitkeep for empty dirs
        for dp, dns, fns in os.walk(self.root):
            if not dns and not fns:
                open(os.path.join(dp, ".gitkeep"), "w").close()


# ---------------------------------------------------------------- C templates
def c_header(name, guard, body, brief):
    g = guard.upper() + "_H"
    return f"""
/**
 * @file    {name}.h
 * @brief   {brief}
 * @date    {TODAY}
 */
#ifndef {g}
#define {g}

#ifdef __cplusplus
extern "C" {{
#endif

{body}
#ifdef __cplusplus
}}
#endif

#endif /* {g} */
"""


def c_source(name, includes, body, brief, priv=""):
    inc = "\n".join(f'#include "{i}"' for i in includes)
    return f"""
/**
 * @file    {name}.c
 * @brief   {brief}
 * @date    {TODAY}
 */
{inc}

/* ---------------- private macros / types ---------------- */

/* ---------------- private variables ---------------- */

/* ---------------- private functions ---------------- */
{priv}
/* ---------------- public functions ---------------- */
{body}
"""


# ---------------------------------------------------------------- root
def root_common(t, a):
    t.d("01_Docs/Requirements", "01_Docs/Design", "01_Docs/Datasheets", "01_Docs/Test",
        "01_Docs/Production", "01_Docs/Meeting", "02_Hardware/Schematic", "02_Hardware/PCB",
        "02_Hardware/BOM", "02_Hardware/Gerber", "04_Tools/flash", "04_Tools/factory_test",
        "04_Tools/host", "05_Release")
    t.f(".gitignore", GITIGNORE_ROOT)
    t.f("05_Release/CHANGELOG.md", f"""
# Changelog

{L(a, "格式参考 Keep a Changelog。开发中的变更先写在 Unreleased 下，发布时移到对应版本号下。",
       "Format: Keep a Changelog. Ongoing changes go under Unreleased and move under the version on release.")}

## [Unreleased]

## [v0.1.0] - {TODAY}

### Added

- {L(a, "创建项目骨架。", "Project skeleton created.")}
""")


GITIGNORE_ROOT = """
# build outputs
build/
out/
output/
*.o
*.d
*.a
*.elf
*.map
*.lst
*.hex
*.bin
!05_Release/**/*.bin
!05_Release/**/*.hex
!05_Release/**/*.elf
!05_Release/**/*.map

# IDE / editor
.vscode/*
!.vscode/settings.json
.idea/
*.uvguix.*
*.uvoptx
DebugConfig/
Listings/
Objects/
*.dep
settings/
.DS_Store
Thumbs.db

# hardware tool temp files
*.bak
*-backups/
"""


# ---------------------------------------------------------------- R&D workflow files
CLANG_FORMAT = """
# Code style of project code. Check: scripts/check.sh   Fix: scripts/check.sh --fix
# Vendor / third-party folders carry their own .clang-format with DisableFormat: true.
BasedOnStyle: LLVM
IndentWidth: 4
TabWidth: 4
UseTab: Never
ColumnLimit: 100
BreakBeforeBraces: Linux
AllowShortFunctionsOnASingleLine: None
AllowShortIfStatementsOnASingleLine: Never
AllowShortLoopsOnASingleLine: false
AllowShortBlocksOnASingleLine: Never
AlignConsecutiveMacros: true
AlignTrailingComments: true
PointerAlignment: Right
IndentCaseLabels: false
SortIncludes: false
"""

CLANG_FORMAT_OFF = """
# Vendor / third-party code keeps its upstream format.
DisableFormat: true
SortIncludes: false
"""


def wf_values(a):
    """Per-type values shared by CONTRIBUTING.md, the MR/PR template and CI."""
    mcu = a.type == "mcu-rtos"
    ci = a.ci != "none"
    v = {
        "version_file": "03_Firmware/config/version.h" if mcu else "03_Firmware/apps/common/include/version.h",
        "merge": L(a, "CI 通过后合并到 develop" if ci else "Code Review 通过后合并到 develop",
                   "Merge into develop after CI passes" if ci else "Merge into develop after review"),
        "ci_must": L(a, "，CI 必须通过" if ci else "", "; CI must pass" if ci else ""),
        "tag_note": L(a, "（CI 会校验 tag 与 version.h 一致）" if ci else "",
                      " (CI checks that the tag matches version.h)" if ci else ""),
    }
    if mcu:
        ide = ide_name(a)
        v["check"] = L(a, "cppcheck + clang-format，只检查自己的代码（不含 hal/ cmsis/ os/）",
                       "cppcheck + clang-format on own code only (never hal/ cmsis/ os/)")
        if a.build == "cmake":
            v["board"] = "`scripts/build.sh debug && scripts/flash.sh`"
            v["release"] = "`scripts/build.sh release && scripts/pack.sh release`"
        else:
            v["board"] = L(a, f"在 {ide} 中编译 Debug 目标并下载", f"Build the Debug target in {ide} and download it")
            v["release"] = L(a, f"在 {ide} 中编译 Release 目标，再运行 `scripts/pack.sh release <{ide} 输出目录>`",
                             f"build the Release target in {ide}, then run `scripts/pack.sh release <{ide} output dir>`")
        v["layer_item"] = L(a, "代码放在正确的层级，没有反向依赖（下层不 include 上层头文件）",
                            "Code sits in the right layer; no upward dependency (lower layers never include upper-layer headers)")
        v["vendor_item"] = L(a, "没有提交编译产物，没有修改厂商代码（hal/ cmsis/ os/）",
                             "No build outputs committed; vendor code (hal/ cmsis/ os/) untouched")
    else:
        v["check"] = L(a, "apps/ 用 cppcheck + clang-format；drivers/ 用 checkpatch.pl（有内核源码时）",
                       "apps/: cppcheck + clang-format; drivers/: checkpatch.pl (once the kernel source is present)")
        v["board"] = L(a, "`scripts/build_all.sh && scripts/pack_image.sh`，烧录或 NFS 挂载调试",
                       "`scripts/build_all.sh && scripts/pack_image.sh`, then flash or boot over NFS")
        v["release"] = "`scripts/build_all.sh && scripts/pack_image.sh`"
        v["layer_item"] = L(a, "代码放在正确的位置（apps/、drivers/、rootfs/overlay/），没有手动修改 output/",
                            "Code sits in the right place (apps/, drivers/, rootfs/overlay/); output/ never edited by hand")
        v["vendor_item"] = L(a, "对 U-Boot / 内核的修改已用 git format-patch 导出到 patches/",
                             "U-Boot / kernel changes are exported to patches/ with git format-patch")
    return v


def mr_checklist(a, v):
    return "\n".join([
        f"- [ ] {v['layer_item']}",
        L(a, "- [ ] `scripts/check.sh` 通过", "- [ ] `scripts/check.sh` passes"),
        L(a, "- [ ] `scripts/run_tests.sh` 通过，新逻辑已补单元测试",
          "- [ ] `scripts/run_tests.sh` passes; new logic has unit tests"),
        L(a, "- [ ] 已在目标板验证（硬件版本：　　固件版本：　　）",
          "- [ ] Verified on the target board (HW rev:      FW version:      )"),
        L(a, "- [ ] 已更新 README / 接口文档 / CHANGELOG（Unreleased）",
          "- [ ] README / interface docs / CHANGELOG (Unreleased) updated"),
        f"- [ ] {v['vendor_item']}",
    ])


def contributing(a, v):
    mcu = a.type == "mcu-rtos"
    variants = ""
    if mcu and a.build == "cmake":
        variants = L(a, """
## 构建变体

| 变体 | 命令 | 用途 |
|---|---|---|
| debug | `scripts/build.sh debug` | 开发调试（-O0 -g，日志等级 4） |
| release | `scripts/build.sh release` | 正式发布（-Os，定义 NDEBUG，日志等级 2） |
| factory | `scripts/build.sh factory` | 产测固件（-Os，`CFG_FACTORY_MODE=1`，日志等级 3），配合 `04_Tools/factory_test/` |
""", """
## Build variants

| Variant | Command | Purpose |
|---|---|---|
| debug | `scripts/build.sh debug` | Development (-O0 -g, log level 4) |
| release | `scripts/build.sh release` | Production (-Os, NDEBUG, log level 2) |
| factory | `scripts/build.sh factory` | Factory-test firmware (-Os, `CFG_FACTORY_MODE=1`, log level 3), used with `04_Tools/factory_test/` |
""")
    elif mcu:
        ide = ide_name(a)
        variants = L(a, f"""
## 构建变体

在 {ide} 工程中建 Debug、Release、Factory 三个 Target：Release 定义 `NDEBUG`；Factory 定义 `NDEBUG` 和 `CFG_FACTORY_MODE=1`（产测固件，日志等级 3，配合 `04_Tools/factory_test/`）。
""", f"""
## Build variants

Create Debug, Release and Factory targets in the {ide} project: Release defines `NDEBUG`; Factory defines `NDEBUG` and `CFG_FACTORY_MODE=1` (factory-test firmware, log level 3, used with `04_Tools/factory_test/`).
""")
    checklist = mr_checklist(a, v)
    if a.lang == "zh":
        return f"""
# 开发协作规范

{a.name} 的日常开发闭环、分支与提交规范、合并请求自检清单和发布流程。本地和 CI 运行同一套脚本；表中命令在 `03_Firmware/` 下执行。

## 日常开发闭环

| 步骤 | 做什么 | 命令 / 位置 |
|---|---|---|
| 1. 拆解任务 | 每个任务对应需求编号 REQ-xxx 或 Issue | `01_Docs/Requirements/` |
| 2. 拉分支 | 从 develop 拉 feature 分支 | `git checkout -b feature/REQ-012-uart-dma develop` |
| 3. 设计 | 接口、数据流、时序；改接口先改文档 | `01_Docs/Design/` |
| 4. 编码 | 遵守分层规则和命名规范 | `03_Firmware/` |
| 5. 静态检查 | {v['check']} | `scripts/check.sh`（`--fix` 自动格式化） |
| 6. 单元测试 | 在主机上运行 | `scripts/run_tests.sh` |
| 7. 板级调试 | 在目标板上验证 | {v['board']} |
| 8. 合并请求 | 按下方清单自检，至少 1 人 Code Review | MR / PR |
| 9. 合并 | {v['merge']} | |
| 10. 更新文档 | README、接口文档、CHANGELOG 的 Unreleased | `05_Release/CHANGELOG.md` |

## 分支模型

| 分支 | 用途 | 规则 |
|---|---|---|
| main | 只放正式发布版本 | 禁止直接 push；每次合并都打 tag `vX.Y.Z` |
| develop | 日常集成 | 只通过 MR / PR 合并{v['ci_must']} |
| feature/REQ-xxx-desc | 新功能 | 从 develop 拉出，合回 develop |
| release/vX.Y.Z | 发布准备：只修 bug、改版本号 | 合并到 main 和 develop |
| hotfix/vX.Y.Z | 已发布版本的紧急修复 | 从 main 拉出，合并到 main 和 develop |

## 提交信息

格式：`<type>(<scope>): <subject> [REQ-xxx]`，例如 `feat(bsp): 增加 UART DMA 接收 [REQ-012]`。

- type：feat 新功能、fix 修复、docs 文档、refactor 重构、test 测试、perf 性能、build 构建、ci 流水线、chore 杂项。
- scope：目录或模块名，如 app、bsp、drivers/bmp280。
- 一个提交只做一件事；不要提交编译产物。

## 合并请求自检清单

{checklist}
{variants}
## 发布流程

1. 从 develop 拉 `release/vX.Y.Z`。
2. 修改 `{v['version_file']}`，这是唯一的版本号来源。
3. 把 CHANGELOG 中 Unreleased 的内容移到新版本标题下。
4. 构建并归档：{v['release']}；产物、sha256sum.txt 和 release_note.md 放在 `05_Release/vX.Y.Z/`。
5. 完成发布测试，测试报告放 `01_Docs/Test/`。
6. 合并到 main 并打 tag `vX.Y.Z`{v['tag_note']}，再合并回 develop。

## 可追溯性

需求编号 REQ-xxx 贯穿全流程：SRS（`01_Docs/Requirements/`）→ 分支名和提交信息 → 测试用例 TC-xxx → 测试报告（`01_Docs/Test/`）。每条需求至少对应一个测试用例。
"""
    return f"""
# Contributing

Daily development loop, branch and commit rules, merge request checklist and release flow of {a.name}. Local development and CI run the same scripts; commands below run in `03_Firmware/`.

## Daily development loop

| Step | What | Command / location |
|---|---|---|
| 1. Break down | Every task maps to a requirement ID REQ-xxx or an issue | `01_Docs/Requirements/` |
| 2. Branch | Create a feature branch from develop | `git checkout -b feature/REQ-012-uart-dma develop` |
| 3. Design | Interfaces, data flow, timing; update docs before changing interfaces | `01_Docs/Design/` |
| 4. Code | Follow the layer rules and naming conventions | `03_Firmware/` |
| 5. Static check | {v['check']} | `scripts/check.sh` (`--fix` formats in place) |
| 6. Unit test | Run on the host | `scripts/run_tests.sh` |
| 7. Board test | Verify on the target board | {v['board']} |
| 8. Merge request | Self-check with the list below; at least one reviewer | MR / PR |
| 9. Merge | {v['merge']} | |
| 10. Docs | README, interface docs, Unreleased section of the CHANGELOG | `05_Release/CHANGELOG.md` |

## Branch model

| Branch | Purpose | Rule |
|---|---|---|
| main | Released versions only | No direct push; tag every merge as `vX.Y.Z` |
| develop | Integration | Merge through MR / PR only{v['ci_must']} |
| feature/REQ-xxx-desc | New feature | From develop, back into develop |
| release/vX.Y.Z | Release preparation: bug fixes and version bump only | Merge into main and develop |
| hotfix/vX.Y.Z | Urgent fix of a released version | From main, merge into main and develop |

## Commit messages

Format: `<type>(<scope>): <subject> [REQ-xxx]`, e.g. `feat(bsp): add UART DMA receive [REQ-012]`.

- type: feat, fix, docs, refactor, test, perf, build, ci, chore.
- scope: folder or module name, such as app, bsp, drivers/bmp280.
- One change per commit; never commit build outputs.

## Merge request checklist

{checklist}
{variants}
## Release flow

1. Create `release/vX.Y.Z` from develop.
2. Bump the version in `{v['version_file']}` (the single source of truth).
3. Move the Unreleased entries of the CHANGELOG under the new version heading.
4. Build and archive: {v['release']}; binaries, sha256sum.txt and release_note.md go to `05_Release/vX.Y.Z/`.
5. Run the release tests and store the report in `01_Docs/Test/`.
6. Merge into main and tag `vX.Y.Z`{v['tag_note']}, then merge back into develop.

## Traceability

Requirement IDs (REQ-xxx) run through the whole flow: SRS (`01_Docs/Requirements/`) → branch names and commit messages → test cases TC-xxx → test reports (`01_Docs/Test/`). Every requirement has at least one test case.
"""


def mr_template(a, v):
    return L(a, f"""
## 关联需求 / Issue

REQ-xxx

## 变更说明

-

## 自检清单

{mr_checklist(a, v)}
""", f"""
## Requirement / issue

REQ-xxx

## Changes

-

## Checklist

{mr_checklist(a, v)}
""")


def srs_template(a):
    return L(a, f"""
# 需求规格书（SRS）

- 项目：{a.name}
- 文档版本：v0.1（{TODAY}）
- 状态：草稿 / 评审中 / 已批准

## 1. 概述

产品定位、使用场景、目标用户；系统框图放 `01_Docs/Design/`。

## 2. 需求列表

| 编号 | 类型 | 描述 | 优先级 | 验收标准 | 测试用例 |
|---|---|---|---|---|---|
| REQ-001 | 功能 | 示例：上电 1 s 内通过串口输出固件版本号 | P0 | 串口日志包含版本号 | TC-001 |
| REQ-002 | 功耗 | 示例：待机电流 ≤ 50 µA | P1 | 电流表实测 3 次均达标 | TC-002 |

- 类型：功能 / 性能 / 功耗 / 可靠性 / 安全 / 认证（CE、FCC、UL 等）。
- 优先级：P0 必须 / P1 应该 / P2 可选。
- 编号发布后不再复用；需求变更记录在第 4 节。

## 3. 约束

- 成本：
- 功耗 / 续航：
- 认证：
- 环境（温度、湿度、防护等级）：
- 接口与协议：

## 4. 变更记录

| 版本 | 日期 | 变更内容 | 作者 |
|---|---|---|---|
| v0.1 | {TODAY} | 初稿 | |
""", f"""
# Software Requirements Specification (SRS)

- Project: {a.name}
- Document version: v0.1 ({TODAY})
- Status: draft / in review / approved

## 1. Overview

Product positioning, use cases, target users; put the system block diagram in `01_Docs/Design/`.

## 2. Requirements

| ID | Type | Description | Priority | Acceptance criteria | Test cases |
|---|---|---|---|---|---|
| REQ-001 | Function | Example: print the firmware version on the UART within 1 s after power-on | P0 | UART log contains the version | TC-001 |
| REQ-002 | Power | Example: standby current ≤ 50 µA | P1 | Measured 3 times with an ammeter | TC-002 |

- Type: function / performance / power / reliability / security / certification (CE, FCC, UL, ...).
- Priority: P0 must / P1 should / P2 could.
- IDs are never reused once published; record changes in section 4.

## 3. Constraints

- Cost:
- Power / battery life:
- Certification:
- Environment (temperature, humidity, IP rating):
- Interfaces and protocols:

## 4. Change log

| Version | Date | Change | Author |
|---|---|---|---|
| v0.1 | {TODAY} | First draft | |
""")


def test_report_template(a):
    return L(a, """
# 测试报告

- 固件版本：vX.Y.Z（commit：）
- 硬件版本：EVT / DVT / PVT
- 测试类型：单元 / 集成 / 系统 / 压力 / 老化 / 功耗 / EMC 预测试
- 测试日期 / 测试人：

## 1. 测试环境

被测设备数量；仪器（示波器、逻辑分析仪、电源、电流表）；工具和脚本版本。

## 2. 用例与结果

| 用例 | 需求 | 步骤 | 预期结果 | 结果 | 备注 |
|---|---|---|---|---|---|
| TC-001 | REQ-001 | 上电，观察串口日志 | 1 s 内输出版本号 | Pass | |

## 3. 问题列表

| 编号 | 描述 | 严重程度 | 状态 | 修复提交 |
|---|---|---|---|---|
| BUG-001 | | 致命 / 严重 / 一般 / 轻微 | 打开 / 已修复 / 已验证 | |

## 4. 结论

通过 / 有条件通过 / 不通过；遗留问题和风险。
""", """
# Test report

- Firmware version: vX.Y.Z (commit: )
- Hardware revision: EVT / DVT / PVT
- Test type: unit / integration / system / stress / burn-in / power / EMC pre-scan
- Date / tester:

## 1. Environment

Number of devices under test; instruments (oscilloscope, logic analyzer, power supply, ammeter); tool and script versions.

## 2. Test cases and results

| Case | Requirement | Steps | Expected | Result | Note |
|---|---|---|---|---|---|
| TC-001 | REQ-001 | Power on, watch the UART log | Version printed within 1 s | Pass | |

## 3. Issues

| ID | Description | Severity | Status | Fix commit |
|---|---|---|---|---|
| BUG-001 | | critical / major / minor / trivial | open / fixed / verified | |

## 4. Conclusion

Pass / conditional pass / fail; open issues and risks.
""")


def editorconfig(a):
    extra = ""
    if a.type == "linux":
        extra = "\n# kernel / U-Boot code follows the kernel coding style\n[03_Firmware/{drivers,kernel,uboot}/**]\nindent_style = tab\nindent_size = 8\n"
    return """
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 4

[{Makefile,*.mk,Config.in,*.dts,*.dtsi}]
indent_style = tab

[*.{yml,yaml}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false
""" + extra


GITLAB_CI = r"""
# GitLab CI: runs the same scripts as local development (see CONTRIBUTING.md).
stages: [check, test, build]

.ubuntu:
  image: ubuntu:24.04
  before_script:
    - apt-get update -qq
    - DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends $APT_PKGS > /dev/null

static-check:
  extends: .ubuntu
  stage: check
  variables:
    APT_PKGS: cppcheck clang-format
  script:
    - bash 03_Firmware/scripts/check.sh

version-tag-check:
  stage: check
  image: alpine:3.20
  rules:
    - if: $CI_COMMIT_TAG
  script:
    - VER=$(sed -n 's/^#define FW_VERSION_STR *"\(.*\)"/\1/p' @VERSION_FILE@)
    - test "v$VER" = "$CI_COMMIT_TAG" || (echo "tag $CI_COMMIT_TAG does not match v$VER in version.h" && exit 1)

unit-test:
  extends: .ubuntu
  stage: test
  variables:
    APT_PKGS: @TEST_PKGS@
  script:
    - bash 03_Firmware/scripts/run_tests.sh
@BUILD_JOB@
"""

GITLAB_BUILD_MCU = """
firmware-build:
  extends: .ubuntu
  stage: build
  variables:
    APT_PKGS: cmake make gcc-arm-none-eabi libnewlib-arm-none-eabi
  rules:
    - exists:
        - 03_Firmware/cmsis/*.ld   # runs once the startup file and linker script are in cmsis/
  script:
    - bash 03_Firmware/scripts/build.sh release
  artifacts:
    paths:
      - 03_Firmware/build/release/*.elf
      - 03_Firmware/build/release/*.bin
      - 03_Firmware/build/release/*.hex
      - 03_Firmware/build/release/*.map
    expire_in: 30 days
"""

GITLAB_BUILD_LINUX = """
# image-build needs vendor sources and a download cache; run it on a dedicated runner, e.g.
# image-build:
#   stage: build
#   tags: [bsp-builder]
#   when: manual
#   script:
#     - cd 03_Firmware && source scripts/env.sh && ./scripts/fetch_sources.sh && ./scripts/build_all.sh && ./scripts/pack_image.sh
#   artifacts:
#     paths: [03_Firmware/output/]
"""

GITHUB_CI = r"""
# GitHub Actions: runs the same scripts as local development (see CONTRIBUTING.md).
name: ci

on:
  push:
    branches: [main, develop, "release/**", "hotfix/**"]
    tags: ["v*"]
  pull_request:

jobs:
  static-check:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - run: sudo apt-get update -qq && sudo apt-get install -y -qq cppcheck clang-format
      - run: bash 03_Firmware/scripts/check.sh

  version-tag-check:
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - run: |
          VER=$(sed -n 's/^#define FW_VERSION_STR *"\(.*\)"/\1/p' @VERSION_FILE@)
          test "v$VER" = "$GITHUB_REF_NAME" || { echo "tag $GITHUB_REF_NAME does not match v$VER in version.h"; exit 1; }

  unit-test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - run: bash 03_Firmware/scripts/run_tests.sh
@BUILD_JOB@
"""

GITHUB_BUILD_MCU = """
  firmware-build:
    needs: [static-check, unit-test]
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - name: Build release (runs once the startup file and linker script are in cmsis/)
        if: hashFiles('03_Firmware/cmsis/*.ld') != ''
        run: |
          sudo apt-get update -qq && sudo apt-get install -y -qq gcc-arm-none-eabi libnewlib-arm-none-eabi
          bash 03_Firmware/scripts/build.sh release
      - uses: actions/upload-artifact@v4
        if: hashFiles('03_Firmware/cmsis/*.ld') != ''
        with:
          name: firmware
          path: |
            03_Firmware/build/release/*.elf
            03_Firmware/build/release/*.bin
            03_Firmware/build/release/*.hex
            03_Firmware/build/release/*.map
"""

GITHUB_BUILD_LINUX = """
  # image-build needs vendor sources and a download cache; run it on a self-hosted runner, e.g.
  # image-build:
  #   runs-on: [self-hosted, bsp-builder]
  #   steps:
  #     - uses: actions/checkout@v4
  #     - run: cd 03_Firmware && source scripts/env.sh && ./scripts/fetch_sources.sh && ./scripts/build_all.sh && ./scripts/pack_image.sh
"""

IDE_BUILD_NOTE = """
# firmware-build: @IDE@ projects need a Windows runner with the IDE installed, e.g.
#   @CMD@
"""


def ci_files(t, a, v):
    if a.ci == "none":
        return
    mcu = a.type == "mcu-rtos"
    gitlab = a.ci == "gitlab"
    p = ident(a.name)
    if mcu and a.build == "cmake":
        job = GITLAB_BUILD_MCU if gitlab else GITHUB_BUILD_MCU
    elif mcu:
        cmd = (f"UV4.exe -b 03_Firmware/project/{p}.uvprojx -t Release -j0 -o build.log" if a.build == "keil"
               else f"iarbuild.exe 03_Firmware/project/{p}.ewp -build Release")
        job = fill(IDE_BUILD_NOTE, IDE=ide_name(a), CMD=cmd)
    else:
        job = GITLAB_BUILD_LINUX if gitlab else GITHUB_BUILD_LINUX
    kw = dict(VERSION_FILE=v["version_file"],
              TEST_PKGS="gcc libc6-dev" if mcu else "gcc libc6-dev cmake make",
              BUILD_JOB=job)
    if gitlab:
        t.f(".gitlab-ci.yml", fill(GITLAB_CI, **kw))
        t.f(".gitlab/merge_request_templates/Default.md", mr_template(a, v))
    else:
        t.f(".github/workflows/ci.yml", fill(GITHUB_CI, **kw))
        t.f(".github/pull_request_template.md", mr_template(a, v))


def workflow_common(t, a):
    v = wf_values(a)
    t.f("CONTRIBUTING.md", contributing(a, v))
    t.f(".editorconfig", editorconfig(a))
    t.f("01_Docs/Requirements/SRS_template.md", srs_template(a))
    t.f("01_Docs/Test/test_report_template.md", test_report_template(a))
    ci_files(t, a, v)


# ---------------------------------------------------------------- shell scripts
HAVE_FN = r"""
have() {
    command -v "$1" > /dev/null 2>&1 && return 0
    if [ -n "${CI:-}" ]; then
        echo "[check] ERROR: $1 not installed"
        fail=1
    else
        echo "[check] WARN: $1 not installed, skipped"
    fi
    return 1
}
"""

CHECK_TAIL = r"""
if [ -n "$CFILES" ] && have cppcheck; then
    echo "[check] cppcheck"
    # shellcheck disable=SC2086
    cppcheck --quiet --error-exitcode=1 --language=c --std=c11 --inline-suppr \
        --enable=warning,performance,portability --suppress=missingIncludeSystem \
        $INCS $CFILES || fail=1
fi

if [ -n "$FMT_FILES" ] && have clang-format; then
    echo "[check] clang-format"
    # shellcheck disable=SC2086
    [ "${1:-}" = "--fix" ] && clang-format -i $FMT_FILES
    # shellcheck disable=SC2086
    clang-format --dry-run --Werror $FMT_FILES || fail=1
fi
@EXTRA@
if [ "$fail" -ne 0 ]; then
    echo "[check] FAILED"
    exit 1
fi
echo "[check] OK"
"""

CHECK_MCU = r"""
#!/usr/bin/env bash
# Static check (cppcheck) + format check (clang-format) of project code. CI runs this same script.
# Skipped: vendor dirs (hal/ cmsis/ os/), third-party folders that contain a LICENSE / COPYING file
# (e.g. middleware/gui/lvgl), EXCLUDE_DIRS, and for formatting only EXCLUDE_FORMAT.
# Usage: scripts/check.sh          check
#        scripts/check.sh --fix    apply clang-format in place, then check
set -uo pipefail
cd "$(dirname "$0")/.."

EXCLUDE_DIRS=""
EXCLUDE_FORMAT='(FreeRTOSConfig\.h|rtconfig\.h|tx_user\.h|_hal_conf\.h|lv_conf\.h|ffconf\.h|lwipopts\.h)$'

DIRS=""
for d in app bsp drivers middleware config test bootloader; do
    [ -d "$d" ] && DIRS="$DIRS $d"
done
# shellcheck disable=SC2086
FILES=$(find $DIRS -name '*.[ch]' | sort)
# shellcheck disable=SC2086
for s in $EXCLUDE_DIRS $(find $DIRS \( -iname 'LICENSE*' -o -iname 'COPYING*' \) -exec dirname {} \;); do
    FILES=$(echo "$FILES" | grep -v "^$s/")
done
CFILES=$(echo "$FILES" | grep '\.c$')
FMT_FILES=$(echo "$FILES" | grep -Ev "$EXCLUDE_FORMAT")
INCS=$(for h in $(echo "$FILES" | grep '\.h$'); do echo "-I$(dirname "$h")"; done | sort -u)
fail=0
@HAVE@@TAIL@
"""

CHECK_LINUX = r"""
#!/usr/bin/env bash
# Static check + format check of user-space apps (apps/). CI runs this same script.
# Kernel modules in drivers/ follow the kernel coding style and are checked with checkpatch.pl
# once kernel/src is present. Third-party folders that contain a LICENSE / COPYING file are skipped.
# Usage: scripts/check.sh          check
#        scripts/check.sh --fix    apply clang-format in place, then check
set -uo pipefail
cd "$(dirname "$0")/.."

EXCLUDE_DIRS=""
EXCLUDE_FORMAT='^$'

FILES=$(find apps -name '*.[ch]' | sort)
# shellcheck disable=SC2086
for s in $EXCLUDE_DIRS $(find apps \( -iname 'LICENSE*' -o -iname 'COPYING*' \) -exec dirname {} \;); do
    FILES=$(echo "$FILES" | grep -v "^$s/")
done
CFILES=$(echo "$FILES" | grep '\.c$')
FMT_FILES=$(echo "$FILES" | grep -Ev "$EXCLUDE_FORMAT")
INCS=$(for h in $(echo "$FILES" | grep '\.h$'); do echo "-I$(dirname "$h")"; done | sort -u)
fail=0
@HAVE@@TAIL@
"""

CHECKPATCH = r"""
CHECKPATCH=kernel/src/scripts/checkpatch.pl
if [ -x "$CHECKPATCH" ] && ls drivers/*/*.c > /dev/null 2>&1; then
    echo "[check] checkpatch"
    "$CHECKPATCH" --no-tree --terse -f drivers/*/*.c || fail=1
fi
"""

RUN_TESTS_MCU = r"""
#!/usr/bin/env bash
# Host-side unit tests: every test/test_*.c is compiled with the host compiler and executed.
# Each test lists the sources it needs in a "TEST_SRCS:" comment, e.g.
#   /* TEST_SRCS: middleware/utils/ring_buffer.c */
# Never link hal/ or os/; put stubs / fakes for hardware in test/.
set -euo pipefail
cd "$(dirname "$0")/.."
CC=${HOST_CC:-gcc}
OUT=build/host-test
mkdir -p "$OUT"
pass=0
fail=0
for t in test/test_*.c; do
    [ -e "$t" ] || continue
    name=$(basename "$t" .c)
    srcs=$(sed -n 's/.*TEST_SRCS:\([^*]*\).*/\1/p' "$t")
    incs="-Itest -Iconfig"
    for s in $srcs; do
        incs="$incs -I$(dirname "$s")"
    done
    # shellcheck disable=SC2086
    if $CC -std=c11 -Wall -Wextra -Werror -g $incs "$t" $srcs -o "$OUT/$name" && "$OUT/$name"; then
        pass=$((pass + 1))
    else
        echo "[test] FAIL: $name"
        fail=$((fail + 1))
    fi
done
echo "[test] passed: $pass  failed: $fail"
[ "$fail" -eq 0 ]
"""

RUN_TESTS_LINUX = r"""
#!/usr/bin/env bash
# Host build of every app in apps/ + ctest. Each app registers at least a "--version" smoke test;
# add unit tests with add_test() in the app's CMakeLists.txt.
set -uo pipefail
cd "$(dirname "$0")/.."
export CC=${HOST_CC:-gcc}
unset CMAKE_TOOLCHAIN_FILE
OUT=output/host-test
fail=0
for dir in apps/*/; do
    app=$(basename "$dir")
    [ "$app" = common ] && continue
    echo "[test] $app"
    if ! { cmake -S "$dir" -B "$OUT/$app" -DCMAKE_BUILD_TYPE=Debug > /dev/null &&
        cmake --build "$OUT/$app" -j > /dev/null &&
        ctest --test-dir "$OUT/$app" --output-on-failure; }; then
        echo "[test] FAIL: $app"
        fail=1
    fi
done
if [ "$fail" -ne 0 ]; then
    echo "[test] FAILED"
    exit 1
fi
echo "[test] OK"
"""

PACK_SH = r"""
#!/usr/bin/env bash
# Archive a built variant into 05_Release/v<version>/ (version from config/version.h)
# together with sha256sum.txt and a release_note.md stub.
# Usage: scripts/pack.sh [release|factory|debug] [artifact_dir]
#   artifact_dir defaults to build/<variant>; for Keil / IAR pass the IDE output folder.
set -euo pipefail
cd "$(dirname "$0")/.."
VARIANT=${1:-release}
SRC=${2:-build/$VARIANT}
NAME=@P@
VER=$(sed -n 's/^#define FW_VERSION_STR *"\(.*\)"/\1/p' config/version.h)
[ -n "$VER" ] || { echo "[pack] FW_VERSION_STR not found in config/version.h"; exit 1; }
SUFFIX=""
[ "$VARIANT" = release ] || SUFFIX="_$VARIANT"
DST=../05_Release/v$VER
mkdir -p "$DST"

n=0
for f in "$SRC"/*.bin "$SRC"/*.hex "$SRC"/*.elf "$SRC"/*.axf "$SRC"/*.out "$SRC"/*.map; do
    [ -f "$f" ] || continue
    cp "$f" "$DST/${NAME}_v${VER}${SUFFIX}.${f##*.}"
    n=$((n + 1))
done
[ "$n" -gt 0 ] || { echo "[pack] no artifacts in $SRC (@HINT@)"; exit 1; }
if command -v sha256sum > /dev/null 2>&1; then SHA="sha256sum"; else SHA="shasum -a 256"; fi
(cd "$DST" && $SHA "${NAME}"_v* > sha256sum.txt)

if [ ! -f "$DST/release_note.md" ]; then
    cat > "$DST/release_note.md" << EOF
@NOTE@
EOF
fi
echo "[pack] $n file(s) -> $DST"
ls -1 "$DST"
"""

NOTE_ZH = """# @TITLE@ v${VER} 发布说明

- 发布日期：$(date +%F)
- 构建变体：${VARIANT}
- Git：$(git rev-parse --short HEAD 2>/dev/null || echo N/A)
- 硬件版本：
- 校验：sha256sum.txt

## 变更

（从 05_Release/CHANGELOG.md 复制本版本的内容）

## 升级说明 / 已知问题

-"""

NOTE_EN = """# @TITLE@ v${VER} release note

- Date: $(date +%F)
- Variant: ${VARIANT}
- Git: $(git rev-parse --short HEAD 2>/dev/null || echo N/A)
- Hardware revision:
- Checksums: sha256sum.txt

## Changes

(copy this version's entries from 05_Release/CHANGELOG.md)

## Upgrade notes / known issues

-"""

PACK_IMAGE_LINUX = r"""
#!/usr/bin/env bash
# Pack u-boot / kernel / dtb / rootfs into $OUT_DIR/update.img, then archive it to
# 05_Release/v<version>/ (version from apps/common/include/version.h) with sha256sum.txt
# and a release_note.md stub. Large images: use Git LFS or an artifact repository.
set -euo pipefail
source "$(dirname "$0")/env.sh"
FW_DIR=$(cd "$(dirname "$0")/.." && pwd)
VER=$(sed -n 's/^#define FW_VERSION_STR *"\(.*\)"/\1/p' "$FW_DIR/apps/common/include/version.h")
IMG=$OUT_DIR/update.img

echo "TODO: pack u-boot/kernel/dtb/rootfs into $IMG (vendor tool, e.g. afptool / mkimage / genimage)"

if [ -f "$IMG" ]; then
    DST=$FW_DIR/../05_Release/v$VER
    mkdir -p "$DST"
    cp "$IMG" "$DST/@P@_v${VER}.img"
    if command -v sha256sum > /dev/null 2>&1; then SHA="sha256sum"; else SHA="shasum -a 256"; fi
    (cd "$DST" && $SHA @P@_v*.img > sha256sum.txt)
    VARIANT=release
    if [ ! -f "$DST/release_note.md" ]; then
        cat > "$DST/release_note.md" << EOF
@NOTE@
EOF
    fi
    echo "[pack] -> $DST"
    ls -1 "$DST"
fi
"""


def check_script(a, linux=False):
    tail = fill(CHECK_TAIL, EXTRA=CHECKPATCH if linux else "")
    return fill(CHECK_LINUX if linux else CHECK_MCU, HAVE=HAVE_FN, TAIL=tail)


# ---------------------------------------------------------------- MCU + RTOS
def rtos_api(rtos):
    """API hints for TODO comments (each comment line stays under the 100-column limit)."""
    k = re.sub(r"[^a-z]", "", rtos.lower())
    table = {
        "freertos": (['xTaskCreate(task_main, "main", CFG_TASK_MAIN_STACK, NULL, CFG_TASK_MAIN_PRIO, NULL);'],
                     "start the scheduler: vTaskStartScheduler();", "vTaskDelay()", "FreeRTOSConfig.h"),
        "rtthread": (['rt_thread_t th = rt_thread_create("main", task_main, RT_NULL,',
                      '                                  CFG_TASK_MAIN_STACK, CFG_TASK_MAIN_PRIO, 10);',
                      "rt_thread_startup(th);"],
                     "start the kernel with rtthread_startup(), or enable RT_USING_USER_MAIN",
                     "rt_thread_mdelay()", "rtconfig.h"),
        "zephyr": (["k_thread_create(), or K_THREAD_DEFINE() at file scope"],
                   "nothing to start: Zephyr starts the kernel before main()", "k_msleep()", "prj.conf"),
        "threadx": (["tx_thread_create() inside tx_application_define()"],
                    "start the kernel: tx_kernel_enter();", "tx_thread_sleep()", "tx_user.h"),
    }
    hit = next((v for key, v in table.items() if key in k), None)  # "RT-Thread Nano", "Azure RTOS ThreadX"
    create, start, delay, conf = hit or (None, f"start the {rtos} scheduler",
                                         f"the {rtos} delay API", "config header")
    if create:
        lines = "\n".join(f"     *   {c}" for c in create)
        create = f"    /* TODO: create tasks with the {rtos} API, e.g.\n{lines}\n     */"
    else:
        create = f"    /* TODO: create tasks with the {rtos} API (CFG_TASK_MAIN_STACK, CFG_TASK_MAIN_PRIO) */"
    return {"create": create, "start": start, "delay": delay, "conf": conf}


def gen_mcu(t, a):
    fw = "03_Firmware"
    drivers = split_list(a.drivers)
    p = ident(a.name)
    cmake = a.build == "cmake"
    api = rtos_api(a.rtos)
    t.d(f"{fw}/os", f"{fw}/hal", f"{fw}/cmsis", f"{fw}/middleware/protocol",
        f"{fw}/middleware/fs", f"{fw}/scripts")

    # config
    t.f(f"{fw}/config/version.h", c_header("version", "version", f"""
#define FW_NAME          "{a.name}"
#define FW_VERSION_MAJOR 0
#define FW_VERSION_MINOR 1
#define FW_VERSION_PATCH 0
#define FW_VERSION_STR   "0.1.0"
#define FW_BUILD_DATE    __DATE__
#define FW_BUILD_TIME    __TIME__
""", "Firmware version information (single source of truth)"))
    t.f(f"{fw}/config/app_config.h", c_header("app_config", "app_config", f"""
/* ---- target ---- */
#define CFG_CHIP "{a.chip}"
#define CFG_RTOS "{a.rtos}"

/* ---- feature switches (1 = enable) ---- */
#define CFG_ENABLE_LOG      1
#define CFG_ENABLE_WATCHDOG 1
#define CFG_ENABLE_OTA      {1 if a.bootloader else 0}

/* ---- build variant: scripts/build.sh factory passes -DCFG_FACTORY_MODE=1 ---- */
#ifndef CFG_FACTORY_MODE
#define CFG_FACTORY_MODE 0 /* 1 = factory-test firmware: self-test, calibration, burn-in */
#endif

/* ---- log level: 0=off 1=err 2=warn 3=info 4=debug (release builds define NDEBUG) ---- */
#ifndef CFG_LOG_LEVEL
#if CFG_FACTORY_MODE
#define CFG_LOG_LEVEL 3 /* factory: info, test results are printed on the debug UART */
#elif defined(NDEBUG)
#define CFG_LOG_LEVEL 2
#else
#define CFG_LOG_LEVEL 4
#endif
#endif

/* ---- task stack sizes (words) / priorities ---- */
#define CFG_TASK_MAIN_STACK 512
#define CFG_TASK_MAIN_PRIO  2
""", "Global compile-time configuration and feature switches"))

    # bsp
    t.f(f"{fw}/bsp/board.h", c_header("board", "board", f"""
#include <stdint.h>

/* Pin / peripheral mapping of THIS board ({a.chip}). Only bsp/ may know these details. */
/* #define BOARD_LED_PORT   GPIOC */
/* #define BOARD_LED_PIN    13    */

void board_init(void);
void board_led_toggle(void);
uint32_t board_get_tick_ms(void);
""", "Board support package interface"))
    t.f(f"{fw}/bsp/board.c", c_source("board", ["board.h"], """
void board_init(void)
{
    /* TODO: clock tree, GPIO, debug UART, systick */
}

void board_led_toggle(void)
{
    /* TODO */
}

uint32_t board_get_tick_ms(void)
{
    return 0; /* TODO */
}
""", "Board support package implementation"))

    # drivers
    for d in drivers:
        t.f(f"{fw}/drivers/{d}/{d}.h", c_header(d, d, f"""
#include <stdint.h>

typedef enum {{
    {d.upper()}_OK = 0,
    {d.upper()}_ERR,
    {d.upper()}_TIMEOUT,
}} {d}_status_t;

{d}_status_t {d}_init(void);
""", f"{d} device driver interface"))
        t.f(f"{fw}/drivers/{d}/{d}.c", c_source(d, [f"{d}.h", "board.h"], f"""
{d}_status_t {d}_init(void)
{{
    /* TODO: access hardware only through bsp/hal interfaces */
    return {d.upper()}_OK;
}}
""", f"{d} device driver"))
    if not drivers:
        t.d(f"{fw}/drivers")

    # middleware utils
    t.f(f"{fw}/middleware/utils/log.h", c_header("log", "log", """
#include "app_config.h"
#include <stdio.h>

/* clang-format off */
#if CFG_ENABLE_LOG
#define LOG_E(fmt, ...) do { if (CFG_LOG_LEVEL >= 1) printf("[E] " fmt "\\r\\n", ##__VA_ARGS__); } while (0)
#define LOG_W(fmt, ...) do { if (CFG_LOG_LEVEL >= 2) printf("[W] " fmt "\\r\\n", ##__VA_ARGS__); } while (0)
#define LOG_I(fmt, ...) do { if (CFG_LOG_LEVEL >= 3) printf("[I] " fmt "\\r\\n", ##__VA_ARGS__); } while (0)
#define LOG_D(fmt, ...) do { if (CFG_LOG_LEVEL >= 4) printf("[D] " fmt "\\r\\n", ##__VA_ARGS__); } while (0)
#else
#define LOG_E(...)
#define LOG_W(...)
#define LOG_I(...)
#define LOG_D(...)
#endif
/* clang-format on */
""", "Leveled logging macros"))
    t.f(f"{fw}/middleware/utils/ring_buffer.h", c_header("ring_buffer", "ring_buffer", """
#include <stdint.h>
#include <stddef.h>

typedef struct {
    uint8_t *buf;
    size_t size;
    volatile size_t head;
    volatile size_t tail;
} ring_buffer_t;

void rb_init(ring_buffer_t *rb, uint8_t *mem, size_t size);
size_t rb_write(ring_buffer_t *rb, const uint8_t *data, size_t len);
size_t rb_read(ring_buffer_t *rb, uint8_t *data, size_t len);
size_t rb_used(const ring_buffer_t *rb);
""", "Lock-free single-producer/single-consumer ring buffer"))
    t.f(f"{fw}/middleware/utils/ring_buffer.c", c_source("ring_buffer", ["ring_buffer.h"], """
void rb_init(ring_buffer_t *rb, uint8_t *mem, size_t size)
{
    rb->buf = mem;
    rb->size = size;
    rb->head = rb->tail = 0;
}

size_t rb_used(const ring_buffer_t *rb)
{
    return (rb->head + rb->size - rb->tail) % rb->size;
}

size_t rb_write(ring_buffer_t *rb, const uint8_t *data, size_t len)
{
    size_t n = 0;
    while (n < len && rb_used(rb) < rb->size - 1) {
        rb->buf[rb->head] = data[n++];
        rb->head = (rb->head + 1) % rb->size;
    }
    return n;
}

size_t rb_read(ring_buffer_t *rb, uint8_t *data, size_t len)
{
    size_t n = 0;
    while (n < len && rb->tail != rb->head) {
        data[n++] = rb->buf[rb->tail];
        rb->tail = (rb->tail + 1) % rb->size;
    }
    return n;
}
""", "Ring buffer implementation"))

    # app
    t.f(f"{fw}/app/app_tasks.h", c_header("app_tasks", "app_tasks", """
void app_tasks_create(void);
""", "Application task creation"))
    drv_inc = [f"{d}.h" for d in drivers]
    drv_init = "\n".join(f"    {d}_init();" for d in drivers) or "    /* TODO: init drivers */"
    t.f(f"{fw}/app/app_tasks.c", c_source("app_tasks", ["app_tasks.h", "app_config.h", "log.h", "board.h"] + drv_inc, f"""
void app_tasks_create(void)
{{
{api["create"]}
    (void)task_main;
}}
""", "Application tasks", priv=f"""
static void task_main(void *arg)
{{
    (void)arg;
{drv_init}
    for (;;) {{
        board_led_toggle();
        /* TODO: business logic / state machine; block with {api["delay"]} */
    }}
}}
"""))
    t.f(f"{fw}/app/main.c", c_source("main", ["board.h", "app_tasks.h", "app_config.h", "version.h", "log.h"], f"""
int main(void)
{{
    board_init();
    LOG_I("%s v%s build %s %s", FW_NAME, FW_VERSION_STR, FW_BUILD_DATE, FW_BUILD_TIME);
#if CFG_FACTORY_MODE
    LOG_I("factory test mode");
    /* TODO: self-test / calibration / burn-in; report results to 04_Tools/factory_test/ */
#endif
    app_tasks_create();
    /* TODO: {api["start"]} */
    for (;;) {{
    }}
}}
""", "Entry point: init board, create tasks, start scheduler"))

    # placeholders
    t.f(f"{fw}/os/README.md", f"Place {a.rtos} kernel source/port here. Do not modify vendor code; put its config ({api["conf"]}) in config/.\n")
    t.f(f"{fw}/hal/README.md", f"Place {a.chip} vendor HAL/LL/SDK here (generated or downloaded). Treat as read-only.\n")
    t.f(f"{fw}/cmsis/README.md", "Place CMSIS core headers, startup file (startup_xxx.s), system_xxx.c and linker script (*.ld / *.sct) here.\n")

    if a.bootloader:
        t.f(f"{fw}/bootloader/README.md", "Independent bootloader project (own build target). Responsibilities: verify image, jump to app, OTA/IAP update.\nKeep the flash partition table in 01_Docs/Design/flash_layout.md and in config/.\n")
        t.f(f"{fw}/bootloader/main.c", c_source("main", [], """
int main(void)
{
    /* 1. minimal hw init  2. check upgrade flag  3. verify app CRC  4. jump to app */
    for (;;) {
    }
}
""", "Bootloader entry"))
        t.f("01_Docs/Design/flash_layout.md", "# Flash layout\n\n| Region | Start | Size | Note |\n|---|---|---|---|\n| Bootloader | 0x08000000 | TBD | |\n| App | TBD | TBD | |\n| OTA buffer / Param | TBD | TBD | |\n")

    # test
    t.f(f"{fw}/test/test_ring_buffer.c", """
/* Host-side unit test, run by scripts/run_tests.sh
 * TEST_SRCS: middleware/utils/ring_buffer.c
 */
#undef NDEBUG
#include <assert.h>
#include <stdio.h>

#include "ring_buffer.h"

static void test_write_read(void)
{
    uint8_t mem[8];
    uint8_t out[8];
    ring_buffer_t rb;
    size_t n;

    rb_init(&rb, mem, sizeof(mem));
    n = rb_write(&rb, (const uint8_t *)"abc", 3);
    assert(n == 3);
    assert(rb_used(&rb) == 3);
    n = rb_read(&rb, out, sizeof(out));
    assert(n == 3 && out[0] == 'a' && out[2] == 'c');
    assert(rb_used(&rb) == 0);
}

static void test_full_and_wrap(void)
{
    uint8_t mem[4];
    uint8_t out[4];
    ring_buffer_t rb;
    size_t n;

    rb_init(&rb, mem, sizeof(mem));
    n = rb_write(&rb, (const uint8_t *)"abcd", 4); /* capacity is size - 1 */
    assert(n == 3);
    n = rb_read(&rb, out, 2);
    assert(n == 2 && out[0] == 'a' && out[1] == 'b');
    n = rb_write(&rb, (const uint8_t *)"xy", 2); /* head wraps around */
    assert(n == 2);
    n = rb_read(&rb, out, sizeof(out));
    assert(n == 3 && out[0] == 'c' && out[1] == 'x' && out[2] == 'y');
}

int main(void)
{
    test_write_read();
    test_full_and_wrap();
    printf("ring_buffer: all tests passed\\n");
    return 0;
}
""")

    # build
    if cmake:
        inc_dirs = " ".join(["app", "config", "bsp", "middleware/utils"]
                            + [f"drivers/{d}" for d in drivers] + ["hal", "cmsis", "os"])
        t.f(f"{fw}/CMakeLists.txt", f"""
cmake_minimum_required(VERSION 3.20)
# Build with scripts/build.sh [debug|release|factory]
project({p} C ASM)

set(CMAKE_C_STANDARD 11)
option(FACTORY_MODE "Build factory-test firmware (CFG_FACTORY_MODE=1)" OFF)
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Debug)
endif()

set(INC_DIRS {inc_dirs})
file(GLOB_RECURSE SRCS
    app/*.c bsp/*.c drivers/*.c middleware/*.c
    # hal/*.c cmsis/*.s os/*.c   <- enable after vendor code is added
)

add_executable(${{PROJECT_NAME}}.elf ${{SRCS}})
target_include_directories(${{PROJECT_NAME}}.elf PRIVATE ${{INC_DIRS}})
target_link_options(${{PROJECT_NAME}}.elf PRIVATE -Wl,-Map=${{PROJECT_NAME}}.map)
# target_link_options(${{PROJECT_NAME}}.elf PRIVATE -T${{CMAKE_SOURCE_DIR}}/cmsis/linker.ld)
if(FACTORY_MODE)
    target_compile_definitions(${{PROJECT_NAME}}.elf PRIVATE CFG_FACTORY_MODE=1)
endif()

# .bin / .hex next to the .elf (used by scripts/pack.sh)
add_custom_command(TARGET ${{PROJECT_NAME}}.elf POST_BUILD
    COMMAND ${{CMAKE_OBJCOPY}} -O binary $<TARGET_FILE:${{PROJECT_NAME}}.elf> ${{PROJECT_NAME}}.bin
    COMMAND ${{CMAKE_OBJCOPY}} -O ihex $<TARGET_FILE:${{PROJECT_NAME}}.elf> ${{PROJECT_NAME}}.hex
    WORKING_DIRECTORY ${{CMAKE_BINARY_DIR}})
""")
        t.f(f"{fw}/scripts/arm-gcc-toolchain.cmake", """
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)
set(CMAKE_C_COMPILER arm-none-eabi-gcc)
set(CMAKE_ASM_COMPILER arm-none-eabi-gcc)
set(CMAKE_OBJCOPY arm-none-eabi-objcopy)
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)
# set(MCU_FLAGS "-mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard")
set(CMAKE_C_FLAGS_INIT "${MCU_FLAGS} -ffunction-sections -fdata-sections -Wall")
set(CMAKE_EXE_LINKER_FLAGS_INIT "${MCU_FLAGS} -Wl,--gc-sections --specs=nano.specs")
""")
        t.f(f"{fw}/scripts/build.sh", r"""
#!/usr/bin/env bash
# Usage: scripts/build.sh [debug|release|factory]   (default: debug)
#   debug    -O0 -g, log level 4                      -> build/debug/
#   release  -Os, NDEBUG, log level 2                 -> build/release/
#   factory  -Os, NDEBUG, CFG_FACTORY_MODE=1, log 3   -> build/factory/
# TOOLCHAIN=<file> overrides scripts/arm-gcc-toolchain.cmake.
set -euo pipefail
cd "$(dirname "$0")/.."
VARIANT=${1:-debug}
case "$VARIANT" in
debug) ARGS="-DCMAKE_BUILD_TYPE=Debug" ;;
release) ARGS="-DCMAKE_BUILD_TYPE=MinSizeRel" ;;
factory) ARGS="-DCMAKE_BUILD_TYPE=MinSizeRel -DFACTORY_MODE=ON" ;;
*)
    echo "usage: $0 [debug|release|factory]" >&2
    exit 1
    ;;
esac
TOOLCHAIN=${TOOLCHAIN:-scripts/arm-gcc-toolchain.cmake}
# shellcheck disable=SC2086
cmake -B "build/$VARIANT" -DCMAKE_TOOLCHAIN_FILE="$TOOLCHAIN" $ARGS
cmake --build "build/$VARIANT" -j
""")
        t.f(f"{fw}/scripts/flash.sh", fill(r"""
#!/usr/bin/env bash
# Usage: scripts/flash.sh [debug|release|factory]   (default: debug)
set -euo pipefail
cd "$(dirname "$0")/.."
ELF=build/${1:-debug}/@P@.elf
# Example (ST-Link + OpenOCD):
#   openocd -f interface/stlink.cfg -f target/stm32f4x.cfg -c "program $ELF verify reset exit"
echo "TODO: flash $ELF"
""", P=p))
    else:
        proj_file = f"{p}.uvprojx" if a.build == "keil" else f"{p}.eww / {p}.ewp"
        t.f(f"{fw}/project/README.md", f"Put the {ide_name(a)} project file here (e.g. {proj_file}). Reference sources from ../app ../bsp ../drivers etc.; never copy sources into this folder.\nCreate Debug / Release / Factory targets: Release defines NDEBUG, Factory defines NDEBUG and CFG_FACTORY_MODE=1.\n")
        t.f(f"{fw}/scripts/flash.sh", f"#!/usr/bin/env bash\n# Flash the image built by {ide_name(a)} (e.g. JLink.exe / STM32_Programmer_CLI / ST-LINK_CLI).\necho \"TODO: flash command\"\n")
    t.f(f"{fw}/scripts/run_tests.sh", RUN_TESTS_MCU)
    note = fill(L(a, NOTE_ZH, NOTE_EN), TITLE=a.name)
    hint = ("run scripts/build.sh $VARIANT first" if cmake
            else f"build the $VARIANT target in {ide_name(a)} and pass its output folder")
    t.f(f"{fw}/scripts/pack.sh", fill(PACK_SH, P=p, NOTE=note, HINT=hint))

    if not a.minimal:
        t.f(f"{fw}/.clang-format", CLANG_FORMAT)
        for vd in ("hal", "cmsis", "os"):
            t.f(f"{fw}/{vd}/.clang-format", CLANG_FORMAT_OFF)
        t.f(f"{fw}/scripts/check.sh", check_script(a))

    # README
    rows = [
        ("app/", "业务逻辑、任务、状态机；不直接访问寄存器", "Business logic, tasks, state machines. No register access."),
        ("middleware/", "与硬件无关的组件（协议、文件系统、工具）", "Hardware-independent components (protocol, fs, utils)."),
        ("os/", f"{a.rtos} 内核与移植层（只读）", f"{a.rtos} kernel and port (read-only)."),
        ("drivers/", "外部器件驱动，只通过 bsp/ 访问硬件", "External device drivers; touch hardware only via bsp/."),
        ("bsp/", "唯一知道本板引脚、时钟的地方", "The only place that knows this board's pins/clocks."),
        ("hal/, cmsis/", "厂商代码（只读）", "Vendor code, read-only."),
        ("config/", "version.h（版本号）、app_config.h（功能开关、构建变体、日志等级）",
         "version.h (version), app_config.h (feature switches, build variant, log level)."),
    ]
    if a.bootloader:
        rows.append(("bootloader/", "独立的 Bootloader 工程", "Independent bootloader target."))
    rows += [
        ("test/", "主机端单元测试（test_*.c）", "Host-side unit tests (test_*.c)."),
        ("scripts/", "构建、烧录、检查、测试、打包脚本", "Build / flash / check / test / pack scripts."),
    ]
    table = "\n".join(f"| {d} | {L(a, zh, en)} |" for d, zh, en in rows)
    ide = ide_name(a)
    cmds = []
    if cmake:
        cmds += ["./scripts/build.sh debug      # debug | release | factory", "./scripts/flash.sh"]
    else:
        cmds += [L(a, f"# 在 {ide} 中打开 project/ 下的工程，编译 Debug / Release / Factory 目标",
                   f"# open the project in project/ with {ide}; build Debug / Release / Factory"), "./scripts/flash.sh"]
    cmds.append(L(a, "./scripts/run_tests.sh        # 主机端单元测试", "./scripts/run_tests.sh        # host-side unit tests"))
    if not a.minimal:
        cmds.append(L(a, "./scripts/check.sh            # 静态检查 + 格式检查（--fix 自动格式化）",
                      "./scripts/check.sh            # static check + format check (--fix formats in place)"))
    pack_cmd = "./scripts/pack.sh release" if cmake else f"./scripts/pack.sh release <{ide} output dir>"
    cmds.append(pack_cmd.ljust(29) + " " + L(a, "# 归档到 05_Release/vX.Y.Z/", "# archive to 05_Release/vX.Y.Z/"))
    cmd_block = "\n".join(cmds)
    footer = "" if a.minimal else L(a, "开发流程、分支与提交规范、发布步骤见根目录 `CONTRIBUTING.md`。",
                                    "Development loop, branch / commit rules and release steps: see `CONTRIBUTING.md` in the repo root.")
    t.f(f"{fw}/README.md", L(a, f"""
# {a.name} 固件

- 芯片：{a.chip}  |  RTOS：{a.rtos}  |  构建：{a.build}

## 分层（只能自上而下调用）

| 目录 | 职责 |
|---|---|
{table}

## 常用命令

```bash
{cmd_block}
```

{footer}
""", f"""
# {a.name} Firmware

- Chip: {a.chip}  |  RTOS: {a.rtos}  |  Build: {a.build}

## Layers (call direction: top -> bottom only)

| Dir | Role |
|---|---|
{table}

## Commands

```bash
{cmd_block}
```

{footer}
"""))


# ---------------------------------------------------------------- Linux
def gen_linux(t, a):
    fw = "03_Firmware"
    drivers = split_list(a.drivers)
    apps = split_list(a.apps) or ["main_app"]
    board = ident(a.name)
    t.d(f"{fw}/uboot/patches", f"{fw}/uboot/configs", f"{fw}/kernel/patches",
        f"{fw}/kernel/configs", f"{fw}/output")

    t.f(f"{fw}/uboot/README.md", f"Put U-Boot source as a git submodule or download it via scripts/fetch_sources.sh. Keep only patches/ and configs/{board}_defconfig under version control.\n")
    t.f(f"{fw}/kernel/README.md", f"Kernel for {a.soc}. Keep vendor kernel out of this repo (submodule/fetch script); version-control only patches/, configs/{board}_defconfig and dts/.\n")
    t.f(f"{fw}/kernel/dts/{board}.dts", f"""
// SPDX-License-Identifier: GPL-2.0
/dts-v1/;
/* #include "<{a.soc.lower()}>.dtsi" */

/ {{
\tmodel = "{a.name} board";
\tcompatible = "vendor,{board}";
}};
""")

    if a.rootfs == "buildroot":
        t.f(f"{fw}/rootfs/README.md", f"Buildroot external tree (BR2_EXTERNAL). Build: make -C <buildroot> BR2_EXTERNAL=$(pwd) {board}_defconfig && make\n")
        t.f(f"{fw}/rootfs/external.desc", f"name: {board.upper()}\ndesc: {a.name} external tree\n")
        t.f(f"{fw}/rootfs/Config.in", "".join(f'source "$BR2_EXTERNAL_{board.upper()}_PATH/package/{x}/Config.in"\n' for x in apps))
        t.f(f"{fw}/rootfs/external.mk", f"include $(sort $(wildcard $(BR2_EXTERNAL_{board.upper()}_PATH)/package/*/*.mk))\n")
        t.f(f"{fw}/rootfs/configs/{board}_defconfig", f"# Buildroot defconfig for {a.name} ({a.soc})\nBR2_ROOTFS_OVERLAY=\"$(BR2_EXTERNAL_{board.upper()}_PATH)/overlay\"\n")
        t.d(f"{fw}/rootfs/overlay/etc/init.d", f"{fw}/rootfs/package")
        for x in apps:
            t.f(f"{fw}/rootfs/package/{x}/Config.in", f"config BR2_PACKAGE_{x.upper()}\n\tbool \"{x}\"\n\thelp\n\t  {x} application of {a.name}.\n")
            t.f(f"{fw}/rootfs/package/{x}/{x}.mk", f"{x.upper()}_VERSION = 0.1.0\n{x.upper()}_SITE = $(BR2_EXTERNAL_{board.upper()}_PATH)/../apps/{x}\n{x.upper()}_SITE_METHOD = local\n$(eval $(cmake-package))\n")
    else:
        t.f(f"{fw}/rootfs/README.md", f"Yocto layer meta-{board}. Add with: bitbake-layers add-layer meta-{board}\n")
        t.f(f"{fw}/rootfs/meta-{board}/conf/layer.conf", f'BBPATH .= ":${{LAYERDIR}}"\nBBFILES += "${{LAYERDIR}}/recipes-*/*/*.bb ${{LAYERDIR}}/recipes-*/*/*.bbappend"\nBBFILE_COLLECTIONS += "{board}"\nBBFILE_PATTERN_{board} = "^${{LAYERDIR}}/"\nBBFILE_PRIORITY_{board} = "10"\nLAYERSERIES_COMPAT_{board} = "scarthgap kirkstone"\n')
        t.d(f"{fw}/rootfs/meta-{board}/recipes-core/images", f"{fw}/rootfs/meta-{board}/recipes-kernel/linux")
        for x in apps:
            t.f(f"{fw}/rootfs/meta-{board}/recipes-apps/{x}/{x}_0.1.0.bb", f'SUMMARY = "{x} application"\nLICENSE = "CLOSED"\nSRC_URI = "file://."\ninherit cmake\n')

    for d in drivers:
        t.f(f"{fw}/drivers/{d}/{d}.c", f"""
// SPDX-License-Identifier: GPL-2.0
/*
 * {d}.c - {d} kernel driver for {a.name}
 */
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/of.h>

static int {d}_probe(struct platform_device *pdev)
{{
\tdev_info(&pdev->dev, "{d} probed\\n");
\treturn 0;
}}

static const struct of_device_id {d}_of_match[] = {{
\t{{ .compatible = "vendor,{d}" }},
\t{{ }}
}};
MODULE_DEVICE_TABLE(of, {d}_of_match);

static struct platform_driver {d}_driver = {{
\t.probe  = {d}_probe,
\t.driver = {{
\t\t.name = "{d}",
\t\t.of_match_table = {d}_of_match,
\t}},
}};
module_platform_driver({d}_driver);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("{d} driver");
""")
        t.f(f"{fw}/drivers/{d}/Makefile", f"obj-m += {d}.o\nKDIR ?= ../../kernel/src\nall:\n\t$(MAKE) -C $(KDIR) M=$(PWD) modules\nclean:\n\t$(MAKE) -C $(KDIR) M=$(PWD) clean\n")
    if not drivers:
        t.d(f"{fw}/drivers")

    for x in apps:
        t.f(f"{fw}/apps/{x}/CMakeLists.txt", f"""
cmake_minimum_required(VERSION 3.16)
project({x} C)
set(CMAKE_C_STANDARD 11)
file(GLOB SRCS src/*.c)
add_executable({x} ${{SRCS}})
target_include_directories({x} PRIVATE include ../common/include)
install(TARGETS {x} DESTINATION bin)

# host tests: scripts/run_tests.sh (add unit tests with add_test)
enable_testing()
add_test(NAME {x}_version COMMAND {x} --version)
""")
        t.f(f"{fw}/apps/{x}/src/main.c", f"""
#include <stdio.h>
#include <string.h>

#include "version.h"

int main(int argc, char **argv)
{{
    if (argc > 1 && strcmp(argv[1], "--version") == 0) {{
        printf("{x} %s\\n", FW_VERSION_STR);
        return 0;
    }}
    /* TODO: application main loop */
    printf("{x} %s\\n", FW_VERSION_STR);
    return 0;
}}
""")
        t.d(f"{fw}/apps/{x}/include")
    t.f(f"{fw}/apps/common/include/version.h", c_header("version", "version", f"""
#define FW_NAME        "{a.name}"
#define FW_VERSION_STR "0.1.0"
""", "Shared version information for user-space apps"))

    t.f(f"{fw}/scripts/toolchain.cmake", "set(CMAKE_SYSTEM_NAME Linux)\nset(CMAKE_SYSTEM_PROCESSOR aarch64)\nset(CROSS_COMPILE $ENV{CROSS_COMPILE})  # e.g. aarch64-linux-gnu-\nset(CMAKE_C_COMPILER ${CROSS_COMPILE}gcc)\nset(CMAKE_CXX_COMPILER ${CROSS_COMPILE}g++)\n# set(CMAKE_SYSROOT /path/to/sysroot)\n")
    t.f(f"{fw}/scripts/env.sh", f"# source scripts/env.sh\nexport ARCH=arm64\nexport CROSS_COMPILE=aarch64-linux-gnu-\nexport BOARD={board}\nexport OUT_DIR=$(cd \"$(dirname \"${{BASH_SOURCE[0]}}\")/..\" && pwd)/output\n")
    t.f(f"{fw}/scripts/build_all.sh", "#!/usr/bin/env bash\nset -e\nsource \"$(dirname \"$0\")/env.sh\"\necho \"[1/4] u-boot\"   # TODO\necho \"[2/4] kernel + dtb\"  # TODO\necho \"[3/4] drivers + apps\"  # TODO\necho \"[4/4] rootfs\"  # TODO\n")
    t.f(f"{fw}/scripts/pack_image.sh", fill(PACK_IMAGE_LINUX, P=board,
                                            NOTE=fill(L(a, NOTE_ZH, NOTE_EN), TITLE=a.name)))
    t.f(f"{fw}/scripts/fetch_sources.sh", "#!/usr/bin/env bash\n# Fetch vendor U-Boot / kernel / Buildroot or Yocto sources into */src (git-ignored)\nset -e\necho \"TODO\"\n")
    t.f(f"{fw}/scripts/run_tests.sh", RUN_TESTS_LINUX)
    t.f(f"{fw}/.gitignore", "uboot/src/\nkernel/src/\noutput/\n*.ko\n*.mod*\nModule.symvers\nmodules.order\n")
    if not a.minimal:
        t.f(f"{fw}/.clang-format", CLANG_FORMAT)
        t.f(f"{fw}/drivers/.clang-format", CLANG_FORMAT_OFF.replace("Vendor / third-party code keeps its upstream format.",
                                                                     "Kernel modules follow the kernel coding style (checked with checkpatch.pl)."))
        t.f(f"{fw}/scripts/check.sh", check_script(a, linux=True))

    rootfs_desc = L(a, "Buildroot BR2_EXTERNAL 树" if a.rootfs == "buildroot" else "Yocto meta 层",
                    "Buildroot BR2_EXTERNAL tree" if a.rootfs == "buildroot" else "Yocto meta layer")
    cmds = ["source scripts/env.sh", "./scripts/fetch_sources.sh", "./scripts/build_all.sh",
            "./scripts/pack_image.sh".ljust(29) + L(a, "# 打包镜像，并归档到 05_Release/vX.Y.Z/", "# pack the image and archive it to 05_Release/vX.Y.Z/"),
            "./scripts/run_tests.sh".ljust(29) + L(a, "# apps/ 主机端编译 + ctest", "# host build of apps/ + ctest")]
    if not a.minimal:
        cmds.append("./scripts/check.sh".ljust(29) + L(a, "# apps/ 静态检查 + 格式检查（--fix 自动格式化）",
                                                      "# static check + format check of apps/ (--fix formats in place)"))
    cmd_block = "\n".join(cmds)
    footer = L(a, "镜像等大文件建议用 Git LFS 或制品库管理。", "Keep large images in Git LFS or an artifact repository.")
    if not a.minimal:
        footer += L(a, "开发流程、分支与提交规范、发布步骤见根目录 `CONTRIBUTING.md`。",
                    " Development loop, branch / commit rules and release steps: see `CONTRIBUTING.md` in the repo root.")
    t.f(f"{fw}/README.md", L(a, f"""
# {a.name} 固件（嵌入式 Linux）

- SoC：{a.soc}  |  rootfs：{a.rootfs}

| 目录 | 说明 |
|---|---|
| uboot/ | Bootloader 补丁 + defconfig（源码由脚本拉取，git 忽略） |
| kernel/ | 内核补丁、defconfig、dts/ |
| rootfs/ | {rootfs_desc} |
| drivers/ | 树外内核模块（内核代码风格） |
| apps/ | 用户态应用（CMake，交叉编译；都支持 --version） |
| scripts/ | env.sh、fetch_sources.sh、build_all.sh、pack_image.sh、run_tests.sh、toolchain.cmake |
| output/ | 构建产物（git 忽略） |

## 常用命令

```bash
{cmd_block}
```

{footer}
""", f"""
# {a.name} Firmware (Embedded Linux)

- SoC: {a.soc}  |  Rootfs: {a.rootfs}

| Dir | Role |
|---|---|
| uboot/ | Bootloader patches + defconfig (source fetched, git-ignored). |
| kernel/ | Kernel patches, defconfig, dts/. |
| rootfs/ | {rootfs_desc}. |
| drivers/ | Out-of-tree kernel modules (kernel coding style). |
| apps/ | User-space applications (CMake, cross-compiled; all support --version). |
| scripts/ | env.sh, fetch_sources.sh, build_all.sh, pack_image.sh, run_tests.sh, toolchain.cmake |
| output/ | Build artifacts (git-ignored). |

## Commands

```bash
{cmd_block}
```

{footer}
"""))


def root_readme(t, a):
    mcu = a.type == "mcu-rtos"
    target = (L(a, f"芯片：{a.chip} / RTOS：{a.rtos}", f"Chip: {a.chip} / RTOS: {a.rtos}") if mcu
              else L(a, f"SoC：{a.soc} / rootfs：{a.rootfs}", f"SoC: {a.soc} / Rootfs: {a.rootfs}"))
    contrib = "" if a.minimal else L(a, "- 开发闭环、合并请求自检清单、发布步骤：见 `CONTRIBUTING.md`",
                                     "- Development loop, merge request checklist, release steps: see `CONTRIBUTING.md`")
    t.f("README.md", L(a, f"""
# {a.name}

{a.desc or "TODO：用一段话描述项目。"}

- 类型：{a.type}  |  {target}
- 版本：v0.1.0  |  创建日期：{TODAY}
- 骨架：gen_embedded_skeleton.py v{GENERATOR_VERSION}

## 目录

| 目录 | 内容 |
|---|---|
| 01_Docs/ | 需求、设计、器件手册、测试、生产文档、会议纪要 |
| 02_Hardware/ | 原理图、PCB、BOM、Gerber |
| 03_Firmware/ | 源码（见 03_Firmware/README.md） |
| 04_Tools/ | 烧录工具、产测工装、上位机 |
| 05_Release/ | 各版本正式固件 + CHANGELOG.md |

## 规范

- 分支：main / develop / feature/* / release/* / hotfix/*
- 提交：`<type>(<scope>): <subject> [REQ-xxx]`，type 为 feat / fix / docs / refactor / test / chore 等
- 版本：MAJOR.MINOR.PATCH，只在 version.h 定义；发布时打 tag vX.Y.Z
- 命名：文件和函数 snake_case（`模块_动作()`），宏全大写，全局变量 `g_`，静态变量 `s_`
{contrib}
""", f"""
# {a.name}

{a.desc or "TODO: one-paragraph project description."}

- Type: {a.type}  |  {target}
- Version: v0.1.0  |  Created: {TODAY}
- Skeleton: gen_embedded_skeleton.py v{GENERATOR_VERSION}

## Directory

| Dir | Content |
|---|---|
| 01_Docs/ | Requirements, design, datasheets, tests, production docs, meeting notes |
| 02_Hardware/ | Schematic, PCB, BOM, Gerber |
| 03_Firmware/ | Source code (see 03_Firmware/README.md) |
| 04_Tools/ | Flash tools, factory test, host software |
| 05_Release/ | Released binaries per version + CHANGELOG.md |

## Conventions

- Git branches: main / develop / feature/* / release/* / hotfix/*
- Commit: `<type>(<scope>): <subject> [REQ-xxx]` with type feat / fix / docs / refactor / test / chore ...
- Version: MAJOR.MINOR.PATCH, single source in version.h; tag releases as vX.Y.Z
- Naming: files/functions snake_case (`module_action()`), macros UPPER_CASE, globals `g_`, statics `s_`
{contrib}
"""))


def print_tree(root):
    lines = [os.path.basename(root) + "/"]

    def walk(p, prefix):
        items = sorted(os.listdir(p), key=lambda x: (not os.path.isdir(os.path.join(p, x)), x))
        items = [i for i in items if i != ".gitkeep"]
        for i, name in enumerate(items):
            last = i == len(items) - 1
            full = os.path.join(p, name)
            lines.append(prefix + ("└── " if last else "├── ") + name + ("/" if os.path.isdir(full) else ""))
            if os.path.isdir(full):
                walk(full, prefix + ("    " if last else "│   "))
    walk(root, "")
    return "\n".join(lines)


SELFTEST_COMBOS = [
    ["--type", "mcu-rtos"],
    ["--type", "mcu-rtos", "--rtos", "RT-Thread", "--drivers", "bmp280,st7789", "--bootloader",
     "--ci", "github", "--lang", "en"],
    ["--type", "mcu-rtos", "--build", "keil"],
    ["--type", "mcu-rtos", "--minimal"],
    ["--type", "linux", "--apps", "gateway,webui", "--drivers", "mydev"],
    ["--type", "linux", "--rootfs", "yocto", "--ci", "github", "--lang", "en"],
]


def selftest():
    """Generate every combo above, then run its run_tests.sh and check.sh. Use after editing templates."""
    tools = {t: bool(shutil.which(t)) for t in ("gcc", "cmake", "cppcheck", "clang-format")}
    print("[selftest] tools:", ", ".join(f"{k}={'yes' if v else 'MISSING'}" for k, v in tools.items()))
    tmp = tempfile.mkdtemp(prefix="skeleton_selftest_")
    failed = 0
    for i, combo in enumerate(SELFTEST_COMBOS):
        out = os.path.join(tmp, str(i))
        steps = [("generate", [sys.executable, os.path.abspath(__file__), "--name", f"Selftest{i}",
                               "--out", out, "--no-zip"] + combo, None)]
        fw = os.path.join(out, f"Selftest{i}", "03_Firmware")
        steps.append(("run_tests.sh", ["bash", "scripts/run_tests.sh"], fw))
        if "--minimal" not in combo:
            steps.append(("check.sh", ["bash", "scripts/check.sh"], fw))
        status = "OK"
        for label, cmd, cwd in steps:
            r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
            if r.returncode != 0:
                status = f"FAIL at {label}\n{r.stdout[-1500:]}{r.stderr[-1500:]}"
                break
        failed += status != "OK"
        print(f"[selftest] {' '.join(combo)}: {status}")
    print(f"[selftest] {len(SELFTEST_COMBOS) - failed}/{len(SELFTEST_COMBOS)} passed  (output: {tmp})")
    return 1 if failed else 0


def main():
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True, help="Project name, e.g. SmartSensor")
    ap.add_argument("--type", required=True, choices=["mcu-rtos", "linux"])
    ap.add_argument("--desc", default="", help="One-line project description")
    ap.add_argument("--out", default=".", help="Output directory")
    ap.add_argument("--drivers", default="", help="Comma-separated device/kernel driver names")
    ap.add_argument("--lang", default="zh", choices=["zh", "en"], help="Language of generated docs (default zh)")
    ap.add_argument("--ci", default="gitlab", choices=["gitlab", "github", "none"],
                    help="CI config + MR/PR template (default gitlab)")
    ap.add_argument("--minimal", action="store_true",
                    help="Skip workflow files (CONTRIBUTING, CI, MR/PR template, doc templates, .editorconfig, .clang-format, check.sh)")
    # MCU
    ap.add_argument("--chip", default="STM32F407")
    ap.add_argument("--rtos", default="FreeRTOS")
    ap.add_argument("--build", default="cmake", choices=["cmake", "keil", "iar"])
    ap.add_argument("--bootloader", action="store_true", help="Add bootloader/ for OTA/IAP")
    # Linux
    ap.add_argument("--soc", default="RK3568")
    ap.add_argument("--rootfs", default="buildroot", choices=["buildroot", "yocto"])
    ap.add_argument("--apps", default="", help="Comma-separated user-space app names")
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--selftest", action="store_true",
                    help="Generate all option combos and run their run_tests.sh / check.sh (after editing templates)")
    a = ap.parse_args()
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", a.name):
        ap.error("--name: ASCII letters, digits, '_' or '-', starting with a letter (e.g. SmartSensor); "
                 "put a Chinese title in --desc")

    root = os.path.join(os.path.abspath(a.out), a.name)
    t = Tree(root)
    root_common(t, a)
    (gen_mcu if a.type == "mcu-rtos" else gen_linux)(t, a)
    if not a.minimal:
        workflow_common(t, a)
    root_readme(t, a)
    t.write()
    print(f"gen_embedded_skeleton.py v{GENERATOR_VERSION}  lang={a.lang}  ci={'none' if a.minimal else a.ci}  minimal={a.minimal}")
    print(print_tree(root))
    if not a.no_zip:
        zpath = root + ".zip"
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for dp, _, fns in os.walk(root):
                for fn in sorted(fns):
                    full = os.path.join(dp, fn)
                    z.write(full, os.path.relpath(full, os.path.dirname(root)))
        print(f"\nZIP: {zpath}")


if __name__ == "__main__":
    main()
