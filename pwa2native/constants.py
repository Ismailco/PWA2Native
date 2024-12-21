"""Constants used throughout the package"""
from colorama import Fore, Style

LOGO = f"""
{Fore.CYAN}██████╗ ██╗    ██╗ █████╗ ██████╗ {Fore.WHITE}███╗   ██╗ █████╗ ███╗████╗██╗██╗   ██╗███████╗
{Fore.CYAN}██╔══██╗██║    ██║██╔══██╗╚════██╗{Fore.WHITE}████╗  ██║██╔══██╗╚══██╔══╝██║██║   ██║██╔════╝
{Fore.CYAN}██████╔╝██║ █╗ ██║███████║ █████╔╝{Fore.WHITE}██╔██╗ ██║███████║   ██║   ██║██║   ██║█████╗
{Fore.CYAN}██╔═══╝ ██║███╗██║██╔══██║██╔═══╝ {Fore.WHITE}██║╚██╗██║██╔══██║   ██║   ██║╚██╗ ██╔╝██╔══╝
{Fore.CYAN}██║     ╚███╔███╔╝██║  ██║███████╗{Fore.WHITE}██║ ╚████║██║  ██║   ██║   ██║ ╚████╔╝ ███████╗
{Fore.CYAN}╚═╝      ╚═╝╚══╝ ╚═╝  ╚═╝╚══════╝{Fore.WHITE}╚═╝  ╚═══╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═══╝  ╚══════╝
{Style.BRIGHT}{Fore.YELLOW}                                                                v0.1.0{Style.RESET_ALL}
"""

ABOUT_TEXT = f"""
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

REQUIRED_PACKAGES = {
    'requests>=2.31.0',
    'colorama>=0.4.6',
    'pathlib>=1.0.1',
    'Pillow>=9.0.0'
}

SUPPORTED_PLATFORMS = ['android', 'ios', 'macos', 'windows']
