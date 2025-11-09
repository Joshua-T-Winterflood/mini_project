#!/usr/bin/env python3
import os
import sys
import json
import logging
import traceback
import networkx as nx
from colorama import Fore
from concurrent.futures import ThreadPoolExecutor


# -------------------------------
# Logging setup
# -------------------------------
def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(threadName)s] %(message)s",
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


# -------------------------------
# Louvain processing for one file
# -------------------------------
@Log()
def process_file(filename: str) -> None:
    logging.info(f"Processing file: {filename}")

    # 1️⃣ Detect weighted vs unweighted automatically
    file_path = os.path.join("Data", filename)
    with open(file_path, "r") as f:
        for line in f:
            if line.strip():
                parts = line.strip().split()
                break

    if len(parts) == 3:
        weighted = True
        G = nx.read_edgelist(file_path, data=(("weight", float),))
        logging.info(f"Detected weighted edgelist: {filename}")
    elif len(parts) == 2:
        weighted = False
        G = nx.read_edgelist(file_path)
        logging.info(f"Detected unweighted edgelist: {filename}")
    else:
        logging.error(f"File format not recognized: {filename}")
        return

    # 2️⃣ Run Louvain community detection
    louvain = nx.community.louvain_communities(G, weight="weight" if weighted else None)
    comms = {n: i for i, group in enumerate(louvain) for n in group}
    nx.set_node_attributes(G, comms, "community")

    # 3️⃣ Export to GEXF
    result_dir = os.path.join("Results", filename.split(".")[0])
    os.makedirs(result_dir, exist_ok=True)
    output_file = os.path.join(result_dir, "Louvain.gexf")

    nx.write_gexf(G, output_file)
    logging.info(Fore.GREEN + f"✅ Exported {output_file}" + Fore.WHITE)


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
        if f.endswith(".edges") or f.endswith(".edgelist")
    ]

    if not files:
        logging.error("No .edges or .edgelist files found in ./Data/")
        sys.exit(1)

    logging.info(f"Found {len(files)} graph file(s) to process.")

    # Process all files in parallel
    with ThreadPoolExecutor() as executor:
        executor.map(worker, files)
