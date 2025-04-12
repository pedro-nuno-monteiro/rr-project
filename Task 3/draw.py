import networkx as nx
import matplotlib.pyplot as plt
import sys
import matplotlib.lines as mlines

def draw_network(G, node_mapping, origem, destino, caminho1, caminho2, algoritmo):
    """!
    @brief Desenha o grafo da rede, usando os dados fornecidos.

    @param G O grafo direcionado a ser desenhado.
    @param node_mapping Mapa de nós.
    @param origem Índice do nó de origem.
    @param destino Índice do nó de destino.
    @param caminho1 Lista de nós que representam o primeiro caminho.
    @param caminho2 Lista de nós que representam o segundo caminho (pode ser None).
    """

    print("G: ", G.edges(data=True))
    input("enter")

    # Obtém as coordenadas dos nós do grafo
    pos = nx.get_node_attributes(G, 'pos')

    # Cria rótulos no formato "1: Nome"
    labels = {nome: f"{num}: {nome}" for num, nome in node_mapping.items()}

    # Verifica se origem e destino existem
    origem_nome = node_mapping.get(origem, None)
    destino_nome = node_mapping.get(destino, None)

    if origem_nome is None or destino_nome is None:
        raise ValueError(f"Os nós origem ({origem}) ou destino ({destino}) não estão no mapeamento.")

    # Define as cores dos nós
    node_colors = {
        nome: 'green' if nome == origem_nome else
                'red' if nome == destino_nome else
                'lightblue'
        for nome in G.nodes
    }

    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Desenha todas as arestas a vermelho
    nx.draw_networkx_edges(G, pos, edge_color='red', alpha=0.3, width=1)

    # Pinta primeiro caminho (verde)
    path_edges1 = list(zip(caminho1, caminho1[1:]))
    nx.draw_networkx_edges(G, pos, edgelist=path_edges1, edge_color='green', width=3)

    # Pinta segundo caminho (azul), se existir
    if caminho2:
        path_edges2 = list(zip(caminho2, caminho2[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges2, edge_color='blue', width=3)
        
    # Adiciona rótulos para os custos das arestas
    edge_labels = {}
    for u, v, d in G.edges(data=True):
        edge_labels[(u, v)] = f"{d['cost']}"
        if edge_labels[(u, v)] == "0.0":
            edge_labels[(u, v)] = "1.0"
    print("G: ", G.edges(data=True))
    input("enter")

    # será colocar 2 arcos em vez de ter 1 bidirecional
    # assim 1 fica com 0 e outro com o valor do custo

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, font_color='blue')

    # Desenha os rótulos dentro de retângulos coloridos
    for nome, (x, y) in pos.items():
        label_text = labels.get(nome, nome)
        plt.text(x, y, label_text, fontsize=8, fontweight='bold',
                bbox=dict(facecolor=node_colors.get(nome, 'lightblue'), edgecolor='black', boxstyle='round,pad=0.3'),
                horizontalalignment='center', verticalalignment='center')

    plt.box(False)

    # Criar objetos para a legenda
    legend_caminho1 = mlines.Line2D([], [], color='green', linewidth=3, label="Caminho Mais Curto")
    legend_inicio = mlines.Line2D([], [], color='green', marker='s', markersize=8, linestyle='None', label="Nó Origem")
    legend_fim = mlines.Line2D([], [], color='red', marker='s', markersize=8, linestyle='None', label="Nó Destino")
    legend_caminho2 = mlines.Line2D([], [], color='blue', linewidth=3, label="Two-Step Approach")
    
    plt.legend(handles=[legend_caminho1, legend_caminho2, legend_inicio, legend_fim], loc='upper right')

    plt.show()

# ------------------------------------------------------
def draw_empty_network(G, node_mapping):
    """!
    @brief Desenha o grafo da rede, sem qualquer escolha.
    
    @param G O grafo direcionado.
    @param node_mapping Mapa dos nós.
    """
    # Obtém as coordenadas dos nós do grafo
    pos = nx.get_node_attributes(G, 'pos')

    # Cria rótulos no formato "1: Nome"
    labels = {nome: f"{num}: {nome}" for num, nome in node_mapping.items()}

    #plt.subplots_adjust(left=0, right=1, top=1, bottom=0) 

    # Desenha as arestas do grafo com cor vermelha e setas para indicar direção
    nx.draw_networkx_edges(G, pos, edge_color='red', arrows=True)
    
    # Desenha os rótulos dentro de retângulos coloridos
    for nome, (x, y) in pos.items():
        label_text = labels.get(nome, nome)
        plt.text(x, y, label_text, fontsize=8, fontweight='bold',
                bbox=dict(facecolor='lightblue', edgecolor='black', boxstyle='round,pad=0.3'),
                horizontalalignment='center', verticalalignment='center')

    # Remove a moldura da figura para um visual mais limpo
    plt.box(False)

    # Exibe o gráfico
    plt.show(block=False)

    plt.savefig("output/rede original.png", dpi=300)
    
    return plt

# ------------------------------------------------------
def draw_graph_5(G, node_mapping, origem, destino, caminho1, caminho2, filename):

    pos = nx.get_node_attributes(G, 'pos')

    # Create node labels and colors
    labels = {nome: f"{num}: {nome}" for num, nome in node_mapping.items()}


    node_colors = {
        nome: 'green' if nome == origem else
            'red' if nome == destino else
            'lightblue'
        for nome in G.nodes
    }

    # Draw base edges with curved arrows
    for u, v, d in G.edges(data=True):

        # Draw forward edge with positive curve
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color='gray',
                            alpha=0.5,
                            width=1,
                            arrows=True,
                            arrowsize=20,
                            connectionstyle=f'arc3, rad=0.05')
        

    # Add edge labels with curved positioning
    edge_labels = {}
    for u, v, d in G.edges(data=True):
        # Label for forward edge
        edge_labels[(u, v)] = f"{d['cost']}"

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                font_size=8,
                                font_color='blue',
                                label_pos=0.5,
                                connectionstyle=f'arc3, rad=0.05')
    
    if caminho1:
        path_edges1 = list(zip(caminho1, caminho1[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges1, edge_color='green', width=3, arrows=True, arrowsize=20)

    # Draw the second path (blue, thicker)
    if caminho2:
        path_edges2 = list(zip(caminho2, caminho2[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges2, edge_color='blue', width=3, arrows=True, arrowsize=20)

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
        plt.Line2D([], [], color='green', linewidth=3, label="Primeiro caminho"),
        plt.Line2D([], [], color='blue', linewidth=3, label="Segundo caminho"),
        plt.Line2D([], [], color='green', marker='s', markersize=8, linestyle='None', label="Source Node"),
        plt.Line2D([], [], color='red', marker='s', markersize=8, linestyle='None', label="Target Node")
    ]
    plt.legend(handles=legend_items, loc='upper right')

    plt.title("Grafo obtido após algoritmo de Suurballe")
    plt.axis('off')
    plt.savefig("output/" + filename + ".png", dpi=300, bbox_inches='tight')
    plt.show()
