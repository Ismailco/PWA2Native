"""iOS packager for PWA2Native"""
from pathlib import Path
import os
from typing import Optional
from colorama import Fore, Style
import json

from .base import PWAPackager
from ..utils.template import TemplateLoader

class IOSPackager(PWAPackager):
    def package_ios(self):
        """Package for iOS"""
        ios_dir = Path(self.output_dir) / "ios"
        ios_dir.mkdir(parents=True, exist_ok=True)

        # Get icon
        icon = self.get_icon_for_size(1024)  # iOS requires 1024x1024 icon

        # Create Xcode project structure
        self._create_ios_structure(ios_dir, icon)

        print(f"{Fore.GREEN}iOS project generated at {ios_dir}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Open the Xcode project and build using Xcode{Style.RESET_ALL}")

    def _create_ios_structure(self, ios_dir: Path, app_icon: Optional[str]):
        """Create iOS project structure"""
        # Create project directories
        project_name = self.app_name.replace(" ", "")
        project_dir = ios_dir / project_name
        for dir_path in [
            project_dir,
            project_dir / "Assets.xcassets",
            project_dir / "Assets.xcassets/AppIcon.appiconset"
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Generate template files
        template_loader = TemplateLoader()

        # Generate AppDelegate.swift
        with open(project_dir / "AppDelegate.swift", "w") as f:
            f.write(template_loader.render_template('ios', 'AppDelegate.swift', {
                'app_name': self.app_name
            }))

        # Generate ViewController.swift
        with open(project_dir / "ViewController.swift", "w") as f:
            f.write(template_loader.render_template('ios', 'ViewController.swift', {
                'url': self.url
            }))

        # Generate Info.plist
        with open(project_dir / "Info.plist", "w") as f:
            f.write(self._get_info_plist())

        # Process app icon if available
        if app_icon:
            self._process_ios_icons(app_icon, project_dir / "Assets.xcassets/AppIcon.appiconset")

        # Generate project.pbxproj
        with open(project_dir / f"{project_name}.xcodeproj/project.pbxproj", "w") as f:
            f.write(template_loader.render_template('ios', 'project.pbxproj', {
                'project_name': project_name
            }))

    def _process_ios_icons(self, source_icon: str, iconset_dir: Path):
        """Process icons for iOS"""
        # iOS icon sizes
        icon_sizes = {
            '20x20': ['40', '60'],  # 2x, 3x
            '29x29': ['58', '87'],  # 2x, 3x
            '40x40': ['80', '120'], # 2x, 3x
            '60x60': ['120', '180'], # 2x, 3x
            '76x76': ['152'],       # 2x
            '83.5x83.5': ['167'],   # 2x
            '1024x1024': ['1024']   # 1x
        }

        # Contents.json template for icon set
        contents = {
            "images": [],
            "info": {
                "version": 1,
                "author": "pwa2native"
            }
        }

        for base_size, multipliers in icon_sizes.items():
            base = float(base_size.split('x')[0])
            for size in multipliers:
                target_size = int(size)
                scale = f"{target_size/base}x"

                icon_name = f"icon_{target_size}.png"
                if self.icon_processor.process_ios_icon(source_icon, str(iconset_dir / icon_name), target_size):
                    contents["images"].append({
                        "size": base_size,
                        "idiom": "iphone" if base != 1024 else "ios-marketing",
                        "filename": icon_name,
                        "scale": scale
                    })

        # Write Contents.json
        with open(iconset_dir / "Contents.json", "w") as f:
            json.dump(contents, f, indent=2)

    def _get_info_plist(self) -> str:
        """Generate Info.plist content"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>$(EXECUTABLE_NAME)</string>
    <key>CFBundleIdentifier</key>
    <string>com.pwa.wrapper.{self.app_name.lower()}</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>{self.app_name}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSRequiresIPhoneOS</key>
    <true/>
    <key>UILaunchStoryboardName</key>
    <string>LaunchScreen</string>
    <key>UIRequiredDeviceCapabilities</key>
    <array>
        <string>armv7</string>
    </array>
    <key>UISupportedInterfaceOrientations</key>
    <array>
        <string>UIInterfaceOrientationPortrait</string>
        <string>UIInterfaceOrientationLandscapeLeft</string>
        <string>UIInterfaceOrientationLandscapeRight</string>
    </array>
</dict>
</plist>
"""
