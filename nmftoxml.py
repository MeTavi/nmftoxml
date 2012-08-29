'''
# Programmed by Aneesha Bakharia
'''

import re 
from numpy import *
import csv 
import os
import sys
import platform

import nmf as nmf # import non negative matrix factorization algorithm
import porter as porter # import porter.py - porter stemmer algorithm
import SurveyQuestionThemes as surveythemer

def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def findthemes(nothemes,wordlist,questionresponses,inc_articles,outputfile):
    #print questionresponses
    synonym_wordlists = []
    synonym_wordlist = wordlist
    synonym_wordlists = synonym_wordlist.splitlines()
    exclude_wordlist = []

    stop_path = "englishstop.txt"
    stop_words = surveythemer.loadStopWords(stop_path)

    surveyQuestionResponse = []
    surveyQuestionResponseNID = []
    
    for response in questionresponses:
      newresp = remove_html_tags(response["text"])
      surveyQuestionResponse.append(newresp)
      surveyQuestionResponseNID.append(response["id"])
        
    listOfAllWords, listOfSurveyQuestionWords, listOfAllSurveyQuestionTitles, stemdictionary = surveythemer.getItemWords(surveyQuestionResponse,stop_words)
    wordMatrix, listOfWordsIncluded, wordCount, fc, ic = surveythemer.createWordMatrix(listOfAllWords,listOfSurveyQuestionWords)
    pc = nothemes
    #size of input matrix
    ic=shape(wordMatrix)[0]
    fc=shape(wordMatrix)[1]
    # Random initialization
    w=array([[random.random() for j in range(pc)] for i in range(ic)])
    h=array([[random.random() for i in range(fc)] for i in range(pc)])
    nmfresult = ""
    themes = ""
    weights,themes = nmf.nmf(wordMatrix,w,h,0.001, 10, 500)
    themexml = surveythemer.display_themes(weights,themes,listOfWordsIncluded,surveyQuestionResponse, stemdictionary, wordCount, inc_articles, surveyQuestionResponseNID)
    f = open(outputfile, 'w')
    f.write(themexml)
    f.close()  
    return 
 
fileName = sys.argv[1]
directoryName = sys.argv[2]
filepath = os.path.abspath(directoryName + '/' + fileName)
nothemes = int(sys.argv[3])
showdocs = int(sys.argv[4])
outputfile = sys.argv[5]

outputfiledir = os.path.abspath(directoryName + '/data/' + outputfile)

data = csv.reader(open(filepath))  

questionresponses = []
# Read the column names from the first line of the file  
fields = data.next()  
items = ""
count = 1
for row in data:  
  #print count
  count = count + 1
  # Zip together the field names and values  
  items = zip(fields, row)  
  item = {}  
  # Add the value to our dictionary  
  for (name, value) in items:  
    item[name] = value.strip() 
  questionresponses.append(item)

findthemes(nothemes,"",questionresponses,showdocs,outputfiledir)