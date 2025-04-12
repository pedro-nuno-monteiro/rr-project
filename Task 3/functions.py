import networkx as nx
import matplotlib.pyplot as plt
from draw import *

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
def suurbale(G, origem, destino, node_mapping):
    
    # step 1: find the minimum cost path tree from source s to all other nodes
    path = nx.shortest_path(G, origem, weight='cost')

    # step 2: transform the network, by

    # step 2.1: compute the reduced costs for all network arcs, as c'(i, j) = c(i, j) + t(s, i) - t(s, j)
    
    # calcula c_ij para cada nó, segundo o caminho mais curto
    # distance é um dicionário que contem o custa da distnância da origem a cada nó
    distance = nx.shortest_path_length(G, origem, weight='cost')

    grafo_residual = G.copy()

    # para cada arco, calculamos o custo reduzido c'(i, j)
    # para isso, temos
    # # c_ij que é o custo do arco entre i e j
    # # t_s_i que é o custo do nó i (anterior)
    # # t_s_j que é o custo do nó j (posterior)

    draw_graph_5(G, node_mapping, origem, destino, caminho1=None, caminho2=None, filename="Grafo Original")

    # se fizer parte da árvore calculada em "path", de certeza que o custo será 0
    for anterior, proximo, data in G.edges(data=True):

        c_ij = data.get('cost', 1)
        t_s_i = distance[anterior] if anterior in distance else float('inf')
        t_s_j = distance[proximo] if proximo in distance else float('inf')
        c_prime = c_ij + t_s_i - t_s_j
        grafo_residual[anterior][proximo]['cost'] = c_prime

    # a partir daqui, o grafo residual tem, para "path", custos de arcos a 0
    # e para as restantes arestas, o custo reduzido

    draw_graph_5(grafo_residual, node_mapping, origem, destino, caminho1=None, caminho2=None, filename="Step 2.1")

    # step 2.2: remove all the arcs on the shortest path that are towards the source
    for i in range(len(path[destino]) - 1):
        u, v = path[destino][i], path[destino][i + 1]
        if grafo_residual.has_edge(v, u):
            grafo_residual.remove_edge(v, u)

    draw_graph_5(grafo_residual, node_mapping, origem, destino, caminho1=None, caminho2=None, filename="Step 2.2")

    # node splitting

    # step 2.3: reverse the direction for the arcs on the shortest path (all of null cost)
    for i in range(len(path[destino]) - 1):
        u, v = path[destino][i], path[destino][i + 1]
        grafo_residual.remove_edge(u, v)
        grafo_residual.add_edge(v, u, cost=0)

    draw_graph_5(grafo_residual, node_mapping, origem, destino, caminho1=None, caminho2=None, filename="Step 2.3")


    # step 3. find a new minimum-cost path from s to d in the changed network
    new_path = nx.shortest_path(grafo_residual, origem, destino, weight='cost')
    
    # step 4. remove the common arcs with opposite directions in the computed paths. 
    # the remaining arcs form two minimum-cost disjoint paths.

    draw_graph_5(grafo_residual, node_mapping, origem, destino, path[destino], new_path, filename="Grafo final")

    return path, new_path
