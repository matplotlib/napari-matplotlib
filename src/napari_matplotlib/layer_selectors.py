import abc
from typing import List, Optional, Tuple, Type, Union

import napari
from magicgui import magicgui
from napari.utils.events.event import EmitterGroup, Event
from qtpy.QtWidgets import QWidget


class BaseLayerSelector(abc.ABC):
    """Base class for creating layer selectors.

    Layer selectors provide the interactive elements for selecting which
    layer(s) to plot from.

    To satisfy the API, layer selectors must take the following arguments
        napari_viewer : napari.Viewer
            The napari viewer from which to select layers from.
        parent_widget : QWidget
            The widget to which any GUI elements will be added.
        valid_layer_types : Tuple[napari.layers.Layer, ...]
            A tuple of the napari layer types the layer selector can select

    Further, the layer selector most have a `selected_layers` property that
    returns the list of currently selected layers.

    To allow actions to be performed when the selectino changes, the base class
    has a `LayerSelector.events.selected_layers()` event that can be connected
    to.
    """

    def __init__(
        self,
        napari_viewer: napari.Viewer,
        parent_widget: QWidget,
        valid_layer_types: Tuple[napari.layers.Layer, ...],
    ):
        self.viewer = napari_viewer
        self.parent_widget = parent_widget
        self.valid_layer_types = valid_layer_types

        self.events = EmitterGroup(source=self, selected_layer=Event)

    @abc.abstractmethod
    def selected_layers(self) -> List[napari.layers.Layer]:
        raise NotImplementedError


class LayerListSelector(BaseLayerSelector):
    def __init__(
        self,
        napari_viewer: napari.Viewer,
        parent_widget: QWidget,
        valid_layer_types: Tuple[napari.layers.Layer, ...],
    ):
        super().__init__(
            napari_viewer=napari_viewer,
            parent_widget=parent_widget,
            valid_layer_types=valid_layer_types,
        )
        self.viewer.layers.selection.events.changed.connect(self.update_layers)

        self.update_layers()

    def update_layers(self, event: napari.utils.events.Event = None) -> None:
        self._selected_layers = list(self.viewer.layers.selection)
        self.events.selected_layer()

    @property
    def selected_layers(self) -> List[napari.layers.Layer]:
        return self._selected_layers


class LayerWidgetSelector(BaseLayerSelector):
    def __init__(
        self,
        napari_viewer: napari.Viewer,
        parent_widget: QWidget,
        valid_layer_types: Tuple[napari.layers.Layer, ...],
    ):
        super().__init__(
            napari_viewer=napari_viewer,
            parent_widget=parent_widget,
            valid_layer_types=valid_layer_types,
        )

        # initialize the selected layers list
        self._selected_layers: List[napari.layers.Layer] = []

        # create the combobox
        self.add_layer_combo_box()

    @property
    def selected_layers(self) -> List[napari.layers.Layer]:
        return self._selected_layers

    def add_layer_combo_box(self, widget_index: int = 0) -> None:
        self._layer_combobox = magicgui(
            self._select_layer,
            layer={"choices": self._get_valid_layers},
            auto_call=True,
        )
        self._layer_combobox()
        self.parent_widget.layout().insertWidget(
            widget_index, self._layer_combobox.native
        )

    def _select_layer(self, layer: napari.layers.Layer) -> None:
        self._selected_layers = [layer]
        self.events.selected_layer()

    def _get_valid_layers(
        self, combo_box: Optional[int] = None
    ) -> List[napari.layers.Layer]:
        return [
            layer
            for layer in self.viewer.layers
            if type(layer) in self.valid_layer_types
        ]


# Type for annotating variables that accept all layer selectors
LayerSelector = Union[Type[LayerListSelector], Type[LayerWidgetSelector]]


def get_layer_selector(selector: Union[str, LayerSelector]) -> LayerSelector:
    if isinstance(selector, str):
        return globals()[selector]

    elif issubclass(selector, BaseLayerSelector):
        # passthrough if already a LayerSelector
        return selector
    else:
        raise TypeError(
            "selector should be a string or LayerSelector subclass"
        )
