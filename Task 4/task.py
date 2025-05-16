from functions import *
from menus import *
from draw import *
from calculos import *

"""!
@file task.py
@mainpage Projeto de Algoritmos em Grafos: TSA e Suurballe

@section intro_sec Introdução
Este programa implementa e compara dois algoritmos para encontrar pares de caminhos
disjuntos em grafos de rede: o Two-Step Approach (TSA) e o algoritmo de Suurballe.
Permite ao utilizador carregar redes, selecionar nós de origem e destino, executar
os algoritmos e visualizar os resultados. Adicionalmente, oferece funcionalidades
para realizar cálculos estatísticos comparativos entre os algoritmos.

@section dependencies Dependências
- Python 3.x
- NetworkX: Para manipulação de grafos.
- Matplotlib: Para visualização de grafos.
- Módulos locais:
    - functions.py: Contém as implementações dos algoritmos (retrieve_data, find_best_paths, suurballe, etc.).
    - menus.py: Funções para interação com o utilizador através de menus (ask_network, ask_origin_destiny, etc.).
    - draw.py: Funções para desenhar os grafos e caminhos (draw_network, draw_empty_network, draw_suurballe).
    - calculos.py: Funções para realizar cálculos estatísticos (calculo_taxa_resolusao, etc.).

@section execution Como Executar
1. Certifique-se de que todas as dependências estão instaladas.
2. Coloque os ficheiros de rede (formato .txt esperado) no diretório 'networks/'.
3. Execute o script `task.py` a partir da linha de comandos: `python task.py`
4. Siga as instruções apresentadas nos menus.

@note O programa cria um diretório 'output/' para guardar as imagens geradas dos grafos.
"""

def main():

    """!
    @brief Função principal que executa o ciclo do menu da aplicação.

    Apresenta um menu principal com opções para determinar caminhos, realizar
    cálculos estatísticos ou sair do programa.
    """

    while True:

        clear_screen()  
        print(" \n-------------- Opções disponíveis ----------------\n")
        print(" 1. Determinar Caminhos")
        print(" 2. Cálculos Estatísticos")
        print(" 3. Sair")
        print("--------------------------------------------------")

        escolha = int(input("Digite a opção pretendida: "))

        if escolha==1:
            G, node_mapping = show_ask_network()
            
            if G is None and node_mapping is None:
                continue

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
            clear_screen()

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
                caminho1, custo1, caminho2, custo2 = find_best_paths(G, origem, destino, algoritmo=algoritmo)

                """!
                @brief Desenha o grafo com os caminhos encontrados.
                @param G Grafo da rede.
                @param node_mapping Mapa dos nós.
                @param origem Nó de origem.
                @param destino Nó de destino.
                @param caminho1 Caminho mais curto.
                @param caminho2 Caminho Two Step Approach.
                @param caminho3 Caminho Suurballe.
                """
                # desenhar o grafo
                draw_network(G, node_mapping, origem, destino, caminho1, caminho2, caminho_sur=None, caminho3 = None, algoritmo=algoritmo)

            if algoritmo == 2:

                option = ask_skip_forward()
                caminho_sur, _, caminho3, _ = suurballe(G, origem, destino, algoritmo=algoritmo, option=option, calculo=False)
                draw_network(G, node_mapping, origem, destino, None, None, caminho_sur, caminho3, algoritmo=algoritmo)            
            if algoritmo == 3:

                option = 0
                caminho_tsa, custo1, caminho2, custo2 = find_best_paths(G, origem, destino, algoritmo=algoritmo)
                caminho_sur, _, caminho3, _ = suurballe(G, origem, destino, algoritmo=algoritmo, option=option, calculo=False)
                draw_network(G, node_mapping, origem, destino, caminho_tsa, caminho2, caminho_sur, caminho3, algoritmo=algoritmo)


        elif escolha == 2:
            G, node_mapping = show_ask_network()
            if G is None and node_mapping is None:
                continue
            escolha = ask_which_calculus()

            if escolha == 1: 
                calculo_taxa_resolusao(G)
            if escolha == 2:
                calculo_taxa_resolusao_otima(G)
            if escolha == 3:
                calculo_erro(G)
        elif escolha == 3:
            clear_screen()
            print("Obrigad@! Volte Sempre!")
            break

        else:
            clear_screen()
            print("Número inválido. Por favor, escolha um número da lista.")


if __name__ == "__main__":
    # Cria o diretório 'output' se não existir
    if not os.path.exists("output"):
        os.makedirs("output")
    main()