from functions import *
from menus import *
from draw import *

"""!
@file task3.py
@mainpage Two Step Approach
@brief Programa para exibir gráficos de rede, implementando o Two Step Approach, para encontrar um par de caminhos disjuntos.

@section dependencies Dependências
- functions.py (retrieve_data, draw_network, ask_origin_destiny, find_best_paths, clear_screen, draw_empty_network)
- networkx
- matplotlib
- os
"""

networks = ["networks/abilene.txt", "networks/atlanta.txt", "networks/nobel-eu.txt", "networks/nobel-germany.txt"]

while True:

    """!
    @brief Função principal do programa.
    @details Exibe o menu e mostra a opção escolhida pelo user.
    """

    clear_screen()  
    print(" \n-------------- Opções disponíveis: ---------------\n")
    print(" Redes disponíveis:")
    for i, ficheiro in enumerate(networks, 1):
        display_name = ficheiro.replace('networks/', '')
        print(f"  {i}. {display_name}")
    print("")
    print(" Outras opções:")
    print("  5. Inserir outra rede")
    print("  6. Sair")
    print("--------------------------------------------------")
    
    escolha = int(input("Digite a opção pretendida: ")) - 1
    
    if 0 <= escolha < len(networks) or escolha == 4:
        
        if escolha == 4:
            novo_ficheiro = ask_network()
            if novo_ficheiro == "":
                continue
            else:
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

            """!
            @brief Exibe a rede antes de solicitar os nós de origem e destino.
            @param G Grafo da rede.
            @param node_mapping Mapa dos nós.
            """
            # Mostrar a rede antes de pedir os nós, para o user poder escolher
            draw_empty_network(G, node_mapping)

            """!
            @brief Solicita os nós de origem e destino ao user.
            @param node_mapping Mapa dos nós.
            @return origem Nó de origem escolhido pelo user.
            @return destino Nó de destino escolhido pelo user.
            """
            # pedir nó origem e nó destino
            origem, destino = ask_origin_destiny(node_mapping)

            algoritmo = ask_which_algorithm()

            if algoritmo == 1:

                """!
                @brief Encontra os caminhos mais curtos entre os nós escolhidos.
                @param G Grafo da rede.
                @param origem Nó de origem.
                @param destino Nó de destino.
                @return caminho1 Primeiro caminho encontrado.
                @return custo1 Custo do primeiro caminho.
                @return caminho2 Segundo caminho encontrado.
                @return custo2 Custo do segundo caminho.
                """
                # encontrar os caminhos mais curtos
                caminho1, custo1, caminho2, custo2 = find_best_paths(G, origem, destino)

                """!
                @brief Desenha o grafo com os caminhos encontrados.
                @param G Grafo da rede.
                @param node_mapping Mapa dos nós.
                @param origem Nó de origem.
                @param destino Nó de destino.
                @param caminho1 Caminho mais curto.
                @param caminho2 Caminho Two Step Approach.
                @param caminho3 Caminho Suurbale.
                """
                # desenhar o grafo
                draw_network(G, node_mapping, origem, destino, caminho1, caminho2, algoritmo=algoritmo)

            if algoritmo == 2:

                caminho1, caminho2 = suurballe(G, origem, destino)
            
            if algoritmo == 3:
                #caminho1, custo1, caminho2, custo2 = find_best_paths(G, node_mapping[origem], node_mapping[destino])
                #caminho1, caminho3 = suurbale(G, node_mapping[origem], node_mapping[destino])
                #if caminho3 == None:
                #    print("Não foi possível encontrar caminho disjunto.")
                #    draw_network(G, node_mapping, origem, destino, caminho1, caminho2, caminho3=None, algoritmo=algoritmo)
                #else:
                #    draw_network(G, node_mapping, origem, destino, caminho1, caminho2, caminho3=caminho3, algoritmo=algoritmo)
                print("\nDesculpe, ainda não está implementado.")
                input("Pressione Enter para continuar...")
    
    elif escolha == 5:
        clear_screen()
        print("Obrigada! Volte Sempre!")
        break

    else:
        clear_screen()
        print("Número inválido. Por favor, escolha um número da lista.")
        
