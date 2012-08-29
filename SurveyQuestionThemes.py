import re # import regular expression module
from numpy import * # import numpy for matrix & array features
from numpy.linalg import svd
from numpy.linalg import norm
#import nnmf # import non negative matrix factorization algorithm
import porter # import porter.py - porter stemmer algorithm
from xml.dom.minidom import Document
##
# A collection of functions for using Non Negative Matrix Factorization to find themes in open ended survey questions

##
# Utility function to return a list of all words that are have a length greater than a specified number of characters.
# @param text The text that must be split in to words.
# @param minWordReturnSize The minimum no of characters a word must have to be included.
def separatewords(text,minWordReturnSize):
  #splitter=re.compile('\\W*')
  splitter=re.compile('[^a-zA-Z0-9_\\+\\-]')
  return [singleWord.lower() for singleWord in splitter.split(text) if len(singleWord)>minWordReturnSize]

##
# Utility function to sort a dictionary by Value in decending order
# Not the most efficient implementation - may need to refactor if speed becomes an issue
# @param dictionary The dictionary data structure.
# @return list A list of keys sorted by their value.
def sortDictionaryByValues(dictionary):
    """ Returns the keys of dictionary d sorted by their values """
    items=dictionary.items()
    backitems=[ [v[1],v[0]] for v in items]
    backitems.sort()
    backitems.reverse()
    return [ backitems[i][1] for i in range(0,len(backitems))]

##
# Utility function to load stop words from a file and return as a list of words
# @param stopWordFile Path and file name of a file containing stop words.
# @return list A list of stop words.
def loadStopWords(stopWordFile):
    stopWords = []
    for line in open(stopWordFile):
        for word in line.split( ): #in case more than one per line
            stopWords.append(word)
    return stopWords

##
# Utility function to remove stop words that are present in a list of words
# @param wordlist Unfiltered list of words
# @param stopwordlist List of stops words
# @return list Filtered list of words
def removeStopWords(wordlist,stopwordlist):
    return [word for word in wordlist if word not in stopwordlist]

##
# This function returns a list of all words that are have a length greater than a specified number of characters.
# @param text The text that must be split in to words.
# @param minWordReturnSize The minimum no of characters a word must have to be included.
def getItemWords(list_of_words,stop_words):
  stemmer=porter.PorterStemmer()
  allwords={}
  itemwords=[]
  itemtitles=[]
  ec=0
  stemlist = {}
  # Loop over every item in list_of_words
  for item in list_of_words:
      words=separatewords(item,1)
      words = removeStopWords(words,stop_words)
      itemwords.append({})
      itemtitles.append("Response " + str(ec+1))
      # Increase the counts for this word in allwords and in articlewords
      for word in words:
        unstemmedword = word
        word=stemmer.stem(word,0,len(word)-1)
	if word in stemlist:
		temp = stemlist[word]
 		try:
        		temp.index(unstemmedword)
   		except ValueError:
			temp.append(unstemmedword)
			stemlist[word] = temp
	else:
		temp = []
		temp.append(unstemmedword)
		stemlist[word] = temp	
        allwords.setdefault(word,0)
        allwords[word]+=1
        itemwords[ec].setdefault(word,0)
        itemwords[ec][word]+=1
      ec+=1
  return allwords,itemwords,itemtitles,stemlist


##
# Returns the document (row) and words (columns) matrix and the list of words as a vector
def createWordMatrix(all_words,words_inItems):
    #print all_words
    #print words_inItems
    wordvector=[]
    # Only take words that are common but not too common
    for w,c in all_words.items():
        wordvector.append(w)
        #if c<len(words_inItems)*0.6: #*0.2
    # Create the word matrix
    cols = len(wordvector)
    rows = len(words_inItems)
    l1=[[(wrd in f and f[wrd] or 0) for wrd in wordvector] for f in words_inItems]
    wordMatrix = array(l1)
    wordCount = []
    sum = 0
    for c in range(0, cols):
        for r in range(0, rows):
            sum += wordMatrix[r][c]
        wordCount.append(sum)
        sum = 0
    return wordMatrix, wordvector, wordCount, cols, rows


##
# Display themes, top six words in a theme and associated documents in theme.
def display_themes(weights_matrix,themes_matrix,list_Of_Included_Words,item_Titles, stemdictionary, wordCount, inc_articles, surveyQuestionResponseNID):
    # Data structures for Graph Representation
    ThemeDictionary = {}
    DocDictionary = {}
    TermDictionary = {}
    # Data structures to represent relationships
    DocInTheme = {}
    TermInTheme = {}
    # Start of NMF interpretation
    norows,nocols = shape(themes_matrix)
    noarticles,nofeatures = shape(weights_matrix)
    d1={}
    count = 1
    theme_html = ""
    themes_html = ""
    # setup XML structure
    # Create the minidom document
    doc = Document()
    # Create the <themes> base element
    themes_xml = doc.createElement("themes")
    doc.appendChild(themes_xml)
    
    for row in range(norows):
	theme_html = ""
	# Create the main <theme> element
	theme_xml = doc.createElement("theme")
	theme_xml.setAttribute("id", str(count))
	theme_xml.setAttribute("title", "Theme " + str(count))
	themes_xml.appendChild(theme_xml)
	
        ThemeDictionary["T" + str(count)] = "Theme " + str(count)
	
	# Create a <words> element
	words_xml = doc.createElement("words")
	theme_xml.appendChild(words_xml)
	
        for col in range(nocols):
            d1[list_Of_Included_Words[col]] = themes_matrix[row,col]
        themes_list_in_order = sortDictionaryByValues(d1)
        for it in themes_list_in_order[0:6]:
          word_index = list_Of_Included_Words.index(it)
          TermDictionary[it] = stemdictionary[it]
          TermInTheme["T" + str(count) + "_" + it] = str("%.2f" % d1[it])
	  
	  word_xml = doc.createElement("word")
	  word_xml.setAttribute("weight", str(d1[it]))
	  wordtext_xml = doc.createTextNode(it)
	  word_xml.appendChild(wordtext_xml)
	  words_xml.appendChild(word_xml)
	  
	theme_html = theme_html + "</p>"
	if (inc_articles==1):
          # Print articles/items/survey responses that map to Theme/Feature
          articlesInTheme = {}
          articleweights=[]
          for article in range(noarticles):
            if (weights_matrix[article,row] > 0.08):
                articlesInTheme[article] = weights_matrix[article,row]
                articleweights.append(weights_matrix[article,row])
                DocDictionary["D" + str(article)] = "Doc" + str(article)
                DocInTheme["T" + str(count) + "_D" + str(article)] = str("%.2f" % weights_matrix[article,row])
            else:
                # Capture all non attached documents
                DocDictionary["D" + str(article)] = "Doc" + str(article)
          max_weight_val = max(articleweights)
          min_weight_val = min(articleweights)

          articles_In_Theme_Order = sortDictionaryByValues(articlesInTheme)

	  # Create a <responses> element
	  reponses_xml = doc.createElement("responses")
	  theme_xml.appendChild(reponses_xml)
	  
	  for article_no in articles_In_Theme_Order:
	    
	    response_xml = doc.createElement("response")
	    response_xml.setAttribute("id", str(surveyQuestionResponseNID[article_no]))
	    response_xml.setAttribute("weight", str(("%.2f" % weights_matrix[article_no,row])))

	    responsetext_xml = doc.createTextNode(item_Titles[article_no])
	    response_xml.appendChild(responsetext_xml)

	    reponses_xml.appendChild(response_xml)

	  # Create Rendered element
	  rendered_xml = doc.createElement("rendered")
	  theme_xml.appendChild(rendered_xml)

	count = count + 1
    return doc.toprettyxml(indent="  ")
   

# Strange way to determine if NaN in Python?
def isNaN(x):
    return (x == x) == False
    
    

def pos(A):
    Ap = (A>=0)*A
    return Ap

def neg(A):
    Am = (A<0)*(-A);
    return Am

def nndsvd(A,k,flag):
    #size of input matrix
    m, n = A.shape
    #the matrices of the factorization
    W = zeros([m, k])
    H = zeros([k, n])

    #1st SVD --> partial SVD rank-k to the input matrix A.
    U,S,V = svd(A,k)
    c = array(U)
    #print "S1",S[0]
    #print "U",U
    #print "c[0][:]",c[:][1]
    #print "c[:][1]",c[0,:]
    #choose the first singular triplet to be nonnegative
    Utemp = zeros([m]);
    for i in range(0, m):
        Utemp[i] = U[i][0]
    #print "Utemp",Utemp
    Wtemp = sqrt(S[0]) * abs(Utemp)
    for i in range(0, k+1):
        W[i][0] = Wtemp[i]
    Htemp = sqrt(S[0]) * abs(V[:][0].T)
    for i in range(0, n):
        H[0][i] = Htemp[i]

    #print "Wtemp", Wtemp
    #print "W", W
    #print "Htemp", Htemp
    #print "H", H

    # second SVD for the other factors (see table 1 in our paper)
    # AB - check on k-1
    for i in range(1, k):
            #print "in loop", i
            uuTemp = zeros([m]);
            for l in range(0, m):
                uuTemp[l] = U[l][i]
            #print "uuTemp",uuTemp
            uu = uuTemp
            #print "uu",uu
            vv = V[:][i]
            #print "vv",vv
            uup = pos(uu)
            uun = neg(uu)
            vvp = pos(vv)
            vvn = neg(vv)
            n_uup = norm(uup)
            n_vvp = norm(vvp)
            n_uun = norm(uun)
            n_vvn = norm(vvn)
            termp = n_uup*n_vvp
            termn = n_uun*n_vvn
            #print "termp",termp
            #print "termn",termn
            #print "S[i]",S[i]
            if (termp >= termn):
                #print "termp >= termn"
                W1temp = sqrt(S[i]*termp)*uup/n_uup
                #print "W1temp",W1temp
                for j in range(0, k):
                    W[j][i] = W1temp[j]
                H1temp = sqrt(S[i]*termp)*vvp.T/n_vvp
                #print "H1temp",H1temp
                for j in range(0, n):
                    H[i][j] = H1temp[j]
                #print "W1temp",
                #print W1temp
                #print "H1temp",
                #print H1temp
                #W[:][i] = sqrt(S[i][i]*termp)*uup/n_uup
                #H[i][:] = sqrt(S[i][i]*termp)*vvp.T/n_vvp
            else:
                #print "termp < termn"
                W1temp = sqrt(S[i]*termn)*uun/n_uun
                #print "W1temp",W1temp
                #print "uun",uun
                for j in range(0, k):
                    W[j][i] = W1temp[j]
                H1temp = sqrt(S[i]*termn)*vvn.T/n_vvn
                #print "H1temp",H1temp
                for j in range(0, n):
                    H[i][j] = H1temp[j]
                #print "W1temp",
                #print W1temp
                #print "H1temp",
                #print H1temp
                #W[:][i] = sqrt(S[i][i]*termn)*uun/n_uun
                #H[i][:] = sqrt(S[i][i]*termn)*vvn.T/n_vvn

    #actually these numbers are zeros
    if (flag==1):
        ArrayAverage = mean(A[:][:])

    #actually these numbers are zeros
    for i in range(0, m):
        for j in range(0, k):
            if (W[i][j]<0.0000000001):
                if (flag==0):
                    W[i][j] = 0
                elif  (flag==1):
                    W[i][j] = ArrayAverage

    for i in range(0, k):
        for j in range(0, n):
            if (H[i][j]<0.0000000001):
                if (flag==0):
                    H[i][j] = 0
                elif (flag==1):
                    H[i][j] = ArrayAverage

    return (W, H)
