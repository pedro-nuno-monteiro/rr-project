import networkx as nx
import matplotlib.pyplot as plt
import os
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
        aresta = linha.split('(')[1].split(')')[0].strip()

        # divide a aresta em source e target
        source, target = aresta.split()
        G.add_edge(source, target)
        G.add_edge(target, source)

    return G, node_mapping


def draw_network(G, node_mapping, origem, destino):

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

    # Desenha as arestas do grafo a vermelho
    nx.draw_networkx_edges(G, pos, edge_color='red', arrows=True)

    # Desenha os rótulos dentro de retângulos coloridos
    for nome, (x, y) in pos.items():
        label_text = labels.get(nome, nome)  # Usa "1: Nome" ou só "Nome" se não estiver no dicionário
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
    
    os.system('cls')
    
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
