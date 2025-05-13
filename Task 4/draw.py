import networkx as nx
import matplotlib.pyplot as plt
import math
import matplotlib.lines as mlines

def draw_network(G, node_mapping, origem, destino, caminho_tsa, caminho2, caminho_sur, caminho3, algoritmo):
    """
    Desenha o grafo destacando até três caminhos e os nós de origem e destino.

    @param G: Grafo direcionado.
    @param node_mapping: Dicionário {índice: nome_do_nó}.
    @param origem: Índice ou nome do nó de origem.
    @param destino: Índice ou nome do nó de destino.
    @param caminho1: Lista de nós do primeiro caminho (mais curto).
    @param caminho2: Lista de nós do segundo caminho (Two-Step).
    @param caminho3: Lista de nós do terceiro caminho (Suurballe).
    @param algoritmo: Inteiro que indica o algoritmo:
        1 - Two Step Approach
        2 - Suurballe
        3 - Todos os três caminhos
    """

    pos = nx.get_node_attributes(G, 'pos')
    labels = {nome: f"{num}: {nome}" for num, nome in node_mapping.items()}

    # nomes dos nós de origem e destino
    origem_nome = node_mapping.get(origem, origem)
    destino_nome = node_mapping.get(destino, destino)

    if origem_nome not in G.nodes:
        raise ValueError(f"O nó de origem '{origem_nome}' não está no grafo.")
    if destino_nome not in G.nodes:
        raise ValueError(f"O nó de destino '{destino_nome}' não está no grafo.")

    node_colors = {
        nome: 'green' if nome == origem_nome else
            'red' if nome == destino_nome else
            'lightblue'
        for nome in G.nodes
    }

    plt.figure(figsize=(10, 7))
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Desenha todas as arestas com opacidade
    nx.draw_networkx_edges(G, pos, edge_color='black', alpha=0.8, width=1.2)

    # Primeiro caminho (mais curto) - verde
    if caminho_tsa:
        path_edges1 = list(zip(caminho_tsa, caminho_tsa[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges1, edge_color='green', width=3, arrows=True, arrowsize=20)

    if caminho_sur:
        path_edges4 = list(zip(caminho_sur, caminho_sur[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges4, edge_color='orange', width=3, arrows=True, arrowsize=20)
    # Segundo caminho (Two-Step) - azul
    if caminho2:
        path_edges2 = list(zip(caminho2, caminho2[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges2, edge_color='blue', width=3, arrows=True, arrowsize=20)

    # Terceiro caminho (Suurballe) - roxo
    if caminho3:
        path_edges3 = list(zip(caminho3, caminho3[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges3, edge_color='purple', width=3, arrows=True, arrowsize=20)

    # Rótulos dos custos das arestas
    edge_labels = {}
    for u, v, d in G.edges(data=True):
        label = str(d.get('cost', 1.0))
        edge_labels[(u, v)] = "1.0" if label == "0.0" else label

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, font_color='blue')

    # Rótulos dos nós
    for nome, (x, y) in pos.items():
        label_text = labels.get(nome, nome)
        plt.text(x, y, label_text, fontsize=8, fontweight='bold',
                bbox=dict(facecolor=node_colors.get(nome, 'lightblue'), edgecolor='black', boxstyle='round,pad=0.3'),
                horizontalalignment='center', verticalalignment='center')

    # Legenda
    legenda = [
        mlines.Line2D([], [], color='green', marker='s', markersize=8, linestyle='None', label="Nó Origem"),
        mlines.Line2D([], [], color='red', marker='s', markersize=8, linestyle='None', label="Nó Destino")
    ]

    if algoritmo == 1:
        legenda.append(mlines.Line2D([], [], color='green', linewidth=3, label="Caminho Mais Curto"))
        legenda.append(mlines.Line2D([], [], color='blue', linewidth=3, label="Two-Step Approach"))
    elif algoritmo == 2:
        legenda.append(mlines.Line2D([], [], color='orange', linewidth=3, label="Caminho Inicial Surballe"))
        legenda.append(mlines.Line2D([], [], color='blue', linewidth=3, label="Suurballe"))
    elif algoritmo == 3:
            # Subplots: um para TSA, outro para Suurballe
            fig, axs = plt.subplots(1, 2, figsize=(18, 7))
            plt.subplots_adjust(left=0.05, right=0.95, top=0.92, bottom=0.08, wspace=0.25)

            # --- Subplot 1: TSA ---
            axs[0].set_title("Two-Step Approach")
            nx.draw_networkx_edges(G, pos, ax=axs[0], edge_color='black', alpha=0.8, width=1.2)
            if caminho_tsa:
                path_edges1 = list(zip(caminho_tsa, caminho_tsa[1:]))
                nx.draw_networkx_edges(G, pos, ax=axs[0], edgelist=path_edges1, edge_color='green', width=3, arrows=True, arrowsize=20)
            if caminho2:
                path_edges2 = list(zip(caminho2, caminho2[1:]))
                nx.draw_networkx_edges(G, pos, ax=axs[0], edgelist=path_edges2, edge_color='blue', width=3, arrows=True, arrowsize=20)
            for nome, (x, y) in pos.items():
                label_text = labels.get(nome, nome)
                axs[0].text(x, y, label_text, fontsize=8, fontweight='bold',
                    bbox=dict(facecolor=node_colors.get(nome, 'lightblue'), edgecolor='black', boxstyle='round,pad=0.3'),
                    horizontalalignment='center', verticalalignment='center')
            axs[0].axis('off')

            # --- Subplot 2: Suurballe ---
            axs[1].set_title("Suurballe")
            nx.draw_networkx_edges(G, pos, ax=axs[1], edge_color='black', alpha=0.8, width=1.2)
            if caminho_sur:
                path_edges4 = list(zip(caminho_sur, caminho_sur[1:]))
                nx.draw_networkx_edges(G, pos, ax=axs[1], edgelist=path_edges4, edge_color='orange', width=3, arrows=True, arrowsize=20)
            if caminho3:
                path_edges3 = list(zip(caminho3, caminho3[1:]))
                nx.draw_networkx_edges(G, pos, ax=axs[1], edgelist=path_edges3, edge_color='purple', width=3, arrows=True, arrowsize=20)
            for nome, (x, y) in pos.items():
                label_text = labels.get(nome, nome)
                axs[1].text(x, y, label_text, fontsize=8, fontweight='bold',
                    bbox=dict(facecolor=node_colors.get(nome, 'lightblue'), edgecolor='black', boxstyle='round,pad=0.3'),
                    horizontalalignment='center', verticalalignment='center')
            axs[1].axis('off')

            # Legenda única para ambos
            legenda.append(mlines.Line2D([], [], color='green', linewidth=3, label="Caminho Mais Curto"))
            legenda.append(mlines.Line2D([], [], color='orange', linewidth=3, label="Caminho Inicial Surballe"))
            legenda.extend([
                mlines.Line2D([], [], color='blue', linewidth=3, label="Two-Step Approach"),
                mlines.Line2D([], [], color='purple', linewidth=3, label="Suurballe")
            ])
            fig.legend(handles=legenda, loc='upper center', ncol=5)
            plt.savefig("output/Rede Final.png", dpi=300)
            plt.show()
            return

    
    plt.legend(handles=legenda, loc='upper right')
    plt.box(False)
    plt.title(f"Rede Final")
    plt.savefig("output/Rede Final.png", dpi=300)
    plt.show()
    

# ------------------------------------------------------
def draw_empty_network(G, node_mapping):
    """!
    @brief Desenha uma rede vazia, sem destacar caminhos ou nós.

    Esta função gera uma visualização gráfica do grafo sem destacar nenhum caminho ou nó específico.

    @param G O grafo direcionado a ser desenhado.
    @param node_mapping Mapa de nós, associando índices aos nomes dos nós no grafo.
    
    @note Esta função é útil para exibir apenas a estrutura do grafo sem informações adicionais, como os caminhos ou a origem/destino.
    """
    # Obtém as coordenadas dos nós do grafo
    pos = nx.get_node_attributes(G, 'pos')

    # Cria rótulos no formato "1: Nome"
    labels = {nome: f"{num}: {nome}" for num, nome in node_mapping.items()}

    #plt.subplots_adjust(left=0, right=1, top=1, bottom=0) 

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

    plt.savefig("output/Rede Original.png", dpi=300)
    
    return plt

# ------------------------------------------------------
def draw_suurballe(G, origem_split, destino_split, caminho1_split, caminho2_split, filename):
    """!
    @brief Desenha um grafo dividido ou transformado e destaca os caminhos encontrados pelo algoritmo Suurballe.

    A função visualiza o grafo após a aplicação do algoritmo Suurballe, destacando os caminhos mais curtos (se encontrados) e as arestas internas (no formato '_in'/'_out'). Cada etapa do algoritmo é ilustrada, mostrando o estado atual do grafo, o primeiro caminho mais curto em verde e o segundo caminho (se houver) em azul.

    @param G Grafo direcionado (potencialmente dividido), representando a rede.
    @param origem_split Nó de origem no formato dividido (com sufixo '_out').
    @param destino_split Nó de destino no formato dividido (com sufixo '_in').
    @param caminho1_split Lista de nós representando o primeiro caminho encontrado (caminho mais curto).
    @param caminho2_split Lista de nós representando o segundo caminho encontrado (pode ser None).
    @param filename Nome do arquivo usado para salvar a imagem gerada, representando o estado atual do grafo.
    
    @note A função cria uma visualização do grafo, destacando os caminhos e as arestas em diferentes cores para facilitar a compreensão do algoritmo.
    @note As arestas internas (de um nó dividido) são desenhadas com uma linha tracejada e de cor prata.
    """
    print(f"\n * A desenhar: {filename}")
    # Cria uma nova figura para cada passo para evitar sobreposição
    plt.figure(f"{filename}", figsize=(12, 8)) # Nome único para a figura
    plt.subplots_adjust(left=0.05, right=0.95, top=0.92, bottom=0.08)

    # Obtém posições diretamente do grafo G (devem ter sido adicionadas antes)
    pos = nx.get_node_attributes(G, 'pos')
    if not pos:
        print(f"Aviso na função draw_suurballe para {filename}: Atributo 'pos' não encontrado. Usando layout spring.")
        pos = nx.spring_layout(G) # Fallback

    # Cria rótulos diretamente dos nomes dos nós
    labels = {node: node for node in G.nodes()} # Usa o próprio nome do nó como rótulo

    # Define cores com base na origem/destino *divididos*
    node_colors = {
        nome: 'lightgreen' if nome == origem_split else
            'salmon' if nome == destino_split else
            'skyblue'
        for nome in G.nodes()
    }

    # Desenha arestas base (cinza)
    internal_edges = [(u,v) for u, v in G.edges() if u.endswith('_in') and v.endswith('_out') and u.rsplit('_',1)[0] == v.rsplit('_',1)[0]]
    other_edges = [e for e in G.edges() if e not in internal_edges]

    nx.draw_networkx_edges(G, pos, edgelist=other_edges, edge_color='black', alpha=0.8, width=1.5, arrows=True, arrowsize=20, connectionstyle='arc3, rad=0.05')
    nx.draw_networkx_edges(G, pos, edgelist=internal_edges, edge_color='silver', style='dashed', alpha=0.6, width=1, arrows=True, arrowsize=15)

    # Adiciona rótulos das arestas (atributo 'cost')
    edge_labels = {}
    for u, v, d in G.edges(data=True):
        cost = d.get('cost', math.inf)
        label = f"{cost:.1f}" if isinstance(cost, (int, float)) and cost != math.inf else ("0.0" if isinstance(cost, (int, float)) and abs(cost)<1e-9 else "inf")
        is_internal = u.endswith('_in') and v.endswith('_out') and u.rsplit('_',1)[0] == v.rsplit('_',1)[0]
        if not (is_internal and abs(cost) < 1e-9): # Não mostra custo 0 nas internas
            edge_labels[(u, v)] = label

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                font_size=7, font_color='darkblue',
                                label_pos=0.4,
                                connectionstyle='arc3, rad=0.1',
                                bbox=dict(facecolor='white', alpha=0.4, edgecolor='none', boxstyle='round,pad=0.1'))

    # Destaca caminho 1 (verde)
    if caminho1_split:
        path_edges1 = list(zip(caminho1_split, caminho1_split[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges1, edge_color='green', width=3, arrows=True, arrowsize=20, style='solid', connectionstyle='arc3, rad=0.05')

    # Destaca caminho 2 (azul)
    if caminho2_split:
        path_edges2 = list(zip(caminho2_split, caminho2_split[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges2, edge_color='blue', width=3, arrows=True, arrowsize=20, style='solid', connectionstyle='arc3, rad=0.05')
    
    # Desenha Nós
    nx.draw_networkx_nodes(G, pos, node_size=350, node_color=[node_colors.get(n, 'gray') for n in G.nodes()])

    # Desenha Rótulos (nomes _in/_out)
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_weight='bold')

    # Legenda adaptada
    legend_items = []
    if caminho1_split: legend_items.append(plt.Line2D([], [], color='green', linewidth=3, label="Caminho 1"))
    if caminho2_split: legend_items.append(plt.Line2D([], [], color='blue', linewidth=3, label="Caminho 2"))
    legend_items.extend([
        plt.Line2D([], [], color='silver', linestyle='dashed', linewidth=1, label="Aresta Interna"),
        plt.Line2D([], [], color='gray', linestyle='solid', linewidth=1, label="Outra Aresta"),
        plt.Line2D([], [], color='lightgreen', marker='o', markersize=8, linestyle='None', label=f"Origem ({origem_split})"),
        plt.Line2D([], [], color='salmon', marker='o', markersize=8, linestyle='None', label=f"Destino ({destino_split})"),
        plt.Line2D([], [], color='skyblue', marker='o', markersize=8, linestyle='None', label="Outro Nó")
    ])
    plt.legend(handles=legend_items, loc='best', fontsize='small')

    plt.title(f"Suurballe - {filename}")
    plt.axis('off')
    output_filename = f"output/{filename}.png" # Usa filename base
    try:
        plt.savefig(output_filename, dpi=300, bbox_inches='tight')
        print(f" * Gráfico guardado na localização: {output_filename}")
    except Exception as e:
        print(f"Erro ao guardar {output_filename}: {e}")
    plt.show()