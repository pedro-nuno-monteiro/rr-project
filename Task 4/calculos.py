import itertools
from functions import *
from menus import *


def calculos_auxiliares(G, otimo, calcular_erro_medio):
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
    
    pares, pares_validos, _, _, _, erro_medio = calculos_auxiliares(G, otimo=False, calcular_erro_medio=True)
    clear_screen()
    
    print("\n\n----------------- Erro Médio do TSA -----------------\n")
    print(f"Total de pares analisados: {len(pares)}")
    print(f"Pares onde ambos TSA e Suurballe encontraram soluções: {pares_validos}")
    print(f"Erro médio do TSA em relação à solução ótima: {erro_medio:.2f}%")
    print("\n------------------------------------------------------")
    
    input("Enter para continuar")