import pandas as pd
import time, math


class NetworkOrig(object):

    def __init__ (self):
        self.net_orig = {}

    def orig_network_size(self):

        return self.net_orig["n"]

    def orig_network_nEdge(self):

        return self.net_orig["nEdge"]

    def orig_network_degree(self, i):

        return self.net_orig["degree"][i]

    def orig_network_AdjMatrix(self, i, j):

        return self.net_orig["AdjMatrix"][i*self.net_orig["n"]+j]

    def orig_network_Neighbor(self, i):

        return self.net_orig["Neighbor"][i]

    def orig_neighbor(self, i, j):

        if j not in self.net_orig["Neighbor"][i]:
            self.net_orig["Neighbor"][i].append(j)

    def read_pajek_unweighted(self, path):

        en = 0 # 初始化边的数量
        try:
            f = pd.read_csv(path, sep=':', header=None, names=["Node1", "Node2"], skiprows=1)
            n = pd.read_csv(path, sep=':', names=["Node1", "Node2"], nrows=1)
        except Exception as e:
            print("打开文件失败: " + e)

        n = int(n['Node1'])

        if n >= 1:
            print("正在处理网络: %s" % (path))

        # 初始化网络
        self.net_orig["n"] = n
        self.net_orig["AdjMatrix"] = [0 for i in range(n*n)]
        self.net_orig["degree"] = [0 for i in range(n)]
        self.net_orig["Neighbor"] = [[] for i in range(n)]
        self.similarity = [[0 for i in range(n)] for j in range(n)]

        # 将Node1，Node2对应结点记录
        for i, j in zip(list(f['Node1']), list(f['Node2'])):
            if i == j: continue
            en += 1
            self.orig_neighbor(i-1, j-1)
            self.net_orig["AdjMatrix"][(i-1)*n+(j-1)] = 1
            self.net_orig["degree"][i-1] += 1

        self.net_orig["nEdge"] = en

        for tmp in self.net_orig["Neighbor"]:
            tmp.reverse()

        for i in range(n):
            self.net_orig["Neighbor"][i].append(i)

        for i in range(n):
            for j in range(n):
                if i != j:
                    if len(self.net_orig["Neighbor"][i]) == 0 and len(self.net_orig["Neighbor"][j]) == 0:
                        self.similarity[i][j] = 0
                    else:
                        self.similarity[i][j] = (self.net_orig["AdjMatrix"][i*n+j]+len(list(set(self.net_orig["Neighbor"][i]) & set(self.net_orig["Neighbor"][j])))) / ((len(self.net_orig["Neighbor"][i])+len(self.net_orig["Neighbor"][j]))/2)

        for i in range(n):
            self.net_orig["Neighbor"][i].remove(i)

        print("edges: %d\n" % (en))


    def read_pajek_unweighted_social(self, path):

        en = 0 # 初始化边的数量

        try:
            f = pd.read_csv(path, sep=':', header=None, names=["Node1", "Node2"], skiprows=1)
            n = pd.read_csv(path, sep=':', names=["Node1", "Node2"], nrows=1)

        except Exception as e:
            print("打开文件失败: " + e)

        n = int(n['Node1'])

        # 初始化网络
        self.net_orig["n"] = n
        self.net_orig["AdjMatrix"] = [0 for i in range(n*n)]
        self.net_orig["degree"] = [0 for i in range(n)]
        self.net_orig["Neighbor"] = [[] for i in range(n)]
        self.similarity = [[0 for i in range(n)] for j in range(n)]

        # 将Node1，Node2对应结点记录
        for i, j in zip(list(f['Node1']), list(f['Node2'])):
            en += 1
            self.orig_neighbor(i-1, j-1)
            self.orig_neighbor(j-1, i-1)
            self.net_orig["AdjMatrix"][(i-1)*n+(j-1)] = 1
            self.net_orig["AdjMatrix"][(j-1)*n+(i-1)] = 1
            self.net_orig["degree"][i-1] += 1
            self.net_orig["degree"][j-1] += 1

        self.net_orig["nEdge"] = en

        for tmp in self.net_orig["Neighbor"]:
            tmp.reverse()

        for i in range(n):
            self.net_orig["Neighbor"][i].append(i)

        for i in range(n):
            for j in range(n):
                if i != j:
                    if len(self.net_orig["Neighbor"][i]) == 0 and len(self.net_orig["Neighbor"][j]) == 0:
                        self.similarity[i][j] = 0
                    else:
                        self.similarity[i][j] = (self.net_orig["AdjMatrix"][i*n+j]+len(list(set(self.net_orig["Neighbor"][i]) & set(self.net_orig["Neighbor"][j])))) / ((len(self.net_orig["Neighbor"][i])+len(self.net_orig["Neighbor"][j]))/2)

        for i in range(n):
            self.net_orig["Neighbor"][i].remove(i)

        print("edges: %d\n" % (en))


if __name__ == '__main__':
    NetworkOrig().read_pajek_unweighted('data/network.dat')

