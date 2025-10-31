import cpnet
import networkx as nx
import matplotlib.pyplot as plt
import os
import sys
import json
import traceback
import func_timeout

limit = 10

def Log(func):
    def inner(*pargs):
        print(f"Start function : {func.__name__} with args : {pargs}")
        try:
            return func_timeout.func_timeout(limit, func, args=pargs)
        
        except func_timeout.FunctionTimedOut as e:
            print(f"Function : {func.__name__} ran for {limit}s and did not terminate, skipping ...")

        finally:
            print(f"Finished function : {func.__name__} with args : {pargs}\n\n")

    return inner

@Log
def process_file(filename : str) -> None:

    with open(f"./MetaData/{filename.split(".")[0]}.json") as file:
        config = json.load(file)
    
    # Handle file configuration
    graph_type = config["GraphType"]
    read_method = "read_weighted_edgelist" if config["EdgesWeighted"] == "True" else "read_edgelist"
    edge_attribs = config.get("EdgeAttributes") 
    edge_attribs = [] if edge_attribs == None else edge_attribs

    try:
        G = eval(f"nx.{read_method}('./Data/{filename}', create_using=nx.{graph_type}())")
    except Exception as e:
        print(f"Failed to process {filename} with metadata : {config} due to : \n {e}")
        return

    algorithm_signatures_collection = ["BE", "MINRES", "Lip", "LowRankCore", "LapCore", "LapSgnCore", "Rombach", "Rossa", "Surprise", "KM_ER", "KM_config", "Divisive"]

    # First argument is the name of the script, i.e. "core_periphery_detection.py"
    args = sys.argv
    if len(args) == 1:
        algorithm_signatures = algorithm_signatures_collection

    else:
        algorithm_signatures = [input for input in args[1:] if input in algorithm_signatures_collection]


    for algorithm_signature in algorithm_signatures:

        algorithm = eval(f"cpnet.{algorithm_signature}()")
        try :
            algorithm.detect(G)
        
        except Exception as e:
            print(f"Algorithm : {algorithm_signature} failed to detect on the dataset : {filename} using the config : {config} due to :\n {traceback.format_exc()}")
            continue
        

        c = algorithm.get_pair_id()
        x = algorithm.get_coreness()
        
        # Seperate each Dataset into a Folder in Results
        path = os.path.join(os.getcwd(), "Results", filename.split("." )[0])
        if not os.path.exists(path):
            os.mkdir(os.path.join(path))

        #Figures
        _, ax = plt.subplots(nrows=1, ncols=1, figsize=(10,8))
        ax = plt.gca()
        ax, _ = cpnet.draw(G, c, x, ax)
        plt.savefig(os.path.join(path, f"{algorithm_signature}.png"))

if __name__ == "__main__":

    # Iterate Through the files in the /Data directory
    relative_directory_path = os.path.join(os.getcwd(), "Data")
    for filename in os.listdir(relative_directory_path):
        if not filename.endswith(".edges"):
            continue
        
        process_file(filename)        

