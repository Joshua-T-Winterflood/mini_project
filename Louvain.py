#!/usr/bin/env python3
import os
import sys
import json
import logging
import traceback
import networkx as nx
from colorama import Fore
from concurrent.futures import ProcessPoolExecutor
import scipy as sp
import matplotlib.pyplot as plt


# -------------------------------
# Logging setup
# -------------------------------
def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(processName)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


# -------------------------------
# Decorator for function logging
# -------------------------------
def Log(end=""):
    def outer(func):
        def inner(*pargs, **kwargs):
            logging.info(f"Start function: {func.__name__} with args: {pargs}")
            try:
                func(*pargs, **kwargs)
            except Exception as e:
                logging.error(
                    Fore.RED
                    + f"Failure in {func.__name__} with args {pargs}:\n{traceback.format_exc()}"
                    + Fore.WHITE
                )
            finally:
                logging.info(f"Finished function: {func.__name__} with args: {pargs}{end}")
        return inner
    return outer

graph_types = {
    "Graph" : nx.Graph,
    "DiGraph" : nx.DiGraph
}


# -------------------------------
# Louvain processing for one file
# -------------------------------
@Log()
def process_file(filename: str) -> None:
    logging.info(f"Processing file: {filename}")
    weighted = False    

    if(filename.endswith(".edges")):

        with open(f"./MetaData/{filename.split(".")[0]}.json") as file:
            config = json.load(file)
    
        graph_type = graph_types.get(config["GraphType"])
        if graph_type == None:
            graph_type = nx.Graph

        if config["EdgesWeighted"] == "True":
            read_method = nx.read_weighted_edgelist
            weighted = True
        else:
            read_method = nx.read_edgelist
    
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

    # 2️⃣ Run Louvain community detection
    louvain = nx.community.louvain_communities(G, weight="weight" if weighted else None)
    comms = {n: i for i, group in enumerate(louvain) for n in group}
    nx.set_node_attributes(G, comms, "community")

    # 3️⃣ Export to GEXF
    result_dir = os.path.join("Results", "Louvain")
    os.makedirs(result_dir, exist_ok=True)
    output_file = os.path.join(result_dir, f"Louvain_{filename.split(".")[0]}.gexf")

    nx.write_gexf(G, output_file)
    logging.info(Fore.GREEN + f"✅ Exported {output_file}" + Fore.WHITE)

    # Get the degree distributions
    path_degree_distribution = os.path.join(os.getcwd(), "Results", "Degree_Distributions", "Louvain")
    if not os.path.exists(path_degree_distribution):
        os.makedirs(path_degree_distribution)
    file_path_degree_distribution = os.path.join(path_degree_distribution, f"Louvain_{filename.split(".")[0]}_degree_distribution.png")

    s = {}
    for node_id, comm_id in comms.items():
        
        # Limit to 5 commmunities and group the rest into a singular community
        if comm_id >= 5:
            if 5 in s:
                s[5] = s[5] = (s[5][0] + G.degree[node_id], s[5][1] + 1)
            else:
                s[5] = (G.degree[node_id], 1)
        else:    
            if comm_id in s:
                s[comm_id] = (s[comm_id][0] + G.degree[node_id], s[comm_id][1] + 1)
            else:
                s[comm_id] = (G.degree[node_id], 1)
    
    x = [community for community, _ in s.items()]
    y = [value[0] / value[1] for _, value in s.items()]


    color_map = {
    0: '#FFA500',  # custom_orange
    1: '#8A2BE2',  # custom_violet
    2: '#FFFF00',  # custom_yellow
    3: '#8B4513',  # custom_brown
    4: '#008000',  # custom_green
    }

    colors = [color_map.get(comm_id, '#CCCCCC') for comm_id in x] 

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.bar(x, y, color=colors)  # line plot with markers
    ax.set_xlabel('Communities')
    ax.set_ylabel('Average Degree')
    ax.set_title('Average Degree per Community')
    ax.set_xticks(x)

    plt.savefig(file_path_degree_distribution) 


# -------------------------------
# Threaded worker wrapper
# -------------------------------
def worker(filename):
    setup_logger()
    process_file(filename)


# -------------------------------
# Main entry point
# -------------------------------
if __name__ == "__main__":
    setup_logger()

    # Collect all relevant files
    data_dir = os.path.join(os.getcwd(), "Data")
    files = [
        f
        for f in os.listdir(data_dir)
        if f.endswith(".edges") or f.endswith(".edgelist") or f.endswith(".mtx")
    ]

    if not files:
        logging.error("No .edges or .edgelist files found in ./Data/")
        sys.exit(1)

    logging.info(f"Found {len(files)} graph file(s) to process.")

    # Process all files in parallel
    with ProcessPoolExecutor() as executor:
        executor.map(worker, files)
