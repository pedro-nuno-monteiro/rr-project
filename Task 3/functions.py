import networkx as nx
import matplotlib.pyplot as plt
import sys
import matplotlib.lines as mlines
import math
import traceback
import random

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
def draw_network(G, node_mapping, origem, destino, caminho1, caminho2):
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

def draw_suurballe_steps(G_split, P1_split, G_transformed, P2_split, G_original, node_mapping, source, target):
    """
    Visualizes the intermediate steps of the Suurballe algorithm on the split graph,
    with increased node separation and legends.
    """
    print("\nGenerating intermediate step visualizations...")

    # --- Calculate Layout based on Original Positions ---
    pos_orig = nx.get_node_attributes(G_original, 'pos')
    pos_split = {}
    node_size = 350 # Slightly larger nodes might help too
    font_size = 8   # Slightly larger font
    # INCREASED OFFSET for better separation <<<<<<<<<<<<<<<<<<<<<<<
    offset = 0.4  # Aumentado de 0.1 - ajuste conforme necessário

    # Determine coordinate range to potentially scale offset, but fixed value is simpler first
    # x_coords = [p[0] for p in pos_orig.values()]
    # y_coords = [p[1] for p in pos_orig.values()]
    # x_range = max(x_coords) - min(x_coords) if x_coords else 1
    # y_range = max(y_coords) - min(y_coords) if y_coords else 1
    # avg_range = (x_range + y_range) / 2
    # dynamic_offset = avg_range * 0.05 # Example dynamic offset calculation
    # offset = dynamic_offset # Use dynamic offset if preferred

    print(f"Using node separation offset: {offset}")

    for node_orig, pos_xy in pos_orig.items():
        node_in = f"{node_orig}_in"
        node_out = f"{node_orig}_out"
        x, y = pos_xy
        # Place _in slightly left/up, _out slightly right/down for visual separation
        pos_split[node_in] = (x - offset, y + offset)
        pos_split[node_out] = (x + offset, y - offset)

        # Ensure source/target split nodes have positions if isolated
        if node_orig == source and f"{source}_out" not in pos_split:
             pos_split[f"{source}_out"] = (x + offset, y - offset)
        if node_orig == target and f"{target}_in" not in pos_split:
             pos_split[f"{target}_in"] = (x - offset, y + offset)

    # Ensure all nodes in G_split have positions, fallback if needed
    for node in G_split.nodes():
        if node not in pos_split:
            print(f"Warning: Position not found for split node {node}. Using default.")
            base_node = node.rsplit('_', 1)[0]
            if base_node in pos_orig:
                 x, y = pos_orig[base_node]
                 if node.endswith("_in"): pos_split[node] = (x - offset, y + offset)
                 else: pos_split[node] = (x + offset, y - offset)
            else: pos_split[node] = (random.uniform(-1,1), random.uniform(-1,1)) # Random fallback

    s_split = f"{source}_out"
    d_split = f"{target}_in"

    # --- Plot 1: G_split and P1_split ---
    plt.figure("Suurballe Step 1: Split Graph & P1", figsize=(14, 9)) # Slightly larger figure
    plt.title(f"Step 1: Split Graph & First Path P1 (Source: {s_split}, Target: {d_split})")
    ax1 = plt.gca() # Get current axes

    # Define edge lists
    internal_edges = [(u,v) for u, v, d in G_split.edges(data=True) if u.endswith('_in') and v.endswith('_out') and u.rsplit('_',1)[0] == v.rsplit('_',1)[0]]
    P1_edges_set = set(zip(P1_split[:-1], P1_split[1:])) if P1_split else set()
    # Other edges are those not internal and not in P1
    other_edges_plot1 = [e for e in G_split.edges() if e not in internal_edges and e not in P1_edges_set]

    # Draw edges with specific styles
    nx.draw_networkx_edges(G_split, pos_split, ax=ax1, edgelist=other_edges_plot1, edge_color='gray', alpha=0.5, arrows=True, label='_nolegend_')
    nx.draw_networkx_edges(G_split, pos_split, ax=ax1, edgelist=internal_edges, edge_color='silver', style='dashed', alpha=0.7, arrows=True, label='_nolegend_')
    if P1_split:
        nx.draw_networkx_edges(G_split, pos_split, ax=ax1, edgelist=list(P1_edges_set), edge_color='green', width=2.5, arrows=True, style='solid', label='_nolegend_')

    # Draw nodes
    node_colors_split1 = {node: 'lightgreen' if node == s_split else 'salmon' if node == d_split else 'skyblue' for node in G_split.nodes()}
    nx.draw_networkx_nodes(G_split, pos_split, ax=ax1, node_size=node_size, node_color=[node_colors_split1.get(n, 'gray') for n in G_split.nodes()], label='_nolegend_')
    nx.draw_networkx_labels(G_split, pos_split, ax=ax1, font_size=font_size)

    # Draw edge labels (original costs)
    edge_labels_split1 = {}
    for u, v, d in G_split.edges(data=True):
         # Don't label internal edges if cost is 0 to reduce clutter
         is_internal = u.endswith('_in') and v.endswith('_out') and u.rsplit('_',1)[0] == v.rsplit('_',1)[0]
         cost = d.get('cost', None)
         if not is_internal or cost != 0:
             edge_labels_split1[(u, v)] = f"{cost:.1f}" if cost is not None else ""

    nx.draw_networkx_edge_labels(G_split, pos_split, ax=ax1, edge_labels=edge_labels_split1, font_size=font_size-1, label_pos=0.4) # Adjust label position

    # --- Add Legend for Plot 1 ---
    legend_handles1 = [
        mlines.Line2D([], [], color='green', linestyle='solid', linewidth=2.5, label='Path 1 (P1)'),
        mlines.Line2D([], [], color='silver', linestyle='dashed', linewidth=1, label='Internal Edges (Cost 0)'),
        mlines.Line2D([], [], color='gray', linestyle='solid', linewidth=1, label='Other Edges'),
        mlines.Line2D([], [], color='lightgreen', marker='o', markersize=8, linestyle='None', label=f'Source ({s_split})'),
        mlines.Line2D([], [], color='salmon', marker='o', markersize=8, linestyle='None', label=f'Target ({d_split})'),
        mlines.Line2D([], [], color='skyblue', marker='o', markersize=8, linestyle='None', label='Other Nodes')
    ]
    ax1.legend(handles=legend_handles1, loc='best', fontsize='small')

    plt.box(False)
    plt.show(block=False) # Show non-blocking

    # --- Plot 2: G_transformed and P2_split ---
    if G_transformed is None or P2_split is None:
        print("Skipping visualization of Step 3 (Transformed Graph & P2) as it wasn't computed.")
        return # Exit if no second path stage was reached

    plt.figure("Suurballe Step 3: Transformed Graph & P2", figsize=(14, 9)) # Slightly larger figure
    plt.title(f"Step 3: Transformed Graph (Reduced Costs) & Second Path P2")
    ax2 = plt.gca() # Get current axes

    # Identify edge types for drawing and legend
    reversed_zero_cost_edges = []
    P1_edges_orig_set = set(zip(P1_split[:-1], P1_split[1:])) if P1_split else set() # Edges from original P1

    # Need P1_edges_set if P1_split exists, handle if None
    if P1_split:
        P1_edges_set = set(zip(P1_split[:-1], P1_split[1:]))
        for u, v, data in G_transformed.edges(data=True):
            # Check if reduced cost is near zero AND if its reverse was in the original P1
            if abs(data.get('reduced_cost', 1)) < 1e-9 and (v, u) in P1_edges_set:
                reversed_zero_cost_edges.append((u, v))
    else: # Should not happen if we reached here, but safety check
        P1_edges_set = set()


    P2_edges_set = set(zip(P2_split[:-1], P2_split[1:])) if P2_split else set()
    reversed_zero_cost_set = set(reversed_zero_cost_edges)

    # Other edges are those not reversed P1 edges and not in P2
    other_edges_plot2 = [e for e in G_transformed.edges() if e not in reversed_zero_cost_set and e not in P2_edges_set]
    # Edges of P2 that are NOT reversed P1 edges
    p2_non_reversed_edges = list(P2_edges_set - reversed_zero_cost_set)


    # Draw edges
    nx.draw_networkx_edges(G_transformed, pos_split, ax=ax2, edgelist=other_edges_plot2, edge_color='gray', alpha=0.5, arrows=True, label='_nolegend_')
    nx.draw_networkx_edges(G_transformed, pos_split, ax=ax2, edgelist=reversed_zero_cost_edges, edge_color='purple', style='dashed', width=1.5, alpha=0.8, arrows=True, label='_nolegend_') # Highlight reversed P1 edges
    if P2_split:
        nx.draw_networkx_edges(G_transformed, pos_split, ax=ax2, edgelist=p2_non_reversed_edges, edge_color='blue', width=2.5, arrows=True, style='solid', label='_nolegend_') # Highlight P2 (non-reversed part)
        # Also draw the parts of P2 that ARE reversed edges, maybe slightly thicker or distinctly
        p2_reversed_part = list(P2_edges_set.intersection(reversed_zero_cost_set))
        nx.draw_networkx_edges(G_transformed, pos_split, ax=ax2, edgelist=p2_reversed_part, edge_color='blue', style='dashed', width=2.5, alpha=0.8, arrows=True, label='_nolegend_') # Reversed P1 edges used by P2

    # Draw nodes (use same positions)
    nodes_in_G_transformed = list(G_transformed.nodes())
    node_colors_split2 = {node: 'lightgreen' if node == s_split else 'salmon' if node == d_split else 'skyblue' for node in nodes_in_G_transformed}
    nx.draw_networkx_nodes(G_transformed, pos_split, ax=ax2, nodelist=nodes_in_G_transformed, node_size=node_size, node_color=[node_colors_split2.get(n, 'gray') for n in nodes_in_G_transformed], label='_nolegend_')
    nx.draw_networkx_labels(G_transformed, pos_split, ax=ax2, labels={n: n for n in nodes_in_G_transformed}, font_size=font_size)

    # Draw edge labels (reduced costs)
    edge_labels_split2 = {}
    for u, v, d in G_transformed.edges(data=True):
        cost = d.get('reduced_cost', math.inf)
        label = f"{cost:.1f}" if cost != math.inf and abs(cost) > 1e-9 else ("0.0" if abs(cost) < 1e-9 else "inf") # Format 0 nicely
        # Avoid labelling edges not drawn if G_transformed might have extra edges? Unlikely here.
        edge_labels_split2[(u,v)] = label

    nx.draw_networkx_edge_labels(G_transformed, pos_split, ax=ax2, edge_labels=edge_labels_split2, font_size=font_size-1, label_pos=0.4) # Adjust label position

    # --- Add Legend for Plot 2 ---
    legend_handles2 = [
        mlines.Line2D([], [], color='blue', linestyle='solid', linewidth=2.5, label='Path 2 (P2)'),
        mlines.Line2D([], [], color='purple', linestyle='dashed', linewidth=1.5, label='Reversed P1 Edges (Cost 0)'),
        mlines.Line2D([], [], color='gray', linestyle='solid', linewidth=1, label='Other Edges'),
        mlines.Line2D([], [], color='lightgreen', marker='o', markersize=8, linestyle='None', label=f'Source ({s_split})'),
        mlines.Line2D([], [], color='salmon', marker='o', markersize=8, linestyle='None', label=f'Target ({d_split})'),
        mlines.Line2D([], [], color='skyblue', marker='o', markersize=8, linestyle='None', label='Other Nodes')
    ]
    # Add entry if P2 uses reversed edges
    if any((e in reversed_zero_cost_set) for e in P2_edges_set):
         legend_handles2.insert(1, mlines.Line2D([], [], color='blue', linestyle='dashed', linewidth=2.5, label='P2 using Reversed P1 Edge'))

    ax2.legend(handles=legend_handles2, loc='best', fontsize='small')


    plt.box(False)
    plt.show(block=False) # Show non-blocking

    print("Intermediate visualizations displayed (may be in separate windows).")

def suurballe_disjoint_paths(G_original, source, target):
    """
    Implements Suurballe's algorithm combined with node splitting to find
    two node-disjoint paths with minimum total cost. NOW RETURNS INTERMEDIATE RESULTS.

    Args:
        G_original (nx.DiGraph): The original graph.
        source: The source node.
        target: The target node.

    Returns:
        tuple: (final_path1, final_path2, G_split, P1_split, G_transformed, P2_split)
               final_path1/2 are lists of nodes in the original graph.
               Returns (None, None, G_split, None, None, None) etc. on failure or if steps
               are not reached. G_split is returned even on early failure if created.
    """
    # Initialize intermediate results to None
    G_split, P1_split, G_transformed, P2_split = None, None, None, None
    s_split, d_split = None, None  # Define to allow returning them even on early exit
    distances = None # Initialize distances

    try:
        # --- Step 0: Node Splitting ---
        G_split, s_split, d_split = split_node_graph(G_original, source, target)

        if s_split not in G_split or d_split not in G_split:
            print(f"Error: Split source {s_split} or target {d_split} not in split graph nodes.")
            # Attempt to check if nodes exist but maybe without edges causing issues later
            if not G_split.has_node(s_split):
                 print(f"Reason: {s_split} does not exist.")
            if not G_split.has_node(d_split):
                 print(f"Reason: {d_split} does not exist.")
            return None, None, G_split, None, None, None

        # --- Step 1: Find the first shortest path tree and path P1 ---
        try:
            # Calculate distances (potentials 't') from s_split to all nodes
            # Use Dijkstra's algorithm which returns distances and paths dictionary
            distances, first_paths_dict = nx.single_source_dijkstra(G_split, s_split, weight='cost')

            # Check if the target node is reachable (present in the distances/paths keys)
            if d_split not in distances:
                 print(f"Target node {d_split} not reachable from {s_split} in split graph (not in Dijkstra results).")
                 return None, None, G_split, None, None, None

            # Get the specific path P1 from s_split to d_split
            P1_split = first_paths_dict[d_split]
            cost1 = distances[d_split] # Cost of the first path
            print(f"First shortest path (split graph): {P1_split} (Cost: {cost1})")

        except nx.NetworkXNoPath:
            # This exception might be raised by shortest_path, but single_source_dijkstra usually handles it via unreachable nodes
            print(f"No path found between {s_split} and {d_split} using Dijkstra.")
            return None, None, G_split, None, None, None # Return G_split found so far
        except KeyError as e:
            # This might happen if d_split isn't in first_paths_dict, indicating unreachability
             print(f"KeyError accessing path/distance for {e}. Target {d_split} likely not reachable from {s_split}.")
             return None, None, G_split, None, None, None # Return G_split found so far


        # --- Step 2: Transform the network G' ---
        G_transformed = nx.DiGraph()

        # 2.1 Compute reduced costs c'ij = cij + ts(i) - ts(j)
        for u, v, data in G_split.edges(data=True):
            cost_uv = data.get('cost', math.inf) # Use get for safety, default to infinity
            # Ensure distances dictionary exists from Step 1 before accessing
            if distances is None:
                 print("Error: Distances dictionary not computed in Step 1.")
                 # This case should ideally be caught earlier
                 return None, None, G_split, P1_split, None, None # Return what we have

            dist_u = distances.get(u, math.inf) # Potential of node u
            dist_v = distances.get(v, math.inf) # Potential of node v

            # Avoid issues with unreachable nodes having infinite distance
            if dist_u == math.inf or dist_v == math.inf:
                reduced_cost = math.inf # Edge involving unreachable node
            else:
                reduced_cost = cost_uv + dist_u - dist_v
                # Floating point precision check - reduced cost shouldn't be significantly negative
                if reduced_cost < -1e-9: # Allow for small tolerance
                    print(f"Warning: Negative reduced cost detected for edge ({u}, {v}): {reduced_cost}. Clamping to 0.")
                    reduced_cost = 0
                # Clamp small negatives to zero, otherwise keep calculated cost
                reduced_cost = max(0, reduced_cost)


            # Add edge with *reduced* cost to the transformed graph
            # Also carry over the original cost for potential reference/debugging
            G_transformed.add_edge(u, v, reduced_cost=reduced_cost, original_cost=cost_uv)

        # 2.2 & 2.3: Modify arcs along P1 in G_transformed
        P1_edges = list(zip(P1_split[:-1], P1_split[1:]))

        for u, v in P1_edges:
            # 2.2 Remove the forward edge (u, v) from G_transformed.
            if G_transformed.has_edge(u, v):
                G_transformed.remove_edge(u, v)
            else:
                 # This might happen if P1 uses an edge not present in G_split initially? Should not occur.
                 print(f"Warning: Edge ({u}, {v}) from P1 not found in G_transformed during removal step.")


            # 2.3 Add reverse direction edge (v, u) with reduced cost set to 0.
            # Retrieve original cost of the reverse edge (v, u) from G_split if it existed
            original_cost_vu = G_split.get_edge_data(v, u, default={'cost': math.inf})['cost']
            # Add/update the reverse edge in G_transformed with reduced_cost=0
            G_transformed.add_edge(v, u, reduced_cost=0, original_cost=original_cost_vu)


        # --- Step 3: Find shortest path P2 in the transformed network G' ---
        try:
            # Use 'reduced_cost' as the weight now
            # Need to handle potential NetworkXNoPath exception here
            P2_split = nx.shortest_path(G_transformed, source=s_split, target=d_split, weight='reduced_cost')
            cost2_reduced = nx.shortest_path_length(G_transformed, source=s_split, target=d_split, weight='reduced_cost')
            print(f"Second shortest path (transformed graph): {P2_split} (Reduced Cost: {cost2_reduced})")

        except nx.NetworkXNoPath:
            print("No second disjoint path found (NetworkXNoPath in transformed graph).")
            # Only one path exists, merge it back
            path1_original = merge_split_path(P1_split)
            # Return intermediate results up to this point
            return path1_original, None, G_split, P1_split, G_transformed, None # P2_split is None


        # --- Step 4: Remove common arcs with opposite directions ---
        P1_edges_set = set(P1_edges)
        P2_edges_set = set(zip(P2_split[:-1], P2_split[1:]))

        edges_to_remove_from_both = set() # Stores the P1 edges (u,v) whose reverse (v,u) is in P2
        for u, v in P1_edges_set:
            if (v, u) in P2_edges_set:
                edges_to_remove_from_both.add((u, v))
                # print(f"Overlap detected: Removing ({u},{v}) from P1 and ({v},{u}) from P2.") # Debugging

        # Build the final paths edge lists by filtering out the overlaps
        final_P1_edges = []
        for u, v in P1_edges:
            if (u, v) not in edges_to_remove_from_both:
                final_P1_edges.append((u, v))

        final_P2_edges = []
        for u, v in P2_edges_set: # Iterate through edges found in the second path P2
            # Keep the edge (u,v) from P2 *unless* its reverse (v,u) was marked for removal (meaning (v,u) was in P1)
            if (v, u) not in edges_to_remove_from_both:
                 final_P2_edges.append((u, v))


        # --- Path Reconstruction from final edge lists ---
        # Build subgraphs containing only the final edges for each path
        path1_nodes_final = []
        path2_nodes_final = []
        G_path1 = nx.DiGraph(final_P1_edges)
        G_path2 = nx.DiGraph(final_P2_edges)

        # Find the path from source to target within each subgraph
        try:
            # Add nodes that might be isolated endpoints but part of the path conceptually
            if s_split not in G_path1: G_path1.add_node(s_split)
            if d_split not in G_path1: G_path1.add_node(d_split)
            if G_path1.number_of_edges() > 0 or (s_split == d_split and G_path1.has_node(s_split)): # Check if path exists
                 path1_nodes_final = nx.shortest_path(G_path1, s_split, d_split)
            else:
                 print("Path 1 has no edges after overlap removal.")
                 path1_nodes_final = []

        except (nx.NetworkXNoPath, KeyError, nx.NodeNotFound):
             # This might happen if P1 got entirely cancelled out or broken
             print("Warning: Path 1 reconstruction failed after overlap removal (No path in G_path1).")
             path1_nodes_final = [] # Path 1 might become Path 2 or vice versa


        try:
            # Add nodes that might be isolated endpoints
            if s_split not in G_path2: G_path2.add_node(s_split)
            if d_split not in G_path2: G_path2.add_node(d_split)
            if G_path2.number_of_edges() > 0 or (s_split == d_split and G_path2.has_node(s_split)): # Check if path exists
                 path2_nodes_final = nx.shortest_path(G_path2, s_split, d_split)
            else:
                 print("Path 2 has no edges after overlap removal.")
                 path2_nodes_final = []

        except (nx.NetworkXNoPath, KeyError, nx.NodeNotFound):
             # This might happen if P2 got entirely cancelled out or broken
             print("Warning: Path 2 reconstruction failed after overlap removal (No path in G_path2).")
             path2_nodes_final = []

        # --- Postprocessing: Merge Nodes Back ---
        final_path1_original = merge_split_path(path1_nodes_final) if path1_nodes_final else None
        final_path2_original = merge_split_path(path2_nodes_final) if path2_nodes_final else None

        # Handle cases where one path might have become empty after reconstruction
        if not final_path1_original and final_path2_original:
             print("Note: Path 1 became empty after overlap removal; only Path 2 remains.")
             # Swap them so path1 is always the valid one if only one exists
             final_path1_original, final_path2_original = final_path2_original, None
        elif not final_path1_original and not final_path2_original and (final_P1_edges or final_P2_edges):
             # If both failed reconstruction but there were edges, something is wrong
             print("Error: Failed to reconstruct both paths even though final edges existed.")
             # Fallback to returning original P1? Or signal error better?
             # Let's return the first path found before overlap issues.
             # return merge_split_path(P1_split), None, G_split, P1_split, G_transformed, P2_split


        # Ensure we return two distinct paths if found and reconstructed
        if final_path1_original and final_path2_original and final_path1_original == final_path2_original:
             print("Warning: Reconstructed paths are identical. Check overlap removal/reconstruction logic.")
             # Based on Suurballe's guarantee, this ideally shouldn't happen if logic is correct.
             # Let's return P1 and indicate failure finding P2 distinctly.
             # Keep P2_split in the return tuple for debugging the intermediate steps.
             return merge_split_path(P1_split), None, G_split, P1_split, G_transformed, P2_split


        # --- Calculate Final Costs & Print ---
        def calculate_original_cost(G_orig, path_orig):
            # (Function as defined before)
            cost = 0
            if path_orig is None or len(path_orig) < 2: return 0
            for i in range(len(path_orig) - 1):
                u, v = path_orig[i], path_orig[i+1]
                # Check if edge exists in original graph before getting data
                if G_orig.has_edge(u,v):
                    cost += G_orig.get_edge_data(u, v, default={'cost': math.inf})['cost']
                else:
                    print(f"Warning: Edge ({u}, {v}) from reconstructed path not found in original graph G for cost calculation.")
                    return math.inf # Indicate error in cost calculation
            return cost

        cost1_final = calculate_original_cost(G_original, final_path1_original)
        cost2_final = calculate_original_cost(G_original, final_path2_original)

        print("-" * 20)
        if final_path1_original:
            print(f"Final Path 1 (Original Nodes): {final_path1_original} (Original Cost: {cost1_final})")
        if final_path2_original:
            print(f"Final Path 2 (Original Nodes): {final_path2_original} (Original Cost: {cost2_final})")
            if cost1_final != math.inf and cost2_final != math.inf:
                 print(f"Total Original Cost: {cost1_final + cost2_final}")
        elif final_path1_original:
             print("Only one path found/reconstructed.")
        else:
             print("No paths successfully reconstructed.")
        print("-" * 20)


        # --- Final Return ---
        # Return final paths AND intermediate steps for visualization/debugging
        return final_path1_original, final_path2_original, G_split, P1_split, G_transformed, P2_split

    except Exception as e:
        print(f"An unexpected error occurred within suurballe_disjoint_paths: {e}")
        traceback.print_exc() # Print detailed traceback for debugging
        # Return Nones, including for intermediate steps potentially generated before error
        # Ensure G_split is returned if it was created, otherwise None
        return None, None, G_split, P1_split, G_transformed, P2_split
    
def split_node_graph(G, source, target):
    """
    Transforms a graph G by splitting each node A into A_in and A_out
    to enable finding node-disjoint paths using arc-disjoint algorithms.
    """
    G_split = nx.DiGraph()
    node_map = {} # Optional: Keep track of original -> split mapping if needed

    for node in G.nodes():
        node_in = f"{node}_in"
        node_out = f"{node}_out"
        node_map[node] = (node_in, node_out)

        G_split.add_node(node_in)
        G_split.add_node(node_out)
        # Add internal edge with zero cost
        G_split.add_edge(node_in, node_out, cost=0)

    # Re-wire the original edges
    for u, v, data in G.edges(data=True):
        u_out = f"{u}_out"
        v_in = f"{v}_in"
        original_cost = data.get('cost', 1) # Get original cost, default to 1 if missing
        G_split.add_edge(u_out, v_in, cost=original_cost)

    # Define the effective start and end points
    s_split = f"{source}_out"
    d_split = f"{target}_in"

    # Ensure s_split and d_split exist even if source/target have no outgoing/incoming edges
    if not G_split.has_node(s_split): G_split.add_node(s_split)
    if not G_split.has_node(d_split): G_split.add_node(d_split)

    return G_split, s_split, d_split

def merge_split_path(split_path):
    """
    Converts a path from the split-node graph back to the original node names.
    """
    if not split_path: # Handle empty path case
        return []
    original_path = []
    for node in split_path:
        original_node = node.rsplit('_', 1)[0] # Remove _in or _out suffix
        if not original_path or original_path[-1] != original_node:
            original_path.append(original_node)
    return original_path