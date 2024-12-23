"""Dependency checker for PWA2Native"""
import sys
import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from importlib.metadata import version, PackageNotFoundError
from colorama import Fore, Style

def check_dependencies():
    """Check if all required packages are installed and install if missing"""
    required = {'requests>=2.31.0', 'colorama>=0.4.6', 'pathlib>=1.0.1', 'Pillow>=9.0.0'}
    missing = []

    for package in required:
        name = package.split('>=')[0]
        required_version = package.split('>=')[1]
        try:
            installed_version = version(name)
            if installed_version < required_version:
                missing.append(package)
        except PackageNotFoundError:
            missing.append(package)

    if missing:
        print("Missing required packages. Installing...")
        try:
            # Add --no-deps to avoid dependency conflicts
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--no-deps'] + missing)

            # Now install dependencies separately with --no-deps
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install',
                'charset-normalizer<4,>=2',
                'idna<4,>=2.5',
                'urllib3<3,>=1.21.1',
                'certifi>=2017.4.17'
            ])
            print("Successfully installed required packages!")
        except subprocess.CalledProcessError:
            print("Error: Failed to install required packages.")
            print("Please run: pip install -r requirements.txt")
            sys.exit(1)
        except Exception as e:
            print(f"Warning: {e}")
            print("The script will continue, but some features might not work as expected.")

class DependencyChecker:
    def __init__(self):
        self.platform_checks = {
            'android': self._check_android,
            'ios': self._check_ios,
            'macos': self._check_macos,
            'windows': self._check_windows
        }

    def check_platform(self, platform: str) -> bool:
        """Check if all dependencies for a specific platform are met"""
        if platform not in self.platform_checks:
            print(f"{Fore.YELLOW}Warning: Unknown platform {platform}{Style.RESET_ALL}")
            return False

        return self.platform_checks[platform]()

    def _check_android(self) -> bool:
        """Check Android development dependencies"""
        # Check for Java
        java_home = self._get_java_home()
        if not java_home:
            print(f"{Fore.RED}Error: JAVA_HOME not set or Java not found{Style.RESET_ALL}")
            return False

        # Check for Android SDK
        android_home = self._get_android_home()
        if not android_home:
            print(f"{Fore.RED}Error: ANDROID_HOME not set or Android SDK not found{Style.RESET_ALL}")
            return False

        # Check for Gradle
        if not shutil.which('gradle'):
            print(f"{Fore.RED}Error: Gradle not found in PATH{Style.RESET_ALL}")
            return False

        return True

    def _check_ios(self) -> bool:
        """Check iOS development dependencies"""
        if sys.platform != 'darwin':
            print(f"{Fore.RED}Error: iOS development requires macOS{Style.RESET_ALL}")
            return False

        # Check for Xcode
        if not shutil.which('xcodebuild'):
            print(f"{Fore.RED}Error: Xcode not found{Style.RESET_ALL}")
            return False

        return True

    def _check_macos(self) -> bool:
        """Check macOS development dependencies"""
        if sys.platform != 'darwin':
            print(f"{Fore.RED}Error: macOS development requires macOS{Style.RESET_ALL}")
            return False

        # Check for Swift
        if not shutil.which('swift'):
            print(f"{Fore.RED}Error: Swift not found{Style.RESET_ALL}")
            return False

        return True

    def _check_windows(self) -> bool:
        """Check Windows development dependencies"""
        if sys.platform != 'win32':
            print(f"{Fore.RED}Error: Windows development requires Windows{Style.RESET_ALL}")
            return False

        # Check for .NET SDK
        try:
            subprocess.run(['dotnet', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"{Fore.RED}Error: .NET SDK not found{Style.RESET_ALL}")
            return False

    def _get_java_home(self) -> Optional[Path]:
        """Get JAVA_HOME path"""
        java_home = os.environ.get('JAVA_HOME')
        if java_home and Path(java_home).exists():
            return Path(java_home)
        return None

    def _get_android_home(self) -> Optional[Path]:
        """Get ANDROID_HOME path"""
        android_home = os.environ.get('ANDROID_HOME')
        if android_home and Path(android_home).exists():
            return Path(android_home)
        return None
