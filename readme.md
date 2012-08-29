NMFtoXML

NMFtoXML is a set of python scripts that imports text from a csv file, runs Non-negative Matrix Factorization and then outputs the resulting clusters to XML.

Dependencies:
Numpy is required.
The projected gradient NMF algorithm is used. The algorithm was ported to Python by Anthony Di Franco.
The PorterStemmer algorithm by Vivake Gupta.

The script can be run from the command line.

The format is: python nmftoxml.py filename directory numberofthemes showdocs outputfilename

eg:
python nmftoxml.py sample.csv C:\nmftoxml 2 1 sample.xml

