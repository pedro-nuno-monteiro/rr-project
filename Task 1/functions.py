import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys




def retrieve_data(data):
    
    """
    @brief Processes input data to create a directed graph.
    
    This function extracts node and link information from the input data provided in the `data` string.
    It creates a directed graph where each node is added with its coordinates and each link is established
    between the appropriate nodes. It removes unnecessary lines and comments, and processes sections
    specifically for nodes and links.

    @param data The input string containing the data to be parsed. It should contain sections for nodes and links.
    @return A directed graph (DiGraph) where nodes are connected by links as specified in the input data.
    """

    # cria um grafo direcionado
    G = nx.DiGraph()
    
    # fetch secção dos nós
    nodes_section = data[data.find("NODES ("):data.find("# LINK ")]

    nodes_section = nodes_section.split('\n')

    linhas_nos = []
    for linha in nodes_section:

        linha = linha.strip()

        if not (linha.startswith('#') or linha.startswith(')')):
            linhas_nos.append(linha)

    # elimina linhas indesejadas
    linhas_nos = linhas_nos[1:-2]

    # adicionar nós ao graph
    for linha in linhas_nos:

        # dividir cada linha em nome [esquerda] e coordenadas [direita]
        no = linha.split('(')
        nome_no = no[0].strip()
        coordenadas = no[1].strip(' )').split()

        # adicionar nó
        G.add_node(nome_no, pos = (float(coordenadas[0]), float(coordenadas[1])))
    
    # fetch secção dos links
    links_section = data[data.find("LINKS ("):data.find("DEMANDS (")]

    linhas_links = []
    for linha in links_section.split('\n'):
        linha = linha.strip()

        if not linha.startswith('#'):
            linhas_links.append(linha)

    linhas_links = linhas_links[1:-3]
    
    # LINK SECTION
    #
    # <link_id> ( <source> <target> ) <pre_installed_capacity> <pre_installed_capacity_cost> <routing_cost> <setup_cost> ( {<module_capacity> <module_cost>}* )

    # adicionar arestas
    for linha in linhas_links:

        if linha.startswith('#') or linha.startswith(')'):
            continue

        # dividir cada linha em nome [esquerda], fonte e destino [meio] e resto [direita]
        # só nos interessa a fonte e o destino de cada aresta
        aresta = linha.split('(')[1].split(')')[0].strip()

        # divide a aresta em source e target
        source, target = aresta.split()
        G.add_edge(source, target)
        G.add_edge(target, source)

    return G

def draw_network(G):
    """
    @brief Draws the network graph using the provided graph data.
    
    This function visualizes the graph `G` by using the positions of nodes stored as attributes in the graph.
    The network is drawn using `matplotlib` and `networkx`, with nodes displayed as light blue circles, and edges
    as red lines. The plot includes labels for the nodes and arrows to indicate the direction of edges.
    
    @param G The directed graph (DiGraph) to be drawn. It must contain node positions as attributes.
    """
    # Obtém as coordenadas dos nós do grafo
    pos = nx.get_node_attributes(G, 'pos')

    # desenha o gráfico, deteta o SO e abre em fullscreen para uma melhor visualização
    fig = plt.figure()
    mng = plt.get_current_fig_manager()
    
    if sys.platform.startswith("linux"):  
        backend = plt.get_backend()
        if backend in ["TkAgg", "Qt5Agg", "QtAgg"]:
            try:
                mng.full_screen_toggle()  
            except AttributeError:
                pass
        elif backend in ["GTK3Agg", "GTK3Cairo"]:  
            try:
                mng.window.maximize()
            except AttributeError:
                pass

    elif sys.platform.startswith("win"):  
        try:
            mng.window.state("zoomed")  
        except AttributeError:
            pass


    plt.subplots_adjust(left=0, right=1, top=1, bottom=0) 

    # Desenha as arestas do grafo com cor vermelha e setas para indicar direção
    nx.draw_networkx_edges(G, pos, edge_color='red', arrows=True)

     

    # Desenha os retângulos com o nome dos nós
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold',
                            bbox=dict(facecolor='lightblue', edgecolor='black', boxstyle='round,pad=0.3'))

    # Remove a moldura da figura para um visual mais limpo
    plt.box(False)

    # Exibe o gráfico
    plt.show()