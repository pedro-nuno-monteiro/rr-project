from functions import retrieve_data, draw_network, ask_origin_destiny, clear_screen, find_best_paths

networks = ["networks/abilene.txt", "networks/atlanta.txt", "networks/nobel-eu.txt", "networks/nobel-germany.txt"]

while True: 
    clear_screen()
    print(" \n-------------- Redes disponíveis: ---------------")
    for i, ficheiro in enumerate(networks, 1):
        display_name = ficheiro.replace('networks/', '')
        print(f"{i}. {display_name}")
    print("5. Inserir outra rede")
    print("6. Sair")
    print("----------------------------------------------------")
    
    escolha = int(input("Digite o número da rede que deseja analisar: ")) - 1
    
    if 0 <= escolha < len(networks):
        with open(networks[escolha], 'r') as file:

            # leitura da info do ficheiro escolhido
            network_data = file.read()

            # criação do grafo e mapeamento dos nós
            G, node_mapping = retrieve_data(network_data)

            # pedir nó origem e nó destino
            origem, destino = ask_origin_destiny(node_mapping)

            # encontrar os caminhos mais curtos
            caminho1, custo1, caminho2, custo2 = find_best_paths(G, node_mapping[origem], node_mapping[destino])

            # desenhar o grafo
            draw_network(G, node_mapping, origem, destino, caminho1, caminho2)
    
    
    elif escolha == 4:
        novo_ficheiro = input("Digite o nome da rede (com extensão .txt): ")
        if novo_ficheiro.endswith('.txt'):
            try:
                with open(novo_ficheiro, 'r') as file:
                    network_data = file.read()
                    G, node_mapping = retrieve_data(network_data)
                    origem, destino = ask_origin_destiny(node_mapping)
                    caminho1, custo1, caminho2, custo2 = find_best_paths(G, node_mapping[origem], node_mapping[destino])
                    draw_network(G, node_mapping, origem, destino, caminho1, caminho2)
            except FileNotFoundError:
                clear_screen()
                print(f"Arquivo '{novo_ficheiro}' não encontrado. Tente novamente.")
        else:
            clear_screen()
            print("O nome do arquivo deve terminar com '.txt'. Tente novamente.")
            
    elif escolha == 5:
        clear_screen()
        print("Obrigada! Volte Sempre!");
        break

    else:
        clear_screen()
        print("Número inválido. Por favor, escolha um número da lista.")
        
