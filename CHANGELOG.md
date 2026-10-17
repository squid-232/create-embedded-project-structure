# Changelog / 更新记录

## 2.0.1 — 2026-10-17

- Added optional Chinese names for project material folders and project-owned explanatory documents, with active links, CI, release scripts and manifests kept in sync.
- Added root-item cleanup: classify original bundles, helper repositories and historical ZIPs into backups, tools and snapshots while preserving file contents and necessary root configuration.
- Clarified default copy-only migration versus explicitly requested relocation; added collision checks, Windows long-path coverage, file counts and SHA-256 verification.
- Added existing-project reuse and snapshot packaging exclusions to avoid overwriting projects or recursively including old archives and caches.
- Updated Chinese and English introductions; Python generator remains v2.0 without template or CLI changes.
- 新增按需中文命名、根目录冗余文件分类归档、引用/清单同步、长路径与完整性复核；保留构建约定和厂商结构。

## 2.0.0 — 2026-10-17

- Added project-type inference, output routing and existing-material archiving rules.
- Added detailed schematic, PCB, component-model, mechanical CAD and 3D-print classification; STEP-header inspection and ambiguous extension handling.
- Added copy-only migration, conflict handling, hardware-only archiving and large-file storage guidance.
- Bundled all five reference documents and retained local Codex-compatible tools and paths.
- Updated both README files with v2 capabilities and usage examples.
- Python generator remains v2.0, byte-identical after newline normalization to the previous package.
- 新增自动识别、资料归档映射、3D 文件细分、文件头判断、大文件规则和原文件保护；同步中英文说明，生成器未改变。

## 1.0.0 — 2026-10-16

- Initial public packaging of the embedded project structure skill and generator v2.0.
- Added Chinese and English introductions, installation instructions, usage examples, and MIT license.
- 首次公开发布嵌入式项目结构技能与 v2.0 生成器，提供中英文介绍、安装说明、示例和 MIT 许可证。
