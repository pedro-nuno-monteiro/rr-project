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
def suurbale(G_original, origem_orig, destino_orig):
    
    print(f"\n--- Suurballe Node-Disjoint para {origem_orig} -> {destino_orig} ---")

    # --- PASSO 0: Node Splitting ---
    try:
        H, s, t = split_node_graph(G_original, origem_orig, destino_orig)
        print(f"Grafo dividido H criado. Origem s={s}, Destino t={t}.")
        draw_graph_5(H, s, t, None, None, "Step0_SplitGraph")
    except Exception as e:
        print(f"Falha no Node Splitting: {e}")
        return None, None

    # --- A partir daqui, usar H, s, t ---

    # Step 1: Find the minimum cost path tree from s to all other nodes in H
    try:
        distance = nx.shortest_path_length(H, source=s, weight='cost')
        path_dict = nx.shortest_path(H, source=s, weight='cost')
        if t not in path_dict:
             print(f"Destino t={t} não alcançável a partir de s={s} em H.")
             return None, None
        P1_split_nodes = path_dict[t] # Caminho P1 no grafo H
        print(f"Step 1: P1 (split) = {P1_split_nodes}")
        draw_graph_5(H, s, t, P1_split_nodes, None, "Step1_H_with_P1")
    except nx.NetworkXNoPath:
         print(f"Não existe caminho de s={s} para t={t} em H.")
         return None, None
    except Exception as e:
         print(f"Erro no Step 1 (Dijkstra/Path): {e}")
         return None, None

    # Step 2: Transform the network H -> H_trans
    H_trans = H.copy()

    # Step 2.1: Compute reduced costs
    print("Step 2.1: Calculando custos reduzidos...")
    for u, v, data in H.edges(data=True): # Iterar H
        c_ij = data.get('cost', 1)
        t_s_u = distance.get(u, float('inf')) # Distância s->u em H
        t_s_v = distance.get(v, float('inf')) # Distância s->v em H
        if t_s_u == float('inf') or t_s_v == float('inf'):
            c_prime = float('inf')
        else:
            c_prime = c_ij + t_s_u - t_s_v
            c_prime = max(0, c_prime) # Garante não-negatividade

        if H_trans.has_edge(u, v):
             H_trans[u][v]['cost'] = c_prime # Atualiza custo em H_trans
        # else: print(f"Aviso 2.1: Aresta ({u},{v}) não encontrada em H_trans.")

    draw_graph_5(H_trans, s, t, None, None, "Step2_1_ReducedCosts")

    # Step 2.2: Remove arcs on the shortest path P1 that are towards the source (v, u)
    print("Step 2.2: Removendo arcos de P1 em direção à origem...")
    removed_count_2_2 = 0
    P1_split_edges = list(zip(P1_split_nodes[:-1], P1_split_nodes[1:]))
    for u, v in P1_split_edges:
        if H_trans.has_edge(v, u):
            H_trans.remove_edge(v, u)
            removed_count_2_2 += 1
    print(f"Removidos {removed_count_2_2} arcos.")

    draw_graph_5(H_trans, s, t, None, None, "Step2_2_AfterReverseRemoval")

    # Step 2.3: Reverse direction for the arcs on P1 (u, v) -> (v, u) cost 0
    print("Step 2.3: Revertendo arcos de P1 com custo 0...")
    removed_count_2_3 = 0
    added_count_2_3 = 0
    for u, v in P1_split_edges:
        if H_trans.has_edge(u, v):
            H_trans.remove_edge(u, v)
            removed_count_2_3 += 1
        # else: print(f"Aviso 2.3: Aresta P1 ({u},{v}) não encontrada para remoção.")
        H_trans.add_edge(v, u, cost=0) # Adiciona (v,u) com cost=0
        added_count_2_3 += 1
    print(f"Removidos {removed_count_2_3} arcos, adicionados {added_count_2_3} arcos invertidos.")

    draw_graph_5(H_trans, s, t, None, None, "Step2_3_AfterReversing")

    # Step 3: Find a new minimum-cost path P2 from s to t in H_trans
    print("Step 3: Procurando P2 no grafo transformado H_trans...")
    try:
        P2_split_nodes = nx.shortest_path(H_trans, source=s, target=t, weight='cost')
        print(f"Step 3: P2 (split) = {P2_split_nodes}")
        draw_graph_5(H_trans, s, t, P1_split_nodes, P2_split_nodes, "Step3_H_trans_with_P2")
    except nx.NetworkXNoPath:
        print("Não foi encontrado um segundo caminho disjunto (Step 3).")
        # Apenas P1 existe. Faz merge e retorna.
        path1_final_merged = merge_split_path(P1_split_nodes)
        return path1_final_merged, None
    except Exception as e:
         print(f"Erro no Step 3 (Shortest Path em H_trans): {e}")
         path1_final_merged = merge_split_path(P1_split_nodes)
         return path1_final_merged, None # Fallback para P1

    # --- PASSO 4: Remover sobreposições e reconstruir (NECESSÁRIO) ---
    print("Step 4: Removendo sobreposições e reconstruindo...")
    P1_edges_set = set(P1_split_edges) # Já calculado: arestas (u,v) de P1
    P2_edges_set = set(zip(P2_split_nodes[:-1], P2_split_nodes[1:])) # Arestas (x,y) de P2

    edges_to_remove_from_P1 = set() # Arestas (u,v) de P1 cujo reverso (v,u) está em P2
    for u, v in P1_edges_set:
        if (v, u) in P2_edges_set:
            edges_to_remove_from_P1.add((u, v))
    print(f"Detectadas {len(edges_to_remove_from_P1)} sobreposições.")

    # Constrói listas finais de arestas (ainda com nós divididos)
    final_P1_split_edges = [(u,v) for u,v in P1_edges_set if (u,v) not in edges_to_remove_from_P1]
    final_P2_split_edges = [(u,v) for u,v in P2_edges_set if (v,u) not in edges_to_remove_from_P1]

    # Reconstrução dos caminhos (ainda com nós divididos)
    path1_final_split = []
    path2_final_split = []
    G_path1_split = nx.DiGraph(final_P1_split_edges)
    G_path2_split = nx.DiGraph(final_P2_split_edges)

    try: # Reconstroi P1 final
        if s not in G_path1_split: G_path1_split.add_node(s)
        if t not in G_path1_split: G_path1_split.add_node(t)
        if G_path1_split.number_of_edges() > 0 or (s == t and G_path1_split.has_node(s)):
             path1_final_split = nx.shortest_path(G_path1_split, s, t)
    except (nx.NetworkXNoPath, nx.NodeNotFound): path1_final_split = []

    try: # Reconstroi P2 final
        if s not in G_path2_split: G_path2_split.add_node(s)
        if t not in G_path2_split: G_path2_split.add_node(t)
        if G_path2_split.number_of_edges() > 0 or (s == t and G_path2_split.has_node(s)):
             path2_final_split = nx.shortest_path(G_path2_split, s, t)
    except (nx.NetworkXNoPath, nx.NodeNotFound): path2_final_split = []

    print(f"Step 4: P1 final reconstruído (split) = {path1_final_split}")
    print(f"Step 4: P2 final reconstruído (split) = {path2_final_split}")

    draw_graph_5(H_trans, s, t, path1_final_split, path2_final_split, "Step4_FinalSplitPaths")

    # --- PASSO FINAL: Merge para Nós Originais ---
    print("--- Merge final para nós originais ---")
    final_path1_merged = merge_split_path(path1_final_split)
    final_path2_merged = merge_split_path(path2_final_split)

    # Trata casos de caminhos vazios ou idênticos após merge
    if not final_path1_merged and final_path2_merged:
        print("Aviso: P1 ficou vazio após merge.")
        final_path1_merged, final_path2_merged = final_path2_merged, None
    elif not final_path1_merged and not final_path2_merged:
         print("Erro: Ambos os caminhos finais estão vazios.")
         # Se P1 original existia, retorna-o como fallback?
         return merge_split_path(P1_split_nodes) if P1_split_nodes else None, None

    if final_path1_merged and final_path2_merged and final_path1_merged == final_path2_merged:
        print("Aviso: Caminhos finais (merged) idênticos.")
        return final_path1_merged, None # Retorna só um

    print(f"Caminho 1 Final (original): {final_path1_merged}")
    print(f"Caminho 2 Final (original): {final_path2_merged}")
    print("--- Suurballe Node-Disjoint concluído ---")

    return final_path1_merged, final_path2_merged

# ------------------------------------------------------
def split_node_graph(G_original, source_orig, target_orig):
    """
    Transforma grafo G_original dividindo cada nó A em A_in, A_out.
    Retorna o grafo dividido H, a nova origem s (source_out) e novo destino t (target_in).
    """
    H = nx.DiGraph()
    new_mapping = {} # Mapeia nome original -> (nome_in, nome_out)

    # --- Cria nós divididos e arestas internas ---
    for node in G_original.nodes():
        node_in = f"{node}_in"
        node_out = f"{node}_out"
        new_mapping[node] = (node_in, node_out)
        H.add_node(node_in)
        H.add_node(node_out)
        H.add_edge(node_in, node_out, cost=0) # Aresta interna custo 0

    # --- Recria arestas originais ---
    for u, v, data in G_original.edges(data=True):
        u_out = new_mapping[u][1] # u_out
        v_in = new_mapping[v][0]  # v_in
        original_cost = data.get('cost', 1)
        H.add_edge(u_out, v_in, cost=original_cost)

    # --- Define s e t no grafo dividido ---
    try:
        s = new_mapping[source_orig][1]  # source_out
        t = new_mapping[target_orig][0] # target_in
    except KeyError as e:
         print(f"Erro: Nó original '{e}' não encontrado ao definir s/t divididos.")
         raise # Re-lança a excepção

    # Garante que s e t existem (caso isolados)
    if not H.has_node(s): H.add_node(s)
    if not H.has_node(t): H.add_node(t)

    # Copia atributos 'pos' para o novo grafo (opcional, para debug/visualização)
    pos_orig = nx.get_node_attributes(G_original, 'pos')
    new_pos = {}
    offset = 0.35 # Pequeno offset para visualização
    for node_orig, pos_xy in pos_orig.items():
         node_in, node_out = new_mapping[node_orig]
         x, y = pos_xy
         if H.has_node(node_in): new_pos[node_in] = (x - offset, y + offset)
         if H.has_node(node_out): new_pos[node_out] = (x + offset, y - offset)
    nx.set_node_attributes(H, new_pos, 'pos')

    return H, s, t

# ------------------------------------------------------
def merge_split_path(split_path):
    """
    Converte um caminho do grafo dividido (com nós _in/_out)
    de volta para os nomes dos nós originais.
    """
    if not split_path: return []
    original_path = []
    for node in split_path:
        original_node = node.rsplit('_', 1)[0]
        if not original_path or original_path[-1] != original_node:
            original_path.append(original_node)
    return original_path