# -*- coding: utf-8 -*-
from lxml import etree
import numpy as np
import pandas as pd
from nltk import tokenize
import nltk
from pprint import pprint
import re
from transformers import pipeline
import requests
from mongoengine import connect
from mongoengine.errors import NotUniqueError

nltk.download("punkt")

"""### Load Model for Sentiment Analysis"""

SENTIMENT_MODEL = pipeline(model="cardiffnlp/twitter-roberta-base-sentiment")

"""### Cross-ref Response """

def find_CrossRef_Response(doi):
    response = requests.get('https://api.crossref.org/works/'+ doi).json()
    return response

"""### Metadata"""

def find_DOI(article_meta):
    for article in article_meta:
        try:
            if(article.attrib['pub-id-type'] == 'doi'):
                return article.text
        except:
            continue

def find_Title(front):
    title = front.findall('.//article-title')
    return title[0].text

def find_Journal(front):
    journal_title= front.findall('.//journal-title')
    return journal_title[0].text

def find_Publisher(front):
    publisher_name = front.findall('.//publisher-name')
    return publisher_name[0].text

def find_Publish_Date(front):
    pub_date = front.findall('.//history')[0]

    for date in pub_date:
        if(date.attrib['date-type']== 'accepted'):
            pub_date = date
    
    published_date = ''
    for pub in pub_date:
        published_date += pub.text + '-'
        
    return published_date[:-1]

def find_Authors(front):
    article_author= front.findall('.//contrib')
    article_authors = []
    for i in article_author:
        if i.attrib['contrib-type'] == 'author' :
            article_authors.append(i)
            
    author_names = ''
    for name in article_authors:
        author = name.findall(".//name")[0]

        for author_name in author:
            author_names += author_name.text + ' '
        author_names += ', '
        
    author_names = author_names[:-2]
    author_names = author_names.split(", ")
    return author_names

def find_Abstract(front, xml_tree):
    abstract = xml_tree.xpath(".//abstract")[0]
    abstract = etree.tostring(abstract, method='text', encoding='unicode')
    return abstract

def find_Metadata(front, xml_tree):
    doi = find_DOI(front[1])
    title = find_Title(front)
    journal = find_Journal(front)
    publisher = find_Publisher(front)
    publish_date = find_Publish_Date(front)
    authors = find_Authors(front)
    abstract = find_Abstract(front, xml_tree)
    
    return doi, title, journal,publisher, publish_date, authors, abstract

"""### Article Section Lengths"""

def get_Article_Length(body):
    full_article_text = etree.tostring(body, method='text', encoding='unicode')
    article_text_length = len(full_article_text.split(" "))

    introduction_length = round(article_text_length/100) * 25
    method_length = round(article_text_length/100) * 50
    result_length = round(article_text_length/100) * 75
    discussion_length = round(article_text_length/100) * 100
    
    return article_text_length, introduction_length, method_length, result_length, discussion_length

def get_Article_Sections(body,introduction_length, method_length, result_length, discussion_length):
    sections = []
    c_sum = 0
    for i in body:
        title = i[0].text

        if (c_sum < introduction_length):
            section = "Introduction"
        elif (c_sum < method_length):
            section = "Method"
        elif (c_sum < result_length):
            section = "Results"
        else:
            section = "Discussion"

        sections.append({
            "title": title,
            "start_point": c_sum,
            "section": section
        })
        c_sum += len(etree.tostring(i, method='text', encoding='unicode').split(" "))
    
    return sections

"""### Citation Schema

#### Section Name
"""

def verify_section(section_name, sections):
    for i in sections:
        if (i['title'] == section_name):
            return True
    else:
        return False

def check_section_name(section):
    section = section.lower()
    if (section == "introduction" or section == "intro"):
        return "Introduction"
    
    elif (section == "methods" or section == "methodology" or section== "method" or section == "materials & method" 
          or section == "materials and method" or section == "material and method" or section == "materials & methods" ):
        return "Method"
     
    elif (section == "results" or section == "result" or section == "conclusion"):
        return "Results"
    
    elif (section == "discussion" or section== "future work" or section == "future"):
        return "Discussion"
    
    else:
        return ''

def split_section_name(section):
    sec = section.split()
    
    for word in sec:
        section_name = check_section_name(word)
        if(section_name != ''):
            return section_name
    else:
        return ''

def get_section_name(section, sections):
    
    section_name = check_section_name(section)
    
    if(section_name != ''):
        return section_name
    
    elif (split_section_name(section) != ''):
        return split_section_name(section)

    else:
        for i in sections:
            if (i['title'].lower() == section.lower()):
                return i['section']

def get_section(citation, sections):
    section = citation.getparent().getparent()
    while True:
        if (section.tag != 'sec'):
            section = section.getparent()
            
        elif(verify_section(section[0].text, sections) == False):
            section = section.getparent()
            
        else:
            break
    
    section = get_section_name(section[0].text, sections)
    
    return section

"""#### Extraction of citation Text"""

def extract_Citation_Text(context, mark, citations_in_one_p):
    text = context.replace('al.', 'al')
    cit_text = nltk.sent_tokenize(text)

    citation_mark_ = mark.replace('al.', 'al')
    for sentence in cit_text:
        sentence_ = sentence.replace('(' , '')
        sentence_ = sentence_.replace(')', '')
        citation_mark_ = citation_mark_.replace('(', '')
        citation_mark_ = citation_mark_.replace(')', '')
        
        try:
            r = re.findall('.*' + citation_mark_ + '.*' , sentence_)
            if(len(r) >= 1):
                check = { 'text': sentence, 'citation': mark }
                if any(d == check for d in citations_in_one_p):
                    continue
                else:
                    #print("found")
                    return sentence
            
        except Exception as e:
            print("err:", e)
            continue

def extract_Citation_Schema(body, sections):
    citations_ref = body.xpath(".//xref")
    citations = []
    
    for i in citations_ref:
        if(i.attrib['ref-type'] == 'bibr'):
            citations.append(i)
    print(len(citations))
    citation_schema = []
    
    citations_in_one_p = []
    prev_context= None
    for citation in citations:            
        citation_mark = etree.tostring(citation, method='text', encoding='unicode')
        # try:
        #     citation_style = re.findall('(.+\d{4})', citation_mark)[0]
            
        # except:
        #     citation_style = citation_mark[:4]
            
        #Extracting the citation context
        context = etree.tostring(citation.getparent(), method='text', encoding='unicode') #citation paragraph
    
        #Extracting the citation section
        section = get_section(citation, sections) 
        
        #Extracting the full citation text
        text = extract_Citation_Text(context, citation.text, citations_in_one_p)
        
        #Checking the citations contain in one paragraph
        if (prev_context == None) or prev_context != context:
            prev_context = context
            citations_in_one_p = []
        else:
            citations_in_one_p.append({
                'text': text,
                'citation': citation.text
            })
            
        citation_id = citation.attrib['rid'].split()
        if len(citation_id) != 1:
            for ref in citation_id:
                citation_schema.append({
                    'reference_id': ref,
                    'citation_mark': citation.text,
                    'citation_section': section,
                    #'citation_context': context,
                    'citation_text': text,
                    'multi_citance': len(citation_id)
                })
        else:
            citation_schema.append({
                'reference_id': citation_id[0],
                'citation_mark': citation.text,
                'citation_section': section,
                #'citation_context': context,
                'citation_text': text,
                'multi_citance': 1
            })
            
    return citation_schema

def get_Citance_Count(citation_schema):
    counts = {}

    # Iterate through the list and update the counts dictionary
    for item in citation_schema:
        if item['citation_text'] != '':
            if item['citation_text'] in counts:
                counts[item['citation_text']] += 1
            else:
                counts[item['citation_text']] = 1

    # Iterate through the list and update the multi_citance field for each item based on the count in the counts dictionary
    for item in citation_schema:
        item['multi_citance'] = counts[item['citation_text']]

    return citation_schema

"""### Reference Schema"""

def get_Reference_DOI(reference):
    pub_ids = reference.findall(".//pub-id")

    doi = ''
    for id in pub_ids:
      if id.attrib['pub-id-type'] == 'doi':
        doi = id.text
        break
    # try:
    #     doi = etree.tostring(doi[0], method='text', encoding='unicode')
    # except:
    #     doi = ''
    
    reference_count = None
    if doi != '':
        crossref_response = requests.get('https://api.crossref.org/works/' + doi)
        if crossref_response.status_code != 404:
            reference_count = crossref_response.json()['message']['is-referenced-by-count']
    
    return reference_count, doi

def extract_Reference_Schema(body):
    references= body.xpath("//ref")
    reference_schema=[]
    for reference in references:
        try:
            article_title = reference.findall(".//article-title")
            article_title = etree.tostring(article_title[0], method='text', encoding='unicode')

        except:
            article_title = 'None'

        article_title = ' '.join(article_title.split())

        ref_author_name = ''
        ref_author = reference.findall('.//surname')
        for name in ref_author:
            try:
                ref_author_name += name.text + ', '
            except:
                break;
        
        reference_text = ''
        try:
            for ref_text in reference[1]:
                reference_text += etree.tostring(ref_text, method='text', encoding='unicode') + ' '
        except:
            reference_text = ''

        referenced_count, ref_doi = get_Reference_DOI(reference)
        #print(referenced_count)

        reference_text = re.sub(r"(\w)([A-Z])", r"\1 \2 ", reference_text)
        reference_full_text_split = ' '.join(reference_text.split())

        reference_schema.append({
        'id': reference.attrib['id'],
        'ref_doi': ref_doi,
        'ref_author': ref_author_name[:-2],
        'ref_text': reference_full_text_split,
        'ref_article_title': article_title,
        'is_referenced_count': referenced_count
    })
        
    return reference_schema

"""### Syntactic Analysis"""

def merge_Reference_Schema(citation_schema, reference_schema):
    for reference in reference_schema:
        reference['citations'] = []
        reference['syntactic_frequency'] = 0
        reference['polarity_score'] = 0
        reference['Introduction'] = 0
        reference['Method'] = 0
        reference['Results'] = 0
        reference['Discussion'] = 0
        reference['score'] = 0

        for citation in citation_schema:
            if(reference['id'] == citation['reference_id']):
                reference['citations'].append(citation)
                
                reference[citation['citation_section']] += 1
                
    for reference in reference_schema:
      if len(reference['citations']) == 0:
        reference_schema.remove(reference)
    return reference_schema

def find_Reference_Frequency(reference_schema):
    reference_frequencies = []
    for i in reference_schema:
        i['syntactic_frequency'] = len(i['citations'])
        reference_frequencies.append(len(i['citations']))
    
    ref_freq_median = np.median(reference_frequencies)
    ref_freq_3rd_quarter =  np.percentile(reference_frequencies, 75)
    
    return reference_schema, ref_freq_median, ref_freq_3rd_quarter

"""## Sentiment Analysis"""

def find_Sentiment(reference_schema):
    for reference in reference_schema:
        for citation in reference['citations']:
            if citation['citation_text'] is not None:
                sentiment = SENTIMENT_MODEL(citation['citation_text'])
                sentiment_score = 0
                if (sentiment[0]['label'] == 'LABEL_1'):
                    sentiment_score = 1
                elif (sentiment[0]['label'] == 'LABEL_2'):
                    sentiment_score = 2 * sentiment[0]['score']
                citation['sentiment'] = sentiment_score
            else:
                citation['sentiment'] = 0
            
            
    return reference_schema

"""### Scoring"""

def category(reference, quartile_one_third, quartile_two_third):
    if (reference['score'] <= quartile_one_third ):
        reference['scoring_category'] = "Least Important"

    elif (reference['score'] <= quartile_two_third):
        reference['scoring_category'] = "Important"

    else:
        reference['scoring_category'] = "Most Important"
    
    return reference['scoring_category']

def scoring(reference_schema, ref_freq_median, ref_freq_3rd_quarter):
    scores = []
    #Semantic Scoring
    for reference in reference_schema:
        total_citations = len(reference['citations'])
        if total_citations == 0:
          reference_schema.remove(reference)
          continue
        sentiment_score = 0
        for citation in reference['citations']:
            sentiment_score += citation['sentiment']
        
        reference['polarity_score'] = sentiment_score / total_citations
        reference['score'] = reference['polarity_score']
        
    
    #Syntactic Scoring
    for reference in reference_schema:
        syntactic = 0
        for citation in reference['citations']:
            syntactic += 1 / citation['multi_citance']
        if (syntactic < ref_freq_median):
            reference['score'] += 1

        elif (reference['syntactic_frequency'] < ref_freq_3rd_quarter):
            reference['score'] += 2

        else:
            reference['score'] += 3
        
        reference['syntactic_score'] = syntactic
            
    #IMRAD Scoring 
    for reference in reference_schema:
        imrad_score = reference['Introduction'] + (reference['Method'] * 2)  + (reference['Results'] * 1.5) + (reference['Discussion'] * 1.25)
       
        imrad_score /= reference['syntactic_frequency']
        reference['score'] += imrad_score
        
        scores.append(reference['score'])
    
    quartile_one_third = np.percentile(scores, 40)
    quartile_two_third = np.percentile(scores, 75)
    
    #Merging all scores    
    for reference in reference_schema:
        reference['scoring_category'] = category(reference, quartile_one_third, quartile_two_third)
    
    return reference_schema

"""### Open Article"""

def open_article(file_path): 
    article = open(file_path, 'r', encoding='utf-8')
    xml_parser = etree.XMLParser(remove_blank_text=True)
    xml_tree = etree.parse(file_path, xml_parser)
    front = xml_tree.xpath("//front")
    front = front[0]
    try:
        doi, title, journal, publisher, publish_date, authors, abstract = find_Metadata(front, xml_tree)
        body = xml_tree.xpath("//body")
        body = body[0]

        article_text_length, introduction_length, method_length, result_length, discussion_length = get_Article_Length(body)
        print("Article length found")

        sections = get_Article_Sections(body, introduction_length, method_length, result_length, discussion_length)

        citation_schema = extract_Citation_Schema(body, sections)
        print("Extracted Citation Schema")

        citation_schema = get_Citance_Count(citation_schema)

        reference_schema = extract_Reference_Schema(body)
        print("Extracted Reference Schema")

        reference_schema = merge_Reference_Schema(citation_schema, reference_schema)

        reference_schema, ref_freq_median, ref_freq_3rd_quarter = find_Reference_Frequency(reference_schema)

        print("Sentiment...")
        reference_schema = find_Sentiment(reference_schema)

        reference_schema = scoring(reference_schema, ref_freq_median, ref_freq_3rd_quarter)
        print("Scoring done")

        schema = {
        "doi": doi,
        "article_title": title,
        "abstract": abstract,
        "journal_title": journal,
        "publisher_name": publisher,
        "publish_date": publish_date,
        "article_authors": authors,
        #"total_citations": len(citation_schema),
        #"total_references": len(reference_schema),
        "references": reference_schema
        }
        return schema

    except Exception as e:
        print(e)
        return {'error': e.message}
  #return schema


# Commented out IPython magic to ensure Python compatibility.
# %%time
# import os
# 
# folder_path = 'dataset/'
# 
# for file_name in os.listdir(folder_path):
#     file_path = os.path.join(folder_path, file_name)
#     if os.path.isfile(file_path):
#         print("Article open: ", file_name)
#         try:
#           open_article(file_path)
#           print("Article succesfully uploaded.")
#           print("-----------------------------")
#         except:
#           print("Article failed: ", file_path)
#           print(traceback.format_exc())
#           continue
# #root = 'peerj-cs-490.xml'

# try:
#   schema = open_article('peerj-cs-490.xml')
# except:
#   print("Article failed:")



