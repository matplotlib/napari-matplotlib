from typing import List, Protocol, Union

import napari
from qtpy.QtWidgets import QWidget
from typing_extensions import runtime_checkable


@runtime_checkable
class LayerSelector(Protocol):
    @property
    def selected_layers(self) -> List[napari.layers.Layer]:
        ...


class LayerListSelector(LayerSelector):
    def __init__(self, viewer: napari.Viewer, parent_widget: QWidget):
        self.viewer = viewer
        self.viewer.layers.selection.events.changed.connect(self.update_layers)

        self.update_layers()

    def update_layers(self, event: napari.utils.events.Event = None) -> None:
        self._selected_layers = list(self.viewer.layers.selection)

    @property
    def selected_layers(self) -> List[napari.layers.Layer]:
        return self._selected_layers


def get_layer_selector(selector: Union[str, LayerSelector]) -> LayerSelector:
    if isinstance(selector, str):
        return globals()[selector]

    elif isinstance(selector, LayerSelector):
        # passthrough if already a LayerSelector
        return selector
    else:
        raise TypeError(
            "selector should be a string or LayerSelector subclass"
        )
