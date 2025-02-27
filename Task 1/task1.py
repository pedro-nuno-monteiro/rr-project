from functions import retrieve_data, draw_network
import os


"""
    @brief Displays a menu for the user to select a network file to analyze.

    This function displays a list of available networks and provides the user
    with options to select one for analysis, add a new network, or exit the program.
    It handles the selection, loading of the network data, and visualization of the network.
    
    @param escolha The index of the network selected by the user
    @param novo_ficheiro The name of the new network file entered by the user
"""

networks = ["abilene.txt", "atlanta.txt", "nobel-eu.txt", "nobel-germany.txt"]
os.system('cls')

while True: 
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
            G = retrieve_data(network_data)
            draw_network(G)
        
    elif escolha == 4:
        novo_ficheiro = input("Digite o nome da rede (com extensão .txt): ")
        if novo_ficheiro.endswith('.txt'):
            try:
                with open(novo_ficheiro, 'r') as file:
                    network_data = file.read()
                    G = retrieve_data(network_data)
                    draw_network(G)
            except FileNotFoundError:
                os.system('cls')
                print(f"Arquivo '{novo_ficheiro}' não encontrado. Tente novamente.")
        else:
            os.system('cls')
            print("O nome do arquivo deve terminar com '.txt'. Tente novamente.")
            
    elif escolha == 5:
        print("Obrigada! Volte Sempre!");
        break

    else:
        os.system('cls')
        print("Número inválido. Por favor, escolha um número da lista.")
