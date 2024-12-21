#!/usr/bin/env python3

import sys
import subprocess
from importlib.metadata import version, PackageNotFoundError

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
        self.url = url
        self.app_name = app_name
        self.output_dir = output_dir
        self.manifest: Optional[dict] = None

    def fetch_manifest(self):
        """Fetch and parse the web app manifest"""
        try:
            response = requests.get(f"{self.url}/manifest.json")
            self.manifest = response.json()
            return True
        except Exception as e:
            print(f"Error fetching manifest: {e}")
            return False

    def package_android(self):
        """Package for Android using TWA"""
        android_dir = Path(self.output_dir) / "android"
        android_dir.mkdir(parents=True, exist_ok=True)

        # Create basic Android project structure
        project_dirs = [
            "app/src/main/java/com/pwa/wrapper",
            "app/src/main/res/values",
            "app/src/main/res/mipmap"
        ]
        for dir_path in project_dirs:
            (android_dir / dir_path).mkdir(parents=True, exist_ok=True)

        # Generate all necessary build files
        self._generate_android_files(android_dir)

        print(f"Android project generated at {android_dir}")
        print("To build: cd dist/android && gradle wrapper && ./gradlew assembleRelease")

    def _generate_android_files(self, android_dir):
        """Generate all necessary Android build files"""
        # Root level build.gradle
        with open(android_dir / "build.gradle", "w") as f:
            f.write(self._get_root_gradle_config())

        # App level build.gradle
        with open(android_dir / "app/build.gradle", "w") as f:
            f.write(self._get_android_gradle_config())

        # settings.gradle
        with open(android_dir / "settings.gradle", "w") as f:
            f.write(self._get_settings_gradle())

        # gradle.properties
        with open(android_dir / "gradle.properties", "w") as f:
            f.write(self._get_gradle_properties())

        # AndroidManifest.xml
        with open(android_dir / "app/src/main/AndroidManifest.xml", "w") as f:
            f.write(self._get_android_manifest())

        # MainActivity.java
        with open(android_dir / "app/src/main/java/com/pwa/wrapper/MainActivity.java", "w") as f:
            f.write(self._get_android_main_activity())

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
        macos_dir = Path(self.output_dir) / "macos"
        macos_dir.mkdir(parents=True, exist_ok=True)

        app_dir = macos_dir / f"{self.app_name}.app"
        contents_dir = app_dir / "Contents"
        macos_binary_dir = contents_dir / "MacOS"
        resources_dir = contents_dir / "Resources"

        # Create directory structure
        for dir_path in [macos_binary_dir, resources_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Generate Info.plist
        with open(contents_dir / "Info.plist", "w") as f:
            f.write(self._get_macos_info_plist())

        # Generate main.swift
        with open(macos_dir / "main.swift", "w") as f:
            f.write(self._get_macos_main_swift())

        # Generate build script
        with open(macos_dir / "build.sh", "w") as f:
            f.write(self._get_macos_build_script())

        # Make build script executable
        os.chmod(macos_dir / "build.sh", 0o755)

        print(f"macOS project generated at {macos_dir}")
        print("To build: cd dist/macos && ./build.sh")

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

    def _get_macos_info_plist(self):
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>{self.app_name}</string>
    <key>CFBundleIdentifier</key>
    <string>com.pwa.wrapper.{self.app_name}</string>
    <key>CFBundleName</key>
    <string>{self.app_name}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
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
{Fore.CYAN}██████╗ ██╗    ██╗ █████╗ ██████╗ {Fore.WHITE}███╗   ██╗ █████╗ ███��████╗██╗██╗   ██╗███████╗
{Fore.CYAN}██╔══██╗██║    ██║██╔══██╗╚════██╗{Fore.WHITE}████╗  ██║██╔══██╗╚══██╔══╝██║██║   ██║██╔════╝
{Fore.CYAN}██████╔╝██║ █╗ ██║███████║ █████╔╝{Fore.WHITE}██╔██╗ ██║███████║   ██║   ██║██║   ██║█████╗
{Fore.CYAN}██╔═══╝ ██║███╗██║██╔══██║██╔═══╝ {Fore.WHITE}██║╚██╗██║██╔══██║   ██║   ██║╚██╗ ██╔╝██╔══╝
{Fore.CYAN}██║     ╚███╔███╔╝██║  ██║███████╗{Fore.WHITE}██║ ╚████║██║  ██║   ██║   ██║ ╚████╔╝ ███████╗
{Fore.CYAN}╚═╝      ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝{Fore.WHITE}╚═╝  ╚═══╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═══╝  ╚══════╝
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

    packager = PWAPackager(
        url=args.url,
        app_name=args.name or 'PWA App',
        output_dir=args.output
    )

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
