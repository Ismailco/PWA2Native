"""Command-line interface for PWA2Native"""
import argparse
import sys
from typing import Optional, List

from .constants import LOGO, ABOUT_TEXT
from .utils.dependencies import check_dependencies
from .packager.android import AndroidPackager
from .packager.ios import IOSPackager
from .packager.macos import MacOSPackager
from .packager.windows import WindowsPackager
from colorama import Fore, Style, init

# Initialize colorama
init()

def show_logo():
    """Display the PWA2Native logo"""
    print(LOGO)

def show_about():
    """Display information about PWA2Native"""
    show_logo()
    print(ABOUT_TEXT)

def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Package PWA for multiple platforms')
    parser.add_argument('url', nargs='?', help='URL of the PWA')
    parser.add_argument('--name', help='Name of the application')
    parser.add_argument('--platforms', help='Platforms to build for (android,ios,macos,windows)', default='all')
    parser.add_argument('--output', help='Output directory', default='./dist')
    parser.add_argument('--version', '-v', action='store_true', help='Show version information')
    parser.add_argument('--about', '-a', action='store_true', help='Show detailed information about PWA2Native')
    return parser.parse_args()

def main():
    """Main entry point"""
    args = parse_args()

    # Show version or about info if requested
    if args.version:
        from . import __version__
        print(f"PWA2Native version {__version__}")
        sys.exit(0)
    elif args.about:
        show_about()
        sys.exit(0)

    # Show logo
    show_logo()

    # Check dependencies
    check_dependencies()

    if not args.url:
        print(f"{Fore.RED}Error: URL is required{Style.RESET_ALL}")
        sys.exit(1)

    # Process platforms
    platforms = args.platforms.lower().split(',') if args.platforms != 'all' else ['android', 'ios', 'macos', 'windows']

    # Create packager instances for each platform
    packagers = {
        'android': AndroidPackager,
        'ios': IOSPackager,
        'macos': MacOSPackager,
        'windows': WindowsPackager
    }

    for platform in platforms:
        if platform in packagers:
            # Create platform-specific packager
            packager = packagers[platform](
                url=args.url,
                app_name=args.name or 'PWA App',
                output_dir=args.output
            )

            # Fetch and validate the manifest
            if not packager.fetch_manifest():
                print(f"{Fore.RED}Error: Could not fetch manifest from {args.url}{Style.RESET_ALL}")
                continue

            # Package for the platform
            try:
                if platform == 'android':
                    packager.package_android()
                elif platform == 'ios':
                    packager.package_ios()
                elif platform == 'macos':
                    packager.package_macos()
                elif platform == 'windows':
                    packager.package_windows()
            except Exception as e:
                print(f"{Fore.RED}Error packaging for {platform}: {e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Warning: Unknown platform: {platform}{Style.RESET_ALL}")

if __name__ == '__main__':
    main()
