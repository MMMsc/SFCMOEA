import time
import numpy as np
from parameter import *


# 版本三，初步搜索中node数量小于3的community重新分配
def get_evalcomm3(population, netOrig):

    max_lengthofvalcomm = 0
    for k in range(popsize):
        if max_lengthofvalcomm < population.pop[k]["ind"]["comm_n"]:
            max_lengthofvalcomm = population.pop[k]["ind"]["comm_n"]
    evalcomm = [{} for k in range(max_lengthofvalcomm)]

    for i in range(popsize):
        # 将clique转换为node，构建community
        for k in range(max_lengthofvalcomm):
            evalcomm[k]["comm"] = [0 for tmp in range(200)]
            evalcomm[k]["size"] = 0

        for k in range(population.pop[i]["ind"]["comm_n"]):
            evalcomm.append({"comm": [], "size": 0})
            numofnode, _ = population.convert_clique_to_node(
                population.pop[i]["ind"]["comm"][k], evalcomm[k]["comm"])
            evalcomm[k]["size"] = numofnode

        nodes = []
        allnodes = [c for c in range(netOrig.net_orig["n"])]

        del_comm = []
        for c1 in range(population.pop[i]["ind"]["comm_n"]):
            if evalcomm[c1]["comm"] == []:
                population.pop[i]["ind"]["comm_n"] -= 1
            cnode = evalcomm[c1]["comm"][:evalcomm[c1]["size"]]
            evalcomm[c1]["comm"] = cnode

            if evalcomm[c1]["size"] < 3:
                del_comm.append(c1)
            for c in evalcomm[c1]["comm"]:
                nodes.append(c)

        # 还没有被分配的结点
        nodes = list(set(allnodes) ^ set(nodes))

        # size小于3的结点重新分配
        for c1 in reversed(del_comm):
            for c in evalcomm[c1]["comm"]:
                if c not in nodes:
                    nodes.append(c)
            del evalcomm[c1]
            population.pop[i]["ind"]["comm_n"] -= 1

        if i == 0:
            with open("remain.txt", "w+", encoding="utf-8") as f:
                f.write("%d\n" % (len(nodes)))

        # 计算未分配的结点对不同community中结点的权重
        for nd in nodes:
            belongs = [0.0 for c in range(population.pop[i]["ind"]["comm_n"])]
            for cnum in range(population.pop[i]["ind"]["comm_n"]):
                for cn in evalcomm[cnum]["comm"]:
                    belongs[cnum] += (netOrig.similarity[nd][cn])
                belongs[cnum] = format(belongs[cnum] / evalcomm[cnum]["size"], '.3f')

            for tmp in list(np.where(np.array(belongs) == max(belongs))[0]):
                evalcomm[tmp]["comm"].append(nd)
                evalcomm[tmp]["size"] += 1

    return evalcomm

