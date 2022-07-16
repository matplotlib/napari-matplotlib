from typing import List

import napari
from qtpy.QtWidgets import QWidget


class LayerListSelector:
    def __init__(self, viewer: napari.Viewer, parent_widget: QWidget):
        self.viewer = viewer
        self.viewer.layers.selection.events.changed.connect(self.update_layers)

        self.update_layers()

    def update_layers(self, event=None):
        self._selected_layers = list(self.viewer.layers.selection)

    @property
    def selected_layers(self) -> List[napari.layers.Layer]:
        return self._selected_layers
