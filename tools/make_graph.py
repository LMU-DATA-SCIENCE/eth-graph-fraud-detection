import pickle
import glob
import tqdm
import networkx as nx
import matplotlib
import numpy

graphs = []

normal_first_graphs = glob.glob("Normal first-order nodes/*.csv")

phishing_first_graphs = glob.glob("Phishing first-order nodes/*.csv")

node_idx = 0

node_list = {}

y = []

i = 0
cnt = 0

for f in normal_first_graphs:
    file_name = f.split("\\")[-1]
    # file_name = '0x000e0e5701b14fb77160bcc7bfe7256522d5927b.csv'
    if file_name == "0x0000000000000000000000000000000000000000.csv": continue
    # if i == 100: break
    graph = nx.Graph()
    node_list = {}
    node_idx = 0
    y.append(0)
    with open("Normal first-order nodes/"+file_name, "r") as ff:
        while True:
            arg = ff.readline()
            if not arg: break
            args = arg.split(",")
            args = args[1:]
            if args[0] == "TxHash": continue
            if not (args[3] in node_list.keys()):
                node_list[args[3]] = node_idx
                node_idx += 1
            if not (args[4] in node_list.keys()):
                node_list[args[4]] = node_idx
                node_idx += 1
            graph.add_edges_from([(node_list[args[3]], node_list[args[4]], dict(weight=float(args[5]), timestamp=int(args[2])))])
            cnt += 1
    graphs.append([graph, 0])
    i += 1

i = 0

for f in phishing_first_graphs:
    file_name = f.split("\\")[-1]
    if file_name == "0x0000000000000000000000000000000000000000.csv": continue
    # if i == 100: break
    y.append(1)
    graph = nx.Graph()
    node_list = {}
    node_idx = 0
    with open("Phishing first-order nodes/"+file_name, "r") as ff:
        while True:
            arg = ff.readline()
            if not arg: break
            args = arg.split(",")
            args = args[1:]
            if args[0] == "TxHash": continue
            if not (args[3] in node_list.keys()):
                node_list[args[3]] = node_idx
                node_idx += 1
            if not (args[4] in node_list.keys()):
                node_list[args[4]] = node_idx
                node_idx += 1
            graph.add_edges_from([(node_list[args[3]], node_list[args[4]], dict(weight=float(args[5]), timestamp=int(args[2])))])
    graphs.append([graph, 1])
    i += 1

with open("graphs.pickle", "wb") as f:
    pickle.dump(graphs, f)
