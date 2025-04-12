import os
import matplotlib.pyplot as plt

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
    

  clear_screen()
  
  print("\n-------------- Escolha do nó algoritmo a utilizar ---------------")
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