from demo_widgets import DFSWidget
import ipywidgets as widgets

dfs = DFSWidget()

play = widgets.Play(max=dfs.count_steps(), interval=1000)
slider = widgets.IntSlider()
widgets.jslink((play, 'value'), (slider, 'value'))
slider.observe(dfs.change_step)

button = widgets.Button(description='New Graph')
button.on_click(dfs.random_graph)

display(widgets.VBox([
    widgets.HBox([play, slider, button]),
    dfs
])