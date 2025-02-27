import networkx as nx
import matplotlib.pyplot as plt
import os


def retrieve_data(data):

    # cria um grafo direcionado
    G = nx.DiGraph()
    
    node_mapping = {}  
    #reverse_mapping = {}
    
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
        aresta = linha.split('(')[1].split(')')[0].strip()

        # divide a aresta em source e target
        source, target = aresta.split()
        G.add_edge(source, target)

    return G, node_mapping


def draw_network(G, node_mapping, origem, destino):

    pos = nx.get_node_attributes(G, 'pos')
    labels = {nome: f"{num}: {nome}" for num, nome in node_mapping.items()}
    
    node_colors = ['lightblue' if nome not in [node_mapping.get(origem), node_mapping.get(destino)] 
                   else 'green' if nome == node_mapping.get(origem) 
                   else 'red' 
                   for nome in G.nodes]
    
    # desenha o gráfico
    plt.figure(figsize=(10, 5))
    nx.draw(G, pos,
            node_color=node_colors,
            node_size=2000,
            with_labels=True,
            labels=labels,
            node_shape='o',
            font_size=7,
            font_weight='bold',
            edge_color='red',
            arrows=True)
    
    plt.title('Topologia da Rede')
    plt.axis('equal')
    plt.show()


def ask_origin_destiny (node_mapping):
    
    os.system('cls')
    
    print("\n-------------- Escolha do nó de origem e destino ---------------")
    for num, nome in node_mapping.items():
        print(f"{num}: {nome}")
        
    print("\n---------------------------------------------------------------")
    while True:
        try:
            origem = int(input("\nDigite o número do nó de origem: "))
            destino = int(input("Digite o número do nó de destino: "))
            
            if origem in node_mapping and destino in node_mapping:
                break
            else:
                print("\nNúmero inválido. Por favor, escolha um número da lista.")
        except ValueError:
            print("\nNúmero inválido. Por favor, escolha um número da lista.")  
    
    return origem, destino
    
    