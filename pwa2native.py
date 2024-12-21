#!/usr/bin/env python3

import sys
import subprocess
from importlib.metadata import version, PackageNotFoundError
from typing import List, Optional

def check_dependencies():
    """Check if all required packages are installed and install if missing"""
    required = {'requests>=2.31.0', 'colorama>=0.4.6', 'pathlib>=1.0.1'}
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

# Check dependencies before importing them
check_dependencies()

# Rest of the imports
import argparse
import os
import json
from typing import Optional
import requests
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
from colorama import init, Fore, Style

# Initialize colorama
init()

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

    def fetch_manifest(self):
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

        self._download_icons()

    def _download_icons(self):
        """Download icons from manifest"""
        if not self.icons:
            return

        icons_dir = Path(self.output_dir) / "icons"
        icons_dir.mkdir(parents=True, exist_ok=True)

        for icon in self.icons:
            try:
                src = icon.get('src')
                if not src:
                    continue

                # Handle relative and absolute URLs
                icon_url = src if src.startswith('http') else f"{self.url}/{src.lstrip('/')}"

                # Download icon
                response = requests.get(icon_url, stream=True)
                if response.status_code == 200:
                    size = icon.get('sizes', 'unknown').split('x')[0]
                    ext = Path(src).suffix or '.png'
                    icon_path = icons_dir / f"icon_{size}{ext}"

                    with open(icon_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    print(f"{Fore.GREEN}Downloaded icon: {icon_path}{Style.RESET_ALL}")
                    icon['local_path'] = str(icon_path)
                else:
                    print(f"{Fore.YELLOW}Warning: Could not download icon from {icon_url}{Style.RESET_ALL}")

            except Exception as e:
                print(f"{Fore.YELLOW}Warning: Error downloading icon: {e}{Style.RESET_ALL}")

    def get_icon_for_size(self, target_size: int) -> Optional[str]:
        """Get the best matching icon for the given size"""
        if not self.icons:
            return None

        best_icon = None
        best_size_diff = float('inf')

        for icon in self.icons:
            if 'local_path' not in icon or 'sizes' not in icon:
                continue

            size = int(icon['sizes'].split('x')[0])
            size_diff = abs(size - target_size)

            if size_diff < best_size_diff:
                best_size_diff = size_diff
                best_icon = icon['local_path']

        return best_icon

    def _process_android_icon(self, source_icon: str, mipmap_dir: Path, size: int):
        """Process icon for Android with proper shape and padding"""
        try:
            from PIL import Image, ImageOps

            # Open and resize the icon
            img = Image.open(source_icon)

            # Create a square image with padding
            desired_size = size
            img = ImageOps.fit(img, (int(desired_size * 0.75), int(desired_size * 0.75)), Image.Resampling.LANCZOS)

            # Create a new square image with white background
            background = Image.new('RGBA', (desired_size, desired_size), (0, 0, 0, 0))

            # Calculate padding
            offset = (desired_size - img.size[0]) // 2

            # Paste the resized image onto the background
            background.paste(img, (offset, offset))

            # Save foreground layer
            background.save(mipmap_dir / "ic_launcher.png")

            # Create adaptive icon background (solid color from manifest)
            background_color = self.background_color or "#FFFFFF"
            adaptive_bg = Image.new('RGBA', (desired_size, desired_size), background_color)
            adaptive_bg.save(mipmap_dir / "ic_launcher_background.png")

            print(f"{Fore.GREEN}Created adaptive icon for size {size}x{size}{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.YELLOW}Warning: Could not process Android icon: {e}{Style.RESET_ALL}")
            return False

    def _process_macos_icon(self, source_icon: str, output_path: str, size: int):
        """Process icon for macOS with proper rounded corners"""
        try:
            from PIL import Image, ImageDraw

            # Open and resize the icon
            img = Image.open(source_icon)
            img = img.resize((size, size), Image.Resampling.LANCZOS)

            # Create mask for rounded corners
            mask = Image.new('L', (size, size), 0)
            draw = ImageDraw.Draw(mask)

            # Calculate corner radius (macOS style)
            radius = size // 4  # macOS-style corner radius

            # Draw rounded rectangle on mask
            draw.rounded_rectangle([(0, 0), (size-1, size-1)], radius=radius, fill=255)

            # Apply mask
            output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            output.paste(img, mask=mask)

            # Save the processed icon
            output.save(output_path)
            return True
        except Exception as e:
            print(f"{Fore.YELLOW}Warning: Could not process macOS icon: {e}{Style.RESET_ALL}")
            return False

    def package_android(self):
        """Package for Android using TWA"""
        android_dir = Path(self.output_dir) / "android"
        android_dir.mkdir(parents=True, exist_ok=True)

        # Create mipmap directories for different densities
        mipmap_densities = {
            'mdpi': 48,
            'hdpi': 72,
            'xhdpi': 96,
            'xxhdpi': 144,
            'xxxhdpi': 192
        }

        for density, size in mipmap_densities.items():
            mipmap_dir = android_dir / f"app/src/main/res/mipmap-{density}"
            mipmap_dir.mkdir(parents=True, exist_ok=True)

            # Get appropriate icon
            icon = self.get_icon_for_size(size)
            if icon:
                if self._process_android_icon(icon, mipmap_dir, size):
                    print(f"{Fore.GREEN}Added adaptive icon for {density}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Warning: No suitable icon found for {density} density{Style.RESET_ALL}")

        # Generate all necessary build files
        self._generate_android_files(android_dir)

        print(f"{Fore.GREEN}Android project generated at {android_dir}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}To build: cd dist/android && gradle wrapper && ./gradlew assembleRelease{Style.RESET_ALL}")

    def _generate_android_files(self, android_dir):
        """Generate all necessary Android build files"""
        # Create full directory structure
        java_path = android_dir / "app/src/main/java/com/pwa/wrapper"
        java_path.mkdir(parents=True, exist_ok=True)

        # Create root level build.gradle
        with open(android_dir / "build.gradle", "w") as f:
            f.write(self._get_root_gradle_config())

        # App level build.gradle
        app_dir = android_dir / "app"
        app_dir.mkdir(parents=True, exist_ok=True)
        with open(app_dir / "build.gradle", "w") as f:
            f.write(self._get_android_gradle_config())

        # settings.gradle
        with open(android_dir / "settings.gradle", "w") as f:
            f.write(self._get_settings_gradle())

        # gradle.properties
        with open(android_dir / "gradle.properties", "w") as f:
            f.write(self._get_gradle_properties())

        # AndroidManifest.xml
        manifest_dir = android_dir / "app/src/main"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        with open(manifest_dir / "AndroidManifest.xml", "w") as f:
            f.write(self._get_android_manifest())

        # MainActivity.java
        with open(java_path / "MainActivity.java", "w") as f:
            f.write(self._get_android_main_activity())

        print(f"{Fore.GREEN}Generated Android project files{Style.RESET_ALL}")

    def _get_root_gradle_config(self):
        return """buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:7.4.2'
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

task clean(type: Delete) {
    delete rootProject.buildDir
}"""

    def _get_settings_gradle(self):
        return """rootProject.name = 'PWAWrapper'
include ':app'"""

    def _get_gradle_properties(self):
        return """android.useAndroidX=true
android.enableJetifier=true
org.gradle.jvmargs=-Xmx2048m
org.gradle.parallel=true"""

    def package_ios(self):
        """Package for iOS using WKWebView"""
        print(f"Packaging {self.app_name} for iOS...")
        # TODO: Implement iOS packaging
        pass

    def package_macos(self):
        """Package for macOS using WebKit"""
        # Get appropriate icon for macOS app
        app_icon = self.get_icon_for_size(1024)  # macOS app icon size
        if not app_icon:
            print(f"{Fore.YELLOW}Warning: No suitable app icon found{Style.RESET_ALL}")

        macos_dir = Path(self.output_dir) / "macos"
        macos_dir.mkdir(parents=True, exist_ok=True)

        app_dir = macos_dir / f"{self.app_name}.app"
        contents_dir = app_dir / "Contents"
        macos_binary_dir = contents_dir / "MacOS"
        resources_dir = contents_dir / "Resources"

        # Create directory structure
        for dir_path in [macos_binary_dir, resources_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Copy icon if available
        if app_icon:
            icon_path = resources_dir / f"{self.app_name}.icns"
            try:
                # Convert PNG to ICNS (requires iconutil on macOS)
                self._convert_to_icns(app_icon, icon_path)
                print(f"{Fore.GREEN}Added app icon{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}Warning: Could not convert icon to ICNS: {e}{Style.RESET_ALL}")

        # Generate Info.plist with icon reference if available
        with open(contents_dir / "Info.plist", "w") as f:
            f.write(self._get_macos_info_plist(icon_path.name if app_icon else None))

        # Generate main.swift
        with open(macos_dir / "main.swift", "w") as f:
            f.write(self._get_macos_main_swift())

        # Generate build script
        with open(macos_dir / "build.sh", "w") as f:
            f.write(self._get_macos_build_script())

        # Make build script executable
        os.chmod(macos_dir / "build.sh", 0o755)

    def _convert_to_icns(self, png_path: str, icns_path: str):
        """Convert PNG to ICNS format for macOS"""
        # Create temporary iconset directory
        iconset_path = Path(png_path).parent / "icon.iconset"
        iconset_path.mkdir(exist_ok=True)

        # Generate different icon sizes
        sizes = [16, 32, 64, 128, 256, 512, 1024]
        for size in sizes:
            # Copy and resize icon for regular and @2x resolutions
            for scale, suffix in [(1, ''), (2, '@2x')]:
                target_size = size * scale
                output_name = f"icon_{size}x{size}{suffix}.png"
                output_path = iconset_path / output_name

                # Process icon with macOS styling
                if self._process_macos_icon(png_path, str(output_path), target_size):
                    print(f"{Fore.GREEN}Created macOS icon: {output_name}{Style.RESET_ALL}")

        # Convert iconset to icns using iconutil
        try:
            subprocess.run(['iconutil', '-c', 'icns', str(iconset_path)], check=True)
            shutil.move(str(iconset_path).replace('.iconset', '.icns'), icns_path)
        finally:
            # Clean up temporary iconset
            shutil.rmtree(iconset_path)

    def _get_macos_info_plist(self, icon_name: Optional[str] = None):
        """Generate Info.plist content with optional icon"""
        plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>{self.app_name}</string>
    <key>CFBundleIdentifier</key>
    <string>com.pwa.wrapper.{self.app_name}</string>
    <key>CFBundleName</key>
    <string>{self.app_name}</string>"""

        if icon_name:
            plist += f"""
    <key>CFBundleIconFile</key>
    <string>{icon_name}</string>"""

        plist += """
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>CFBundleSupportedPlatforms</key>
    <array>
        <string>MacOSX</string>
    </array>
</dict>
</plist>
"""
        return plist

    def package_windows(self):
        """Package for Windows using WebView2"""
        print(f"Packaging {self.app_name} for Windows...")
        # TODO: Implement Windows packaging
        pass

    def _get_android_gradle_config(self):
        return """
plugins {
    id 'com.android.application'
}

android {
    compileSdkVersion 33

    defaultConfig {
        applicationId "com.pwa.wrapper"
        minSdkVersion 19
        targetSdkVersion 33
        versionCode 1
        versionName "1.0"
    }

    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
}

dependencies {
    implementation 'androidx.browser:browser:1.4.0'
    implementation 'androidx.appcompat:appcompat:1.5.1'
}
"""

    def _get_android_manifest(self):
        return f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.pwa.wrapper">

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:roundIcon="@mipmap/ic_launcher"
        android:label="{self.app_name}"
        android:theme="@style/Theme.AppCompat.Light.NoActionBar">
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
    <uses-permission android:name="android.permission.INTERNET" />
</manifest>
"""

    def _get_android_main_activity(self):
        return f"""
package com.pwa.wrapper;

import android.app.Activity;
import android.os.Bundle;
import android.net.Uri;
import androidx.browser.customtabs.CustomTabsIntent;

public class MainActivity extends Activity {{
    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);

        String url = "{self.url}";
        CustomTabsIntent.Builder builder = new CustomTabsIntent.Builder();
        CustomTabsIntent customTabsIntent = builder.build();
        customTabsIntent.launchUrl(this, Uri.parse(url));
        finish();
    }}
}}
"""

    def _get_macos_main_swift(self):
        return f"""
import Cocoa
import WebKit

class AppDelegate: NSObject, NSApplicationDelegate {{
    var window: NSWindow!
    var webView: WKWebView!

    func applicationDidFinishLaunching(_ notification: Notification) {{
        let windowRect = NSRect(x: 0, y: 0, width: 1024, height: 768)
        window = NSWindow(
            contentRect: windowRect,
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )

        window.title = "{self.app_name}"
        window.center()

        webView = WKWebView(frame: window.contentView!.bounds)
        webView.autoresizingMask = [.width, .height]

        if let url = URL(string: "{self.url}") {{
            webView.load(URLRequest(url: url))
        }}

        window.contentView?.addSubview(webView)
        window.makeKeyAndOrderFront(nil)
    }}
}}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
"""

    def _get_macos_build_script(self):
        return f"""#!/bin/bash
swiftc main.swift \\
    -target x86_64-apple-macosx10.15 \\
    -sdk $(xcrun --show-sdk-path) \\
    -framework Cocoa \\
    -framework WebKit \\
    -o "{self.app_name}.app/Contents/MacOS/{self.app_name}"
"""

def show_logo():
    """Display the colorful PWA2Native logo"""
    logo = f"""
{Fore.CYAN}██████╗ ██╗    ██╗ █████╗ ██████╗ {Fore.WHITE}███╗   ██╗ █████╗ ███╗████╗██╗██╗   ██╗███████╗
{Fore.CYAN}██╔══██╗██║    ██║██╔══██╗╚════██╗{Fore.WHITE}████╗  ██║██╔══██╗╚══██╔══╝██║██║   ██║██╔════╝
{Fore.CYAN}██████╔╝██║ █╗ ██║███████║ █████╔╝{Fore.WHITE}██╔██╗ ██║███████║   ██║   ██║██║   ██║█████╗
{Fore.CYAN}██╔═══╝ ██║███╗██║██╔══██║██╔═══╝ {Fore.WHITE}██║╚██╗██║██╔══██║   ██║   ██║╚██╗ ██╔╝██╔══╝
{Fore.CYAN}██║     ╚███╔███╔╝██║  ██║███████╗{Fore.WHITE}██║ ╚████║██║  ██║   ██║   ██║ ╚████╔╝ ███████╗
{Fore.CYAN}╚═╝      ╚═╝╚══╝ ╚═╝  ╚═╝╚══════╝{Fore.WHITE}╚═╝  ╚═══╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═══╝  ╚══════╝
{Style.BRIGHT}{Fore.YELLOW}                                                                v0.1.0{Style.RESET_ALL}
"""
    print(logo)

def show_about():
    """Display information about the script"""
    show_logo()
    about_text = f"""
{Fore.CYAN}Convert Progressive Web Apps to Native Applications{Style.RESET_ALL}
=============================================================

{Fore.GREEN}Status:{Style.RESET_ALL} Development
{Fore.GREEN}Created by:{Style.RESET_ALL} Ismail Courr
{Fore.GREEN}GitHub:{Style.RESET_ALL} https://github.com/ismailco/PWA2Native
{Fore.GREEN}License:{Style.RESET_ALL} MIT

{Fore.YELLOW}Features:{Style.RESET_ALL}
- Android support using TWA (Trusted Web Activities)
- macOS support using WebKit
- Automatic manifest fetching and parsing
- Platform-specific build configuration generation
"""
    print(about_text)

def main():
    # Show logo at startup
    show_logo()

    parser = argparse.ArgumentParser(description='Package PWA for multiple platforms')
    parser.add_argument('url', nargs='?', help='URL of the PWA')
    parser.add_argument('--name', help='Name of the application')
    parser.add_argument('--platforms', help='Platforms to build for (android,ios,macos,windows)', default='all')
    parser.add_argument('--output', help='Output directory', default='./dist')
    parser.add_argument('--version', '-v', action='store_true', help='Show version information')
    parser.add_argument('--about', '-a', action='store_true', help='Show detailed information about PWA2Native')

    args = parser.parse_args()

    if args.about:
        show_about()
        return

    if args.version:
        print(f"{Fore.CYAN}PWA2Native{Style.RESET_ALL} v0.1.0")
        return

    if not args.url:
        parser.error('URL is required when not using --version or --about')

    # Create packager instance
    packager = PWAPackager(
        url=args.url,
        app_name=args.name or 'PWA App',
        output_dir=args.output
    )

    # First fetch and validate the manifest
    if not packager.fetch_manifest():
        print(f"{Fore.RED}Error: Could not fetch manifest from {args.url}{Style.RESET_ALL}")
        if not packager.confirm_continue():
            sys.exit(1)

    # Process platforms
    platforms = args.platforms.lower().split(',') if args.platforms != 'all' else ['android', 'ios', 'macos', 'windows']

    for platform in platforms:
        if platform == 'android':
            packager.package_android()
        elif platform == 'ios':
            packager.package_ios()
        elif platform == 'macos':
            packager.package_macos()
        elif platform == 'windows':
            packager.package_windows()
        else:
            print(f"Unknown platform: {platform}")

if __name__ == '__main__':
    main()
