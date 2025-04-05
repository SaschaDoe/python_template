#!/usr/bin/env python3

import os
import platform
import subprocess
import sys
import textwrap
from pathlib import Path

# --- Configuration ---
# You can adjust default versions or settings here
DEFAULT_PYTHON_VERSION = ">=3.9" # Minimum Python version compatibility

# --- Prerequisites ---
# Before running this script, ensure you have:
# * Python installed (version matching DEFAULT_PYTHON_VERSION or higher recommended).
# * Git installed and available in your system's PATH.
# * Pre-commit installed and available in your system's PATH.
# * Latest version of pip installed (run 'python -m pip install --upgrade pip' if needed).
#   (See detailed installation guide printed below if pre-commit is not found).
# ---

# --- Helper Functions ---
def run_command(command, cwd=None, check=True, suppress_output=False):
    """Runs a shell command."""
    cmd_str = ' '.join(command)
    print(f"Running command: {cmd_str}")
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True,
            encoding='utf-8', # Explicitly set encoding
            # Use shell=True cautiously if needed, but prefer list form
            # shell=False # Default and generally safer
        )
        if not suppress_output:
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                # Print stderr to stderr stream for clarity
                print(f"Stderr:\n{result.stderr}", file=sys.stderr)
        return True, result # Return success status and result object
    except FileNotFoundError:
        print(f"\nError: Command '{command[0]}' not found.", file=sys.stderr)
        print("This usually means it's not installed or its location is not included in your system's PATH environment variable.", file=sys.stderr)
        if command[0] == "pre-commit":
            print_precommit_install_instructions(file=sys.stderr)
        elif command[0] == "git":
             print("\nError: Git command not found. Please install Git and ensure its location (e.g., C:\\Program Files\\Git\\bin) is in your system's PATH.", file=sys.stderr)
        return False, None # Return failure status
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd_str}", file=sys.stderr)
        print(f"Return code: {e.returncode}", file=sys.stderr)
        print(f"Stdout:\n{e.stdout}", file=sys.stderr)
        print(f"Stderr:\n{e.stderr}", file=sys.stderr)
        return False, e # Return failure status and exception object
    except Exception as e:
        print(f"An unexpected error occurred while running {cmd_str}: {e}", file=sys.stderr)
        return False, e

def print_precommit_install_instructions(file=sys.stderr):
    """Prints detailed instructions for installing pre-commit globally, including PATH and pip troubleshooting."""
    print("------------------------------------------------------------", file=file)
    print("INSTALLING PRE-COMMIT (Recommended Method: pipx)", file=file)
    print("------------------------------------------------------------", file=file)
    print("`pre-commit` was not found. The recommended way to install it globally is using `pipx`.", file=file)
    print("However, `pipx` requires Python and Pip to be correctly configured in your PATH.", file=file)

    # Determine platform specifics
    system = platform.system()
    python_executable_cmd = "python" # Default command
    find_python_cmd = ""
    scripts_subdir = "Scripts" # Windows default
    path_sep = ";" if system == "Windows" else ":"

    if system == "Windows":
        find_python_cmd = "where.exe python"
    elif system in ["Linux", "Darwin"]: # Darwin is macOS
        find_python_cmd = "which python3" # Prefer python3 on Unix-like
        scripts_subdir = "bin"
        # Check if python3 works, fallback to python if not
        try:
            subprocess.check_call([python_executable_cmd, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
             python_executable_cmd = "python" # Fallback if 'python3' not found

    print("\nSTEP 1: Ensure Python and Pip are installed and in your PATH", file=file)
    print("----------------------------------------------------------", file=file)
    print("Open a NEW terminal/command prompt (don't use an existing one yet).", file=file)
    print("Check if Python and Pip are recognized using the default command:", file=file)
    print(f"  `{python_executable_cmd} --version`")
    print(f"  `{python_executable_cmd} -m pip --version`") # Check pip as a module of python

    print("\n>>> If the above commands fail or show errors:", file=file)

    print("\n  1a. FIND YOUR PYTHON INSTALLATION:", file=file)
    print(f"      Run: `{find_python_cmd}`")
    print(f"      This shows where the '{python_executable_cmd}' command points to.", file=file)
    print(f"      Note down the FULL PATH to the executable (e.g., C:\\Python312\\python.exe or /usr/local/bin/python3).")
    print(f"      Let's call this `<path_to_your_python_executable>`.", file=file)
    print(f"      The directory containing this executable is the one needed for the PATH.", file=file)
    print(f"      (e.g., C:\\Python312 or /usr/local/bin)", file=file)
    print("      Also note the directory containing pip/scripts (usually '<base_dir>/{}').".format(scripts_subdir), file=file)
    print(f"      (e.g., C:\\Python312\\Scripts or /usr/local/bin)", file=file)

    print("\n  1b. ADD PYTHON TO SYSTEM PATH (if needed):", file=file)
    if system == "Windows":
        print("      - Search 'Environment Variables' -> 'Edit the system environment variables'.")
        print("      - Click 'Environment Variables...'.")
        print("      - Under 'System variables' (or 'User variables'), find 'Path', select, click 'Edit...'.")
        print("      - Click 'New', add the directory containing python.exe (e.g., C:\\Python312).")
        print("      - Click 'New' AGAIN, add the corresponding 'Scripts' directory (e.g., C:\\Python312\\Scripts).")
        print("      - Click OK, OK, OK.")
    elif system in ["Linux", "Darwin"]:
        print("      - Edit your shell config file (e.g., ~/.bashrc, ~/.zshrc, ~/.profile).")
        print("      - Add/modify the PATH line (replace with your Python 'bin' directory):")
        print("        `export PATH=\"/path/to/your/python/bin:$PATH\"`")
        print("      - Save file, then run `source ~/.your_config_file` or restart terminal.")
    else:
        print("      - Consult your OS docs for modifying the PATH.")
    print("      >>> IMPORTANT: CLOSE and REOPEN your terminal after modifying the PATH! <<<", file=file)
    print("      - Try `{python_executable_cmd} --version` and `{python_executable_cmd} -m pip --version` again in the NEW terminal.", file=file)


    print("\n  1c. FIX 'No module named pip' ERROR (if it occurs):", file=file)
    print(f"      If `{python_executable_cmd} -m pip --version` gives 'No module named pip', it means pip is missing from that specific Python installation.", file=file)
    print(f"      Use the `ensurepip` module to restore it. Replace `<path_to_your_python_executable>` with the path you found in step 1a.", file=file)
    if system == "Windows":
         print("      (You might need to run this command in a terminal opened 'As Administrator'):", file=file)
         print("      `<path_to_your_python_executable> -m ensurepip --upgrade`", file=file)
         print("      Example: `C:\\Python312\\python.exe -m ensurepip --upgrade`", file=file)
    else: # Linux/macOS
         print("      (You might need to use `sudo` if Python is installed in a system location):", file=file)
         print("      `sudo <path_to_your_python_executable> -m ensurepip --upgrade`", file=file)
         print("      Example: `sudo /usr/bin/python3 -m ensurepip --upgrade`", file=file)
    print(f"      After running ensurepip, verify again:", file=file)
    print(f"      `<path_to_your_python_executable> -m pip --version`", file=file)


    print(f"\nSTEP 2: Install pipx (using the Python ({python_executable_cmd}) now in your PATH)", file=file)
    print("--------------------------------------------------------------------", file=file)
    print("Once Python and Pip are working from Step 1, install pipx.", file=file)
    print("In a NEW terminal:", file=file)
    print(f"  `{python_executable_cmd} -m pip install --user pipx`")
    print(f"  `{python_executable_cmd} -m pipx ensurepath`")
    print("\n>>> IMPORTANT: CLOSE and REOPEN your terminal AGAIN after running `ensurepath`! <<<", file=file)

    print("\nSTEP 3: Install pre-commit using pipx", file=file)
    print("---------------------------------------", file=file)
    print("In a NEW terminal (after installing pipx and restarting):", file=file)
    print("  `pipx install pre-commit`")
    print("Verify installation: `pre-commit --version`")

    print("\nSTEP 4: Re-run the setup script or `pre-commit install`", file=file)
    print("--------------------------------------------------------", file=file)
    print("Once pre-commit is installed globally via pipx, you can either:", file=file)
    print("  a) Re-run this setup script (`python setup_project.py`).")
    print("  b) Navigate to your project directory in the terminal and manually run `pre-commit install`.")
    print("------------------------------------------------------------", file=file)


def create_file(path: Path, content: str):
    """Creates a file with the given content, handling potential errors."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content.strip() + "\n"), encoding='utf-8')
        print(f"Created: {path}")
    except IOError as e:
        print(f"Error writing file {path}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred while creating {path}: {e}", file=sys.stderr)

def create_directory_structure(project_root: Path, project_name: str):
    """Creates the project directory structure with README files."""
    structure = {
        "src": {
            project_name: {
                "feature_name": {
                    "01_config": {
                        "README.md": "Configuration files and settings for the feature",
                        "container.py": '''from enum import Enum
from injector import Injector, Module, singleton
from loguru import logger
from typing import Protocol

class ScreenType(Enum):
    """Enum representing different screens in the application."""
    MAIN = "main"
    SECONDARY = "secondary"

class NavigationMediator(Protocol):
    """Protocol defining the navigation mediator interface."""
    def navigate_to(self, screen_type: ScreenType) -> None:
        """Navigate to the specified screen."""
        ...

class ApplicationModule(Module):
    """Configure application-wide dependencies."""
    
    def configure(self, binder):
        # Configure navigation mediator as singleton
        binder.bind(NavigationMediator, to=NavigationMediatorImpl, scope=singleton)
        # Add other bindings here

def create_container() -> Injector:
    """Create and configure the dependency injection container."""
    return Injector([ApplicationModule()])''',
                        "logging_config.py": '''from loguru import logger
import sys
from pathlib import Path

def setup_logging():
    """Configure default logging for the application."""
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                "level": "INFO",
            },
            {
                "sink": logs_dir / "error.log",
                "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
                "level": "ERROR",
                "rotation": "10 MB",
            }
        ]
    )'''
                    },
                    "02_io": {
                        "presentation": {
                            "components": {
                                "README.md": "Reusable UI components",
                                "custom_button.py": '''
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette

class CustomButton(QPushButton):
    """Custom styled button component."""
    
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
''',
                            },
                            "navigation": {
                                "README.md": "Navigation related components",
                                "navigation_mediator.py": '''
from typing import Protocol
from PySide6.QtWidgets import QStackedWidget
from loguru import logger
from ..components.custom_button import CustomButton
from ...01_config.container import ScreenType

class NavigationMediatorImpl:
    """Implementation of the navigation mediator."""
    
    def __init__(self, stacked_widget: QStackedWidget):
        self._stacked_widget = stacked_widget
        logger.info("Navigation mediator initialized")
    
    def navigate_to(self, screen_type: ScreenType) -> None:
        """Navigate to the specified screen."""
        logger.info(f"Navigating to screen: {screen_type.value}")
        if screen_type == ScreenType.MAIN:
            self._stacked_widget.setCurrentIndex(0)
        elif screen_type == ScreenType.SECONDARY:
            self._stacked_widget.setCurrentIndex(1)
''',
                            },
                            "screens": {
                                "main_screen": {
                                    "README.md": "Main screen components",
                                    "main_screen.py": '''
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from loguru import logger
from ...components.custom_button import CustomButton
from ...01_config.container import ScreenType

class MainScreen(QWidget):
    """Main screen of the application."""
    
    def __init__(self, navigation_mediator):
        super().__init__()
        self._navigation_mediator = navigation_mediator
        self._setup_ui()
        logger.info("Main screen initialized")
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        label = QLabel("Main Screen")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        button = CustomButton("Go to Secondary Screen")
        button.clicked.connect(lambda: self._navigation_mediator.navigate_to(ScreenType.SECONDARY))
        layout.addWidget(button)
''',
                                },
                                "secondary_screen": {
                                    "README.md": "Secondary screen components",
                                    "secondary_screen.py": '''
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from loguru import logger
from ...components.custom_button import CustomButton
from ...01_config.container import ScreenType

class SecondaryScreen(QWidget):
    """Secondary screen of the application."""
    
    def __init__(self, navigation_mediator):
        super().__init__()
        self._navigation_mediator = navigation_mediator
        self._setup_ui()
        logger.info("Secondary screen initialized")
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        label = QLabel("Secondary Screen")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        button = CustomButton("Go to Main Screen")
        button.clicked.connect(lambda: self._navigation_mediator.navigate_to(ScreenType.MAIN))
        layout.addWidget(button)
''',
                                },
                                "main_window.py": '''
from PySide6.QtWidgets import QMainWindow, QStackedWidget
from loguru import logger
from ..navigation.navigation_mediator import NavigationMediatorImpl
from .main_screen.main_screen import MainScreen
from .secondary_screen.secondary_screen import SecondaryScreen
from ...01_config.container import create_container

class MainWindow(QMainWindow):
    """Main window of the application."""
    
    def __init__(self):
        super().__init__()
        self._setup_container()
        self._setup_ui()
        logger.info("Main window initialized")
    
    def _setup_container(self):
        self._container = create_container()
    
    def _setup_ui(self):
        self.setWindowTitle("Template Application")
        self.setMinimumSize(800, 600)
        
        # Create stacked widget for screens
        self._stacked_widget = QStackedWidget()
        self.setCentralWidget(self._stacked_widget)
        
        # Create navigation mediator
        self._navigation_mediator = self._container.get(NavigationMediatorImpl)
        
        # Create and add screens
        main_screen = MainScreen(self._navigation_mediator)
        secondary_screen = SecondaryScreen(self._navigation_mediator)
        
        self._stacked_widget.addWidget(main_screen)
        self._stacked_widget.addWidget(secondary_screen)
'''
                            },
                        },
                        "services": "External service integrations and adapters"
                    },
                    "03_application": "Application use cases and business logic",
                    "04_domain": "Domain models, entities, and value objects"
                }
            }
        },
        "tests": {
            "01_config": "Tests for configuration and settings",
            "02_io": {
                "presentation": {
                    "components": "Tests for UI components",
                    "screens": {
                        "view_name": "Tests for ViewModels, Views, and Models"
                    }
                },
                "services": "Tests for service integrations"
            },
            "03_application": "Tests for application use cases",
            "04_domain": "Tests for domain models and business rules"
        }
    }

    def create_dirs_and_readme(base_path: Path, structure: dict):
        for name, content in structure.items():
            current_path = base_path / name
            current_path.mkdir(parents=True, exist_ok=True)
            
            if isinstance(content, dict):
                create_dirs_and_readme(current_path, content)
            else:
                # Create README.md with description
                readme_content = f"# {name}\n\n{content}"
                (current_path / "README.md").write_text(readme_content, encoding='utf-8')

    create_dirs_and_readme(project_root, structure)

def check_pip_version():
    """Check if pip needs to be updated and notify the user."""
    try:
        import pkg_resources
        current_version = pkg_resources.get_distribution("pip").version
        print(f"Current pip version: {current_version}")
        
        # Get latest version from PyPI
        import requests
        response = requests.get("https://pypi.org/pypi/pip/json")
        latest_version = response.json()["info"]["version"]
        
        if pkg_resources.parse_version(current_version) < pkg_resources.parse_version(latest_version):
            print(f"\nA new release of pip is available: {current_version} -> {latest_version}")
            print("To update pip, run:")
            print("python -m pip install --upgrade pip")
            print("Note: It's recommended to update pip before installing project dependencies.")
            return False
        return True
    except Exception as e:
        print(f"Warning: Could not check pip version: {e}")
        return True

def main():
    project_root = Path.cwd()
    print(f"Setting up project in: {project_root}")

    # Check pip version
    check_pip_version()
    
    # --- Get Project Name ---
    default_project_name = project_root.name.lower().replace(" ", "_").replace("-", "_")
    project_name_input = input(f"Enter project name (package name) [{default_project_name}]: ")
    project_name = project_name_input or default_project_name
    
    # Create directory structure
    create_directory_structure(project_root, project_name)

    # Create entry point file
    entry_point_content = '''
#!/usr/bin/env python3

import sys
from PySide6.QtWidgets import QApplication
from loguru import logger

from src.{project_name}.feature_name.01_config.logging_config import setup_logging
from src.{project_name}.feature_name.02_io.presentation.screens.main_window import MainWindow

def main():
    """Entry point for the application."""
    # Setup logging
    setup_logging()
    logger.info("Starting application")
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
'''

    entry_point_path = project_root / "src" / project_name / "main.py"
    create_file(entry_point_path, entry_point_content)

    # --- Define File Contents ---

    # Dynamically determine target Python version parts for config files
    py_major_minor = f"{DEFAULT_PYTHON_VERSION.replace('>=','').split('.')[0]}.{DEFAULT_PYTHON_VERSION.replace('>=','').split('.')[1]}" # e.g., "3.9"
    py_short_ver = f"py{py_major_minor.replace('.', '')}" # e.g., "py39"

    # pyproject.toml (Using f-string interpolation carefully)
    pyproject_content = f'''
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{project_name}"
version = "0.1.0"
description = "A new Python project using PySide6 and other tools."
readme = "README.md"
requires-python = "{DEFAULT_PYTHON_VERSION}"
license = {{ text = "MIT" }}
authors = [
    {{ name = "Your Name", email = "you@example.com" }}
]
classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: {py_major_minor}",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Scientific/Engineering :: Visualization",
    "Intended Audience :: Developers"
]
dependencies = [
    "loguru~=0.7",
    "PySide6~=6.6",
    "qasync~=0.23",
    "injector~=0.20",
    "typeguard~=4.1"
]

[project.urls]
Homepage = "https://github.com/your_username/{project_name}"
Issues = "https://github.com/your_username/{project_name}/issues"

[project.optional-dependencies]
dev = [
    "pre-commit~=3.6",
    "mypy~=1.9",
    "ruff~=0.4",
    "hypothesis~=6.99",
    "pytest~=8.1",
    "pytest-qt~=4.2",
    "pytest-cov~=5.0",
    "types-PySide6~=6.6"
]

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --cov=. --cov-report=term-missing"
testpaths = [
    "tests"
]
markers = [
    "fast: Tests that execute quickly",
    "slow: Tests that take longer to execute",
    "ui: Tests related to the user interface"
]

[tool.ruff]
target-version = "{py_short_ver}"
line-length = 88

[tool.ruff.lint]
select = [
    "E",
    "W",
    "F",
    "I",
    "C",
    "B",
    "UP",
    "RUF",
    "TID",
    "ARG",
    "PTH"
]
ignore = []
fixable = ["ALL"]
unfixable = []
exclude = [
    ".bzr",
    ".direnv",
    ".eggs",
    ".git",
    ".git-rewrite",
    ".hg",
    ".ipynb_checkpoints",
    ".mypy_cache",
    ".nox",
    ".pants.d",
    ".pyenv",
    ".pytest_cache",
    ".pytype",
    ".ruff_cache",
    ".svn",
    ".tox",
    ".venv",
    "venv",
    "env",
    "ENV",
    "__pypackages__",
    "_build",
    "buck-out",
    "build",
    "dist",
    "node_modules",
    "*/migrations/*"
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"

[tool.mypy]
python_version = "{py_major_minor}"
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true
'''

    # .pre-commit-config.yaml
    pre_commit_content = """
    # See https://pre-commit.com for more information
    # See https://pre-commit.com/hooks.html for more hooks
    ci:
        autofix_commit_msg: "chore: auto fixes from pre-commit hooks"
        autoupdate_commit_msg: "chore: pre-commit autoupdate"

    repos:
    -   repo: https://github.com/pre-commit/pre-commit-hooks
        rev: v4.6.0 # Check for latest tag
        hooks:
        -   id: trailing-whitespace
        -   id: end-of-file-fixer
        -   id: check-yaml
        -   id: check-added-large-files
        -   id: check-toml
        -   id: check-merge-conflict
        -   id: debug-statements

    -   repo: https://github.com/astral-sh/ruff-pre-commit
        # Ruff version. Should generally match version in pyproject.toml
        rev: v0.4.1 # Check for latest tag matching ruff version
        hooks:
        -   id: ruff
            args: [--fix, --exit-non-zero-on-fix]
        -   id: ruff-format

    -   repo: https://github.com/pre-commit/mirrors-mypy
        # MyPy version. Should generally match version in pyproject.toml
        rev: v1.9.0 # Check for latest tag matching mypy version
        hooks:
        -   id: mypy
            # args: ["--ignore-missing-imports"] # Add args if needed
            additional_dependencies:
                # Add ALL 'types-*' packages from pyproject.toml here
                - types-PySide6~=6.6 # Match pyproject.toml
                # Add other types-* packages here
                # Mypy itself (match pyproject version):
                - mypy~=1.9
    """

    # docs/README.md (Minor update to refer to script troubleshooting)
    docs_readme_content = f"""
    # Documentation for {project_name}

    This directory contains documentation for the `{project_name}` project.

    This project template was set up using a helper script and includes:
    * **Core Dependencies**: loguru, PySide6, qasync, injector, TypeGuard
    * **Development Tools**: pre-commit, mypy, ruff
    * **Testing Framework**: pytest, pytest-qt, pytest-cov, hypothesis
    * **Configuration**: `pyproject.toml`, `.pre-commit-config.yaml`, `.gitignore`

    ## Project Setup

    1.  **Prerequisites:**
        * Python ({DEFAULT_PYTHON_VERSION} or newer) - Must be correctly installed and added to system PATH.
        * Git - Must be installed and in system PATH.
        * Pre-commit - Recommended global install via `pipx`.

    2.  **Clone the Repository (if applicable):**
        ```bash
        # git clone <your-repo-url>
        # cd {project_name}
        ```

    3.  **Create and Activate Virtual Environment:**
        Using `venv` (recommended):
        ```bash
        python -m venv .venv
        # On Linux/macOS:
        source .venv/bin/activate
        # On Windows (cmd/powershell):
        # .venv\\Scripts\\activate
        ```

    4.  **Install Dependencies:**
        Install the project in editable mode along with all development dependencies:
        ```bash
        pip install -e ".[dev]"
        ```

    5.  **Set up Pre-commit Hooks:**
        This should be run once per clone/checkout. The setup script attempts this automatically. If it failed, or for new clones, run:
        ```bash
        pre-commit install
        ```
        *If the `pre-commit` command is not found or fails:* This setup script prints a detailed troubleshooting guide when it detects this failure. Follow those steps carefully (involving checking PATH, potentially fixing `pip` with `ensurepip`, and installing `pre-commit` globally via `pipx`). Once fixed, run `pre-commit install` again manually.

    ## Running the Project

    *TODO: Add specific instructions on how to run your application's main entry point.*

    ## Running Tests

    Execute the test suite using `pytest`:
    ```bash
    pytest
    ```
    * Run specific markers: `pytest -m fast`
    * Run with coverage: `pytest --cov`

    ## Linting and Formatting

    Pre-commit handles checks automatically on commit. To run manually:
    ```bash
    ruff check .
    ruff format . --check # Check formatting without changing files
    mypy . # Adjust path if using src layout, e.g., mypy src/ tests/
    ```
    To apply fixes:
    ```bash
    ruff check . --fix
    ruff format .
    ```

    ## Building the Project

    To create distributable packages (wheel, sdist):
    ```bash
    pip install build
    python -m build
    ```
    Packages appear in the `dist/` directory.
    """

    # --- Create Directories ---
    dirs_to_create = [
        project_root / "tests",
        project_root / "docs",
        # project_root / "src" / project_name # Uncomment if using src layout
    ]
    print("\nCreating directories...")
    for dir_path in dirs_to_create:
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"Ensured directory exists: {dir_path}")
            if dir_path.name == "tests":
                (dir_path / "__init__.py").touch(exist_ok=True)
        except OSError as e:
             print(f"Error creating directory {dir_path}: {e}", file=sys.stderr)

    # if (project_root / "src" / project_name).exists(): # Add __init__.py if src layout
    #    (project_root / "src" / project_name / "__init__.py").touch(exist_ok=True)

    # --- Create Files ---
    print("\nCreating configuration files...")
    create_file(project_root / "pyproject.toml", pyproject_content)
    create_file(project_root / ".pre-commit-config.yaml", pre_commit_content)
    create_file(project_root / "docs" / "README.md", docs_readme_content)

    if not (project_root / "README.md").exists():
        create_file(project_root / "README.md", f"# {project_name}\n\n*TODO: Project description*")
    if not (project_root / ".gitignore").exists():
        gitignore_content = """
        # Byte-compiled / optimized / DLL files
        __pycache__/
        *.py[cod]
        *$py.class

        # C extensions
        *.so

        # Distribution / packaging
        .Python
        build/
        develop-eggs/
        dist/
        downloads/
        eggs/
        .eggs/
        lib/
        lib64/
        parts/
        sdist/
        var/
        wheels/
        *.egg-info/
        .installed.cfg
        *.egg
        MANIFEST

        # PyInstaller
        *.manifest
        *.spec

        # Installer logs
        pip-log.txt
        pip-delete-this-directory.txt

        # Unit test / coverage reports
        htmlcov/
        .tox/
        .nox/
        .coverage
        .coverage.*
        .cache
        nosetests.xml
        coverage.xml
        *.cover
        *.py,cover
        .pytest_cache/

        # Environments
        .env
        .venv
        venv/
        env/
        ENV/
        venv.bak/
        env.bak/

        # IDE / Editor specific / Cache files
        .spyderproject
        .spyproject
        .ropeproject
        .mypy_cache/
        .pyright_cache/
        .ruff_cache/
        .pytype/
        pytype_output/
        .idea/
        .vscode/
        *.swp
        *.swo
        *~
        .project
        .settings/
        .tmproj
        *.sublime-workspace
        *.sublime-project

        # macOS / Windows specific
        .DS_Store
        Thumbs.db
        """
        create_file(project_root / ".gitignore", gitignore_content)


    # --- Initialize Git and Pre-commit ---
    print("\nInitializing Git and pre-commit...")
    git_initialized_successfully = False
    # Check if it's already a git repository
    is_git_repo = (project_root / ".git").is_dir()
    if not is_git_repo:
        print("Initializing Git repository...")
        success, _ = run_command(["git", "init"], cwd=project_root, suppress_output=True)
        if success:
             git_initialized_successfully = True
        else:
             # run_command already prints git errors if FileNotFoundError
             print("Warning: Failed to initialize Git.", file=sys.stderr)
    else:
        print("Git repository already exists.")
        git_initialized_successfully = True # Treat existing repo as success for pre-commit step

    # Install pre-commit hooks only if git init succeeded or already existed
    if git_initialized_successfully:
        print("Attempting to install pre-commit hooks...")
        success, result = run_command(["pre-commit", "install"], cwd=project_root) # Keep result
        if not success:
            # Error messages (including detailed instructions from print_precommit_install_instructions
            # if pre-commit wasn't found) are handled by run_command.
            # Add a final pointer here.
            print("\nError Detail: Failed during `pre-commit install` step.", file=sys.stderr)
            print("-> If 'pre-commit' command was not found, follow the detailed troubleshooting guide printed above.", file=sys.stderr)
            print("-> If pre-commit ran but failed, check its specific error message.", file=sys.stderr)
            print("-> Once fixed, run `pre-commit install` manually inside this project directory.", file=sys.stderr)

    # Initialize Git and make initial commit
    if git_initialized_successfully:
        print("\nAdding files to Git...")
        run_command(["git", "add", "."], cwd=project_root)
        print("Files added to Git. You can now make your initial commit with:")
        print("git commit -m \"Initial project structure\"")

    # --- Final Instructions ---
    print("\n--- Project Setup Complete! ---")
    print(f"Project '{project_name}' configured in {project_root}")
    print("\nNext Steps:")
    print("1. (IMPORTANT) Update pip to the latest version:")
    print("   python -m pip install --upgrade pip")
    print("2. (IMPORTANT) Review `pyproject.toml`: Update author details, URLs, description, check dependency versions.")
    print("3. (IMPORTANT) Review `.pre-commit-config.yaml`: Ensure hook revisions (`rev:`) match tool versions if needed, and add necessary `types-*` to mypy's `additional_dependencies`.")
    print("4. Review `docs/README.md` and add project-specific details.")
    print("5. Create and activate a virtual environment (e.g., `python -m venv .venv && source .venv/bin/activate`).")
    print("6. Install dependencies: `pip install -e \".[dev]\"`")
    print("7. Add your project code (e.g., create `src/{project_name}/__init__.py` or `{project_name}/__init__.py`).")
    print("8. Add tests to the `tests/` directory.")
    print("9. Make your first commit: `git add .` then `git commit -m \"Initial project structure\"`")
    print("   (If pre-commit hooks were installed successfully, they will run automatically.)")
    print("   (If pre-commit install failed earlier, ensure it's fixed and run `pre-commit install` before committing.)")


if __name__ == "__main__":
    main()