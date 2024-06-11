import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import time


def build_graph(g):

    begin = []
    end = []
    for i in range(len(g)):
        for j in range(len(g[0])):
            if g[i][j] == 1:
                begin.append(i)
                end.append(j)
    df = pd.DataFrame({'from': begin, 'to': end})

    G = nx.from_pandas_edgelist(df, 'from', 'to')

    nx.draw(G, with_labels=True, node_size=80, font_size=5, node_color="skyblue",
            pos=nx.spring_layout(G), edge_color="grey")


def read_net(inputpath):

    try:
        f = pd.read_csv(inputpath, sep=':', header=None,
                        names=["Node1", "Node2"], skiprows=1)
        n = pd.read_csv(inputpath, sep=':', names=["Node1", "Node2"], nrows=1)
    except Exception as e:
        print("打开文件失败: " + e)

    n = int(n['Node1'])
    e = 0

    degree = [0 for i in range(n)]
    nodes = [[0 for i in range(n)] for j in range(n)]
    similarity = [[0 for i in range(n)] for j in range(n)]
    neighbors = [[] for i in range(n)]
    for i, j in zip(list(f['Node1']), list(f['Node2'])):
        e += 1
        nodes[i-1][j-1] = 1
        nodes[j-1][i-1] = 1
        degree[i-1] += 1
        degree[j-1] += 1
        if j-1 not in neighbors[i-1]:
            neighbors[i-1].append(j-1)
        if i-1 not in neighbors[j-1]:
            neighbors[j-1].append(i-1)
    # print(nodes)

    for i in range(n):
        for j in range(n):
            if i != j:
                for node in list(set(neighbors[i]) & set(neighbors[j])):
                    similarity[i][j] += 1 / degree[node]

    return n, e, nodes, similarity, degree


def read_synnet(inputpath):

    try:
        f = pd.read_csv(inputpath, sep=':', header=None,
                        names=["Node1", "Node2"], skiprows=1)
        n = pd.read_csv(inputpath, sep=':', names=["Node1", "Node2"], nrows=1)
    except Exception as e:
        print("打开文件失败: " + e)

    n = int(n['Node1'])
    e = 0

    degree = [0 for i in range(n)]
    nodes = [[0 for i in range(n)] for j in range(n)]
    similarity = [[0 for i in range(n)] for j in range(n)]
    neighbors = [[] for i in range(n)]
    for i, j in zip(list(f['Node1']), list(f['Node2'])):
        e += 1
        nodes[i-1][j-1] = 1
        degree[i-1] += 1
        if j-1 not in neighbors[i-1]:
            neighbors[i-1].append(j-1)
    # print(nodes)

    for i in range(n):
        for j in range(n):
            if i != j:
                for node in list(set(neighbors[i]) & set(neighbors[j])):
                    similarity[i][j] += 1 / degree[node]

    return n, e, nodes, similarity, degree


def sigmoid(x):

    return 1.0 / (1+np.exp(-x))


def softmax(x):

    return np.exp(x) / np.sum(np.exp(x))


def argmax(x):

    return np.argmax(x, axis=0)


# 叠加多层的做法
def GNN(w, N, adjM, simM):

    M1 = [[] for i in range(N)]
    hchange = [[] for i in range(N)]
    Prob = [[] for i in range(N)]
    M2 = [[0 for j in range(N)] for i in range(N)]

    M1 = w * simM
    # Prob = np.array(simM)

    for i in range(N):
        count = 0
        for tmp in adjM[i]:
            if tmp > 0:
                count += 1

        # M1[i] = np.array(simM[i])
        # M1[i] = w * simM[i]
        # print(simM[1])
        # print(M1[1])
        # time.sleep(99)
        hchange[i] = sigmoid(M1[i])
        Prob[i] = softmax(hchange[i])
        Prob[i][i] = 0

        # # 将经过sigoid和softmax的结果进行排序，按原有连接数量的比例进行筛选
        index = np.argsort(Prob[i])

        for j in range(N):
            if j < (N-count):
                M2[i][index[j]] = 0
            else:
                M2[i][index[j]] = 1

    return M2

# 叠加多层的做法
def GNN2(w, N, adjM, simM):

    M1 = [[] for i in range(N)]
    hchange = [[] for i in range(N)]
    Prob = [[] for i in range(N)]
    M2 = [[0 for j in range(N)] for i in range(N)]
    s = []

    # AdjM = [[0 for i in range(N)] for j in range(N)]
    # for i in range(N):
    #     for j in range(N):
    #         if adjM[i*N+j] == 1:
    #             AdjM[i][j] = 1

    M1 = w * adjM

    for i in range(N):
        hchange[i] = sigmoid(M1[i])
        Prob[i] = softmax(hchange[i])
        index = np.argsort(Prob[i])
        
        if N <= 1000:
            s.append(index[-1])
            s.append(index[-2])
        elif N > 1000 and N <= 2000:
            s.append(index[-1])
            s.append(index[-2])
            s.append(index[-3])
        else:
            s.append(index[-1])
            s.append(index[-2])
            s.append(index[-3])
            s.append(index[-4])

    return s
