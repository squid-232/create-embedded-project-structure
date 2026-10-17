# Create Embedded Project Structure

[简体中文](README.zh-CN.md) | English

A reusable Codex skill and standalone Python generator for **MCU + RTOS** and **embedded Linux** projects. Turn project requirements into a consistent directory structure, layered firmware skeleton, and practical engineering workflow.

## What it provides

- MCU templates for CMake, Keil, and IAR; FreeRTOS and RT-Thread conventions.
- Embedded Linux layouts for Buildroot and Yocto, with application and external-driver scaffolding.
- Project skeleton folders and ZIP archives, with Chinese or English generated documentation.
- Debug, release, and factory build conventions; host-side tests and quality-check scripts.
- GitHub Actions or GitLab CI templates, contribution guidelines, requirements and test-report templates.
- Guidance for architecture, EVT / DVT / PVT / MP readiness, release packaging, and optional Notion specification pages.

Templates need vendor sources, board configuration, and project-specific implementation before hardware use. Linux source-fetch and whole-image build scripts require BSP-specific completion.

## What's new in skill v2

The skill package is now **2.0.0**. The bundled Python skeleton generator remains **v2.0**, unchanged from the previous package. These additions are agent instructions and reference rules, not a new Python classification command.

- **Project-type inference:** inspect chip, RTOS and project-file evidence to distinguish MCU, Linux, heterogeneous SoCs and multiple firmware targets.
- **Output routing:** add existing-material archiving alongside directory trees, skeleton ZIPs, Notion specifications and development workflows.
- **Migration mapping:** classify documents, hardware, sources, tools and releases with source path, destination, evidence and notes; preserve vendor SDK directory structures.
- **Hardware and 3D routing:** schematics to `02_Hardware/Schematic/`; whole-board models to `PCB/3D/`; component models to `PCB/Library/3D/`; enclosures and complete assemblies to `Mechanical/`; print models to `Mechanical/print/`. All hardware paths are under `02_Hardware/`.
- **Content-based evidence:** inspect STEP headers and product names, and distinguish model `.obj` files from build outputs and assembly-source `.asm` files from CAD assemblies.
- **Copy and storage rules:** provide a mapping first; copy only when actual organization is requested, preserve originals, and leave conflicts unresolved instead of overwriting. Recommend Git LFS above 50 MB and external storage with a link and SHA-256 above 500 MB or when LFS is unavailable. Document-only and hardware-only archiving does not require a project-type decision.

Uncertain files remain in a clarification list. The standalone generator still generates skeletons; it does not automatically sort existing files.

```text
$create-embedded-project-structure
Inspect the schematics, PCB files, STEP models, manuals and example projects
in this folder. Return a classification map and unresolved items first.
```

To perform the copies, explicitly request organization into a destination folder while preserving the originals.

## Requirements

- **Python 3.12+**; the generator uses only the standard library.
- Codex for the conversational skill workflow. The generator also runs independently.
- Bash, GCC, cppcheck, and clang-format 18 for generated MCU host checks; Linux host tests also need CMake.
- Windows users can generate files with Python; run generated shell checks in a suitable Bash / WSL environment.
- Notion MCP is optional and only needed for writing Notion pages.

The skill instructions and reference documents are currently in Chinese. This repository introduction and generated project documentation support Chinese and English.

## Install the skill

Clone the repository:

```bash
git clone https://github.com/squid-232/create-embedded-project-structure.git
```

Copy `skills/create-embedded-project-structure/` into your project's `.agents/skills/` directory. Keep the full folder, including `scripts/` and `references/`.

PowerShell example, from the repository root:

```powershell
New-Item -ItemType Directory -Force 'C:\path\to\project\.agents\skills'
Copy-Item -Recurse 'skills\create-embedded-project-structure' 'C:\path\to\project\.agents\skills\'
```

Start a new Codex turn and invoke:

```text
$create-embedded-project-structure
Design an STM32F407 + FreeRTOS project named SmartSensor with a BMP280 driver,
CMake, GitHub CI, and English documentation. Generate the project skeleton ZIP.
```

## Run the generator directly

From the repository root:

```bash
# MCU + RTOS
python skills/create-embedded-project-structure/scripts/gen_embedded_skeleton.py --name SmartSensor --type mcu-rtos --chip STM32F407 --rtos FreeRTOS --build cmake --drivers bmp280,st7789 --bootloader --ci github --lang en --out ./out

# Embedded Linux
python skills/create-embedded-project-structure/scripts/gen_embedded_skeleton.py --name EdgeGateway --type linux --soc RK3568 --rootfs buildroot --apps gateway,webui --ci github --lang en --out ./out
```

Each command generates `out/<Name>/` and `out/<Name>.zip`. Use a new project name or empty output location to avoid overwriting matching template files.

| Option | Purpose |
| --- | --- |
| `--name`, `--type` | Required; type is `mcu-rtos` or `linux` |
| `--lang zh\|en` | Generated documentation language; default: Chinese |
| `--ci gitlab\|github\|none` | CI provider; default: GitLab |
| `--build cmake\|keil\|iar` | MCU build layout; default: CMake |
| `--rootfs buildroot\|yocto` | Linux root filesystem layout |
| `--minimal` | Skip workflow files; retain tests and applicable build/packaging scripts |
| `--no-zip` | Generate a folder without an archive |
| `--help` | Full command-line reference |

## Generated layout

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

MCU layering follows `app → middleware → drivers → bsp → hal/cmsis`. Vendor code stays separate from application code. Linux projects track configurations, patches, and device trees rather than copying entire vendor source trees into the repository.

## Validation

To exercise the bundled generator's six built-in combinations on Linux:

```bash
CI=1 python skills/create-embedded-project-structure/scripts/gen_embedded_skeleton.py --selftest
```

Install the check tools first. With `CI=1`, missing quality tools cause check failures instead of skipped checks. These are host-side checks; flashing, cross-compilation, and board qualification are separate steps.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Keep generated paths, reference documents, and skill behavior consistent. Report your Python version, command, and reproducible error when opening an issue.

## License

[MIT](LICENSE). Third-party SDKs, RTOS kernels, and libraries added to generated projects retain their respective licenses.
