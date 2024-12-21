"""Android packager for PWA2Native"""
from pathlib import Path
from typing import Dict, Any
from colorama import Fore, Style

from .base import PWAPackager
from ..utils.template import TemplateLoader

class AndroidPackager(PWAPackager):
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
                if self.icon_processor.process_android_icon(icon, mipmap_dir, size):
                    print(f"{Fore.GREEN}Added adaptive icon for {density}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Warning: No suitable icon found for {density} density{Style.RESET_ALL}")

        # Generate all necessary build files
        self._generate_android_files(android_dir)

        print(f"{Fore.GREEN}Android project generated at {android_dir}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}To build: cd dist/android && gradle wrapper && ./gradlew assembleRelease{Style.RESET_ALL}")

    def _generate_android_files(self, android_dir: Path):
        """Generate Android project files"""
        template_loader = TemplateLoader()

        # Create necessary directories
        (android_dir / "app/src/main/java/com/pwa/wrapper").mkdir(parents=True, exist_ok=True)

        # Generate manifest
        manifest_path = android_dir / "app/src/main/AndroidManifest.xml"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(manifest_path, "w") as f:
            f.write(self._get_android_manifest())

        # Generate build.gradle files
        with open(android_dir / "build.gradle", "w") as f:
            f.write(template_loader.render_template('android', 'build.gradle'))

        with open(android_dir / "app/build.gradle", "w") as f:
            f.write(template_loader.render_template('android', 'app.build.gradle', {
                'app_name': self.app_name,
                'url': self.url
            }))

        # Generate MainActivity.java
        with open(android_dir / "app/src/main/java/com/pwa/wrapper/MainActivity.java", "w") as f:
            f.write(template_loader.render_template('android', 'MainActivity.java', {
                'url': self.url
            }))

    def _get_android_manifest(self) -> str:
        """Generate Android manifest"""
        return f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.pwa.wrapper">

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:roundIcon="@mipmap/ic_launcher"
        android:label="{self.app_name}"
        android:theme="@style/Theme.AppCompat.Light.NoActionBar">

        <meta-data
            android:name="android.app.icon_background"
            android:resource="@mipmap/ic_launcher_background" />
        <meta-data
            android:name="android.app.icon_foreground"
            android:resource="@mipmap/ic_launcher_foreground" />

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
