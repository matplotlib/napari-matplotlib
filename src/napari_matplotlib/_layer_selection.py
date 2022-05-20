import typing

import napari
import napari.layers
from magicgui import magicgui


@typing.no_type_check
class LayerListSelection:
    def setup_selection_callbacks(self) -> None:
        """
        Setup callbacks for:
        - Layer selection changing
        - z-step changing
        """
        # z-step changed in viewer
        self.viewer.dims.events.current_step.connect(self._draw)
        # Layer selection changed in viewer
        self.viewer.layers.selection.events.changed.connect(self.update_layers)

    def update_layers(self, event: napari.utils.events.Event) -> None:
        """
        Update the layers attribute with currently selected layers and re-draw.
        """
        self.layers = list(self.viewer.layers.selection)
        self._on_update_layers()
        self._draw()

    def _on_update_layers(self) -> None:
        """
        This function is called when self.layers is updated via
        ``self.update_layers()``.

        This is a no-op, and is intended for derived classes to override.
        """


@typing.no_type_check
class LayerComboBoxSelection:
    def add_layer_combo_box(self, widget_index: int = 0):
        self._layer_combobox = magicgui(
            self._select_layer,
            layer={"choices": self._get_valid_layers},
            auto_call=True,
        )
        self._layer_combobox()
        self.layout().insertWidget(widget_index, self._layer_combobox.native)

    def _select_layer(self, layer: napari.layers.Layer):
        self.layers = [layer]
        self._on_update_layers()

    def _get_valid_layers(self, combo_box):
        return [
            layer
            for layer in self.viewer.layers
            if type(layer) in self.input_layer_types
        ]
