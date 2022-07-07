"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/plugins/guides.html?#widgets

Replace code below according to your needs.
"""
import imageio
from typing import TYPE_CHECKING

from magicgui import magic_factory
from qtpy.QtWidgets import QHBoxLayout, QPushButton, QWidget

from ._hypha_proxy import execute

if TYPE_CHECKING:
    import napari


class ExampleQWidget(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # in one of two ways:
    # 1. use a parameter called `napari_viewer`, as done here
    # 2. use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        btn = QPushButton("Click me!")
        btn.clicked.connect(self._on_click)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(btn)

    def _on_click(self):
        if len(self.viewer.layers) > 0:
            image_array = self.viewer.layers[-1].data
            assert image_array.shape[2] == 3, "Expected 3 channel image"
            image_array = image_array.transpose(2, 0, 1).astype("float32")
        else:
            image_array = imageio.imread(
                "https://static.imjoy.io/img/img02.png"
            )
            self.viewer.add_image(image_array, name="image")
            image_array = image_array.transpose(2, 0, 1).astype(
                "float32"
            )  # Shape: (3, 349, 467)

        results = execute(
            inputs=[image_array, {"diameter": 30}],
            server_url="https://ai.imjoy.io",
            model_name="cellpose-python",
            decode_json=True,
        )

        mask = results["mask"]
        self.viewer.add_labels(mask, name="mask")


@magic_factory
def example_magic_widget(img_layer: "napari.layers.Image"):
    print(f"you have selected {img_layer}")


# Uses the `autogenerate: true` flag in the plugin manifest
# to indicate it should be wrapped as a magicgui to autogenerate
# a widget.
def example_function_widget(img_layer: "napari.layers.Image"):
    print(f"you have selected {img_layer}")
