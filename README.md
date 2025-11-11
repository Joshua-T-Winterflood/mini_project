<h1>
    Core Periphery Detection / Communities Detection Applied to Datasets
</h1>
<p>
    This is a script which applies the core-periphery detection algorithm from <a href="https://github.com/YasAsgari/core-periphery-detection" target="_blank">Repository on GitHub</a> to some datasets.
</p>
<p>
    To perform the core periphery detection perform the following steps:
<ol>
    <li> Install dependencies, see <code>requirements.txt</code> file. </li>
    <li>Create the directories /Data, /MetaData,
    <li>Insert <code>.edges</code> or <code>.mtx</code> files into the /Data directory.</li> 
    <li>
        Insert meta data in the form of <code>.json</code> files into the <code>/MetaData</code> directory.
        For each <code>.edges</code> file in <code>/Data</code>, create a JSON file in
        <code>/MetaData</code> directory with the same base name.
        For example, if there is an <code>example.edges</code> file, there should be an
        <code>example.json</code> file.
        The JSON file may contain configurations such as:
        <pre><code>{
    "GraphType": "Graph" | "DiGraph",
    "EdgesWeighted": "True" | "False"
}
        </code></pre>
        </li>
        <li>Execute the Scripts. i.e. <code>python core_periphery_detection.py</code> and <code> python Louvain.py</code> from the root directory. 
        <li>Obtain the results from the <code>/Results</code> directory which contains two subfolders : the <code>/GEXF</code> directory contains the processes graphs, of which the nodes are associated with the attributes : coreness, core-periphery (<code>/BE</code> directory) or community (<code>/Louvain</code> directory). These files can then be visualized in Gephi. 
        The other subfolder is <code>/Degree_Distributions</code> which contains the degree distributions over the core/periphery nodes (<code>/BE</code> directory), where the color red stands for core nodes and blue for periphery nodes. In the <code>/Louvain</code> directory you can find the degree distribution over the major 5 communities detected in the dataset, i.e. the 5 communities which have the largest amount of nodes are selected and the rest of the nodes is grouped into a remainder group.
        </li>
</ol>
</p>