import networkx as nx
import matplotlib.pyplot as plt

def retrieve_data(data):

    # cria gráfico direcionado
    G = nx.DiGraph()
    
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
    for linha in linhas_nos:

        # dividir cada linha em nome [esquerda] e coordenadas [direita]
        no = linha.split('(')
        nome_no = no[0].strip()
        coordenadas = no[1].strip(' )').split()

        # adicionar nó
        G.add_node(nome_no, pos = (float(coordenadas[0]), float(coordenadas[1])))
    
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

    return G

def draw_network(G):

    pos = nx.get_node_attributes(G, 'pos')

    # desenha o gráfico
    plt.figure(figsize=(10, 5))
    nx.draw(G, pos,
            node_color='lightblue',
            node_size=500,
            with_labels=True,
            node_shape='o',
            font_size=8,
            font_weight='bold',
            edge_color='red',
            arrows=True)
    
    plt.title('Atlanta Network')
    plt.axis('equal')
    plt.show()

with open('atlanta.txt', 'r') as file:
    network_data = file.read()

# criar grafo a partir do ficheiro
G = retrieve_data(network_data)

# desenhar grafo
draw_network(G)