"""Android packager for PWA2Native"""
from pathlib import Path
import os
import subprocess
from typing import Optional
from colorama import Fore, Style

from .base import PWAPackager
from ..utils.template import TemplateLoader

class AndroidPackager(PWAPackager):
    def package_android(self):
        """Package for Android"""
        try:
            android_dir = Path(self.output_dir) / "android"
            android_dir.mkdir(parents=True, exist_ok=True)

            # Create project structure
            self._create_android_structure(android_dir)

            # Process icon
            icon = self.get_icon_for_size(512)  # Android adaptive icon
            if icon:
                self._process_android_icon(icon, android_dir / "app/src/main/res")

            # Copy and process templates
            self._process_android_templates(android_dir)

            print(f"{Fore.GREEN}Android project created at: {android_dir}{Style.RESET_ALL}")
            print("To build the project:")
            print("1. cd dist/android")
            print("2. ./gradlew assembleRelease")

        except Exception as e:
            print(f"{Fore.RED}Error packaging for Android: {e}{Style.RESET_ALL}")

    def _create_android_structure(self, android_dir: Path):
        """Create Android project structure"""
        # Create project directories
        app_dir = android_dir / "app"
        java_dir = app_dir / "src/main/java/com/pwa/wrapper"
        res_dir = app_dir / "src/main/res"

        for dir_path in [app_dir, java_dir, res_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Create Gradle files
        self._create_gradle_files(android_dir, app_dir)

        # Create Gradle wrapper
        self._create_gradle_wrapper(android_dir)

    def _create_gradle_files(self, project_dir: Path, app_dir: Path):
        """Create necessary Gradle build files"""
        # Project-level build.gradle
        with open(project_dir / "build.gradle", "w") as f:
            f.write("""
buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.1.0'
    }
}
""")

        # Settings.gradle
        with open(project_dir / "settings.gradle", "w") as f:
            f.write("""
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "PWAWrapper"
include ':app'
""")

        # Gradle properties
        with open(project_dir / "gradle.properties", "w") as f:
            f.write("""
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true
android.defaults.buildfeatures.buildconfig=true
android.nonTransitiveRClass=true
android.suppressUnsupportedCompileSdk=33
""")

        # App-level build.gradle
        template_loader = TemplateLoader()
        app_gradle = template_loader.render_template('android', 'app.build.gradle', {
            'app_name': self.app_name
        })

        with open(app_dir / "build.gradle", "w") as f:
            f.write(app_gradle)

        # Create proguard-rules.pro
        with open(app_dir / "proguard-rules.pro", "w") as f:
            f.write("# Add any ProGuard rules here")

        # Local properties (for SDK path)
        android_sdk = os.getenv('ANDROID_SDK_ROOT') or os.getenv('ANDROID_HOME')
        if android_sdk:
            with open(project_dir / "local.properties", "w") as f:
                f.write(f"sdk.dir={android_sdk}")

    def _create_gradle_wrapper(self, project_dir: Path):
        """Create Gradle wrapper"""
        try:
            subprocess.run(['gradle', 'wrapper'], cwd=project_dir, check=True)
        except subprocess.CalledProcessError:
            print(f"{Fore.YELLOW}Warning: Could not create Gradle wrapper. Please ensure Gradle is installed.{Style.RESET_ALL}")
        except FileNotFoundError:
            print(f"{Fore.YELLOW}Warning: Gradle not found. Please install Gradle to build the Android project.{Style.RESET_ALL}")

    def _process_android_templates(self, android_dir: Path):
        """Process Android templates"""
        template_loader = TemplateLoader()

        # Copy and process MainActivity.java
        main_activity = template_loader.render_template('android', 'MainActivity.java', {
            'url': self.url,
            'app_name': self.app_name
        })

        with open(android_dir / "app/src/main/java/com/pwa/wrapper/MainActivity.java", "w") as f:
            f.write(main_activity)

        # Copy and process AndroidManifest.xml
        manifest = template_loader.render_template('android', 'AndroidManifest.xml', {
            'app_name': self.app_name
        })

        manifest_dir = android_dir / "app/src/main"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        with open(manifest_dir / "AndroidManifest.xml", "w") as f:
            f.write(manifest)

    def _process_android_icon(self, icon_path: str, res_dir: Path):
        """Process icon for Android"""
        try:
            # Create mipmap directories and process icons for each density
            densities = {
                'mdpi': 48,
                'hdpi': 72,
                'xhdpi': 96,
                'xxhdpi': 144,
                'xxxhdpi': 192
            }

            for density, size in densities.items():
                mipmap_dir = res_dir / f"mipmap-{density}"
                mipmap_dir.mkdir(parents=True, exist_ok=True)

                output_path = mipmap_dir / "ic_launcher.png"
                if self.icon_processor.process_android_icon(str(icon_path), str(output_path), size):
                    print(f"{Fore.GREEN}Created Android icon for {density}: {output_path}{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.YELLOW}Warning: Could not process Android icon: {e}{Style.RESET_ALL}")
