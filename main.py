import time
import argparse
from parameter import *
from clique_info import CliqueInfo
from clique_network import CliqueNet
from maxcliques import BuildClique
from population import Population
from evaluation import Evaluation
import numpy as np
from build_netInfo import build_netInfo
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from evaluate import *
from read_network import NetworkOrig
from evalcomms import *


def build_graph(g, N):
    begin = []
    end = []
    for i in range(N):
        for j in range(N):
            if g[i * N + j] == 1:
                begin.append(i)
                end.append(j)
    df = pd.DataFrame({'from': begin, 'to': end})

    G = nx.from_pandas_edgelist(df, 'from', 'to')

    nx.draw(G, with_labels=True, node_size=80, font_size=5, node_color="skyblue",
            pos=nx.spring_layout(G), edge_color="grey")


def run(op2, runTime, dimension, walk):

    op1 = "r"

    inputpath = ""
    inputcommunity = ""
    inputemb = ""
    output_MOD = ""
    outputgNMI = ""
    output_path = ""

    inputpath += "../data/large_network/ca-Gr.txt"
    inputemb += "../data/emb/Gr_"+str(dimension)+"_"+str(walk)+".emb"
    outputgNMI += "result/large_network/ca-Gr/fNMI"
    output_MOD += "result/large_network/ca-Gr/Modolarity"

    netOrig = NetworkOrig()

    if op1 == 'r':
        netOrig.read_pajek_unweighted_social(inputpath)
    elif op1 == 'g':
        netOrig.read_pajek_unweighted(inputpath)

    varDim = netOrig.net_orig["n"]
    seed = np.random.rand(varDim, varDim)
    output_path = ""

    emb = np.loadtxt(inputemb, skiprows=1, dtype=np.float32)
    n = pd.read_csv(inputemb, sep=' ', names=["Node1", "Node2"], nrows=1)
    if np.isnan(emb).any():
        print('ERROR! Emb file ERROR')
        quit()
    emb = emb[emb[:, 0].argsort(), :]
    sorted_col = emb[:, 0]

    for i in range(1, varDim+1):
        if not np.isin(i, sorted_col):
            new_array = np.zeros((1, int(n["Node2"]) + 1), dtype=np.float32)
            emb = np.insert(emb, i - 1, new_array, axis=0)
    emb = emb[:, 1:]
    p = 3  # 闵可夫斯基距离中的幂
    dist = np.power(np.sum(np.power(np.abs(emb[:, None, :] - emb), p), axis=2), 1/p)

    start = time.perf_counter()

    nodes = GNN2(seed, varDim, dist, netOrig.similarity)
    nodes = list(set(nodes))
    remain = open(op2 + "_remain.txt", 'a+', encoding="utf-8")
    remain.write("%d\n" % len(nodes))

    nds = {}
    for n in nodes:
        nds[n] = netOrig.net_orig["degree"][n]
    nds = sorted(nds.items(), key=lambda x: x[1])

    nodes = []
    degrees = []
    for tmp in nds:
        nodes.append(list(tmp)[0])
        degrees.append(list(tmp)[1])

    buildClique = BuildClique(netOrig, nodes, degrees)
    buildClique.maxclique(output_path)

    cliqueInfo = CliqueInfo(netOrig, buildClique)
    print("building clique network")
    cliqueInfo.construct_clique_network()
    # cliqueInfo.output_clique_network(output_path)

    cliqueNet = CliqueNet(cliqueInfo)
    cliqueNet.parameter_of_clique_network(varDim)

    print("\ninitalizing population\n")
    population = Population(cliqueNet, cliqueInfo)
    evaluation = Evaluation(cliqueInfo, netOrig, population)
    population.init_population()

    for i in range(1, generation + 1):
        print("---------------" "%3d/%-3d""---------------" % (i, generation))
        population.evolve_population()

        # 记录每一次迭代后的f函数
        fv = open("result/fvalue/"+op2+str(i)+".txt", 'a+', encoding="utf-8")
        for psize in range(popsize):
            fv.write("%f %f\n" % (population.pop[psize]["ind"]["obj"][0], population.pop[psize]["ind"]["obj"][1]))
        fv.close()

    end = time.perf_counter()
    t = open(op2 + "_time.txt", 'a+', encoding="utf-8")
    t.write("%s\n" % (end - start))
    print((end - start), 's')

    # 构造生成的community
    evalcomm = get_evalcomm3(population, netOrig)
    print(evalcomm)
    time.sleep(999)

    # population.dump_population(output_path, j)

    evaluation.uoModularity(population.pop, 0, output_MOD, evalcomm, runTime, dimension, walk)

    # real network不需要经过这一步
    if op1 == 'g':
        evaluation.gNMI(population.pop, inputcommunity, 0, outputgNMI, evalcomm, runTime)


if __name__ == '__main__':
    # datasets = ["dolphins", "fb3437", "football", "jazz", "karate", "netsci", "polblogs", "polbooks", "yeast"]
    # datasets = ["dolphins", "football", "karate", "polblogs", "polbooks", "yeast"]
    datasets = ["football"]
    # datasets = ["LFR-1", "LFR-2", "LFR-3", "LFR-4", "LFR-5", "LFR-6", "LFR-7", "LFR-8"]
    # datasets = ["LFR-1", "LFR-2", "LFR-3", "LFR-4", "LFR-5", "LFR-6", "LFR-7", "LFR-8", "LFR-9", "LFR-10", "LFR-11",
    #             "LFR-12", "LFR-13", "LFR-14", "LFR-15", "LFR-16", "LFR-17", "LFR-18", "LFR-19", "LFR-20", "LFR-21",
    #             "LFR-22", "LFR-23", "LFR-24", "LFR-25", "LFR-26"]
    # datasets = ["ca-Ast", "ca-Con", "ca-Gr", "ca-HepP", "ca-HepT", "loc-bri", "loc-gow"]

    for data in datasets:
        for dimension in [8, 16, 32, 64, 128]:
            for walk in [10, 20, 80]:
                for runTime in range(5):
                    run(data, runTime, dimension, walk)
    # run()

'''
    real network:
        input_network: /root/MCMOEA/example/data/social_network.dat
        input_community:
        output_community: /root/MCMOEA/example/result/social_network/social_network
        output_clique: /root/MCMOEA/example/result/social_network/social_network
        output_index:
        output_T: /root/MCMOEA/example/result/social_network/social_network_esclipe_t.dat
        reading network : /root/MCMOEA/example/data/social_network.dat

    generate network:
        input_network: /root/MCMOEA/example/data/network.dat
        input_community: /root/MCMOEA/example/data/community.dat
        output_community: synthetic_network
        output_clique: synthetic_network
        output_index: gNMI
        output_T: synthetic_network_esclipe_t.dat
        reading network : /root/MCMOEA/example/data/network.dat
    '''
