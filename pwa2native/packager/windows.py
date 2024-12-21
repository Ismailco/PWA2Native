"""Windows packager for PWA2Native"""
from pathlib import Path
import os
from typing import Optional
from colorama import Fore, Style

from .base import PWAPackager
from ..utils.template import TemplateLoader

class WindowsPackager(PWAPackager):
    def package_windows(self):
        """Package for Windows using Edge WebView2"""
        windows_dir = Path(self.output_dir) / "windows"
        windows_dir.mkdir(parents=True, exist_ok=True)

        # Get icon
        icon = self.get_icon_for_size(256)  # Windows prefers 256x256 icons

        # Create Visual Studio project structure
        self._create_windows_structure(windows_dir, icon)

        print(f"{Fore.GREEN}Windows project generated at {windows_dir}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Open the solution in Visual Studio and build{Style.RESET_ALL}")

    def _create_windows_structure(self, windows_dir: Path, app_icon: Optional[str]):
        """Create Windows project structure"""
        template_loader = TemplateLoader()
        project_name = self.app_name.replace(" ", "")

        # Create project directories
        (windows_dir / project_name).mkdir(exist_ok=True)
        (windows_dir / "packages").mkdir(exist_ok=True)

        # Generate .csproj file
        with open(windows_dir / f"{project_name}/{project_name}.csproj", "w") as f:
            f.write(template_loader.render_template('windows', 'project.csproj', {
                'project_name': project_name
            }))

        # Generate Program.cs
        with open(windows_dir / f"{project_name}/Program.cs", "w") as f:
            f.write(template_loader.render_template('windows', 'Program.cs', {
                'app_name': self.app_name,
                'url': self.url
            }))

        # Generate MainWindow.cs
        with open(windows_dir / f"{project_name}/MainWindow.cs", "w") as f:
            f.write(template_loader.render_template('windows', 'MainWindow.cs', {
                'app_name': self.app_name,
                'url': self.url
            }))

        # Process icon if available
        if app_icon:
            self._process_windows_icon(app_icon, windows_dir / f"{project_name}/app.ico")

        # Generate solution file
        with open(windows_dir / f"{project_name}.sln", "w") as f:
            f.write(template_loader.render_template('windows', 'solution.sln', {
                'project_name': project_name
            }))

    def _process_windows_icon(self, source_icon: str, output_path: str):
        """Convert icon to ICO format for Windows"""
        try:
            from PIL import Image
            img = Image.open(source_icon)
            img.save(output_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (256, 256)])
            print(f"{Fore.GREEN}Created Windows icon: {output_path}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}Warning: Could not create Windows icon: {e}{Style.RESET_ALL}")
