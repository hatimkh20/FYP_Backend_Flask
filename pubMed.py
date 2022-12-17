from lxml import etree
import numpy as np
import pandas as pd
import json
from nltk import tokenize
import nltk
import string
import math
import pprint
import re


# metadata

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
    journal_title = front.findall('.//journal-title')
    return journal_title[0].text


def find_Publisher(front):
    publisher_name = front.findall('.//publisher-name')
    return publisher_name[0].text


def find_Publish_Date(front):
    pub_date = front.findall('.//history')[0]

    for date in pub_date:
        if(date.attrib['date-type'] == 'accepted'):
            pub_date = date

    published_date = ''
    for pub in pub_date:
        published_date += pub.text + '-'

    return published_date[:-1]


def find_Authors(front):
    article_author = front.findall('.//contrib')
    article_authors = []
    for i in article_author:
        if i.attrib['contrib-type'] == 'author':
            article_authors.append(i)

    author_names = ''
    for name in article_authors:
        author = name.findall(".//name")[0]

        for author_name in author:
            author_names += author_name.text + ' '
        author_names += ', '

    author_names = author_names[:-2]
    return author_names


def find_Abstract(front):
    abstract = xml_tree.xpath(".//abstract")[0]
    abstract = etree.tostring(abstract, method='text', encoding='unicode')
    return abstract


def find_Metadata(front):
    doi = find_DOI(front[1])
    title = find_Title(front)
    journal = find_Journal(front)
    publisher = find_Publisher(front)
    publish_date = find_Publish_Date(front)
    authors = find_Authors(front)
    abstract = find_Abstract(front)

    return doi, title, journal, publisher, publish_date, authors, abstract

# Article Section Lengths


def get_Article_Length(body):
    full_article_text = etree.tostring(body, method='text', encoding='unicode')
    article_text_length = len(full_article_text.split(" "))

    introduction_length = round(article_text_length/100) * 25
    method_length = round(article_text_length/100) * 50
    result_length = round(article_text_length/100) * 75
    discussion_length = round(article_text_length/100) * 100

    return article_text_length, introduction_length, method_length, result_length, discussion_length


def get_Article_Sections(body):
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
        c_sum += len(etree.tostring(i, method='text',
                     encoding='unicode').split(" "))

    return sections


# Citation Schema

# ------section name

def verify_section(section_name):
    for i in sections:
        if (i['title'] == section_name):
            return True
    else:
        return False


def check_section_name(section):
    section = section.lower()
    if (section == "introduction" or section == "intro"):
        return "Introduction"

    elif (section == "methods" or section == "methodology" or section == "method" or section == "materials & method"
          or section == "materials and method" or section == "material and method" or section == "materials & methods"):
        return "Method"

    elif (section == "results" or section == "result" or section == "conclusion"):
        return "Results"

    elif (section == "discussion" or section == "future work" or section == "future"):
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


def get_section_name(section):

    section_name = check_section_name(section)

    if(section_name != ''):
        return section_name

    elif (split_section_name(section) != ''):
        return split_section_name(section)

    else:
        for i in sections:
            if (i['title'].lower() == section.lower()):
                return i['section']


def get_section(citation):
    section = citation.getparent().getparent()
    while True:
        if (section.tag != 'sec'):
            section = section.getparent()

        elif(verify_section(section[0].text) == False):
            section = section.getparent()

        else:
            break

    section = get_section_name(section[0].text)

    return section


# -----Extraction of citation Text


def extract_Citation_Text(context, mark):
    text = context.replace('al.', 'al')
    cit_text = nltk.sent_tokenize(text)

    citation_mark_ = mark.replace('al.', 'al')

    for sentence in cit_text:
        sentence_ = sentence.replace('(', '')
        citation_mark_ = citation_mark_.replace('(', '')

        try:
            r = re.findall('.*' + citation_mark_ + '.*', sentence_)
            if(len(r) >= 1):
                return sentence

        except:
            continue


def extract_Citation_Schema(body):
    citations_ref = body.xpath(".//xref")
    citations = []

    for i in citations_ref:
        if(i.attrib['ref-type'] == 'bibr'):
            citations.append(i)

    citation_schema = []

    for citation in citations:
        citation_mark = citation.getchildren()
        citation_mark = etree.tostring(
            citation, method='text', encoding='unicode')

        try:
            citation_style = re.findall('(.+\d{4})', citation_mark)[0]

        except:
            citation_style = citation_mark[:4]

        context = etree.tostring(citation.getparent(
        ), method='text', encoding='unicode')  # citation paragraph

        section = get_section(citation)  # section

        text = extract_Citation_Text(context, citation_style)

        citation_schema.append({
            'reference_id': citation.attrib['rid'],
            'citation_mark': citation_style,
            'citation_section': section,
            'citation_context': context,
            'citation_text': text
        })

    return citation_schema

# -----Reference Schema


def extract_Reference_Schema(body):
    references = body.xpath("//ref")
    reference_schema = []
    for reference in references:
        try:
            article_title = reference.findall(".//article-title")
            article_title = etree.tostring(
                article_title[0], method='text', encoding='unicode')

        except:
            article_title = 'None'

        article_title = ' '.join(article_title.split())

        ref_author_name = ''
        ref_author = reference.findall('.//surname')
        for name in ref_author:
            try:
                ref_author_name += name.text + ', '
            except:
                break

        reference_text = ''
        for ref_text in reference[1]:
            reference_text += etree.tostring(ref_text,
                                             method='text', encoding='unicode') + ' '

        reference_text = re.sub(r"(\w)([A-Z])", r"\1 \2 ", reference_text)
        reference_full_text_split = ' '.join(reference_text.split())

        reference_schema.append({
            'id': reference.attrib['id'],
            'ref_author': ref_author_name[:-2],
            'ref_text': reference_full_text_split,
            'ref_article_title': article_title,
        })

    return reference_schema


# ---Syntactic Analysis

def merge_Reference_Schema(citation_schema, reference_schema):
    for reference in reference_schema:
        reference['citations'] = []
        reference['syntactic_frequency'] = 0
        reference['semantic_positive'] = 0
        reference['semantic_negative'] = 0
        reference['Introduction'] = 0
        reference['Method'] = 0
        reference['Results'] = 0
        reference['Discussion'] = 0
        reference['score'] = 0

        for citation in citation_schema:

            if(reference['id'] == citation['reference_id']):
                reference['citations'].append(citation)

                reference[citation['citation_section']] += 1

    return reference_schema


def find_Reference_Frequency(reference_schema):
    for i in reference_schema:
        i['syntactic_frequency'] = len(i['citations'])

    return reference_schema


# ----Scoring


def category(reference):
    if (reference['score'] <= 1.25):
        reference['scoring-category'] = "Least Important"

    elif (reference['score'] < 2):
        reference['scoring-category'] = "Important"

    else:
        reference['scoring-category'] = "Most Important"

    return reference['scoring-category']


def scoring(reference_schema):
    avg_ref_per_citations = len(citation_schema) / len(reference_schema)
    avg_ref_per_citations = avg_ref_per_citations

    # Syntactic Scoring
    for reference in reference_schema:
        if (reference['syntactic_frequency'] < avg_ref_per_citations):
            reference['score'] = 1

        elif (reference['syntactic_frequency'] < avg_ref_per_citations * 2):
            reference['score'] = 1.5

        else:
            reference['score'] = 2

    # IMRAD Scoring
    for reference in reference_schema:
        imrad_score = reference['Introduction'] + (reference['Method'] * 1.5) + (
            reference['Results'] * 1.5) + (reference['Discussion'] * 1.25)
        imrad_score /= reference['syntactic_frequency']

        reference['score'] *= imrad_score

        reference['scoring-category'] = category(reference)

    return reference_schema


# ----Open Article

root = 'peerj-cs-421.xml'
article = open(root, 'r', encoding='utf-8')
xml_parser = etree.XMLParser(remove_blank_text=True)
xml_tree = etree.parse(root, xml_parser)

front = xml_tree.xpath("//front")
front = front[0]

try:
    doi, title, journal, publisher, publish_date, authors, abstract = find_Metadata(
        front)
except Exception as e:
    print(e)


body = xml_tree.xpath("//body")
body = body[0]

article_text_length, introduction_length, method_length, result_length, discussion_length = get_Article_Length(
    body)

sections = get_Article_Sections(body)

citation_schema = extract_Citation_Schema(body)

reference_schema = extract_Reference_Schema(body)

reference_schema = merge_Reference_Schema(citation_schema, reference_schema)

reference_schema = find_Reference_Frequency(reference_schema)

reference_schema = scoring(reference_schema)

schema = {
    "doi": doi,
    "article_title": title,
    "abstract": abstract,
    "journal_title": journal,
    "publisher_name": publisher,
    "publish_date": publish_date,
    "article_authors": authors,
    "total_citations": len(citation_schema),
    "total_references": len(reference_schema),
    "references": reference_schema
}


# --JSON SCHEMA
with open("data.json", 'w', encoding='utf-8') as f:
    json.dump(schema, f, ensure_ascii=False, default=str)
    df = pd.DataFrame(reference_schema)
