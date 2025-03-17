import os, sys

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
    
    return origem, destino

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

  while True:
    try:
      option = int(input("\nDigite a opção pretendida: "))
        
      if option in [1, 2]:
        break
      else:
        print("\nNúmero inválido. Por favor, escolha um número da lista.")
    except ValueError:
      print("\nNúmero inválido. Por favor, escolha um número da lista.")  

  return option