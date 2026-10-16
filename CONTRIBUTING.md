# Contributing / 参与贡献

Issues and pull requests in English or Chinese are welcome.
欢迎使用中文或英文提交 Issue 和 Pull Request。

- Explain the project type, expected output, actual output, Python version, and reproduction command.
- 描述项目类型、预期结果、实际结果、Python 版本和复现命令。
- Keep changes focused. Update skill references and both README files when behavior or usage changes.
- 保持修改聚焦；行为或用法变化时同步更新技能参考文档和中英文 README。
- Use Python 3.12+ and run `CI=1 python skills/create-embedded-project-structure/scripts/gen_embedded_skeleton.py --selftest` on Linux after changing templates.
- 修改模板后，使用 Python 3.12+ 在 Linux 运行上述检查。需要 GCC、CMake、cppcheck 和 clang-format 18。
- Do not commit generated projects, vendor SDKs, credentials, or personal Notion links.
- 不要提交生成的项目、厂商 SDK、凭据或私人 Notion 链接。
- Contributions are provided under the repository's MIT license.
- 贡献内容遵循本仓库的 MIT 许可证。
