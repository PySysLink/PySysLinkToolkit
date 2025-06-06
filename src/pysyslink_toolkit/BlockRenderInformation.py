from enum import Enum
# ...existing code...
import json

class BlockShape(Enum):
    square = "square"
    triangle = "triangle"
    circle = "circle"

class FigurePath:
    x_values: list[float]
    y_values: list[float]
    color: str = '#000000'

    def to_dict(self):
        return {
            "x_values": self.x_values,
            "y_values": self.y_values,
            "color": self.color
        }

class BlockRenderFigure:
    paths: list[FigurePath] = []
    show_grid: bool = False
    show_axes: bool = True

    def to_dict(self):
        return {
            "paths": [p.to_dict() for p in self.paths],
            "show_grid": self.show_grid,
            "show_axes": self.show_axes
        }

class BlockRenderInformation:
    """
    If both figure and icon are set, figure has priority. If show_image_and_text is False,
    and either icon is not "" or figure is not None, icon or figure will be shown. If True,
    both the image and the text are shown.
    """
    shape: BlockShape = BlockShape.square
    icon: str = ""
    figure: BlockRenderFigure | None = None
    text: str = "No text"
    show_image_and_text: bool = False

    # New properties for dimensions
    default_width: float = 120.0
    default_height: float = 50.0
    min_width: float = 60.0
    min_height: float = 25.0
    max_width: float = 360.0
    max_height: float = 150.0

    input_ports: int = 1
    output_ports: int = 1

    def to_dict(self):
        return {
            "shape": self.shape.value,
            "icon": self.icon,
            "text": self.text,
            "show_image_and_text": self.show_image_and_text,
            "figure": self.figure.to_dict() if self.figure else None,
            "default_width": self.default_width,
            "default_height": self.default_height,
            "min_width": self.min_width,
            "min_height": self.min_height,
            "max_width": self.max_width,
            "max_height": self.max_height,
            "input_ports": self.input_ports,
            "output_ports": self.output_ports
        }

    def to_json(self):
        return json.dumps(self.to_dict())
