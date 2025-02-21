import networkx as nx
import matplotlib.pyplot as plt

def parse_sndlib_network(data):
    # Create a new directed graph
    G = nx.DiGraph()
    
    # Parse nodes section
    nodes_section = data[data.find("NODES ("):data.find("LINKS (")]
    node_lines = [line.strip() for line in nodes_section.split('\n') if line.strip() and not line.startswith('#')]
    
    # Add nodes with their positions
    for line in node_lines[1:-1]:  # Skip "NODES (" and ")"
        node_data = line.split('(')
        node_id = node_data[0].strip()
        coords = node_data[1].strip(' )').split()
        G.add_node(node_id, pos=(float(coords[0]), float(coords[1])))
    
    # Parse links section
    links_section = data[data.find("LINKS ("):data.find("DEMANDS (")]
    link_lines = [line.strip() for line in links_section.split('\n') if line.strip() and not line.startswith('#')]
    
    # Add edges
    for line in link_lines[1:-1]:  # Skip "LINKS (" and ")"
        link_data = line.split('(')[1].split(')')[0].strip()
        source, target = link_data.split()
        G.add_edge(source, target)
    
    return G

def draw_network(G):
    # Get node positions
    pos = nx.get_node_attributes(G, 'pos')
    
    # Draw the network
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos,
            node_color='lightblue',
            node_size=500,
            with_labels=True,
            node_shape='o',
            font_size=8,
            font_weight='bold',
            arrows=True)
    
    plt.title('Abilene Network Topology')
    plt.axis('equal')
    plt.show()

with open('abilene.txt', 'r') as file:
    network_data = file.read()

# Create and draw the network
G = parse_sndlib_network(network_data)
draw_network(G)