import cpnet
import networkx as nx
import matplotlib.pyplot as plt
import os


def process_file(filename : str) -> None:
    algorithm = cpnet.BE()
    G = nx.read_weighted_edgelist("./Data/" + filename, create_using=nx.DiGraph())
    algorithm.detect(G)
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
    plt.savefig(os.path.join(path, "BE.png"))


    # Write the Data to the folders

    





if __name__ == "__main__":

    # Iterate Through the files in the /Data directory
    relative_directory_path = "./Data"
    for filename in os.listdir(relative_directory_path):
        if not filename.endswith(".edges"):
            raise NotImplementedError(f"The file : {filename} is not compatible with the expected data layout")
        
        process_file(filename)        
