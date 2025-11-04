<h1>
    Core Periphery Detection Applied to Datasets
</h1>
<p>
    This is a script which applies the core-periphery detection algorithm from <a href="https://github.com/YasAsgari/core-periphery-detection" target="_blank">Repository on GitHub</a> to some datasets.
</p>
<p>
    To perform the core periphery detection perform the following steps:
<ol>
    <li> Install dependencies, see <code>requirements.txt</code> file. </li>
    <li>Create the directories /Data, /MetaData, /Results
    <li>Insert <code>.edges</code> or <code>.mtx</code> files into the /Data directory.</li> 
    <li>Insert Metadata for the <code>.edges</code> files into the /MetaData directory.
    <li>Execute the Script. i.e. <code>python core_periphery_detection.py</code> from the root directory with the optional arguments : algorithm signatures, for instance <code>python core_periphery_detection.py BE Rossa</code> to apply only the algorithms BE and Rossa from  <a href="https://github.com/YasAsgari/core-periphery-detection" target="_blank">Repository on GitHub.</a></li>
    <li>Obtain the .png images of the figures from the /Results directory.</li>
</ol>
</p>