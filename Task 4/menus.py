import os
import matplotlib.pyplot as plt

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
    print(" 2. Suurbale")
    print(" 3. Usar ambos os métodos")

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