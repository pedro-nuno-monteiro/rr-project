import networkx as nx
import matplotlib.pyplot as plt

# ------------------------------------------------------
def suurbale(G, origem, destino):
    
    # step 1: find the minimum cost path tree from source s to all other nodes
    path = nx.shortest_path(G, origem, weight='cost')
    
    # step 2: transform the network, by

    # step 2.1: compute the reduced costs for all network arcs, as c'(i, j) = c(i, j) + t(s, i) - t(s, j)
    
    # calcula c_ij para cada nó, segundo o caminho mais curto
    distance = nx.shortest_path_length(G, origem, weight='cost')
    print("distância: ", distance)
    grafo_residual = G.copy()

    # para cada arco, calculamos o custo reduzido c'(i, j)
    # para isso, temos
    # # c_ij que é o custo do arco entre i e j
    # # t_s_i que é o custo do nó i (anterior)
    # # t_s_j que é o custo do nó j (posterior)

    # se fizer parte da árvore calculada em "path", de certeza que será 0
    for anterior, proximo, data in G.edges(data=True):

        c_ij = data.get('cost', 1)
        print("anterior: ", anterior)
        print("proximo: ", proximo)
        print("data: ", data)
        print("custo caminho entre os 2, c_ij = ", c_ij)
        t_s_i = distance[anterior] if anterior in distance else float('inf')
        print("custo do no anterior = ", t_s_i)
        t_s_j = distance[proximo] if proximo in distance else float('inf')
        print("custo do no posterior = ", t_s_j)
        c_prime = c_ij + t_s_i - t_s_j
        print("c' = ", c_ij, "+", t_s_i, "-", t_s_j, " = ", c_prime)
        
        grafo_residual[anterior][proximo]['cost'] = c_prime

    # a partir daqui, o grafo residual tem, para "path", custos de arcos a 0
    # e para as restantes arestas, o custo reduzido

    # step 2.2: remove all the arcs on the shortest path that are towards the source
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        if grafo_residual.has_edge(u, v):
            grafo_residual.remove_edge(u, v)

    # node splitting



    # step 2.3: reverse the direction for the arcs on the shortest path (all of null cost)
    #for i in range(len(path) - 1):
    #    u, v = path[i], path[i + 1]
    #    grafo_residual.add_edge(v, u, weight=0)

    # step 3. find a new minimum-cost path from s to d in the changed network
    try:
        new_path = nx.shortest_path(grafo_residual, origem, destino, weight='cost')
        new_cost = nx.shortest_path_length(grafo_residual, origem, destino, weight='cost')
    except nx.NetworkXNoPath:
        print(f"\n[AVISO] Não há caminho alternativo disponível de {origem} para {destino} após transformação pelo método Suurbale.")
        return path, None
    
    
    # step 4. remove the common arcs with opposite directions in the computed paths. 
    # the remaining arcs form two minimum-cost disjoint paths.
    combined_path = path + new_path[1:]  # Merge the two paths
    disjoint_paths = []
    visited_edges = set()

    for i in range(len(combined_path) - 1):
        u, v = combined_path[i], combined_path[i + 1]
        if (v, u) not in visited_edges:
            visited_edges.add((u, v))
            disjoint_paths.append((u, v))

    return path, new_path, grafo_residual

# ------------------------------------------------------
def draw_suurbale_graph(G, node_mapping, origem, destino, caminho1, caminho2, caminho3):
    # Get node positions
    pos = nx.get_node_attributes(G, 'pos')

    # Create a figure with adjusted layout
    plt.figure(figsize=(12, 8))
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Create node labels and colors
    labels = {nome: f"{num}: {nome}" for num, nome in node_mapping.items()}
    origem_nome = node_mapping.get(origem, None)
    destino_nome = node_mapping.get(destino, None)

    if origem_nome is None or destino_nome is None:
        raise ValueError(f"Os nós origem ({origem}) ou destino ({destino}) não estão no mapeamento.")

    node_colors = {
        nome: 'green' if nome == origem_nome else
              'red' if nome == destino_nome else
              'lightblue'
        for nome in G.nodes
    }

    # Draw base edges with curved arrows
    for u, v, d in G.edges(data=True):
        # Draw forward edge
        nx.draw_networkx_edges(G, pos, 
                             edgelist=[(u, v)],
                             edge_color='gray',
                             alpha=0.3,
                             width=1,
                             arrows=True,
                             arrowsize=20,  # Increased arrow size
                             connectionstyle=f"arc3,rad=0.2")
        
        # Draw backward edge
        nx.draw_networkx_edges(G, pos,
                             edgelist=[(v, u)],
                             edge_color='gray',
                             alpha=0.3,
                             width=1,
                             arrows=True,
                             arrowsize=20,  # Increased arrow size
                             connectionstyle=f"arc3,rad=0.2")

    # Draw paths with curved arrows
    def draw_path_edges(path, color):
        if path:
            path_edges = list(zip(path, path[1:]))
            for u, v in path_edges:
                nx.draw_networkx_edges(G, pos,
                                     edgelist=[(u, v)],
                                     edge_color=color,
                                     width=3,
                                     arrows=True,
                                     arrowsize=25,  # Bigger arrows for highlighted paths
                                     connectionstyle=f"arc3,rad=0.2")

    # Draw the three paths
    draw_path_edges(caminho1, 'green')
    draw_path_edges(caminho2, 'blue')
    draw_path_edges(caminho3, 'magenta')

    # Add edge labels with curved positioning
    edge_labels = {}
    for u, v, d in G.edges(data=True):
        # Label for forward edge
        edge_labels[(u, v)] = f"{d['cost']}"

    nx.draw_networkx_edge_labels(G, pos,
                                edge_labels=edge_labels,
                                font_size=8,
                                font_color='blue',
                                label_pos=0.3)  # Adjust label position for curved edges

    # Draw node labels with colored backgrounds
    for nome, (x, y) in pos.items():
        label_text = labels.get(nome, nome)
        plt.text(x, y, label_text,
                fontsize=8,
                fontweight='bold',
                bbox=dict(facecolor=node_colors.get(nome, 'lightblue'),
                         edgecolor='black',
                         boxstyle='round,pad=0.3'),
                horizontalalignment='center',
                verticalalignment='center')

    # Add legend
    legend_items = [
        plt.Line2D([], [], color='green', linewidth=3, label="Shortest Path"),
        plt.Line2D([], [], color='blue', linewidth=3, label="Alternative Path"),
        plt.Line2D([], [], color='magenta', linewidth=3, label="Suurbale Path"),
        plt.Line2D([], [], color='green', marker='s', markersize=8, linestyle='None', label="Source Node"),
        plt.Line2D([], [], color='red', marker='s', markersize=8, linestyle='None', label="Target Node")
    ]
    plt.legend(handles=legend_items, loc='upper right')

    plt.title("Suurballe's Algorithm Graph")
    plt.axis('off')
    plt.tight_layout()
    plt.show()

