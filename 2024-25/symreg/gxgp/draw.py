#   *        Giovanni Squillero's GP Toolbox
#  / \       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2   +      A no-nonsense GP in pure Python
#    / \
#  10   11   Distributed under MIT License

import inspect


def draw(node: "Node"):
    import networkx as nx
    from networkx.drawing.nx_pydot import graphviz_layout

    G = nx.DiGraph()
    for n1 in list(node.subtree):
        for n2 in list(n1._successors):
            G.add_edge(id(n1), id(n2))

    pos = graphviz_layout(G, prog="dot")  # dot neato twopi circo fdp sfdp
    # plt.figure()
    # plt.title(node.long_name)

    nx.draw_networkx_nodes(
        G,
        nodelist=[id(n) for n in node.subtree if not
        n.is_leaf],
        pos=pos,
        node_size=800,
        node_color='lightpink',
        node_shape='o'  # so^>v<dph8
    )
    nx.draw_networkx_nodes(
        G,
        nodelist=[id(n) for n in node.subtree if
                  n.is_leaf and len(inspect.getfullargspec(n._func).kwonlyargs) == 1],
        pos=pos,
        node_size=500,
        node_color='lightgreen',
        node_shape='s'  # so^>v<dph8
    )
    nx.draw_networkx_nodes(
        G,
        nodelist=[id(n) for n in node.subtree if
                  n.is_leaf and len(inspect.getfullargspec(n._func).kwonlyargs) == 0],
        pos=pos,
        node_size=500,
        node_color='lightblue',
        node_shape='s'  # so^>v<dph8
    )
    nx.draw_networkx_labels(
        G,
        pos=pos,
        labels={id(n): n.short_name for n in node.subtree},
    )
    nx.draw_networkx_edges(
        G,
        pos=pos,
        node_size=800,
    )
