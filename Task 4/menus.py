import os
import matplotlib.pyplot as plt
from functions import *

"""!
@file menus.py
@brief Módulo para interfaces de menu interativas.
Contém funções para exibir menus, solicitar entradas do utilizador e gerir a interação com o programa.
"""

networks = ["networks/abilene.txt", "networks/atlanta.txt", "networks/nobel-eu.txt", "networks/nobel-germany.txt"]

def show_ask_network():

    """!
    @brief Apresenta um menu para o utilizador selecionar uma rede de uma lista predefinida
           ou inserir o caminho para um novo ficheiro de rede.

    A função limpa o ecrã, exibe as redes disponíveis na lista `networks`.
    O utilizador pode escolher uma rede pelo número ou optar por inserir o nome de um
    novo ficheiro de rede (que deve estar na pasta 'networks/' e ter extensão '.txt').
    Se um novo ficheiro for adicionado com sucesso, ele é acrescentado à lista `networks`
    para a sessão atual.
    Finalmente, lê os dados da rede escolhida, cria o grafo usando `retrieve_data`
    e retorna o grafo e o mapeamento de nós.

    @return Tuple (G, node_mapping):
        - G (nx.DiGraph): O grafo NetworkX criado a partir do ficheiro de rede selecionado.
        - node_mapping (dict): Um dicionário que mapeia índices numéricos (da ordem de leitura)
                               para os nomes dos nós (strings).
    @note Se o ficheiro não for encontrado ou houver erro na leitura/formato,
          a função pode levantar exceções (p.ex., FileNotFoundError, ValueError de retrieve_data).
    """

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
    @brief Solicita ao utilizador o nome do ficheiro da rede.

    Esta função pede ao utilizador para digitar o nome de um ficheiro de rede
    (que se espera ter a extensão '.txt'). Constrói o caminho completo para o
    ficheiro, assumindo que ele reside no diretório 'networks/'.

    @return str: O caminho completo para o ficheiro da rede (p.ex., "networks/nome_ficheiro.txt").
                 Retorna uma string vazia ou pode levantar erro se a entrada for inválida,
                 dependendo da gestão de erros implementada posteriormente.
                 A versão atual retorna o caminho mesmo que o ficheiro não exista ou
                 a extensão seja incorreta, a validação é feita no chamador.
    @note A função valida se o nome do ficheiro termina com '.txt'. Se não, imprime
          uma mensagem de erro e, na implementação atual, o comportamento de retorno
          para nomes inválidos não impede a continuação (o chamador deve validar).
          Também informa sobre FileNotFoundError, mas não o trata diretamente aqui.
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
    @brief Solicita ao utilizador os nós de origem e destino com base num mapeamento fornecido.

    Limpa o ecrã e exibe uma lista numerada de nós disponíveis (baseada no `node_mapping`).
    O utilizador é solicitado a inserir os números correspondentes aos nós de origem e
    destino. A função valida se os números são válidos (existem no mapeamento) e
    se origem e destino são diferentes.
    Um gráfico da rede (presumivelmente aberto por `draw_empty_network` antes desta chamada)
    é mencionado como auxílio visual, e a função fecha qualquer figura Matplotlib aberta
    após a seleção.

    @param node_mapping Dicionário que mapeia um identificador numérico (int) para o
                        nome do nó (str). Ex: `{0: 'NóA', 1: 'NóB', ...}`.
    @return Tuple (origem_nome, destino_nome):
        - origem_nome (str): O nome do nó de origem selecionado.
        - destino_nome (str): O nome do nó de destino selecionado.
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

    Utiliza o comando 'cls' para Windows ('nt') e 'clear' para outros
    sistemas operativos (Linux, macOS).
    """

    os.system('cls' if os.name == 'nt' else 'clear')

# ------------------------------------------------------
def ask_which_algorithm():

    """!
    @brief Exibe um menu para o utilizador escolher um algoritmo ou combinação a ser utilizada.

    Apresenta as opções:
    1. Two-Step Approach
    2. Suurballe
    3. Usar ambos os métodos (para comparação visual lado a lado)
    Valida a entrada do utilizador para garantir que a escolha é uma das opções válidas.

    @return int: A opção escolhida pelo utilizador (1, 2 ou 3).
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
    @brief Pergunta ao utilizador se deseja visualizar todos os passos intermédios de um
           algoritmo (especificamente pensado para o Suurballe) ou apenas o resultado final.

    Apresenta as opções:
    1. Passar todos os passos à frente (visualização final).
    0. Ver grafos passo a passo.
    Valida a entrada do utilizador.

    @return bool: True se o utilizador escolher passar à frente (opção 1),
                  False se escolher ver passo a passo (opção 0).
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

    """!
    @brief Apresenta um menu para o utilizador escolher qual cálculo estatístico realizar.

    As opções são:
    1. Calcular taxa de resolução (percentagem de pares de nós para os quais os
       algoritmos TSA e Suurballe encontram soluções).
    2. Calcular taxa de resolução ótima (percentagem de vezes que o TSA encontra uma
       solução com custo igual ao do Suurballe, considerando Suurballe como ótimo).
    3. Calcular erro médio do custo (erro percentual médio do custo do TSA em
       relação ao Suurballe).
    Valida a entrada do utilizador.

    @return int: A opção escolhida pelo utilizador (1, 2 ou 3).
    """

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