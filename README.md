# DCPM - Dragusheen C++ Project Manager

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/dragusheen-studio/dcpm)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**DCPM** is a lightweight, recursive dependency manager for C++ projects. Built for performance and simplicity, it automates the management of external libraries, version locking, and CMake integration without the overhead of heavy package managers.

## Key Features

* **Interactive Project Wizard**: Initialize structured executables or libraries instantly.
* **Recursive Dependency Resolution**: Automatically crawls and installs sub-dependencies.
* **Deterministic Builds**: Ensures project stability across environments using a `dcpm.lock` file.
* **Flat-Tree Module Management**: Simplifies inclusion paths and prevents CMake recursive conflicts.
* **Smart Synchronization**: One-command alignment between your local modules and the project's lockfile.

## Installation

DCPM requires Python 3.8+, Git, and CMake.

```bash
# Clone the repository
git clone [https://github.com/dragusheen-studio/dcpm.git](https://github.com/dragusheen-studio/dcpm.git)
cd dcpm

# Install the CLI locally
pip install .
```

## Available Commands

| Command | Description |
| :--- | :--- |
| `init` | Start the interactive wizard to set up a new project. |
| `add` | Register a new dependency from a Git URL. |
| `install` | Download modules and synchronize versions using the lockfile. |
| `update` | Update dependencies to their latest versions. |
| `build` | Compile the project using CMake. |
| `run` | Execute the compiled binary. |
| `remove` | Unregister and delete a dependency. |

## Project Architecture

DCPM maintains a clean and predictable file structure:

```text
.
├── .dcpm/
│   ├── config.json  # Project manifest & dependency list
│   ├── lock.json    # Frozen Git commit hashes
│   ├── dcpm.cmake   # Generated bridge for CMake
│   └── modules/     # Installed dependencies
├── include/         # Header files
├── src/             # Source files
└── CMakeLists.txt   # Main build configuration
```

## Documentation

For detailed guides, examples, and advanced usage, please refer to the [DCPM Wiki](https://github.com/dragusheen-studio/dcpm/wiki).

## License

Distributed under the **MIT License**. See the `LICENSE` file for more information.
