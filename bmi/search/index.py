"""
 Copyright (C) 2021 Pablo Castells y Alejandro Bellogín

 Este código se ha implementado para la realización de las prácticas de
 la asignatura "Búsqueda y minería de información" de 4º del Grado en
 Ingeniería Informática, impartido en la Escuela Politécnica Superior de
 la Universidad Autónoma de Madrid. El fin del mismo, así como su uso,
 se ciñe a las actividades docentes de dicha asignatura.
"""
from urllib.request import urlopen
from bs4 import BeautifulSoup
import os, os.path
import zipfile
import shutil

class TermFreq():
    def __init__(self, t):
        self.info = t
    def term(self):
        return self.info[0]
    def freq(self):
        return self.info[1]


class Index:
    def __init__(self, index_path):
        self.index_path = index_path

class Builder:
    def __init__(self, index_path):
        self.index_path = index_path
        if os.path.exists(index_path): 
            shutil.rmtree(index_path)
        os.makedirs(index_path)

    def process_files(self, collection_path):
        if os.path.isfile(collection_path):
            with open(collection_path, encoding = 'utf-8') as f:
                for url in f:
                    self.writer.add_document(path=url, content=BeautifulSoup(urlopen(url).read(), "lxml").text)

    def build(self,collection_path):
        files = []
        if os.path.isdir(collection_path):
            files = os.listdir(collection_path)
        elif zipfile.is_zipfile(collection_path):
            with ZipFile(collection_path) as myzip:
                files = myzip.namelist()
        else:
            files.append(collection_path)

        for file in files:
            self.process_files(file)

    def commit(self):
        self.writer.commit()

