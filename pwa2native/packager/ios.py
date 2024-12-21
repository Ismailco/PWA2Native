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
        project_source_dir = project_dir / project_name
        xcodeproj_dir = project_dir / f"{project_name}.xcodeproj"

        for dir_path in [
            project_dir,
            project_source_dir,
            project_source_dir / "Assets.xcassets",
            project_source_dir / "Assets.xcassets/AppIcon.appiconset",
            xcodeproj_dir
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Generate template files
        template_loader = TemplateLoader()

        # Generate AppDelegate.swift
        with open(project_source_dir / "AppDelegate.swift", "w") as f:
            f.write(template_loader.render_template('ios', 'AppDelegate.swift', {
                'app_name': self.app_name
            }))

        # Generate ViewController.swift
        with open(project_source_dir / "ViewController.swift", "w") as f:
            f.write(template_loader.render_template('ios', 'ViewController.swift', {
                'url': self.url
            }))

        # Generate Info.plist
        with open(project_source_dir / "Info.plist", "w") as f:
            f.write(self._get_info_plist())

        # Process app icon if available
        if app_icon:
            self._process_ios_icons(app_icon, project_source_dir / "Assets.xcassets/AppIcon.appiconset")

        # Generate project.pbxproj
        with open(xcodeproj_dir / "project.pbxproj", "w") as f:
            f.write(template_loader.render_template('ios', 'project.pbxproj', {
                'project_name': project_name
            }))

        # Generate build script
        build_script = template_loader.render_template('ios', 'build.sh', {
            'project_name': project_name
        })
        build_script_path = project_dir / "build.sh"
        with open(build_script_path, "w") as f:
            f.write(build_script)

        # Make build script executable
        os.chmod(build_script_path, 0o755)

        print(f"{Fore.GREEN}iOS project created at: {project_dir}{Style.RESET_ALL}")
        print("To build the project:")
        print("1. cd dist/ios/<project_name>")
        print("2. ./build.sh")

    def _process_ios_icons(self, source_icon: str, iconset_dir: Path):
        """Process icons for iOS"""
        # iOS icon sizes
        icon_sizes = {
            '20x20': ['40', '60'],      # 2x, 3x for notifications
            '29x29': ['58', '87'],      # 2x, 3x for settings
            '40x40': ['80', '120'],     # 2x, 3x for spotlight
            '60x60': ['120', '180'],    # 2x, 3x for app icon
            '1024x1024': ['1024']       # App Store
        }

        # Contents.json template
        contents = {
            "images": [],
            "info": {
                "version": 1,
                "author": "pwa2native"
            }
        }

        # Process each icon size
        for base_size, multipliers in icon_sizes.items():
            base = float(base_size.split('x')[0])
            for size in multipliers:
                target_size = int(size)
                scale = f"{target_size/base}x"
                icon_name = f"icon_{target_size}.png"

                # Process icon
                if self.icon_processor.process_ios_icon(source_icon, str(iconset_dir / icon_name), target_size):
                    contents["images"].append({
                        "size": f"{base}x{base}",
                        "idiom": "iphone" if base != 1024 else "ios-marketing",
                        "scale": scale,
                        "filename": icon_name
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
