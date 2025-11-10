import cpnet
import networkx as nx
import matplotlib.pyplot as plt
import os
import sys
import json
import traceback
import scipy as sp
import concurrent.futures
import logging
from colorama import Fore

def Log(end=""):
    def outer(func):
        def inner(*pargs, **kwargs):
            logging.info(f"Start function: {func.__name__} with args: {pargs}")
            try:
                func(*pargs, **kwargs)
            
            except Exception as e:
                logging.info(Fore.RED + f"Failure : Function : {func.__name__} failed with args : {pargs} due to : \n{e}" + Fore.WHITE)
            
            finally:
                logging.info(f"Finished function: {func.__name__} with args: {pargs}{end}")
        return inner
    return outer

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(threadName)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def worker(filename):
    setup_logger()
    process_file(filename)

graph_types = {
    "Graph" : nx.Graph,
    "DiGraph" : nx.DiGraph
}

@Log()
def process_file(filename: str) -> None:
    if(filename.endswith(".edges")):

        with open(f"./MetaData/{filename.split(".")[0]}.json") as file:
            config = json.load(file)
    
        graph_type = graph_types.get(config["GraphType"])
        if graph_type == None:
            graph_type = nx.Graph
        read_method = nx.read_weighted_edgelist if config["EdgesWeighted"] == "True" else nx.read_edgelist
        edge_attribs = config.get("EdgeAttributes") 
        edge_attribs = [] if edge_attribs == None else edge_attribs

        try:

            G = read_method(f'./Data/{filename}', create_using=graph_type())

        except Exception as e:

            logging.info(Fore.RED + f"Failed to process {filename} with metadata : {config} due to : \n {e}" + Fore.WHITE)
            return
        
    elif(filename.endswith(".mtx")):
        M = sp.io.mmread(f"./Data/{filename}")
        G = nx.from_scipy_sparse_array(M)

    # --- Run algorithms ---
    algorithm_signatures_collection = [
        "BE"
    ]

    for algorithm_signature in algorithm_signatures_collection:
        process_file_with_algorithm(filename, algorithm_signature, G)

@Log()
def process_file_with_algorithm(filename: str, algorithm_signature: str, G):

    path = os.path.join(os.getcwd(), "Results", algorithm_signature)
    gexf_path = os.path.join(path, f"BE_{filename.split(".")[0]}.gexf")

    path_degree_distribution = os.path.join(os.getcwd(), "Results", "Degree_Distributions", algorithm_signature)
    if not os.path.exists(path_degree_distribution):
        os.makedirs(path_degree_distribution)
    file_path_degree_distribution = os.path.join(path_degree_distribution, f"{algorithm_signature}_{filename.split(".")[0]}_degree_distribution.png")

    if os.path.exists(gexf_path) and os.path.exists(file_path_degree_distribution):
        logging.info(f"Images already generated, skipping recomputation ...")
        return

    algorithm = eval(f"cpnet.{algorithm_signature}()")

    try:
        algorithm.detect(G)
    except Exception as e:
        logging.info(Fore.RED + f"Algorithm : {algorithm_signature} failed to detect on the dataset : {filename} due to :\n {traceback.format_exc(e)}" + Fore.WHITE)
        return

    c = algorithm.get_pair_id()
    x = algorithm.get_coreness()

    # Save core-periphery attributes
    nx.set_node_attributes(G, c, name="core_periphery")
    nx.set_node_attributes(G, x, name="coreness")

    # Ensure results folder exists
    if not os.path.exists(path):
        os.mkdir(path)

    # Export to GEXF
    try:
        nx.write_gexf(G, gexf_path)
        logging.info(f"Graph with core-periphery attributes exported to {gexf_path}")
    except Exception as e:
        logging.info(Fore.RED + f"Failed to export GEXF for {filename} due to:\n{traceback.format_exc(e)}" + Fore.WHITE)

    # Get the degree distributions
    s = {}
    for node_id, coreness in x.items():
        if coreness in s:
            s[coreness] = (s[coreness][0] + G.degree[node_id], s[coreness][1] + 1)
        else:
            s[coreness] = (G.degree[node_id], 1)
    
    x = [coreness for coreness, _ in s.items()]
    y = [value[0] / value[1] for _, value in s.items()]
    colors = ['#2BB5FF' if c == 0 else '#FF1C19' if c == 1 else 'gray' for c in x]

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.bar(x, y, color=colors)  # line plot with markers
    ax.set_xlabel('Coreness')
    ax.set_ylabel('Average Degree')
    ax.set_title('Average Degree per Coreness')
    ax.set_xticks(x)

    plt.savefig(file_path_degree_distribution) 


if __name__ == "__main__":

    # Iterate Through the files in the /Data directory
    relative_directory_path = os.path.join(os.getcwd(), "Data")
    files = [
        f for f in os.listdir(relative_directory_path)
        if f.endswith(".edges") or
        f.endswith(".mtx")
    ]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(worker, files) 


