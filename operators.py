import random, gc, time
from parameter import *


class Operator():

    def __init__(self, cliqueNet, community, individual):

        self.individual = individual
        self.community = community
        self.cliqueNet = cliqueNet

        self.n = self.cliqueNet.network_size()

    def decode(self, gene):

        cn = 0
        c = [{} for i in range(self.n)]
        ind = {}

        c[cn] = self.community.new_community(gene[0])
        cn += 1

        for i in range(1, self.n):
            c[cn] = self.community.new_community(gene[i])
            # for j in range(cn+1):
            j = 0
            while (j != cn):
                bs = self.community.between(c[j], c[cn])

                # 构造有可能的community
                if self.community.tightness_inc(c[j], c[cn], bs) > 0:
                    c[j], c[cn] = self.community.merge(c[j], c[cn], bs)
                    del(c[cn])
                    break
                j += 1
            if j == cn:
                cn += 1

        ind["comm"] = c
        ind["comm_n"] = cn
        ind["refcount"] = 1
        # gene长度为clique数量
        ind["gene"] = [0 for i in range(self.n)]

        # 相当于将label作为初始的gene，label为由0-1构成的list，表示该community是否包含第i个clique
        ind["gene"] = self.community.community_to_label(c, ind["gene"], cn)
        # evalutate
        ind = self.individual.eval_individual(ind)

        return ind

    def crossover(self, p1, p2):

        gene = []

        if random.random() < 0.5:
            crossover_point = sorted(random.sample(range(len(p1['gene'])), 2))
            gene = p1['gene'][:crossover_point[0]]+p2["gene"][crossover_point[0]:crossover_point[1]]+p1["gene"][crossover_point[1]:]
            return self.individual.new_individual(gene)
        else:
            return p1

    # 轮盘赌算法
    def roulette_neighbor(self, i):

        l = self.cliqueNet.neighbor(i)
        prob = random.random()
        end = self.cliqueNet.link_sum(i) * prob

        for node in l:
            s = self.cliqueNet.weight(i, node)
            if (end <= s):
                return node
            else:
                end -= s

    def mutation(self, ind):

        child = ind.copy()

        if random.random() < pm:
            inx1 = random.randint(0, child["comm_n"] - 1)
            inx2 = random.randint(0, child["comm_n"] - 1)
            child["gene"][inx1], child["gene"][inx2] = child["gene"][inx2], child["gene"][inx1]
            child["comm"][inx1], child["comm"][inx2] = child["comm"][inx2], child["comm"][inx1]
        else:
            start = random.randint(0, child["comm_n"] - 1)
            end = random.randint(0, child["comm_n"] - 1)
            if end < start:
                start, end = end, start
            child["gene"][start:end + 1] = reversed(child["gene"][start: end + 1])
            child["comm"][start:end + 1] = reversed(child["comm"][start: end + 1])

        return child


