from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCharts import QChart, QChartView, QLineSeries
from PySide6.QtGui import QPainter
import random


class ConcentrationChart(QWidget):
    def __init__(self, user_id: int):
        super().__init__()

        layout = QVBoxLayout(self)

        series = QLineSeries()
        for i in range(10):
            series.append(i, random.randint(40, 100))

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Poziom koncentracji (ostatnie sesje)")
        chart.createDefaultAxes()

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)

        layout.addWidget(chart_view)
