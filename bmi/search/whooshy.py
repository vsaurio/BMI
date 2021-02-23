"""
 Copyright (C) 2021 Pablo Castells y Alejandro Bellogín

 Este código se ha implementado para la realización de las prácticas de
 la asignatura "Búsqueda y minería de información" de 4º del Grado en
 Ingeniería Informática, impartido en la Escuela Politécnica Superior de
 la Universidad Autónoma de Madrid. El fin del mismo, así como su uso,
 se ciñe a las actividades docentes de dicha asignatura.
"""

import whoosh
from whoosh.fields import Schema, TEXT, ID
from whoosh.formats import Format
from whoosh.qparser import QueryParser
from bmi.search.search import Searcher
from bmi.search.index import Index
from bmi.search.index import Builder
from bmi.search.index import TermFreq

# A schema in Whoosh is the set of possible fields in a document in
# the search space. We just define a simple 'Document' schema
Document = Schema(
        path=ID(stored=True),
        content=TEXT(vector=Format))

class WhooshBuilder(Builder):
    def build(self,collection):
        self.writer = whoosh.index.create_in(self.index_path, Document).writer()
        super().build(collection)

class WhooshIndex(Index):
    def __init__(self, index_path):
        self.index_path = index_path
        self.reader = whoosh.index.open_dir(self.index_path).reader()

    def all_terms(self):
        return list(self.reader.all_terms())

    def all_terms_with_freq(self):
        res = []
        for fieldname, term  in list(self.reader.all_terms()):
            freq = self.reader.frequency(fieldname, term)
            res.append((term.decode('utf-8'), freq))
        return res

    def total_freq(self,term):
        return self.reader.frequency("content", term)

    def doc_vector(self, doc_id):
        vector = []
        for termFreq in list(self.reader.vector_as("frequency", doc_id, "content")):
            vector.append(TermFreq(termFreq))
        return vector

    def doc_path(self,doc_id):
        return self.reader.stored_fields(doc_id)['path']

    def term_freq(self, term, doc_id):
        vector = self.reader.vector(doc_id, "content")
        vector.skip_to(term)
        return vector.value_as("frequency")

    def doc_freq(self,term):
        return self.reader.doc_frequency("content", term)

    def postings(self, term):
        return list(self.reader.postings("content", term).items_as("frequency"))

class WhooshSearcher(Searcher):
    def __init__(self, index_path):
        self.index_path = index_path

    def search(self, query, cutoff):
        index = whoosh.index.open_dir(self.index_path)
        searcher = index.searcher()
        qparser = QueryParser("content", schema=index.schema)
        search = []
        for docid, score in searcher.search(qparser.parse(query)).items():
           search.append((index.reader().stored_fields(docid)['path'], score))
        return search