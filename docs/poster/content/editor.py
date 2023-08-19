from demo_widgets import EditorWidget

w = EditorWidget(G, GA)

def node_clicked(node, alt, ctrl):
    if alt:
        # delete node when alt+clicked
        G.delNode(node)
    elif ctrl and w.selected_node:
        # add edge when ctrl+clicked
        G.newEdge(w.selected_node, node)

w.on_node_click = node_clicked

display(w)