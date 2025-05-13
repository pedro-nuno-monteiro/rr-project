import os
import matplotlib.pyplot as plt
from functions import *

networks = ["networks/abilene.txt", "networks/atlanta.txt", "networks/nobel-eu.txt", "networks/nobel-germany.txt"]

def show_ask_network():
    clear_screen()
    print(" ----------- Redes disponíveis ---------------\n")
    
    for i, ficheiro in enumerate(networks, 1):
        display_name = ficheiro.replace('networks/', '')
        print(f"  {i}. {display_name}")
        
    print("\n  5. Inserir outra rede")
    print(" ---------------------------------------------\n")
    escolha = int(input("Selecione a rede pretendida: ")) - 1
    
    if escolha == 4:
            novo_ficheiro = ask_network()
            if novo_ficheiro != "":
                networks.append(novo_ficheiro)
                escolha = len(networks) - 1
                
    with open(networks[escolha], 'r') as file:
        """!
        @brief Leitura dos dados do ficheiro escolhido.
        """
        # leitura da info do ficheiro escolhido
        network_data = file.read()

        """!
        @brief Criação do grafo e mapeamento dos nós.
        @param network_data Dados da rede do ficheiro.
        @return G Grafo criado.
        @return node_mapping Mapa dos nós.
        """
        # criação do grafo e mapeamento dos nós
        G, node_mapping = retrieve_data(network_data)
        
        return G, node_mapping
    
# ------------------------------------------------------
def ask_network():
    """!
    @brief Solicita ao user o nome do ficheiro da rede.
    
    Esta função solicita ao user o nome do ficheiro da rede que deseja adicionar.
    
    @return caminho_ficheiro Caminho do ficheiro da rede.
    """
    
    novo_ficheiro = input("Digite o nome da rede (com extensão .txt): ")
    caminho_ficheiro = f"networks/{novo_ficheiro}"
    if caminho_ficheiro.endswith('.txt'):
        return caminho_ficheiro
    else:
        clear_screen()
        print("O nome do arquivo deve terminar com '.txt'. Tente novamente.")
        
    if FileNotFoundError: 
        print(f"Arquivo '{novo_ficheiro}' não encontrado. O ficheiro tem de estar na pasta networks. Tente novamente.")

# ------------------------------------------------------
def ask_origin_destiny(node_mapping):
    
    """!
    @brief Solicita ao user os nós de origem e destino.

    Esta função solicita ao user os números correspondentes aos nós de origem e de 
    destino.

    @param node_mapping Mapa de nós.

    @return Tuple (origem, destino) onde:
        @param origem: O número do nó de origem selecionado.
        @param destino: O número do nó de destino selecionado.
    """
    
    clear_screen()
    
    print("\n-------------- Escolha do nó de origem e destino ---------------")
    for num, nome in node_mapping.items():
        print(f"{num}: {nome}")
        
    print("")
    print("NOTA: Será aberto um gráfico com a rede, onde poderá ver os nós.")
    print("      Este gráfico irá fechar-se automaticamente após a escolha dos nós.")
    print("---------------------------------------------------------------")
    while True:
        try:
            origem = int(input("\nDigite o número do nó de origem: "))
            destino = int(input("Digite o número do nó de destino: "))
            
            if origem == destino:
                print("\nO nó de origem e o nó de destino não podem ser iguais. Tente novamente.")
                continue
            
            if origem in node_mapping and destino in node_mapping:
                break
            else:
                print("\nNúmero inválido. Por favor, escolha um número da lista.")
        except ValueError:
            print("\nNúmero inválido. Por favor, escolha um número da lista.")  
    
    plt.close()

    return node_mapping[origem], node_mapping[destino]

# ------------------------------------------------------
def clear_screen():
    """!
    @brief Limpa a tela do terminal.
    """

    os.system('cls' if os.name == 'nt' else 'clear')

# ------------------------------------------------------
def ask_which_algorithm():

    """!
    @brief Exibe um menu para o usuário escolher um algoritmo a ser utilizado.

    Esta função exibe um menu interativo que permite ao usuário escolher entre três opções de algoritmos: "Two Step Approach", "Suurballe" ou uma opção ainda não implementada para usar ambos os métodos. A função valida a entrada do usuário para garantir que a escolha seja uma opção válida.

    @return A opção escolhida pelo usuário como um número inteiro:
            1 para "Two Step Approach",
            2 para "Suurballe",
            3 para "Usar ambos os métodos".
    
    @note A opção 3 ainda não está implementada.
    """
    
    clear_screen()
    
    print("\n-------------- Escolha do nó algoritmo a utilizar ---------------\n")
    print(" 1. Two Step Approach")
    print(" 2. Suurballe")
    print(" 3. Usar ambos os métodos")
    print(" ---------------------------------------------------------------")

    while True:
        try:
            option = int(input("\nDigite a opção pretendida: "))
            
            if option in [1, 2, 3]:
                break
            else:
                print("\nNúmero inválido. Por favor, escolha um número da lista.")
        except ValueError:
            print("\nNúmero inválido. Por favor, escolha um número da lista.")  

    return option

# ------------------------------------------------------
def ask_skip_forward():
    """!
    @brief Pergunta ao usuário se deseja passar todos os passos à frente.

    Esta função exibe uma mensagem a perguntar se o user deseja passar à frente todos os passos.

    @return True se o usuário escolher 's', False se o usuário escolher 'n'.
    """

    clear_screen()

    print("\n-------------- Escolha de visualização ---------------\n")
    print(" O programa irá apresentar todos os passos do algoritmo")
    print(" mostrando, para cada, o grafo correspondente.\n")
    print(" Escolha se deseja\n  - passar todos os passos à frente (1)\n  - ver grafos passo a passo (0)")
    print(" -------------------------------------------------------")

    while True:
        option = int(input("\nDigite a opção pretendida: "))
        
        if option == 1:
            clear_screen()
            print("\n-------------- Visualização final ---------------\n")
            print(" É apresentado o grafo final")
            print(" e guardado no ficheiro 'output/Rede Final.png'")
            return True
        elif option == 0:
            clear_screen()
            return False
        else:
            print("Opção inválida. Por favor, digite 1 ou 0.")
            
# ------------------------------------------------------
def ask_which_calculus():
    clear_screen()
    print("\n-------------- Escolha do cálculo a realizar ---------------\n")
    print(" 1. Calcular taxa de resolução")
    print(" 2. Calcular taxa de resolução ótima")
    print(" 3. Calcular erro médio do custo")
    
    print(" -------------------------------------------------------------")
    
    while True:
        try:
            escolha = int(input("\nDigite a opção pretendida: "))
            if escolha in [1, 2, 3]:
                break
            else:
                print("\nNúmero inválido. Por favor, escolha um número da lista.")
        except ValueError:
            print("\nNúmero inválido. Por favor, escolha um número da lista.")
    
    return escolha  

# ------------------------------------------------------