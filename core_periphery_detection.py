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

@Log()
def process_file(filename: str) -> None:
    if filename.endswith(".edges"):
        with open(f"./MetaData/{filename.split('.')[0]}.json") as file:
            config = json.load(file)

        # Handle file configuration
        graph_type = config["GraphType"]
        read_method = (
            "read_weighted_edgelist"
            if config["EdgesWeighted"] == "True"
            else "read_edgelist"
        )
        edge_attribs = config.get("EdgeAttributes")
        edge_attribs = [] if edge_attribs is None else edge_attribs

        # --- Detect delimiter automatically ---
        data_path = f"./Data/{filename}"
        delimiter = None
        with open(data_path, "r") as f:
            for line in f:
                if not line.strip() or line.startswith(("#", "%")):
                    continue
                if "," in line:
                    delimiter = ","
                elif "\t" in line:
                    delimiter = "\t"
                elif ";" in line:
                    delimiter = ";"
                else:
                    delimiter = None  # whitespace default
                break

        logging.info(f"Detected delimiter for {filename}: {repr(delimiter or 'whitespace')}")

        try:
            # --- Build eval string safely ---
            cmd = (
                f"nx.{read_method}("
                f"r'{data_path}', "
                f"create_using=nx.{graph_type}(), "
                f"delimiter={repr(delimiter)}, "
                f"comments='#')"
            )
            G = eval(cmd)

        except Exception as e:
            logging.info(
                Fore.RED
                + f"Failed to process {filename} with metadata {config} due to:\n{e}"
                + Fore.WHITE
            )
            return

    elif filename.endswith(".mtx"):
        M = sp.io.mmread(f"./Data/{filename}")
        G = nx.from_scipy_sparse_array(M)

    # --- Run algorithms ---
    algorithm_signatures_collection = [
        "BE"
    ]

    args = sys.argv
    if len(args) == 1:
        algorithm_signatures = algorithm_signatures_collection
    else:
        algorithm_signatures = [
            arg for arg in args[1:] if arg in algorithm_signatures_collection
        ]

    for algorithm_signature in algorithm_signatures:
        process_file_with_algorithm(filename, algorithm_signature, G)

@Log()
def process_file_with_algorithm(filename: str, algorithm_signature: str, G):
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
    path = os.path.join(os.getcwd(), "Results", filename.split(".")[0])
    if not os.path.exists(path):
        os.mkdir(path)

    # Export to GEXF
    gexf_path = os.path.join(path, f"{algorithm_signature}.gexf")
    try:
        nx.write_gexf(G, gexf_path)
        logging.info(f"Graph with core-periphery attributes exported to {gexf_path}")
    except Exception as e:
        logging.info(Fore.RED + f"Failed to export GEXF for {filename} due to:\n{traceback.format_exc(e)}" + Fore.WHITE)



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


