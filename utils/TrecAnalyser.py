import os, lucene, sys
import xml.etree.ElementTree as ET

from lxml import etree
from nltk.stem import WordNetLemmatizer

from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import \
    FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions

from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader, Term
from org.apache.lucene.queryparser.classic import QueryParser, MultiFieldQueryParser, QueryParserBase
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.analysis.en import EnglishAnalyzer
from org.apache.lucene.search.similarities import BM25Similarity, TFIDFSimilarity, ClassicSimilarity, DFISimilarity
from org.apache.lucene.analysis import LowerCaseFilter, StopFilter, TokenFilter
from org.apache.lucene.analysis.en import PorterStemFilter, KStemFilter
from org.apache.lucene.analysis.standard import StandardTokenizer
from org.apache.lucene.analysis.tokenattributes import CharTermAttribute

from org.apache.pylucene.analysis import PythonAnalyzer
from org.apache.pylucene.analysis import PythonTokenFilter
import gensim.downloader as api

INDEX_DIR = "Index/IndexFiles"
word_vectors = api.load("glove-wiki-gigaword-100")


class Indexer(object):

    def __init__(self, root, storeDir, analyzer):
        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        store = SimpleFSDirectory(Paths.get(storeDir))
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)
        indexDocs(root, writer)
        writer.commit()
        writer.close()
        print("indexer")


def indexDocs(root, writer):
    nDocs = 0
    for filename in os.listdir(root):
        if not filename.endswith('.gz'):
            documents = get_document(root + filename)
            for doc in documents:
                writer.addDocument(doc)
                nDocs += 1
    print(nDocs, ' Files indexed correctly')


def get_document(path):
    with open(path, encoding='latin-1') as f:
        xml = f.read()
    parser = etree.XMLParser(recover=True)
    root = ET.fromstring("<root>" + xml + "</root>", parser)
    docTexts = []

    t1 = FieldType()
    t1.setStored(True)
    t1.setTokenized(False)
    t1.setIndexOptions(IndexOptions.DOCS_AND_FREQS)

    t2 = FieldType()
    t2.setStored(True)
    t2.setTokenized(True)
    t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

    for document in root.findall('DOC'):
        doc = Document()
        path_doc = 'Documents/' + str(document.find('DOCNO').text)[1:-1] + '.txt'
        doc.add(Field("docno", document.find('DOCNO').text, t1))
        doc.add(Field("fileID", document.find('FILEID').text, t1))
        filed = ['FIRST', 'SECOND', 'HEAD', 'DATELINE',
                 'BYLINE', 'NOTE', 'TEXT']

        for element in filed:
            res = ""
            for f in document.findall(element):
                if f.text is not None:
                    res = res + " " + f.text
            if element in ['FIRST', 'SECOND']:
                doc.add(Field(element.lower(), res, t1))
            else:
                doc.add(Field(element.lower(), res, t2))

            doc.add(Field("path", os.path.abspath(path_doc), t1))

        docTexts.append(doc)

    return docTexts


def run(searcher, analyzer, command, improve, nomber):
    query = QueryParser("text", analyzer).parse(command)
    if improve is 2:
        string = query.toString()
        command = ""
        for word in string.split('text:'):
            command = command + " " + word
        command = expand_query_with_word2vec(command)
        # print("the expanded query ", command)
        query = QueryParser("text", analyzer).parse(command)

    if improve is 1:
        string = query.toString()
        command = ""
        for word in string.split('text:'):
            command = command + " " + word
        command = expand_query_with_wordnet(command)
        # print("the expanded query ", command)
        query = QueryParser("text", analyzer).parse(command)

    scoreDocs = searcher.search(query, 242918).scoreDocs

    documents = []
    i = 1
    for scoreDoc in scoreDocs:
        context = []
        doc = searcher.doc(scoreDoc.doc)
        context.append(doc.get('docno'))
        context.append(doc.get('head'))
        context.append(doc.get('path'))
        context.append(doc.get('text'))
        context.append(scoreDoc.score)
        context.append(i)
        i = i + 1

        documents.append(context)
    return documents


def getAnalyser(type):
    # pas de pretraitement
    if type == 0:
        return WhitespaceAnalyzer()

    # supprimer les stops words
    if type == 1:
        return StandardAnalyzer()

    # PorterStemmerAnalyzer
    if type == 2:
        return PorterStemmerAnalyzer()

    # KrovetzStemmerAnalyzer
    if type == 3:
        return KrovetzStemmerAnalyzer()

    # LemmatizerAnalyzer
    if type == 4:
        return LemmatizerAnalyser()

    # StandardTokenizer, StandardFilter, EnglishPossessiveFilter,
    # LowerCaseFilter, StopFilter, and PorterStemFilter. without lemmatization
    if type == 5:
        return EnglishAnalyzer()


def getSearcher(type, searcher):
    if type == 0:
        searcher.setSimilarity(ClassicSimilarity())

    if type == 1:
        searcher.setSimilarity(BM25Similarity())


def launch_lucene():
    vm_env = lucene.getVMEnv()

    if vm_env is None:
        vm_env = lucene.initVM(vmargs=['-Djava.awt.headless=true'])
        # nltk.download('wordnet')

    assert vm_env is not None
    vm_env.attachCurrentThread()


def search(query, cleaning, similarty, improve):
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    analyzer = getAnalyser(cleaning)
    path = INDEX_DIR + str(cleaning) + ".index"
    if not os.path.exists(path):
        Indexer(base_dir + '/AP/', os.path.join(base_dir, path), analyzer)

    directory = SimpleFSDirectory(Paths.get(os.path.join(base_dir, path)))
    searcher = IndexSearcher(DirectoryReader.open(directory))
    getSearcher(similarty, searcher)
    documents = run(searcher, analyzer, query, improve, 1000)
    del searcher
    return documents


class PorterStemmerAnalyzer(PythonAnalyzer):

    def createComponents(self, fieldName):
        source = StandardTokenizer()
        filter = LowerCaseFilter(source)
        filter = PorterStemFilter(filter)
        filter = StopFilter(filter, EnglishAnalyzer.ENGLISH_STOP_WORDS_SET)

        return self.TokenStreamComponents(source, filter)

    def initReader(self, fieldName, reader):
        return reader


class KrovetzStemmerAnalyzer(PythonAnalyzer):
    def createComponents(self, fieldName):
        source = StandardTokenizer()
        filter = LowerCaseFilter(source)
        filter = KStemFilter(filter)
        filter = StopFilter(filter, EnglishAnalyzer.ENGLISH_STOP_WORDS_SET)

        return self.TokenStreamComponents(source, filter)

    def initReader(self, fieldName, reader):
        return reader


class LemmatizerAnalyser(PythonAnalyzer):

    def createComponents(self, fieldName):
        source = StandardTokenizer()
        filter = LowerCaseFilter(source)
        filter = StopFilter(filter, EnglishAnalyzer.ENGLISH_STOP_WORDS_SET)
        filter = LemmatizerFilter(filter)

        return self.TokenStreamComponents(source, filter)

    def initReader(self, fieldName, reader):
        return reader


class LemmatizerFilter(PythonTokenFilter):

    def __init__(self, input):
        super(LemmatizerFilter, self).__init__(input)
        self.input = input
        self.termAtt = self.addAttribute(CharTermAttribute.class_)

    def incrementToken(self):
        if self.input.incrementToken():
            text = self.termAtt.toString()
            self.termAtt.setEmpty()
            self.termAtt.append(self.lemmatize(text))
            return True

        return False

    def lemmatize(self, text):
        lemmatizer = WordNetLemmatizer()

        return lemmatizer.lemmatize(text)


def expand_query_with_word2vec(query):
    expanded = ""

    for word in query.split(' '):
        if word in word_vectors:
            expanded = expanded + expand_token_w2c(word.lower())

    return query + expanded


def expand_token_w2c(token):
    words = word_vectors.similar_by_word(token)[0:1]
    query = ""
    for word in words:
        query = query + " " + word[0]
    # print(token, query)

    return query


def expand_query_with_wordnet(query):
    expanded = ""

    for word in query.split(' '):
        if word in word_vectors:
            expanded = expanded + expand_token_wn(word.lower())
            expanded = expanded.replace("/", " ")

    return query + expanded


def expand_token_wn(token):
    from nltk.corpus import wordnet

    query = ""
    for syn in wordnet.synsets(token)[0:1]:
        for l in syn.lemmas():
            query = query + " " + l.name()
            if l.antonyms():
                query = query + " " + l.antonyms()[0].name()

    # print(token, query)

    return query
