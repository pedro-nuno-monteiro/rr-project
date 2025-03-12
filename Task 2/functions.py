import networkx as nx
import matplotlib.pyplot as plt
import os, sys

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
    
    node_mapping = {}  
    
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
    for index, linha in enumerate(linhas_nos):

        # dividir cada linha em nome [esquerda] e coordenadas [direita]
        no = linha.split('(')
        nome_no = no[0].strip()
        coordenadas = no[1].strip(' )').split()
        # adicionar nó
        G.add_node(nome_no, pos = (float(coordenadas[0]), float(coordenadas[1])))
        node_mapping[index] = nome_no

    
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
        elementos = linha.split()
        source, target = elementos[2], elementos[3]  # Nó origem e destino
        routing_cost = float(elementos[11])  # Custo da aresta
        
        # Adiciona a aresta com custo como atributo
        # Estamos a guardar na variável 'cost' para ser compatível com o método de Dijkstra
        G.add_edge(source, target, cost=routing_cost)
        G.add_edge(target, source, cost=routing_cost)

    return G, node_mapping

def draw_network(G, node_mapping, origem, destino, caminho):
    """
    @brief Draws the network graph using the provided graph data.

    This function visualizes the graph `G` by using the positions of nodes stored as attributes in the graph.
    The network is drawn using `matplotlib` and `networkx`, with nodes displayed as light blue circles, and edges
    as red lines. The plot includes labels for the nodes and arrows to indicate the direction of edges.

    @param G The directed graph (DiGraph) to be drawn. It must contain node positions as attributes.
    """

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

    # Criar figura e ajustar para tela cheia
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

    # Criar lista de arestas do caminho mais curto
    path_edges = list(zip(caminho, caminho[1:]))

    # Desenhar todas as arestas do grafo a vermelho, EXCETO as do caminho mais curto
    all_edges = list(G.edges)
    red_edges = [edge for edge in all_edges if edge not in path_edges and (edge[1], edge[0]) not in path_edges]
    nx.draw_networkx_edges(G, pos, edgelist=red_edges, edge_color='red', arrows=True, width=2, arrowsize=20)


    # Destacar as arestas do caminho mais curto a verde
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='green', arrows=True, width=3, arrowsize=20)

    # Adiciona rótulos para os custos das arestas
    edge_labels = {(u, v): f"{d['cost']}" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, font_color='blue')

    # Desenha os rótulos dentro de retângulos coloridos
    for nome, (x, y) in pos.items():
        label_text = labels.get(nome, nome)
        plt.text(x, y, label_text, fontsize=8, fontweight='bold',
                 bbox=dict(facecolor=node_colors.get(nome, 'lightblue'), edgecolor='black', boxstyle='round,pad=0.3'),
                 horizontalalignment='center', verticalalignment='center')

    # Remove a moldura da figura
    plt.box(False)

    # Exibe o gráfico
    plt.show()

def ask_origin_destiny(node_mapping):
    
    """
    @brief Asks the user to select the origin and destination nodes.

    This function prompts the user to input the numbers corresponding to the origin and 
    destination nodes. It ensures that the input is valid, checking against the provided 
    node mapping.

    @param node_mapping Dictionary mapping node numbers to their names.

    @return A tuple (origem, destino) where:
        @param origem: The selected origin node number.
        @param destino: The selected destination node number.
    """
    
    clear_screen()
    
    print("\n-------------- Escolha do nó de origem e destino ---------------")
    for num, nome in node_mapping.items():
        print(f"{num}: {nome}")
        
    print("\n---------------------------------------------------------------")
    while True:
        try:
            origem = int(input("\nDigite o número do nó de origem: "))
            destino = int(input("Digite o número do nó de destino: "))
            
            if origem in node_mapping and destino in node_mapping:
                break
            else:
                print("\nNúmero inválido. Por favor, escolha um número da lista.")
        except ValueError:
            print("\nNúmero inválido. Por favor, escolha um número da lista.")  
    
    return origem, destino

def find_best_path(G, origem, destino):
    """
    @brief Finds the best path between two nodes based on the lowest cost.

    This function uses Dijkstra's algorithm to compute the most efficient path between 
    the source and destination nodes, considering the link costs stored in the graph. 
    It returns both the computed path and the total cost.

    @param G The directed graph containing nodes and edges with associated costs.
    @param origem The source node from which the path will be calculated.
    @param destino The destination node to which the path will be determined.

    @return A tuple (path, cost), where:
        @param path: Ordered list of nodes representing the shortest path.
        @param cost: Total cost of the path based on the 'cost' attribute of the edges.
    """
    path = nx.shortest_path(G, source=origem, target=destino, weight='cost')
    print(f"Caminho mais curto: {path}")
    cost = nx.shortest_path_length(G, source=origem, target=destino, weight='cost')
    print(f"Custo total: {cost}")
    return path, cost

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')