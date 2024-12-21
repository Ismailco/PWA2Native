"""Template loading utility for PWA2Native"""
import os
from pathlib import Path
from string import Template
from typing import Dict, Any

class TemplateLoader:
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent / "templates"

    def render_template(self, platform: str, template_name: str, context: Dict[str, Any] = None) -> str:
        """
        Render a template file with the given context

        Args:
            platform: Platform name (android, ios, macos, windows)
            template_name: Name of the template file
            context: Dictionary of variables to replace in the template

        Returns:
            Rendered template string
        """
        template_path = self.template_dir / platform / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        if context:
            return Template(template_content).safe_substitute(context)
        return template_content
