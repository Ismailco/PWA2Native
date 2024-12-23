"""macOS packager for PWA2Native"""
from pathlib import Path
import os
import shutil
import subprocess
from typing import Optional
from colorama import Fore, Style
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from .base import PWAPackager
from ..utils.template import TemplateLoader

class MacOSPackager(PWAPackager):
    def package_macos(self):
        """Package for macOS"""
        macos_dir = Path(self.output_dir) / "macos"
        macos_dir.mkdir(parents=True, exist_ok=True)

        # Get icon
        icon = self.get_icon_for_size(1024)  # macOS prefers large icons

        # Create app structure and files
        self._create_macos_structure(macos_dir, icon)

        print(f"{Fore.GREEN}macOS app generated at {macos_dir}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}To build: cd dist/macos && ./build.sh{Style.RESET_ALL}")

    def _create_macos_structure(self, macos_dir: Path, app_icon: Optional[str]):
        """Create macOS app bundle structure"""
        # Create app bundle directories
        app_bundle = macos_dir / f"{self.app_name}.app"
        contents = app_bundle / "Contents"
        macos = contents / "MacOS"
        resources = contents / "Resources"

        for dir_path in [app_bundle, contents, macos, resources]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Create Info.plist
        with open(contents / "Info.plist", "w") as f:
            f.write(self._get_info_plist())

        # Process and copy icon if available
        if app_icon:
            icon_path = resources / "icon.icns"
            if self._convert_to_icns(app_icon, str(icon_path)):
                print(f"{Fore.GREEN}Created app icon: {icon_path}{Style.RESET_ALL}")

        # Generate main.swift
        template_loader = TemplateLoader()
        main_swift = template_loader.render_template('macos', 'main.swift', {
            'app_name': self.app_name,
            'url': self.url,
            'navigation_links': self._generate_navigation_links(),
            'shortcuts_menu': self._generate_shortcuts_menu()
        })

        with open(macos_dir / "main.swift", "w") as f:
            f.write(main_swift)

        # Generate and make executable the build script
        build_script = template_loader.render_template('macos', 'build.sh', {
            'app_name': self.app_name
        })
        build_script_path = macos_dir / "build.sh"
        with open(build_script_path, "w") as f:
            f.write(build_script)
        os.chmod(build_script_path, 0o755)

    def _convert_to_icns(self, png_path: str, icns_path: str) -> bool:
        """Convert PNG to ICNS format for macOS"""
        try:
            # Create temporary iconset directory
            iconset_path = Path(png_path).parent / "icon.iconset"
            iconset_path.mkdir(exist_ok=True)

            # Generate different icon sizes
            sizes = [16, 32, 64, 128, 256, 512, 1024]
            for size in sizes:
                # Process icon for regular and @2x resolutions
                for scale, suffix in [(1, ''), (2, '@2x')]:
                    target_size = size * scale
                    output_name = f"icon_{size}x{size}{suffix}.png"
                    output_path = iconset_path / output_name

                    if self.icon_processor.process_macos_icon(png_path, str(output_path), target_size):
                        print(f"{Fore.GREEN}Created macOS icon: {output_name}{Style.RESET_ALL}")

            # Convert iconset to icns using iconutil
            try:
                subprocess.run(['iconutil', '-c', 'icns', str(iconset_path)], check=True)
                shutil.move(str(iconset_path).replace('.iconset', '.icns'), icns_path)
                return True
            finally:
                # Clean up temporary iconset
                shutil.rmtree(iconset_path)
        except Exception as e:
            print(f"{Fore.YELLOW}Warning: Could not create ICNS file: {e}{Style.RESET_ALL}")
            return False

    def _get_info_plist(self) -> str:
        """Generate Info.plist content"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>{self.app_name}</string>
    <key>CFBundleIconFile</key>
    <string>icon.icns</string>
    <key>CFBundleIdentifier</key>
    <string>com.pwa.wrapper.{self.app_name.lower()}</string>
    <key>CFBundleName</key>
    <string>{self.app_name}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
"""

    def _generate_shortcuts_menu(self) -> str:
        """Generate Swift code for shortcuts menu"""
        if not self.manifest or 'shortcuts' not in self.manifest:
            return "// No shortcuts available"

        shortcuts = self.manifest['shortcuts']
        if not shortcuts:
            return "// No shortcuts available"

        menu_code = [
            "let shortcutsMenuItem = NSMenuItem()",
            'let shortcutsMenu = NSMenu(title: "Shortcuts")',
            "shortcutsMenuItem.submenu = shortcutsMenu",
            ""
        ]

        for i, shortcut in enumerate(shortcuts):
            name = shortcut.get('name', '')
            url = shortcut.get('url', '')
            if name and url:
                menu_code.extend([
                    f'let menuItem{i} = NSMenuItem(',
                    f'    title: "{name}",',
                    '    action: #selector(loadURL(_:)),',
                    f'    keyEquivalent: "{str(i + 1) if i < 9 else ""}"',
                    ')',
                    f'menuItem{i}.target = self',
                    f'shortcutURLs["{name}"] = "{url}"',
                    f'shortcutsMenu.addItem(menuItem{i})',
                    ''
                ])

        menu_code.append("mainMenu.addItem(shortcutsMenuItem)")
        return "\n        ".join(menu_code)

    def _fetch_navigation_links(self) -> list:
        """Fetch navigation links from the website"""
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                nav_links = []

                # Find navigation links in common navigation elements
                for nav in soup.find_all(['nav', 'header']):
                    for link in nav.find_all('a'):
                        href = link.get('href', '')
                        text = link.get_text().strip()

                        if text and href and not href.startswith('#'):
                            # Make relative URLs absolute
                            if not href.startswith(('http://', 'https://')):
                                href = urljoin(self.url, href)
                            nav_links.append({'title': text, 'url': href})

                return nav_links
        except Exception as e:
            print(f"{Fore.YELLOW}Warning: Could not fetch navigation links: {e}{Style.RESET_ALL}")
        return []

    def _generate_navigation_links(self) -> str:
        """Generate Swift code for navigation links"""
        nav_links = self._fetch_navigation_links()

        if not nav_links:
            return "// No navigation links found"

        code_lines = []
        for i, link in enumerate(nav_links):
            code_lines.extend([
                f'let navItem{i} = NSMenuItem(',
                f'    title: "{link["title"]}",',
                '    action: #selector(loadURL(_:)),',
                '    keyEquivalent: ""',
                ')',
                f'navItem{i}.target = self',
                f'shortcutURLs["{link["title"]}"] = "{link["url"]}"',
                f'navigationMenu.addItem(navItem{i})'
            ])

        return "\n        ".join(code_lines)
