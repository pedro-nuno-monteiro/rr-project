import networkx as nx
import matplotlib.pyplot as plt
import sys
import matplotlib.lines as mlines
from matplotlib.widgets import CheckButtons

def retrieve_data(data):
    
    """!
    @brief Processa os dados de entrada, para criar um grafo direcionado.
    
    Esta função extrai informações de nós e links dos dados de entrada fornecidos pelo ficheiro de entrada.
    Cria um grafo direcionado, onde cada nó é adicionado com suas coordenadas e cada link é estabelecido. 

    @param data A string de entrada contém os dados a serem analisados. Deve conter seções para nós e links.
    @return Um grafo direcionado, onde os nós são conectados por links conforme o ficheiro de entrada.
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

# ------------------------------------------------------
def draw_network(G, node_mapping, origem, destino, caminho1, caminho2, caminho3, algoritmo):
    """!
    @brief Desenha o grafo da rede, usando os dados fornecidos.

    @param G O grafo direcionado a ser desenhado.
    @param node_mapping Mapa de nós.
    @param origem Índice do nó de origem.
    @param destino Índice do nó de destino.
    @param caminho1 Lista de nós que representam o primeiro caminho.
    @param caminho2 Lista de nós que representam o segundo caminho (pode ser None).
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

    #elif sys.platform.startswith("win"):
    #    try:
    #        mng.window.state("zoomed")
    #    except AttributeError:
    #        pass

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
        
    if caminho3:
        path_edges3 = list(zip(caminho3, caminho3[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges3, edge_color='magenta', width=3)

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
    legend_caminho1 = mlines.Line2D([], [], color='green', linewidth=3, label="Caminho Mais Curto")
    legend_inicio = mlines.Line2D([], [], color='green', marker='s', markersize=8, linestyle='None', label="Nó Origem")
    legend_fim = mlines.Line2D([], [], color='red', marker='s', markersize=8, linestyle='None', label="Nó Destino")
    legend_caminho2 = mlines.Line2D([], [], color='blue', linewidth=3, label="Two-Step Approach")
    legend_caminho3 = mlines.Line2D([], [], color='magenta', linewidth=3, label="Suurbale")
    
    if algoritmo == 1:
        plt.legend(handles=[legend_caminho1, legend_caminho2, legend_inicio, legend_fim], loc='upper right')
    if algoritmo == 2:
        plt.legend(handles=[legend_caminho1, legend_caminho3, legend_inicio, legend_fim], loc='upper right')
    if algoritmo == 3:
        plt.legend(handles=[legend_caminho1, legend_caminho2, legend_caminho3, legend_inicio, legend_fim], loc='upper right')

   
    # Adicionar legenda
    plt.show()

# ------------------------------------------------------
def find_best_paths(G, origem, destino):
    """!
    @brief Encontra os dois melhores caminhos disjuntos entre os dois nós com base no menor custo.

    Esta função primeiro calcula o caminho mais curto entre os nós de origem e destino.
    Em seguida, remove todos os nós e arestas intermediários envolvidos no primeiro caminho,
    garantindo que o segundo caminho seja completamente disjunto. Se não existir um segundo caminho, notifica o usuário.

    @param G O grafo direcionado.
    @param origem O nó de origem.
    @param destino O nó de destino.

    @return Tuple (path1, cost1, path2, cost2), onde:
        - path1: O primeiro caminho mais curto.
        - cost1: O custo total do primeiro caminho.
        - path2: O segundo caminho mais curto (caso contrário, None).
        - cost2: O custo total do segundo caminho (caso contrário, None).
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

    #elif sys.platform.startswith("win"):  
    #    try:
    #        mng.window.state("zoomed")  
    #    except AttributeError:
    #        pass


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

# ------------------------------------------------------
def suurbale(G, origem, destino):
    
    # step 1: find the minimum cost path tree from source s to all other nodes
    path = nx.shortest_path(G, origem, destino, weight='cost')
    cost = nx.shortest_path_length(G, origem, destino, weight='cost')
    #print(f"Shortest path from {origem} to {destino}: {path} with cost {cost}")

    # step 2: transform the network, by

    # step 2.1: compute the reduced costs for all network arcs, as c'(i, j) = c(i, j) + t(s, i) - t(s, j)
    distance = nx.single_source_dijkstra_path_length(G, origem, weight='cost')
    transformed_graph = nx.DiGraph()

    for u, v, data in G.edges(data=True):
        #print("u, v, data", u, v, data)
        c_ij = data.get('cost', 1)
        #print("c_ij: ", c_ij)
        t_s_i = distance[u] if u in distance else float('inf')
        #print("t_s_i: ", t_s_i)
        t_s_j = distance[v] if v in distance else float('inf')
        #print("t_s_j: ", t_s_j)
        c_prime = c_ij + t_s_i - t_s_j
        #print("c_prime: ", c_prime)
        transformed_graph.add_edge(u, v, weight=c_prime)

    # step 2.2: remove all the arcs on the shortest path that are towards the source
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        if transformed_graph.has_edge(u, v):
            transformed_graph.remove_edge(u, v)

    # step 2.3: reverse the direction for the arcs on the shortest path (all of null cost)
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        transformed_graph.add_edge(v, u, weight=0)

    # step 3. find a new minimum-cost path from s to d in the changed network
    try:
        new_path = nx.shortest_path(transformed_graph, origem, destino, weight='weight')
        new_cost = nx.shortest_path_length(transformed_graph, origem, destino, weight='weight')
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

    print(f"Combined path: {path} and {new_path}")
    print(f"Disjoint paths: {disjoint_paths}")

    return path, new_path