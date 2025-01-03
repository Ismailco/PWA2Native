"""Icon processing utilities for PWA2Native"""
from pathlib import Path
import requests
from typing import Optional, Dict, Any
from colorama import Fore, Style
from PIL import Image, ImageOps, ImageDraw

class IconProcessor:
    def __init__(self, packager):
        self.packager = packager
        self.icons_dir = Path(packager.output_dir) / "icons"
        self.icons_dir.mkdir(parents=True, exist_ok=True)

    def download_icons(self):
        """Download icons from manifest"""
        if not self.packager.icons:
            return

        for icon in self.packager.icons:
            try:
                src = icon.get('src')
                if not src:
                    continue

                # Handle relative and absolute URLs
                icon_url = src if src.startswith('http') else f"{self.packager.url}/{src.lstrip('/')}"

                # Download icon
                response = requests.get(icon_url, stream=True)
                if response.status_code == 200:
                    size = icon.get('sizes', 'unknown').split('x')[0]
                    ext = Path(src).suffix or '.png'
                    icon_path = self.icons_dir / f"icon_{size}{ext}"

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
        if not self.packager.icons:
            return None

        best_icon = None
        best_size_diff = float('inf')

        for icon in self.packager.icons:
            if 'local_path' not in icon or 'sizes' not in icon:
                continue

            size = int(icon['sizes'].split('x')[0])
            size_diff = abs(size - target_size)

            if size_diff < best_size_diff:
                best_size_diff = size_diff
                best_icon = icon['local_path']

        return best_icon

    def process_android_icon(self, source_icon: str, output_path: str, size: int) -> bool:
        """Process icon for Android with proper shape and padding"""
        try:
            from PIL import Image, ImageOps

            # Open and resize the icon
            icon = Image.open(source_icon)
            icon = icon.resize((size, size), Image.Resampling.LANCZOS)

            # Create circular mask
            mask = Image.new('L', (size, size), 0)
            ImageOps.fit(icon, mask.size, centering=(0.5, 0.5))

            # Save the processed icon
            icon.save(output_path, 'PNG')
            return True

        except Exception as e:
            print(f"Error processing icon: {e}")
            return False

    def process_macos_icon(self, source_icon: str, output_path: str, size: int) -> bool:
        """Process icon for macOS with proper rounded corners"""
        try:
            # Open and resize the icon
            img = Image.open(source_icon)

            # Calculate the target size (macOS icons are typically 80% of the container)
            target_size = int(size * 0.8)
            img = img.resize((target_size, target_size), Image.Resampling.LANCZOS)

            # Create new image with padding
            padded = Image.new('RGBA', (size, size), (0, 0, 0, 0))

            # Calculate padding
            padding = (size - target_size) // 2

            # Create mask for rounded corners
            mask = Image.new('L', (target_size, target_size), 0)
            draw = ImageDraw.Draw(mask)

            # Calculate corner radius (macOS style)
            radius = target_size // 4

            # Draw rounded rectangle on mask
            draw.rounded_rectangle([0, 0, target_size, target_size], radius=radius, fill=255)

            # Apply mask to resized image
            img.putalpha(mask)

            # Paste onto padded background
            padded.paste(img, (padding, padding))

            # Save the processed icon
            padded.save(output_path)
            return True
        except Exception as e:
            print(f"{Fore.YELLOW}Warning: Could not process macOS icon: {e}{Style.RESET_ALL}")
            return False

    def process_ios_icon(self, source_icon: str, output_path: str, size: int) -> bool:
        """Process icon for iOS with proper shape and padding"""
        try:
            from PIL import Image, ImageOps

            # Open and resize the icon
            icon = Image.open(source_icon)

            # Convert to RGBA if needed
            if icon.mode != 'RGBA':
                icon = icon.convert('RGBA')

            # Create a square image with the target size
            icon = ImageOps.fit(icon, (size, size), Image.Resampling.LANCZOS)

            # Add rounded corners for iOS style
            mask = Image.new('L', (size, size), 0)
            radius = size // 5  # iOS-style corner radius

            # Save the processed icon
            icon.save(output_path, 'PNG', quality=95)
            return True

        except Exception as e:
            print(f"{Fore.YELLOW}Warning: Error processing iOS icon: {e}{Style.RESET_ALL}")
            return False
