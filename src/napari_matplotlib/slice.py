import napari
from qtpy.QtWidgets import QComboBox, QHBoxLayout, QSpinBox

from napari_matplotlib.base import NapariMPLWidget

__all__ = ["SliceWidget"]

_dims = ["x", "y", "z"]


class SliceWidget(NapariMPLWidget):
    def __init__(self, napari_viewer: napari.viewer.Viewer):
        super().__init__(napari_viewer)

        self.layer = self.viewer.layers[-1]

        button_layout = QHBoxLayout()
        self.layout().addLayout(button_layout)

        self.dim_selector = QComboBox()
        button_layout.addWidget(self.dim_selector)

        self.selectors = {}
        for d in _dims:
            self.selectors[d] = QSpinBox()
            button_layout.addWidget(self.selectors[d])

        self.update_dim_selector()
        self.viewer.layers.selection.events.changed.connect(
            self.update_dim_selector
        )

    def update_dim_selector(self) -> None:
        """
        Update options in the dimension selector from currently selected layer.
        """
        dims = ["x", "y", "z"]
        self.dim_selector.clear()
        self.dim_selector.addItems(dims[0 : self.layer.data.ndim])
