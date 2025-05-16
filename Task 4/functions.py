import networkx as nx
from draw import *

"""!
@file functions.py
@brief Módulo com funções principais para manipulação de grafos e algoritmos de caminhos.
Inclui funções para processar dados de entrada, encontrar caminhos disjuntos com TSA e Suurballe, e realizar transformações no grafo como node splitting.
"""

def retrieve_data(data):
    
    """!
    @brief Processa os dados de entrada (string) para criar um grafo direcionado NetworkX.

    Esta função analisa uma string contendo informações sobre nós (com coordenadas)
    e links (arestas com custos) para construir um grafo. Os nós são adicionados
    com um atributo 'pos' para as suas coordenadas, e as arestas são adicionadas
    com um atributo 'cost'. As arestas são consideradas bidirecionais (adiciona
    target->source com o mesmo custo).

    @param data A string de entrada que contém os dados da rede a serem analisados.
                Deve seguir um formato específico com seções "NODES (...)" e "LINKS (...)".

    @return Tuple (G, node_mapping):
        - G (nx.DiGraph): O grafo direcionado criado a partir dos dados.
        - node_mapping (dict): Um dicionário que mapeia um índice numérico (baseado na ordem
                               de leitura dos nós) para o nome (string) de cada nó.
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
    @brief Encontra os dois melhores caminhos disjuntos em termos de nós (exceto origem/destino)
           entre dois nós, com base no menor custo, usando a abordagem Two-Step.

    Esta função primeiro calcula o caminho mais curto (path1) entre os nós de origem e
    destino usando Dijkstra (baseado no atributo 'cost' das arestas).
    Em seguida, cria uma cópia do grafo e remove todas as arestas de path1 e todos os
    nós intermediários de path1 (nós que não são nem a origem nem o destino).
    Depois, calcula o caminho mais curto (path2) nesta cópia modificada do grafo.
    Se não existir um segundo caminho, notifica e retorna None para path2 e cost2.

    @param G O grafo NetworkX direcionado.
    @param origem O nome (string) do nó de origem.
    @param destino O nome (string) do nó de destino.
    @param algoritmo Inteiro que indica o contexto do algoritmo (p.ex., 1 para TSA, 3 para Ambos).
                     Usado para controlar mensagens de impressão específicas do algoritmo.
                     Se None, impressões genéricas ou nenhumas são feitas.

    @return Tuple (path1, cost1, path2, cost2), onde:
        - path1 (list/None): O primeiro caminho mais curto (lista de nós). None se não houver caminho.
        - cost1 (float/None): O custo total do primeiro caminho. None se não houver caminho.
        - path2 (list/None): O segundo caminho mais curto disjunto em nós. None se não existir.
        - cost2 (float/None): O custo total do segundo caminho. None se não existir.
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
    elif algoritmo == 3: 
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
        if algoritmo == 1:          
            print(f"Segundo caminho: {path2} (Custo: {cost2})")
        
    except nx.NetworkXNoPath:
        if algoritmo == 3:
            print("Método TSA: ")
        if algoritmo == 1 or algoritmo == 3:
            
            print("\tAviso: Não há um segundo caminho possível.")
            
        path2, cost2 = None, None

    return path1, cost1, path2, cost2
# ------------------------------------------------------

def suurballe(G, origem_orig, destino_orig, algoritmo, option, calculo):
    """!
    @brief Implementa o algoritmo de Suurballe para encontrar dois caminhos disjuntos em arestas
           entre nós de origem e destino num grafo.

    O algoritmo segue vários passos:
    0. Encontra um caminho inicial P1_original no grafo G.
    0.5. Realiza "node splitting" nos nós de P1_original, criando um grafo H.
    1. Encontra o primeiro caminho P1_split no grafo transformado H.
    2. Transforma a rede H: calcula custos reduzidos, remove/inverte arcos de P1_split.
    3. Encontra o segundo caminho P2_split no grafo residual H_residual.
    4. Remove arcos opostos (desentrelaçamento) para formar os caminhos finais P1 e P2.
    Finalmente, os caminhos P1 e P2 são mapeados de volta para os nós do grafo original.

    @param G O grafo NetworkX direcionado original.
    @param origem_orig O nome (string) do nó de origem no grafo original.
    @param destino_orig O nome (string) do nó de destino no grafo original.
    @param algoritmo Inteiro que indica o contexto (p.ex., 2 para Suurballe, 3 para Ambos).
                     Controla impressões e, potencialmente, chamadas de desenho.
    @param option Booleano. Se True, salta o desenho dos passos intermédios do Suurballe.
                  Usado para acelerar quando apenas o resultado final é desejado.
    @param calculo Booleano. Se True, suprime a maioria das mensagens de impressão.
                   Útil quando a função é chamada em loop para cálculos estatísticos.

    @return Tuple (P1, cost1, P2, cost2), onde:
        - P1 (list/None): O primeiro caminho disjunto em arestas (lista de nós).
                          None se nenhum caminho for encontrado.
        - cost1 (float/None): O custo total do primeiro caminho. None se P1 for None.
        - P2 (list/None): O segundo caminho disjunto em arestas. None se não existir.
        - cost2 (float/None): O custo total do segundo caminho. None se P2 for None.
    """

    # --- PASSO 0: Encontrar P1 no grafo original ---
    if algoritmo == 2 and not option: 
        print("\n--- Step 0: Encontrar 1º caminho no grafo original ---")
    
    try:
        # PASSO 0: Encontrar o primeiro caminho no grafo ORIGINAL
        P1_original = nx.shortest_path(G, source=origem_orig, target=destino_orig, weight='cost')
    except nx.NetworkXNoPath:
        print("Não há caminho inicial.")
        return None, None, None, None
    
    if algoritmo == 2 and not option:
        draw_suurballe(G, origem_orig, destino_orig, P1_original, None, "Step 0 - Primeiro Caminho no Grafo Original")
        # --- Node Splitting ---
        print("\n--- Step 0.5: Node Splitting ---")
    
    # H é o Grafo com node splitting
    # s é o nó de origem (com sufixo _out) e t é o nó de destino (com sufixo _in)
    H, s, t = split_nodes(G, origem_orig, destino_orig, path=P1_original)
    
    if algoritmo == 2 and not option:
        draw_suurballe(H, s, t, None, None, "Step 0.5 - Grafo após Node Splitting")
        # --- Step 1: Encontrar P1 no grafo transformado ---
        print("\n--- Step 1: Encontrar 1º caminho no grafo transformado ---")
    
    try:
        path = nx.shortest_path(H, source=s, weight='cost')
    except nx.NetworkXNoPath:
        print(f"Destino {t} não alcançável.")
        return merge_split_path(P1_original), None, None, None

    if t not in path:
        print(f"Destino {t} não alcançável a partir de {s}.")
        return merge_split_path(P1_original), None, None, None

    # P1_split é o caminho encontrado no grafo transformado
    # até o nó de destino
    P1_split = path[t]

    if algoritmo == 2 and not option: 
        print(f"1.º Caminho, P1, (split nodes): {P1_split}")
        draw_suurballe(H, s, t, P1_split, None, "Step 1 - 1º Caminho com Node Splitting")
    
    # --- Step 2: Transformar a rede ---
    if algoritmo == 2 and not option:
        print("\n--- Step 2: Transformar a Rede ---")
    
    # alterações no grafo residual
    H_residual = H.copy()
    distance = nx.shortest_path_length(H, source=s, weight='cost')
    
    # 2.1: Custos reduzidos
    if algoritmo == 2 and not option:
        print("\n * Step 2.1: Custos Reduzidos")
    
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

    if algoritmo == 2 and not option:
        draw_suurballe(H_residual, s, t, None, None, "Step 2.1 - Custos Reduzidos")
    
    # 2.2: Inverter arcos de P1
    if algoritmo == 2 and not option: 
        print("\n * Step 2.2: Remover arcos de P1 direcionados para a origem")
    
    # Remover arcos direcionados para a origem
    node_pairs = list(zip(P1_split[:-1], P1_split[1:]))
    for u, v in node_pairs:

        # fica só os nomes sem _in/_out
        base_u = u.rsplit('_', 1)[0]
        base_v = v.rsplit('_', 1)[0]

        # criar os nomes dos arcos inversos para facilitar
        reverse_u = f"{base_v}_out"
        reverse_v = f"{base_u}_in"

        # remove o arco de v para u
        if H_residual.has_edge(reverse_u, reverse_v):
            H_residual.remove_edge(reverse_u, reverse_v)
    
    if algoritmo == 2 and not option:
        draw_suurballe(H_residual, s, t, None, None, "Step 2.2 - Arcos Removidos")

    # Step 2.3: Inverter direção dos arcos de P1 e definir custo como 0
    for i in range(len(P1_split)-1):

        # u, v são os nós de origem e destino
        # do arco que queremos inverter
        u, v = P1_split[i], P1_split[i+1]

        # se o arco existe, inverter a direção
        # e definir o custo como 0
        if H_residual.has_edge(u, v):
            H_residual.remove_edge(u, v)
            H_residual.add_edge(v, u, cost=0)

    if algoritmo == 2 and not option:
        print("\n * Step 2.3: Inverter direção dos arcos de P1 e definir custo como 0")
        draw_suurballe(H_residual, s, t, None, None, "Step 2.3 - Arcos Invertidos")
    
    # --- Step 3: Encontrar P2 no grafo residual ---
    if algoritmo == 2 and not option:
        print("\n--- Step 3: Encontrar 2º Caminho no Grafo Residual ---")
    
    try:
        P2_split = nx.shortest_path(H_residual, source=s, target=t, weight='cost')
        
        if algoritmo == 2 and not option: 
            print(f"2.º Caminho, P2, (split nodes): {P2_split}")
            draw_suurballe(H_residual, s, t, None, P2_split, "Step 3 - 2º Caminho no Grafo Residual")

    except nx.NetworkXNoPath:
        if not calculo:
            print("Não existe segundo caminho disjunto.")
        return merge_split_path(P1_original), None, None, None
    
    # Validação do P2
    if not is_valid_path(P2_split, G):
        if not calculo:
            print("P2 não corresponde a um caminho válido no grafo original.")
        return merge_split_path(P1_original), None, None, None
    
    # --- Step 4: Remover arcos opostos ---
    if algoritmo == 2 and not option:
        print("\n--- Step 4: Remover arcos em comum ---")
    
    # P1_edges e P2_edges são as arestas do primeiro e segundo caminho
    P1_edges = list(zip(P1_split[:-1], P1_split[1:]))
    P2_edges = list(zip(P2_split[:-1], P2_split[1:]))
    
    # Encontrar arcos em comum
    arcos_em_comum = set()
    for i, (u1, v1) in enumerate(P1_edges):
        for j, (u2, v2) in enumerate(P2_edges):
            if u1 == v2 and v1 == u2:
                arcos_em_comum.add(u1)
                arcos_em_comum.add(v1)
    
    # Criar um grafo com todas as arestas de ambos os caminhos
    deinterlace_graph = nx.DiGraph()
    for u, v in P1_edges:
        deinterlace_graph.add_edge(u, v)
    for u, v in P2_edges:
        deinterlace_graph.add_edge(u, v)

    if algoritmo == 2 and not option and arcos_em_comum:
        draw_suurballe(H_residual, s, t, P1_split, P2_split, "Step 4 - Grafo com Arcos em Comum")

    # Encontrar o caminho mais curto entre os nós de origem e destino
    try:
        P1_final = nx.shortest_path(deinterlace_graph, P1_split[0], P1_split[-1])
        
        # Remover arestas do primeiro caminho
        # no grafo temporário
        temp_graph = deinterlace_graph.copy()
        for u, v in zip(P1_final[:-1], P1_final[1:]):
            temp_graph.remove_edge(u, v)

        # segundo caminho final
        P2_final = nx.shortest_path(temp_graph, P2_split[0], P2_split[-1])

    except nx.NetworkXNoPath:
        if not calculo:
            print("SURBALLE:")
            print("\tNão foi possível encontrar o segundo caminho disjunto.")
        P1_final = P1_split
        P2_final = P2_split
    
    if algoritmo == 2 and not option:
        
        draw_suurballe(H_residual, s, t, P2_final, P1_final, "Step 4 - Caminhos Desentrelaçados")
        print("\n--- Merge final para nós originais ---")

    # Merge final para nós originais
    # P1_final e P2_final são os caminhos finais
    P1 = merge_split_path(P1_final)
    P2 = merge_split_path(P2_final)

    cost1 = path_cost(P1, G)
    cost2 = path_cost(P2, G)

    if algoritmo == 2 or algoritmo == 3:
        print("\nMétodo Suurballe:")
        print(f"\n\tCaminho 1: {P1} (Custo: {cost1})")
        print(f"\n\tCaminho 2: {P2} (Custo: {cost2})")

    # Verificação final de disjunção
    if not P1 or not P2:
        if not calculo:
            print("Não existe segundo caminho disjunto.")
        return P1, cost1, None, None

    if P1 == P2:
        if not calculo:
            print("Os caminhos são iguais.")
        return P1, cost1, None, None

    return P1, cost1, P2, cost2

# ------------------------------------------------------
def split_nodes(G, source_orig, target_orig, path=None):

    """!
    @brief Divide os nós especificados de um grafo G em nós de entrada (`_in`) e saída (`_out`).

    Cria um novo grafo H. Para cada nó no `path` fornecido (ou todos os nós se `path`
    for None e a lógica for ajustada, mas atualmente foca no `path`),
    o nó `N` é substituído por `N_in` e `N_out`. Uma aresta interna de `N_in` para
    `N_out` com custo zero é adicionada.
    As arestas originais `(U, V)` em G são remapeadas em H:
    - Se U foi dividido: de `U_out`
    - Se V foi dividido: para `V_in`
    Os nós de origem e destino (`source_orig`, `target_orig`) são mapeados para
    suas versões `_out` e `_in` respectivamente, se foram divididos.

    @param G Grafo NetworkX direcionado original a ser transformado.
    @param source_orig O nome (string) do nó de origem no grafo G.
    @param target_orig O nome (string) do nó de destino no grafo G.
    @param path Opcional. Uma lista de nós (strings, nomes dos nós) que devem ser divididos.
                Se um nó está neste `path`, ele será dividido. Nós não presentes
                no `path` não são divididos e mantêm o seu nome original em H.
                Se `path` for `None` ou vazio, nenhum nó é dividido desta forma específica,
                mas `source_orig` e `target_orig` podem ainda ser tratados como `_out`/`_in`
                se fizerem parte do conjunto de nós a dividir (que neste caso seria vazio).
                A lógica atual implica que APENAS nós em `path` são divididos.

    @return Tuple (H, s, t):
        - H (nx.DiGraph): O novo grafo com nós divididos.
        - s (str): O nó de origem em H (p.ex., `source_orig_out` ou `source_orig`).
        - t (str): O nó de destino em H (p.ex., `target_orig_in` ou `target_orig`).
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

    Esta função recebe uma lista de nós que podem ter sufixos '_in' ou '_out'
    (indicando que vieram de um processo de "node splitting") e remove esses
    sufixos para retornar uma lista de nomes de nós originais. Nós consecutivos
    no caminho que mapeiam para o mesmo nó original são consolidados (apenas uma
    instância do nó original é mantida).

    @param split_path Lista de strings, onde cada string é um nome de nó do grafo dividido.
                      Pode conter nomes como 'A_in', 'A_out', ou 'B' (se 'B' não foi dividido).
    @return Uma lista de strings com os nomes dos nós originais, sem sufixos e sem
            duplicatas consecutivas. Retorna lista vazia se `split_path` for None ou vazio.
    @note Exemplo: ['S_out', 'A_in', 'A_out', 'B_in', 'B_out', 'T_in'] -> ['S', 'A', 'B', 'T']
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

    """!
    @brief Verifica se um caminho (potencialmente de um grafo dividido) corresponde a um caminho
           válido no grafo original.

    Primeiro, o `path` (que pode conter nós com sufixos `_in`/`_out`) é convertido
    para um caminho com nomes de nós originais usando `merge_split_path`.
    Depois, verifica-se se cada par consecutivo de nós no caminho merged forma uma
    aresta existente no `original_graph`.

    @param path A lista de nós do caminho, possivelmente com sufixos `_in`/`_out`.
    @param original_graph O grafo NetworkX original (sem nós divididos).
    @return True se o caminho merged for válido (não vazio, com pelo menos 2 nós, e todas
            as arestas existem no `original_graph`), False caso contrário.
    """

    merged_path = merge_split_path(path)
    if not merged_path or len(merged_path) < 2:
        return False
    for u, v in zip(merged_path[:-1], merged_path[1:]):
        if not original_graph.has_edge(u, v):
            return False
    return True

# ------------------------------------------------------
def path_cost(path, G):

    """!
    @brief Calcula o custo de um caminho no grafo G.
    @param path Lista de nós representando o caminho.
    @param graph_G O grafo NetworkX original.
    @return O custo total do caminho, ou None se o caminho for inválido/vazio ou uma aresta não existir.
    """

    if not path or len(path) < 2:
        return None
    cost = 0
    for u, v in zip(path[:-1], path[1:]):
        if G.has_edge(u, v):
            cost += G[u][v].get('cost', 1)
        else:
            return None
    return cost