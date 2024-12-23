"""Base packager class for PWA2Native"""
from pathlib import Path
from typing import List, Optional, Dict
import requests
from colorama import Fore, Style

from ..utils.icons import IconProcessor

class PWAPackager:
    def __init__(self, url: str, app_name: str, output_dir: str):
        self.url = url.rstrip('/')  # Remove trailing slash
        self.app_name = app_name
        self.output_dir = output_dir
        self.manifest: Optional[dict] = None
        self.icons: List[dict] = []
        self.theme_color: str = "#FFFFFF"
        self.background_color: str = "#FFFFFF"
        self.display: str = "standalone"
        self.start_url: str = "/"
        self.description: str = ""
        self.icon_processor = IconProcessor(self)

    def fetch_manifest(self) -> bool:
        """Fetch and parse the web app manifest"""
        try:
            response = requests.get(f"{self.url}/manifest.json")
            if response.status_code != 200:
                print(f"{Fore.RED}Error: Could not fetch manifest from {self.url}/manifest.json{Style.RESET_ALL}")
                return False

            self.manifest = response.json()
            self._parse_manifest()
            print(f"{Fore.GREEN}Successfully fetched and parsed manifest{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}Error fetching manifest: {e}{Style.RESET_ALL}")
            return False

    def _parse_manifest(self):
        """Parse the manifest and extract necessary data"""
        if not self.manifest:
            return

        # Update app name if not provided in constructor
        if not self.app_name or self.app_name == 'PWA App':
            self.app_name = self.manifest.get('name', self.manifest.get('short_name', 'PWA App'))

        # Get icons
        self.icons = self.manifest.get('icons', [])
        if not self.icons:
            print(f"{Fore.YELLOW}Warning: No icons found in manifest{Style.RESET_ALL}")

        # Get colors and display preferences
        self.theme_color = self.manifest.get('theme_color', '#FFFFFF')
        self.background_color = self.manifest.get('background_color', '#FFFFFF')
        self.display = self.manifest.get('display', 'standalone')
        self.start_url = self.manifest.get('start_url', '/')
        self.description = self.manifest.get('description', '')

        # Download icons
        self.icon_processor.download_icons()

    def get_icon_for_size(self, target_size: int) -> Optional[str]:
        """Get the best matching icon for the given size"""
        return self.icon_processor.get_icon_for_size(target_size)

    def package_android(self):
        """Package for Android - implemented in android.py"""
        raise NotImplementedError

    def package_ios(self):
        """Package for iOS - implemented in ios.py"""
        raise NotImplementedError

    def package_macos(self):
        """Package for macOS - implemented in macos.py"""
        raise NotImplementedError

    def package_windows(self):
        """Package for Windows - implemented in windows.py"""
        raise NotImplementedError
