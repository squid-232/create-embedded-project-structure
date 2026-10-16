# 嵌入式 Linux 结构参考


嵌入式 Linux 项目的完整结构和原则。顶层的 `01_Docs`、`02_Hardware`、`04_Tools`、`05_Release`，以及 `CONTRIBUTING.md`、CI 配置、`.editorconfig` 与 MCU 项目相同，这里只说明 `03_Firmware/`。
## 目录树
```plain text
03_Firmware/
├── uboot/
│   ├── src/                 # 厂商 U-Boot 源码（fetch 获取，git 忽略）
│   ├── patches/             # 0001-xxx.patch
│   └── configs/             # <board>_defconfig
├── kernel/
│   ├── src/                 # 内核源码（git 忽略）
│   ├── patches/
│   ├── configs/             # <board>_defconfig
│   └── dts/                 # <board>.dts / .dtsi
├── rootfs/
│   # Buildroot：BR2_EXTERNAL 树
│   ├── external.desc  Config.in  external.mk
│   ├── configs/<board>_defconfig
│   ├── package/<app>/       # Config.in + <app>.mk（SITE_METHOD = local）
│   └── overlay/             # 叠加到根文件系统：etc/init.d、配置文件
│   # Yocto：meta-<board>/conf/layer.conf、recipes-*/
├── drivers/<drv>/           # 树外内核模块：<drv>.c + Makefile（obj-m）；内核代码风格，用 checkpatch.pl 检查
├── apps/
│   ├── common/include/      # version.h 等共享头文件
│   └── <app>/               # CMakeLists.txt、src/、include/；支持 --version，注册 ctest 冒烟测试
├── scripts/
│   ├── env.sh               # ARCH、CROSS_COMPILE、BOARD、OUT_DIR
│   ├── fetch_sources.sh     # 拉取 U-Boot / 内核 / Buildroot 源码
│   ├── build_all.sh         # 依次构建 uboot → kernel+dtb → drivers+apps → rootfs
│   ├── pack_image.sh        # 打包 update.img，归档到 05_Release/vX.Y.Z/（sha256sum.txt、release_note.md）
│   ├── run_tests.sh         # apps 主机端编译 + ctest
│   ├── check.sh             # apps 的 cppcheck + clang-format；drivers 用 checkpatch.pl
│   └── toolchain.cmake      # 应用交叉编译
├── output/                  # 所有产物（git 忽略）
├── .clang-format            # apps/ 代码格式（drivers/ 内 DisableFormat）
├── .gitignore
└── README.md
```
## 原则
- 仓库里只放差异部分：大体积的厂商源码用 fetch 脚本或 git submodule 获取，只提交 patches、defconfig、dts。
- 修改内核或 U-Boot 时一律导出 patch（`git format-patch`），按编号顺序应用。
- 应用用 CMake + toolchain.cmake 交叉编译，同时注册为 Buildroot package 或 Yocto recipe，保证整机镜像可以一键复现。
- 设备树中 `compatible` 与驱动的 `of_match_table` 保持一致，统一用 `vendor,<name>` 格式。
- 启动脚本、默认配置放 `rootfs/overlay/`，不要手动改 output 里的根文件系统。
- 产物统一输出到 `output/`；`pack_image.sh` 把正式镜像归档到 `05_Release/vX.Y.Z/`。镜像体积大，用 Git LFS 或制品库保存，不要直接提交到 Git。
- CI 只跑 apps 的静态检查和单元测试（`check.sh`、`run_tests.sh`）。整机镜像构建需要厂商源码和下载缓存，放在专用 runner 上（CI 文件里有注释模板）。
## Buildroot 和 Yocto 怎么选
<table header-row="true">
<tr>
<td>情况</td>
<td>选择</td>
</tr>
<tr>
<td>小团队、单产品、构建要快</td>
<td>Buildroot</td>
</tr>
<tr>
<td>厂商 BSP 基于 Yocto、多产品线、需要包管理和 SDK</td>
<td>Yocto</td>
</tr>
</table>
## 功能特性 → 目录
<table header-row="true">
<tr>
<td>功能</td>
<td>位置</td>
</tr>
<tr>
<td>OTA（SWUpdate / RAUC）</td>
<td>`rootfs/package/swupdate` 配置 + `scripts/pack_ota.sh`、A/B 分区文档</td>
</tr>
<tr>
<td>Web 管理界面</td>
<td>`apps/webui/`</td>
</tr>
<tr>
<td>MCU 协处理器</td>
<td>`03_Firmware/mcu/`（按 MCU 结构组织），Linux 部分移到 `03_Firmware/linux/`</td>
</tr>
<tr>
<td>产测</td>
<td>`04_Tools/factory_test/`、`rootfs/overlay/usr/bin/factory_test`</td>
</tr>
</table>
