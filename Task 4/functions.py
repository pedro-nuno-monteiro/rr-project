import networkx as nx
from draw import *
from menus import clear_screen

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
def suurballe(G, origem_orig, destino_orig):
    """!
    @brief Implementa o algoritmo de Suurballe para encontrar dois caminhos disjuntos em um grafo.

    Esta função utiliza o algoritmo de Suurballe para encontrar dois caminhos mais curtos disjuntos entre dois nós de um grafo direcionado. O primeiro caminho é encontrado usando o algoritmo de Dijkstra, e o segundo caminho é calculado após a remoção dos nós pertencentes ao primeiro caminho.

    @param G Grafo direcionado em que os caminhos serão calculados.
    @param origem_orig Nó de origem no grafo.
    @param destino_orig Nó de destino no grafo.
    
    @return Uma lista contendo dois caminhos: o primeiro caminho mais curto e o segundo caminho mais curto disjunto.

    @note Caso o segundo caminho não exista, o valor retornado será `None` para o segundo caminho.
    """
    
    clear_screen()

    print(f"\n--- Algoritmo de Suurballe com Node Splitting de {origem_orig} para {destino_orig} ---")
    print("")
    print("- Ao longo do algoritmo, serão apresentados vários gráficos, de acordo")
    print("- com os diferentes passos do algoritmo (0 a 4).")
    print("")
    print("- NOTA: Para passar ao passo seguinte, é necessário fechar o gráfico atual.")

    # --- PASSO MODIFICADO: Primeiro calcula P1 no grafo original ---
    try:
        # PASSO 0: Encontrar o primeiro caminho no grafo ORIGINAL
        P1_original = nx.shortest_path(G, source=origem_orig, target=destino_orig, weight='cost')
    except nx.NetworkXNoPath:
        print("Não há caminho inicial.")
        return None, None
    
    draw_suurballe(G, origem_orig, destino_orig, P1_original, None, "Step 0 - Primeiro Caminho Original")
    
    H, s, t = split_nodes(G, origem_orig, destino_orig, path=P1_original)

    # --- A partir daqui, usar H, s, t ---

    # step 1: find the minimum cost path tree from source s to all other nodes

    # path contém todos os caminhos mais curtos desde a origem, s, até todos os restantes nós
    try:
        path = nx.shortest_path(H, source = s, weight = 'cost')
    except nx.NetworkXNoPath:
        print(f"Destino t={t} não alcançável a partir de s={s} em H.")
        return None, None

    if t not in path:
        print(f"Destino t={t} não alcançável a partir de s={s} em H.")
        return None, None

    # caminho mais curto até ao destino
    P1_split_nodes = path[t] # Caminho P1 no grafo H
    print(f"Step 1: P1 (split) = {P1_split_nodes}")
    draw_suurballe(H, s, t, P1_split_nodes, None, "Step 1 - 1º Caminho mais curto")

    # step 2: transform the network, by
    H_residual = H.copy()
    distance = nx.shortest_path_length(H, source=s, weight='cost')

    # step 2.1: compute the reduced costs and update edge costs in the residual graph as c'(i, j) = c(i, j) + t(s, i) - t(s, j)
    # para cada arco, calculamos o custo reduzido c'(i, j)
    # para isso, temos
    # # c_ij que é o custo do arco entre i e j
    # # t_s_i que é o custo do nó i (anterior)
    # # t_s_j que é o custo do nó j (posterior)

    # distance é um dicionário que contem o custa da distância da origem a cada nó
    
    for u, v, data in H.edges(data=True):
        cost = data.get('cost', 1)
        t_s_i = distance.get(u, float('inf'))
        t_s_j = distance.get(v, float('inf'))
        if t_s_i != float('inf') and t_s_j != float('inf'):
            c_prime = cost + t_s_i - t_s_j
            if H_residual.has_edge(u, v):
                H_residual[u][v]['cost'] = c_prime
        elif H_residual.has_edge(u, v):
            H_residual[u][v]['cost'] = float('inf') # Se um dos nós não é alcançável

    draw_suurballe(H_residual, s, t, P1_split_nodes, None, "Step 2.1 - Custos Reduzidos")

    # step 2.2: reverse the arcs on the shortest path P1
    P1_split_edges = list(zip(P1_split_nodes[:-1], P1_split_nodes[1:]))
    for u, v in P1_split_edges:
        if H_residual.has_edge(u, v):
            cost = H_residual[u][v].get('cost', 0) # Custo original (pode ser zero após redução)
            H_residual.remove_edge(u, v)
            H_residual.add_edge(v, u, cost=-cost) # Custo negativo para indicar o reverso

    print("Step 2.2: Revertendo arcos de P1...")
    draw_suurballe(H_residual, s, t, P1_split_nodes, None, "Step 2.2 - Arcos Invertidos")

    # step 3. find a new minimum-cost path from s to t in the transformed network
    print("Step 3: Procurando P2 no grafo transformado H_residual...")
    try:
        P2_split_nodes = nx.shortest_path(H_residual, source=s, target=t, weight='cost')
        print(f"Step 3: P2 (split) = {P2_split_nodes}")
        draw_suurballe(H_residual, s, t, P1_split_nodes, P2_split_nodes, "Step 3 - Com 2.º Caminho")
    except nx.NetworkXNoPath:
        print("Não foi encontrado um segundo caminho disjunto (Step 3).")
        return merge_split_path(P1_original), None
    except Exception as e:
        print(f"Erro no Step 3 (Shortest Path em H_residual): {e}")
        return merge_split_path(P1_original), None

    # step 4. remove the common arcs with opposite directions in the computed paths.
    # the remaining arcs form two minimum-cost disjoint paths.
    print("Step 4: Removendo sobreposições e reconstruindo...")
    P1_edges = list(zip(P1_split_nodes[:-1], P1_split_nodes[1:]))
    P2_edges = list(zip(P2_split_nodes[:-1], P2_split_nodes[1:]))

    path1_final_nodes = list(P1_split_nodes)
    path2_final_nodes = list(P2_split_nodes)

    i = 0
    while i < len(path1_final_nodes) - 1:
        u1, v1 = path1_final_nodes[i], path1_final_nodes[i+1]
        j = 0
        while j < len(path2_final_nodes) - 1:
            u2, v2 = path2_final_nodes[j], path2_final_nodes[j+1]
            if u1 == v2 and v1 == u2:  # Found an opposite arc
                del path1_final_nodes[i:i+2]
                if j + 1 < len(path2_final_nodes):
                    del path2_final_nodes[j:j+2]
                else:
                    del path2_final_nodes[j:j+1] # Handle case where P2 ends at the reverse arc
                # Restart the inner loop as paths have changed
                i = 0
                j = 0
                continue
            j += 1
        i += 1

    print(f"Step 4: P1 final (split) após remoção = {path1_final_nodes}")
    print(f"Step 4: P2 final (split) após remoção = {path2_final_nodes}")

    #draw_suurballe(H_residual, s, t, path1_final_nodes, path2_final_nodes, "Step 4 - FinalSplitPaths")

    # --- PASSO FINAL: Merge para Nós Originais ---
    print("--- Merge final para nós originais ---")
    final_path1_merged = merge_split_path(path1_final_nodes)
    final_path2_merged = merge_split_path(path2_final_nodes)

    # Trata casos de caminhos vazios ou idênticos após merge
    if not final_path1_merged and final_path2_merged:
        print("Aviso: P1 ficou vazio após merge.")
        final_path1_merged, final_path2_merged = final_path2_merged, None
    elif not final_path1_merged and not final_path2_merged:
        print("Erro: Ambos os caminhos finais estão vazios.")
        return merge_split_path(P1_split_nodes) if P1_split_nodes else None, None

    if final_path1_merged and final_path2_merged and final_path1_merged == final_path2_merged:
        print("Aviso: Caminhos finais (merged) idênticos.")
        return final_path1_merged, None # Retorna só um

    print(f"Caminho 1 Final (original): {final_path1_merged}")
    print(f"Caminho 2 Final (original): {final_path2_merged}")
    print("--- Suurballe Node-Disjoint concluído ---")

    return final_path1_merged, final_path2_merged

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