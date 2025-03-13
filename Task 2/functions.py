import networkx as nx
import matplotlib.pyplot as plt
import os, sys
import matplotlib.lines as mlines


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

def draw_network(G, node_mapping, origem, destino, caminho1, caminho2):
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

    # Criar objetos para a legenda
    legend_caminho1 = mlines.Line2D([], [], color='green', linewidth=3, label="Caminho Primário")
    legend_caminho2 = mlines.Line2D([], [], color='blue', linewidth=3, label="Caminho Secundário")
    legend_inicio = mlines.Line2D([], [], color='green', marker='s', markersize=8, linestyle='None', label="Nó Origem")
    legend_fim = mlines.Line2D([], [], color='red', marker='s', markersize=8, linestyle='None', label="Nó Destino")

    # Adicionar legenda
    plt.legend(handles=[legend_caminho1, legend_caminho2, legend_inicio, legend_fim], loc='upper right')
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

def find_best_paths(G, origem, destino):
    """
    @brief Finds the best two disjoint paths between two nodes based on the lowest cost.

    This function first computes the shortest path between the source and destination nodes.
    Then, it removes all intermediate nodes and edges involved in the first path (except origem and destino),
    ensuring the second path is completely disjoint. If no second path exists, it notifies the user.

    @param G The directed graph containing nodes and edges with associated costs.
    @param origem The source node.
    @param destino The destination node.

    @return A tuple (path1, cost1, path2, cost2), where:
        - path1: The first shortest path.
        - cost1: The total cost of the first path.
        - path2: The second shortest path (if available, else None).
        - cost2: The total cost of the second path (if available, else None).
    """

    # primeiro - verificar se existe caminho entre nós selecionados

    if not nx.has_path(G, origem, destino):
        print("Não há caminho entre os nós selecionados.")
        return None, None, None, None

    # Primeiro caminho
    path1 = nx.shortest_path(G, source=origem, target=destino, weight='cost')
    cost1 = nx.shortest_path_length(G, source=origem, target=destino, weight='cost')
    
    print(f"Primeiro caminho: {path1} (Custo: {cost1})")

    # Cópia do grafo para podermos remover o primeiro caminho e calcular o segundo
    G_copia = G.copy()

    # Remoção do primeiro caminho
    for i in range(len(path1) - 1):
        if G_copia.has_edge(path1[i], path1[i+1]):
            G_copia.remove_edge(path1[i], path1[i+1])
        if G_copia.has_edge(path1[i+1], path1[i]):  
            G_copia.remove_edge(path1[i+1], path1[i])

    # Remoção dos nós intermediários
    for node in path1[1:-1]:
        G_copia.remove_node(node)

    # Segundo caminho
    try:
        path2 = nx.shortest_path(G_copia, source=origem, target=destino, weight='cost')
        cost2 = nx.shortest_path_length(G_copia, source=origem, target=destino, weight='cost')
        print(f"Segundo caminho: {path2} (Custo: {cost2})")
    except nx.NetworkXNoPath:
        print("Não há um segundo caminho possível.")
        path2, cost2 = None, None

    return path1, cost1, path2, cost2

def clear_screen():
    """"
    "Limpa a tela do terminal."
    """

    os.system('cls' if os.name == 'nt' else 'clear')

def draw_empty_network(G, node_mapping):
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

    # desenha o gráfico, deteta o SO e abre em fullscreen para uma melhor visualização
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