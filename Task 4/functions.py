import networkx as nx
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

def find_best_paths(G, origem, destino, algoritmo):
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
    if algoritmo == 1:
        print(f"Primeiro caminho: {path1} (Custo: {cost1})")
    else: 
        print("CAMINHO MAIS CURTO: ")
        print(f"\tCaminho: {path1}")
    
    # Cópia do grafo para podermos remover o primeiro caminho e calcular o segundo
    G_copia = G.copy()

    # Remoção do primeiro caminho
    for i in range(len(path1) - 1):

        # se tem a aresta, remove-a
        if G_copia.has_edge(path1[i], path1[i+1]):
            G_copia.remove_edge(path1[i], path1[i+1])
        
        # se tem a aresta inversa, remove-a (grafos bidirecionais)
        if G_copia.has_edge(path1[i+1], path1[i]):  
            G_copia.remove_edge(path1[i+1], path1[i])

    # Remoção dos nós intermediários
    for node in path1[1:-1]:
        G_copia.remove_node(node)

    # Segundo caminho
    try:
        path2 = nx.shortest_path(G_copia, source=origem, target=destino, weight='cost')
        cost2 = nx.shortest_path_length(G_copia, source=origem, target=destino, weight='cost')
        if algoritmo == 3:
            print("Método TSA: ")
            print(f"\tCaminho: {path2}")
        else:          
            print(f"Segundo caminho: {path2} (Custo: {cost2})")
        
    except nx.NetworkXNoPath:
        if algoritmo == 3:
            print("Método TSA: ")
        
        print("\tAviso: Não há um segundo caminho possível.")
        path2, cost2 = None, None

    return path1, cost1, path2, cost2
# ------------------------------------------------------

def suurballe(G, origem_orig, destino_orig, algoritmo):
    """!
    @brief Implementa o algoritmo de Suurballe para encontrar dois caminhos disjuntos em um grafo.

    Esta função utiliza o algoritmo de Suurballe para encontrar dois caminhos mais curtos disjuntos entre dois nós de um grafo direcionado. O primeiro caminho é encontrado usando o algoritmo de Dijkstra, e o segundo caminho é calculado após a remoção dos nós pertencentes ao primeiro caminho.

    @param G Grafo direcionado em que os caminhos serão calculados.
    @param origem_orig Nó de origem no grafo.
    @param destino_orig Nó de destino no grafo.
    
    @return Uma lista contendo dois caminhos: o primeiro caminho mais curto e o segundo caminho mais curto disjunto.

    @note Caso o segundo caminho não exista, o valor retornado será `None` para o segundo caminho.
    """

    # --- PASSO 0: Encontrar P1 no grafo original ---
    if algoritmo == 2: 
        print("\n--- Step 0: Encontrar 1º caminho no grafo original ---")
    
    try:
        # PASSO 0: Encontrar o primeiro caminho no grafo ORIGINAL
        P1_original = nx.shortest_path(G, source=origem_orig, target=destino_orig, weight='cost')
    except nx.NetworkXNoPath:
        print("Não há caminho inicial.")
        return None, None
    
    if algoritmo == 2:
        draw_suurballe(G, origem_orig, destino_orig, P1_original, None, "Step 0 - Primeiro Caminho no Grafo Original")
        # --- Node Splitting ---
        print("\n--- Step 0.5: Node Splitting ---")
    
    # H é o Grafo com node splitting
    # s é o nó de origem (com sufixo _out) e t é o nó de destino (com sufixo _in)
    H, s, t = split_nodes(G, origem_orig, destino_orig, path=P1_original)
    if algoritmo == 2:
        draw_suurballe(H, s, t, None, None, "Step 0.5 - Grafo após Node Splitting")
        # --- Step 1: Encontrar P1 no grafo transformado ---
        print("\n--- Step 1: Encontrar 1º caminho no grafo transformado ---")
    
    try:
        path = nx.shortest_path(H, source=s, weight='cost')
    except nx.NetworkXNoPath:
        print(f"Destino {t} não alcançável.")
        return merge_split_path(P1_original), None

    if t not in path:
        print(f"Destino {t} não alcançável a partir de {s}.")
        return merge_split_path(P1_original), None

    # P1_split é o caminho encontrado no grafo transformado
    # até o nó de destino
    P1_split = path[t]

    if algoritmo == 2: 
        print(f"1.º Caminho, P1, (split nodes): {P1_split}")
        draw_suurballe(H, s, t, P1_split, None, "Step 1 - 1º Caminho com Node Splitting")
    
    # --- Step 2: Transformar a rede ---
    if algoritmo == 2:
        print("\n--- Step 2: Transformar a Rede ---")
    
    # alterações no grafo residual
    H_residual = H.copy()
    distance = nx.shortest_path_length(H, source=s, weight='cost')
    
    # 2.1: Custos reduzidos
    if algoritmo == 2:
        print("Step 2.1: Custos Reduzidos")
    
    # Calcular os custos reduzidos para cada aresta
    # c_ij' = c_ij + t_s_i - t_s_j
    # onde c_ij é o custo original da aresta (u, v)
    for u, v, data in H.edges(data=True):
        c_ij = data.get('cost', 1)
        t_s_i = distance.get(u, float('inf'))
        t_s_j = distance.get(v, float('inf'))
        if H_residual.has_edge(u, v):
            if t_s_i != float('inf') and t_s_j != float('inf'):
                H_residual[u][v]['cost'] = c_ij + t_s_i - t_s_j
            else:
                H_residual[u][v]['cost'] = float('inf')
    if algoritmo == 2:
        draw_suurballe(H_residual, s, t, None, None, "Step 2.1 - Custos Reduzidos")
    
    # 2.2: Inverter arcos de P1
    if algoritmo == 2: 
        print("Step 2.2: Remover arcos de P1 direcionados para a origem")
        print("Step 2.3: Inverter direção dos arcos de P1 e definir custo como 0")
    
    P1_edges = list(zip(P1_split[:-1], P1_split[1:]))
    print(f"Arcos de P1: {P1_edges}")
        
    # Step 2.2: Remove arcs that point towards source
    # We process edges in reverse order (from destination to source)
    node_pairs = list(zip(P1_split[:-1], P1_split[1:]))  # Get original edges
    for u, v in node_pairs:
        base_u = u.rsplit('_', 1)[0]  # Get base node name without _in/_out
        base_v = v.rsplit('_', 1)[0]
        # Remove edge from v to u (the reverse direction)
        reverse_u = f"{base_v}_out"
        reverse_v = f"{base_u}_in"
        if H_residual.has_edge(reverse_u, reverse_v):
            H_residual.remove_edge(reverse_u, reverse_v)
    
    if algoritmo == 2:
        draw_suurballe(H_residual, s, t, None, None, "Step 2.2 - Arcos Removidos ")

    # Step 2.3: Reverse remaining arcs (those pointing towards destination)
    for i in range(len(P1_split)-1):
        u, v = P1_split[i], P1_split[i+1]  # Edge pointing towards destination
        if H_residual.has_edge(u, v):
            # Remove original edge and add reversed edge with cost 0
            H_residual.remove_edge(u, v)
            H_residual.add_edge(v, u, cost=0)

    if algoritmo == 2:
        print("Step 2.3: Inverter direção dos arcos de P1 e definir custo como 0")
        draw_suurballe(H_residual, s, t, None, None, "Step 2.3 - Arcos Invertidos")
    
    # --- Step 3: Encontrar P2 no grafo residual ---
    if algoritmo == 2:
        print("\n--- Step 3: Encontrar 2º Caminho no Grafo Residual ---")
    
    try:
        P2_split = nx.shortest_path(H_residual, source=s, target=t, weight='cost')
        
        if algoritmo == 2: 
            print(f"2.º Caminho, P2, (split nodes): {P2_split}")
            draw_suurballe(H_residual, s, t, None, P2_split, "Step 3 - 2º Caminho no Grafo Residual")

    except nx.NetworkXNoPath:
        print("Não existe segundo caminho disjunto.")
        return merge_split_path(P1_original), None
    
    # Validação do P2
    if not is_valid_path(P2_split, G):
        print("P2 não corresponde a um caminho válido no grafo original.")
        return merge_split_path(P1_original), None
    
    # --- Step 4: Remover arcos opostos ---
    if algoritmo == 2:
        print("\n--- Step 4: Remover arcos em comum ---")
    
    P1_edges = set(zip(P1_split[:-1], P1_split[1:]))
    P2_edges = set(zip(P2_split[:-1], P2_split[1:]))
    
    # Encontrar arcos em comum (opostos) entre P1 e P2
    # Se (u, v) está em P1 e (v, u) está em P2, então são opostos
    opposite_edges = set()
    for (u, v) in P1_edges:
        if (v, u) in P2_edges:
            opposite_edges.add((u, v))
            opposite_edges.add((v, u))
    
    print(f"Arcos em comum: {opposite_edges}")
    input("enter")

    if algoritmo == 2:
        if opposite_edges:
            print(f"Arcos em comum: {opposite_edges}")
        else:
            print("Não há arcos em comum entre P1 e P2.")

    # Reconstruir caminhos
    # path1_final começa com o nó de origem
    path1_final = [s]

    # se arco (u, v) não está em opposite_edges, adiciona u e v ao caminho
    # se u não é o último nó do caminho, adiciona-o
    for u, v in zip(P1_split[:-1], P1_split[1:]):
        if (u, v) not in opposite_edges:
            if path1_final[-1] != u:
                path1_final.append(u)
            path1_final.append(v)
    
    # path2_final começa com o nó de origem
    path2_final = [s]

    # se arco (u, v) não está em opposite_edges, adiciona u e v ao caminho
    # se u não é o último nó do caminho, adiciona-o
    for u, v in zip(P2_split[:-1], P2_split[1:]):
        if (u, v) not in opposite_edges:
            if path2_final[-1] != u:
                path2_final.append(u)
            path2_final.append(v)
    
    if algoritmo == 2:
        print(f"P1 após remoção: {path1_final}")
        print(f"P2 após remoção: {path2_final}")
    
        draw_suurballe(H_residual, s, t, path1_final, path2_final, "Step 4 - Caminhos Finais no Grafo Residual")
    
        # --- Unsplitting nodes final ---
        print("\n--- Merge final para nós originais ---")
    
    final_P1 = merge_split_path(path1_final)
    final_P2 = merge_split_path(path2_final)
        
    if algoritmo == 2:
        print(f"Caminho 1 Final: {final_P1}")
        print(f"Caminho 2 Final: {final_P2}")
    
    # Verificação final de disjunção
    if not final_P1 or not final_P2:
        print("Não existe segundo caminho disjunto.")
        return final_P1, None
    
    if final_P1 == final_P2:
        print("Os caminhos são iguais.")
        return final_P1, None
    
    common_nodes = set(final_P1[1:-1]) & set(final_P2[1:-1])
    if common_nodes:
        print("MÉTODO SUURBALLE: ")
        print("\tAviso: Caminhos compartilham nós internos.")
        print("\tNão é possível garantir disjunção total, logo não existe um segundo caminho.")
        return final_P1, None
    else:
        if algoritmo == 3:
            print("MÉTODO SUURBALLE: ")
            print(f"\tCaminho: {final_P2}")
    
    return final_P1, final_P2

# ------------------------------------------------------
def split_nodes(G, source_orig, target_orig, path=None):

    """!
    @brief Divide os nós de um grafo em nós de entrada e saída.

    Esta função divide cada nó de um grafo em dois nós: um nó de entrada (no formato `A_in`) e um nó de saída (no formato `A_out`). Ela cria um novo grafo com esses nós divididos e ajusta as arestas entre eles. A origem e o destino também são ajustados para os nós de saída e entrada, respectivamente.

    @param G Grafo direcionado original a ser dividido.
    @param source_orig Nó de origem no grafo original.
    @param target_orig Nó de destino no grafo original.

    @return Um grafo direcionado `H` com nós divididos, o novo nó de origem `s` (com sufixo `_out`), e o novo nó de destino `t` (com sufixo `_in`).
    """
    
    # fazemos as alterações num grafo copiado
    H = nx.DiGraph()
    
    # Mapeia nome original -> (nome_in, nome_out)
    new_mapping = {} 

    nodes_to_split = set(path) if path else set()

    # --- Cria nós divididos e arestas internas ---
    for node in G.nodes():
        if node in nodes_to_split:
            node_in = f"{node}_in"
            node_out = f"{node}_out"
            new_mapping[node] = (node_in, node_out)
            H.add_node(node_in)
            H.add_node(node_out)

            # acrescenta null cost arc
            H.add_edge(node_in, node_out, cost = 0)
        else:
            H.add_node(node)
            new_mapping[node] = (node, node)

    # --- Recria arestas originais ---
    for u, v, data in G.edges(data=True):
        u_out = new_mapping[u][1] if u in nodes_to_split else u # u_out
        v_in = new_mapping[v][0]  if v in nodes_to_split else v # v_in
        original_cost = data.get('cost', 1)
        H.add_edge(u_out, v_in, cost=original_cost)

    # --- Define s e t no grafo dividido ---
    s = new_mapping[source_orig][1] if source_orig in nodes_to_split else source_orig # source_out
    t = new_mapping[target_orig][0] if target_orig in nodes_to_split else target_orig # target_in

    # Garante que s e t existem (caso isolados)
    if not H.has_node(s): H.add_node(s)
    if not H.has_node(t): H.add_node(t)

    # Copia atributos 'pos' para o novo grafo (opcional, para debug/visualização)
    pos_orig = nx.get_node_attributes(G, 'pos')
    new_pos = {}
    offset = 0.4 # Pequeno offset para visualização
    for node_orig, pos_xy in pos_orig.items():
        node_in, node_out = new_mapping[node_orig]
        x, y = pos_xy
        if H.has_node(node_in): new_pos[node_in] = (x - offset, y + offset)
        if H.has_node(node_out): new_pos[node_out] = (x + offset, y - offset)
    nx.set_node_attributes(H, new_pos, 'pos')

    return H, s, t

# ------------------------------------------------------
def merge_split_path(split_path):
    """!
    @brief Converte um caminho do grafo dividido (com nós '_in'/'_out') de volta para os nomes originais dos nós.

    Esta função recebe um caminho que foi gerado a partir de um grafo dividido (onde os nós foram modificados para incluir sufixos '_in' e '_out') e converte esse caminho de volta para os nomes dos nós originais. Ela remove os sufixos '_in' e '_out' e retorna o caminho com os nós originais.

    @param split_path Caminho com os nós divididos (com sufixos '_in' ou '_out').

    @return Um caminho com os nomes dos nós originais, sem os sufixos '_in' ou '_out'.
    
    @note Caso o caminho esteja vazio, a função retorna uma lista vazia.
    """
    
    if not split_path: return []
    original_path = []
    for node in split_path:
        original_node = node.rsplit('_', 1)[0]
        if not original_path or original_path[-1] != original_node:
            original_path.append(original_node)
    return original_path

# ------------------------------------------------------
def is_valid_path(path, original_graph):
    """Verifica se um caminho no grafo split corresponde a um caminho válido no original."""
    merged_path = merge_split_path(path)
    if not merged_path or len(merged_path) < 2:
        return False
    for u, v in zip(merged_path[:-1], merged_path[1:]):
        if not original_graph.has_edge(u, v):
            return False
    return True