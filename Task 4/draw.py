import networkx as nx
import matplotlib.pyplot as plt
import math
import matplotlib.lines as mlines

def draw_network(G, node_mapping, origem, destino, caminho1, caminho2, algoritmo):
    """!
    @brief Desenha o grafo da rede, destacando os caminhos e nós importantes.

    Esta função gera uma visualização gráfica do grafo, destacando o caminho mais curto entre o nó de origem e o nó de destino. Além disso, permite destacar dois caminhos diferentes (caso existam) e colorir os nós de origem e destino de forma distinta. O algoritmo usado para encontrar os caminhos pode ser especificado.

    @param G O grafo direcionado a ser desenhado.
    @param node_mapping Mapa de nós, associando índices aos nomes dos nós no grafo.
    @param origem Índice do nó de origem, que será destacado na visualização.
    @param destino Índice do nó de destino, que será destacado na visualização.
    @param caminho1 Lista de nós que representam o primeiro caminho a ser destacado.
    @param caminho2 Lista de nós que representam o segundo caminho a ser destacado (pode ser None).
    @param algoritmo Inteiro indicando o algoritmo utilizado:
        1. "Two Step Approach"
        2. "Suurballe"

    @note A função gera uma imagem do grafo e a salva no diretório de saída como "rede_final.png".
    """

    # Obtém as coordenadas dos nós do grafo
    pos = nx.get_node_attributes(G, 'pos')

    # Cria rótulos no formato "1: Nome"
    labels = {nome: f"{num}: {nome}" for num, nome in node_mapping.items()}

    origem_nome = None
    if isinstance(origem, int) and origem in node_mapping:
        origem_nome = node_mapping[origem]
    elif isinstance(origem, str) and origem in G.nodes():
        origem_nome = origem
    else:
        # Se não for int válido nem str válido, lança erro
        raise ValueError(f"Nó de origem '{origem}' inválido ou não encontrado.")

    destino_nome = None
    if isinstance(destino, int) and destino in node_mapping:
        destino_nome = node_mapping[destino]
    elif isinstance(destino, str) and destino in G.nodes():
        destino_nome = destino
    else:
        # Se não for int válido nem str válido, lança erro
        raise ValueError(f"Nó de destino '{destino}' inválido ou não encontrado.")

    # Define as cores dos nós
    node_colors = {
        nome: 'green' if nome == origem_nome else
                'red' if nome == destino_nome else
                'lightblue'
        for nome in G.nodes
    }

    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Adiciona um título baseado no algoritmo
    if algoritmo == 1:
        plt.title("Visualização do Algoritmo Two Step Approach")
    elif algoritmo == 2:
        plt.title("Visualização do Algoritmo Suurballe")

    plt.tight_layout()  # Ajusta a disposição dos subplots para evitar sobreposição

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
    edge_labels = {}
    for u, v, d in G.edges(data=True):
        edge_labels[(u, v)] = f"{d['cost']}"
        if edge_labels[(u, v)] == "0.0":
            edge_labels[(u, v)] = "1.0"

    # será colocar 2 arcos em vez de ter 1 bidirecional
    # assim 1 fica com 0 e outro com o valor do custo

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, font_color='blue')

    # Desenha os rótulos dentro de retângulos coloridos
    for nome, (x, y) in pos.items():
        label_text = labels.get(nome, nome)
        plt.text(x, y, label_text, fontsize=8, fontweight='bold',
                bbox=dict(facecolor=node_colors.get(nome, 'lightblue'), edgecolor='black', boxstyle='round,pad=0.3'),
                horizontalalignment='center', verticalalignment='center')

    plt.box(False)


    # Criar objetos para a legenda
    legend_caminho1 = mlines.Line2D([], [], color='green', linewidth=3, label="Caminho Mais Curto")
    legend_inicio = mlines.Line2D([], [], color='green', marker='s', markersize=8, linestyle='None', label="Nó Origem")
    legend_fim = mlines.Line2D([], [], color='red', marker='s', markersize=8, linestyle='None', label="Nó Destino")
    legend_caminho2 = mlines.Line2D([], [], color='blue', linewidth=3, label="2º Caminho Mais Curto")
        
    
    plt.legend(handles=[legend_caminho1, legend_caminho2, legend_inicio, legend_fim], loc='upper right')

    plt.savefig("output/rede_final.png", dpi=300)
    
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

    plt.savefig("output/rede_original.png", dpi=300)
    
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
    print(f"\nA desenhar: {filename}")
    # Cria uma nova figura para cada passo para evitar sobreposição
    plt.figure(f"{filename}", figsize=(12, 8)) # Nome único para a figura

    # Obtém posições diretamente do grafo G (devem ter sido adicionadas antes)
    pos = nx.get_node_attributes(G, 'pos')
    if not pos:
        print(f"Aviso em draw_graph_5 para {filename}: Atributo 'pos' não encontrado. Usando layout spring.")
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

    nx.draw_networkx_edges(G, pos, edgelist=other_edges, edge_color='gray', alpha=0.5, width=1, arrows=True, arrowsize=15, connectionstyle='arc3, rad=0.05')
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
                                bbox=dict(facecolor='white', alpha=0.4, edgecolor='none', boxstyle='round,pad=0.1'))

    # Destaca caminho 1 (verde)
    if caminho1_split:
        path_edges1 = list(zip(caminho1_split, caminho1_split[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges1, edge_color='green', width=3, arrows=True, arrowsize=20, style='solid')

    # Destaca caminho 2 (azul)
    if caminho2_split:
        path_edges2 = list(zip(caminho2_split, caminho2_split[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges2, edge_color='blue', width=3, arrows=True, arrowsize=20, style='solid')

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

    plt.title(f"Suurballe Step: {filename}")
    plt.axis('off')
    output_filename = f"output/{filename}.png" # Usa filename base
    try:
        plt.savefig(output_filename, dpi=300, bbox_inches='tight')
        print(f"Gráfico guardado na localização: {output_filename}")
    except Exception as e:
        print(f"Erro ao guardar {output_filename}: {e}")
    plt.show()