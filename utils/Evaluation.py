from utils.TrecAnalyser import search
import matplotlib.pyplot as plt
import numpy as np
import math
import matplotlib.pyplot as plt


def read_queries(path):

    # path = "/home/chaima/PycharmProjects/projet/Queries/requetesLongues.txt"

    with open(path) as fp:
        line = fp.readline()
        queries = []
        while line:
            queries.append(line)
            line = fp.readline()
        return queries


def execute(cleaning, similarty, improve, type, path):
    print(cleaning, similarty, improve)
    # queries = read_queries("Short")
    queries = read_queries(path)
    All_doc = read_relavant_documents()

    measure = []
    for query in queries:
        if type == "Short":
            a = query.split('#')[1].replace("\n", "")
        else:
            a = query.split('#')[1].replace("\n", "") + " " + query.split('#')[2].replace("\n", "")
        b = str(int(query.split('#')[0].replace(" ", "")))
        print("numero de la requete ", a)
        obtained_doc = search(a, cleaning, similarty, improve)
        relevant_doc = All_doc[b]
        # measure.append([str(a), relevant_doc, obtained_doc])
        generate_trec_eval_doc(type + "_"+str(cleaning)+"_"+str(similarty)+"_"+str(improve), b, obtained_doc)


def read_relavant_documents():
    path = "/home/chaima/PycharmProjects/projet/Queries/qrels.1-50.AP8890.txt"

    relevant_query = {}

    with open(path) as fp:
        line = fp.readline()
        while line:
            id_request, zero, document, relevance = line.split(' ')
            # print(id_request, zero, document, relevance)
            if id_request in relevant_query.keys():
                relevance = relevance.rstrip()
                if int(relevance) is 1:
                    relevant_query[id_request].append(document)
            else:
                if int(relevance) is 1:
                    relevant_query[id_request] = [document]
                else:
                    relevant_query[id_request] = []

            line = fp.readline()
    return relevant_query


class MAP_query:
    def __init__(self, query, relevant_doc, obtained_doc):
        self.query = query
        self.relevant_doc = relevant_doc
        self.obtained_doc = obtained_doc

    # Precision = No. of relevant documents retrieved / No. of total documents retrieved
    def precision(self):

        number_relevant_retrieved = 0
        for doc in self.obtained_doc:
            if doc[0].replace(" ", "") in self.relevant_doc:
                number_relevant_retrieved = number_relevant_retrieved + 1

        # print("query precision ", number_relevant_retrieved / len(self.obtained_doc))
        return number_relevant_retrieved / len(self.obtained_doc)

    # Recall = No. of relevant documents retrieved / No. of total relevant documents
    def recall(self):

        number_relevant_retrieved = 0
        for doc in self.obtained_doc:
            if doc[0].replace(" ", "") in self.relevant_doc:
                number_relevant_retrieved = number_relevant_retrieved + 1

        if len(self.relevant_doc) > 0:
            return number_relevant_retrieved / len(self.relevant_doc)
        else:
            return 0


class MAP:
    def __init__(self, queries):
        self.queries = queries

    def Mean_Avg_Precision(self):
        MAP = 0
        for query in self.queries:
            MAP = MAP + MAP_query(query[0], query[1], query[2]).precision()

        return MAP / len(self.queries)

    def Precision_Recall_Curve(self):
        row = []
        columns = []
        for query in self.queries:
            row.append(MAP_query(query[0], query[1], query[2]).precision())
            columns.append(MAP_query(query[0], query[1], query[2]).recall())

        return row, columns


def obtained_documents_for_request(documents):
    obtained = []
    for doc in documents:
        obtained.append(doc[0])

    return obtained


def draw_plots():

    t = [0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]
    short_5_1_2 = [0.2684, 0.1533, 0.1238, 0.1087, 0.0771, 0.0695, 0.0622, 0.0553, 0.0468, 0.0397, 0.0289]
    short_5_1_1 = [0.3043, 0.1633, 0.1265, 0.1164, 0.0921, 0.0831, 0.0661, 0.0572, 0.0481, 0.0354, 0.0234]

    short_5_1_0 = [0.4032, 0.2323, 0.1835, 0.1694, 0.1377, 0.1295, 0.1038, 0.0886, 0.0735, 0.0488, 0.0268]
    short_5_0_0 = [0.3816, 0.2266, 0.1823, 0.1656, 0.1239, 0.1128, 0.0932, 0.0825, 0.0694, 0.0444, 0.0249]

    short_4_1_0 = [0.4063, 0.2334, 0.1863, 0.1710, 0.1297, 0.1199, 0.0994, 0.0876, 0.0735, 0.0516, 0.0270]
    short_4_0_0 = [0.3469, 0.2111, 0.1738, 0.1586, 0.1231, 0.1163, 0.0877, 0.0782, 0.0677, 0.0446, 0.0248]

    short_3_0_0 = [0.3399, 0.2087, 0.1684, 0.1544, 0.1195, 0.1095, 0.0870, 0.0798, 0.0712, 0.0461, 0.0251]
    short_3_1_0 = [0.3809, 0.2347, 0.1865, 0.1668, 0.1330, 0.1245, 0.0990, 0.0879, 0.0749, 0.0516, 0.0273]

    short_2_0_0 = [0.3602, 0.2151, 0.1776, 0.1593, 0.1249, 0.1136, 0.0927, 0.0800, 0.0683, 0.0442, 0.0252]
    short_2_1_0 = [0.3972, 0.2310, 0.1850, 0.1692, 0.1397, 0.1296, 0.1041, 0.0888, 0.0731, 0.0485, 0.0269]

    short_1_0_0 = [0.2990, 0.1906, 0.1583, 0.1458, 0.1156, 0.1061, 0.0824, 0.0685, 0.0596, 0.0401, 0.0245]
    short_1_1_0 = [0.3735, 0.2274, 0.1739, 0.1559, 0.1154, 0.1072, 0.0919, 0.0770, 0.0678, 0.0456, 0.0263]

    short_0_0_0 = [0.1785, 0.0891, 0.0653, 0.0491, 0.0225, 0.0197, 0.0157, 0.0137, 0.0112, 0.0060, 0.0006]
    short_0_1_0 = [0.2254, 0.1098, 0.0785, 0.0624, 0.0321, 0.0260, 0.0209, 0.0179, 0.0144, 0.0086, 0.0007]

    long_0_0_0 = [0.2627, 0.1526, 0.1189, 0.1024, 0.0684, 0.0578, 0.0459, 0.0389, 0.0254, 0.0125, 0.0020]
    long_0_1_0 = [0.3685, 0.1859, 0.1453, 0.1222, 0.0836, 0.0689, 0.0536, 0.0455, 0.0305, 0.0174, 0.0028]

    long_1_0_0 = [0.4310, 0.2490, 0.1976, 0.1723, 0.1462, 0.1359, 0.1118, 0.0993, 0.0827, 0.0552, 0.0322]
    long_1_1_0 = [0.4512, 0.2663, 0.2085, 0.1889, 0.1504, 0.1389, 0.1193, 0.1076, 0.0895, 0.0635, 0.0354]

    long_2_0_0 = [0.4299, 0.2648, 0.2065, 0.1814, 0.1458, 0.1329, 0.1133, 0.1019, 0.0891, 0.0634, 0.0354]
    long_2_1_0 = [0.5379, 0.2804, 0.2244, 0.1974, 0.1637, 0.1516, 0.1237, 0.1079, 0.0944, 0.0729, 0.0412]

    long_3_0_0 = [0.4333, 0.2510, 0.2108, 0.1880, 0.1515, 0.1370, 0.1191, 0.1057, 0.0915, 0.0688, 0.0389]
    long_3_1_0 = [0.5315, 0.2841, 0.2290, 0.1968, 0.1616, 0.1472, 0.1246, 0.1114, 0.0952, 0.0745, 0.0401]

    long_4_0_0 = [0.4002, 0.2397, 0.2038, 0.1796, 0.1407, 0.1305, 0.1070, 0.0971, 0.0786, 0.0559, 0.0277]
    long_4_1_0 = [0.4002, 0.2397, 0.2038, 0.1796, 0.1407, 0.1305, 0.1070, 0.0971, 0.0786, 0.0559, 0.0277]

    long_5_0_0 = [0.4482, 0.2733, 0.2169, 0.1880, 0.1512, 0.1376, 0.1166, 0.1037, 0.0893, 0.0628, 0.0361]
    long_5_1_0 = [0.5355, 0.2764, 0.2202, 0.1953, 0.1628, 0.1513, 0.1268, 0.1086, 0.0946, 0.0741, 0.0407]

    long_5_1_1 = [0.2767, 0.1462, 0.1220, 0.1134, 0.0913, 0.0846, 0.0649, 0.0568, 0.0509, 0.0418, 0.0332]
    long_5_1_2 = [0.3248, 0.1790, 0.1503, 0.1340, 0.1003, 0.0865, 0.0761, 0.0661, 0.0554, 0.0431, 0.0262]

    plt.plot(t, short_0_0_0, 'r', label='Pas prétraitement')  # plotting t, a separately
    plt.plot(t, short_1_0_0, 'g', label='Suppression de stop words')  # plotting t, a separately
    plt.plot(t, short_2_0_0, 'c', label='Stemmatisation avec Porter')  # plotting t, a separately
    plt.plot(t, short_3_0_0, 'm', label='Stemmatisation avec Krovetz')  # plotting t, a separately
    plt.plot(t, short_4_0_0, 'y', label='Lemmatisation')  # plotting t, a separately
    plt.plot(t, short_5_0_0, 'k', label='Prétraitement Anglais')  # plotting t, a separately

    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.legend(loc='best')
    plt.show()


def generate_trec_eval_doc(file, id_query, documents):

    with open(file, "a+") as f:
        print(f)
        for doc in documents:
            string = str(id_query)+" Q0" + str(doc[0])
            if string not in f.read():
                f.write(str(id_query)+" Q0" + str(doc[0]) + " " + str(doc[5]) + " " + str(doc[4]) + " STANDARD\n")
            # print(str(id_query)+" Q0" + str(doc[0]) + " " + str(doc[5]) + " " + str(doc[4]) + " STANDARD\n")

    print("sortie \n")
