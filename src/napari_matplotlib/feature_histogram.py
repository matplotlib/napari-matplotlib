from typing import Optional

import numpy as np
from qtpy.QtWidgets import QCheckBox, QComboBox, QLabel, QWidget

from .base import SingleAxesWidget

__all__ = ["FeatureHistogramWidget"]

import napari

from .util import Interval


class FeatureHistogramWidget(SingleAxesWidget):
    """
    Display a histogram of the features stored in the currently selected layer.
    """

    n_layers_input = Interval(1, 1)
    input_layer_types = (
        napari.layers.Image,
        napari.layers.Labels,
        napari.layers.Points,
        napari.layers.Surface,
    )

    def __init__(
        self,
        napari_viewer: napari.viewer.Viewer,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(napari_viewer)

        # Feature selection
        self.layout().addWidget(QLabel("Feature:"))
        self.plot_column_name = QComboBox()
        self.plot_column_name.currentIndexChanged.connect(self._draw)
        self.layout().addWidget(self.plot_column_name)

        # Logarithmic plot yes/no
        self.logarithmic_plot = QCheckBox("Logarithmic")
        self.logarithmic_plot.stateChanged.connect(self._draw)
        self.layout().addWidget(self.logarithmic_plot)

        # listen to laer changed
        napari_viewer.layers.selection.events.changed.connect(
            self.update_available_columns
        )

        # setup GUI
        self._update_layers(None)
        self.update_available_columns()

    def update_available_columns(self) -> None:
        """
        Update the feature list pulldown as soon as the user changes the selected layer
        """
        selected_layer = self.layers[0]

        former_plot_column_index = self.plot_column_name.currentIndex()

        if selected_layer is not None:
            features = selected_layer.features
            if features is not None:
                self.plot_column_name.clear()
                self.plot_column_name.addItems(list(features.keys()))

        self.plot_column_name.setCurrentIndex(former_plot_column_index)

    def draw(self) -> None:
        """
        Clear the axes and histogram the currently selected feature.
        """
        layer = self.layers[0]
        if layer is None:
            self.clear()
            return

        selected_column = self.plot_column_name.currentText()
        if selected_column is not None and len(selected_column) > 0:
            data = layer.features[selected_column]
            bins = np.linspace(np.min(data), np.max(data), 100)
            self.clear()
            self.axes.hist(
                data,
                bins=bins,
                label=layer.name + " / " + selected_column,
                log=self.logarithmic_plot.isChecked(),
            )
            self.axes.legend()
