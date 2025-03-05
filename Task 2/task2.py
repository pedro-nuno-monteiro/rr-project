from functions import retrieve_data, draw_network, ask_origin_destiny
import os


networks = ["abilene.txt", "atlanta.txt", "nobel-eu.txt", "nobel-germany.txt"]

while True: 
    os.system('cls')
    print(" \n-------------- Redes disponíveis: ---------------")
    for i, ficheiro in enumerate(networks, 1):
        print(f"{i}. {ficheiro}")
    print("5. Inserir outra rede")
    print("6. Sair")
    print("----------------------------------------------------")
    
    escolha = int(input("Digite o número da rede que deseja analisar: ")) - 1
    
    if 0 <= escolha < len(networks):
        with open(networks[escolha], 'r') as file:
            network_data = file.read()
            G, node_mapping = retrieve_data(network_data)
            origem, destino = ask_origin_destiny(node_mapping)
            draw_network(G, node_mapping, origem, destino)
        
    elif escolha == 4:
        novo_ficheiro = input("Digite o nome da rede (com extensão .txt): ")
        if novo_ficheiro.endswith('.txt'):
            try:
                with open(novo_ficheiro, 'r') as file:
                    network_data = file.read()
                    G, node_mapping = retrieve_data(network_data)
                    origem, destino = ask_origin_destiny(node_mapping)
                    draw_network(G, node_mapping, origem, destino)
            except FileNotFoundError:
                os.system('cls')
                print(f"Arquivo '{novo_ficheiro}' não encontrado. Tente novamente.")
        else:
            os.system('cls')
            print("O nome do arquivo deve terminar com '.txt'. Tente novamente.")
            
    elif escolha == 5:
        os.system('cls')
        print("Obrigada! Volte Sempre!");
        break

    else:
        os.system('cls')
        print("Número inválido. Por favor, escolha um número da lista.")
        
