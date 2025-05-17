import itertools
from functions import *
from menus import *

"""!
@file calculos.py
@brief Módulo para cálculos estatísticos relacionados com a resolução de caminhos em grafos.
Este módulo contém funções para calcular taxas de resolução, taxas de resolução ótima e erro médio entre algoritmos de caminhos disjuntos como TSA e Suurballe.
"""

def calculos_auxiliares(G, otimo, calcular_erro_medio):
    """!
    @brief Realiza cálculos auxiliares para comparar os algoritmos TSA e Suurballe.

    Itera sobre todos os pares de nós únicos no grafo, executa ambos os algoritmos
    (TSA e Suurballe) para cada par e recolhe estatísticas como o número de
    soluções encontradas por cada um, soluções ótimas (se aplicável) e o erro
    percentual do TSA em relação ao Suurballe.

    @param G O grafo (NetworkX DiGraph) sobre o qual os cálculos são realizados.
    @param otimo Booleano. Se True, verifica se o custo do TSA é igual ao do Suurballe
                 (considerado como ótimo) e conta essas ocorrências.
    @param calcular_erro_medio Booleano. Se True, calcula o erro percentual médio
                               do custo total do TSA em relação ao custo total do Suurballe.

    @return Tuple contendo:
        - pares (list): Lista de todos os pares de nós (origem, destino) no grafo.
        - pares_validos (int): Número de pares para os quais tanto o TSA como o Suurballe
                               encontraram uma solução (ambos os caminhos).
        - resolvidos_tsa (int): Número total de pares para os quais o TSA encontrou
                                 ambos os caminhos.
        - resolvidos_sur (int): Número total de pares para os quais o Suurballe encontrou
                                ambos os caminhos.
        - resolvidos_otimos (int): Se 'otimo' for True, o número de pares válidos onde
                                   o custo do TSA foi igual ao custo do Suurballe.
                                   Caso contrário, este valor não é significativo.
        - erro_medio (float): Se 'calcular_erro_medio' for True, o erro percentual
                              médio do TSA em relação ao Suurballe para os 'pares_validos'.
                              Caso contrário, é 0.0.
    """

    pares = list(itertools.combinations(G.nodes, 2))
    resolvidos_tsa = 0
    resolvidos_sur = 0
    resolvidos_otimos = 0
    erro_acumulado = 0.0  # Acumula as diferenças percentuais
    pares_validos = 0     # Conta pares onde ambos TSA e Suurballe funcionaram

    for origem, destino in pares:
        # Executa TSA
        _, cost_1_tsa, path2, cost_2_tsa = find_best_paths(G, origem, destino, algoritmo=None)
        # Executa Suurballe
        _, cost_1_sur, P2, cost_2_sur = suurballe(G, origem, destino, algoritmo=None, option=0, calculo=True)
        
        # Verifica se ambos encontraram soluções
        tsa_valido = (path2 is not None) and (cost_2_tsa is not None)
        sur_valido = (P2 is not None) and (cost_2_sur is not None)
        
        if tsa_valido:
            resolvidos_tsa += 1
        if sur_valido:
            resolvidos_sur += 1
        
        # Se ambos algoritmos encontraram soluções, compara custos
        if tsa_valido and sur_valido:
            custo_tsa = cost_1_tsa + cost_2_tsa
            custo_sur = cost_1_sur + cost_2_sur
            
            if calcular_erro_medio:
                erro_percentual = ((custo_tsa - custo_sur) / custo_sur) * 100
                erro_acumulado += erro_percentual
                pares_validos += 1
            
            if otimo and (custo_tsa == custo_sur):
                resolvidos_otimos += 1
    
    # Calcula o erro médio se solicitado
    erro_medio = (erro_acumulado / pares_validos) if pares_validos > 0 else 0.0
    
    return pares, pares_validos , resolvidos_tsa, resolvidos_sur, resolvidos_otimos, erro_medio

# ------------------------------------------------------
def calculo_taxa_resolusao(G):
    """!
    @brief Calcula e exibe a taxa de resolução dos algoritmos TSA e Suurballe.

    Utiliza a função `calculos_auxiliares` para obter o número total de pares de nós
    e o número de pares resolvidos por cada algoritmo. Em seguida, imprime a taxa
    de resolução percentual para cada um.

    @param G O grafo (NetworkX DiGraph) para análise.
    @note Espera que o utilizador pressione Enter para continuar após a exibição.
    """

    
    pares, _,resolvidos_tsa, resolvidos_sur, _, _ = calculos_auxiliares(G, otimo=False, calcular_erro_medio=False)
    
    clear_screen()
    print("\n\n----------------- Taxa de resolução TSA -----------------\n")
    print(f"Total de pares: {len(pares)}")
    print(f"Total de pares resolvidos pelo TSA: {resolvidos_tsa}")
    print(f"Taxa de resolução do TSA: {resolvidos_tsa / len(pares) * 100:.2f}%")
    print("\n----------------- Taxa de resolução Surballe -----------------\n")
    print(f"Total de pares: {len(pares)}")
    print(f"Total de pares resolvidos pelo Suurballe: {resolvidos_sur}")
    print(f"Taxa de resolução do Suurballe: {resolvidos_sur / len(pares) * 100:.2f}%")
    print("\n---------------------------------------------------------------")

    input("Enter para continuar")

# ------------------------------------------------------   
def calculo_taxa_resolusao_otima(G):
    """!
    @brief Calcula e exibe a taxa de resolução ótima do TSA em comparação com o Suurballe.

    Considera uma solução do TSA como ótima se o seu custo total for igual ao custo
    total da solução do Suurballe para o mesmo par de nós. A taxa é calculada como
    a percentagem de soluções ótimas encontradas pelo TSA em relação ao total de
    soluções encontradas pelo Suurballe (que é considerado o benchmark ótimo).

    @param G O grafo (NetworkX DiGraph) para análise.
    @note Utiliza `calculos_auxiliares`. Espera que o utilizador pressione Enter para continuar.
    """


    pares, _, _, resolvidos_sur, resolvidos_otimos, _ = calculos_auxiliares(G, otimo=True, calcular_erro_medio=False)
    
    clear_screen()
    
    print("\n\n----------------- Taxa de resolução ótima -----------------\n")
    print(f"Total de pares: {len(pares)}")
    print(f"Total de soluções ótimas: {resolvidos_sur}")
    print(f"Total de soluções ótimas encontradas pelo TSA: {resolvidos_otimos}")
    print(f"Taxa de resolução ótima: {resolvidos_otimos / resolvidos_sur * 100:.2f}%")
    print("\n---------------------------------------------------------------")
    input("Enter para continuar")    

# ------------------------------------------------------    
def calculo_erro(G):
    """!
    @brief Calcula e exibe o erro médio percentual do custo do TSA em relação ao Suurballe.

    O erro é calculado para pares de nós onde ambos os algoritmos encontraram uma solução.
    O erro percentual para um par é ((custo_TSA - custo_Suurballe) / custo_Suurballe) * 100.
    A função exibe o erro médio acumulado sobre todos esses pares válidos.

    @param G O grafo (NetworkX DiGraph) para análise.
    @note Utiliza `calculos_auxiliares`. Espera que o utilizador pressione Enter para continuar.
    """

    
    pares, pares_validos, _, _, _, erro_medio = calculos_auxiliares(G, otimo=False, calcular_erro_medio=True)
    clear_screen()
    
    print("\n\n----------------- Erro Médio do TSA -----------------\n")
    print(f"Total de pares analisados: {len(pares)}")
    print(f"Pares onde ambos TSA e Suurballe encontraram soluções: {pares_validos}")
    print(f"Erro médio do TSA em relação à solução ótima: {erro_medio:.2f}%")
    print("\n------------------------------------------------------")
    input("Enter para continuar")