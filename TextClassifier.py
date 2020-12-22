from __future__ import unicode_literals, print_function
import plac
import random
from pathlib import Path
import thinc.extra.datasets

import spacy
from spacy.util import minibatch, compounding

import pandas as pd

#NOMBRE DEL MODELO A CREAR
modelfile = "TEXTCATTestModel"

#CARGO EL DATASET
train_data = pd.read_csv('TEXTCAT dataset - 1000 datos.csv', usecols=['label', 'text'])

#LE DOY EL FORMATO ADECUADO AL DATASET
TRAIN_DATA = []
for index, data in train_data.iterrows():
    if data['label'] == 47: #muy inseguro
      TRAIN_DATA.append((data['text'],{'cats': {'Muy Inseguro': True, 'Inseguro': False, 'Seguro':False, 'Muy Seguro':False} })) 
    else: 
      if data['label'] == 48: #inseguro
        TRAIN_DATA.append((data['text'],{'cats': {'Muy Inseguro': False, 'Inseguro': True, 'Seguro':False, 'Muy Seguro':False} }))  
      else :
        if data['label'] == 49: #seguro
          TRAIN_DATA.append((data['text'],{'cats': {'Muy Inseguro': False, 'Inseguro': False, 'Seguro':True, 'Muy Seguro':False} })) 
        else: 
          if data['label'] == 50: #muy seguro
            TRAIN_DATA.append((data['text'],{'cats': {'Muy Inseguro': False, 'Inseguro': False, 'Seguro':False, 'Muy Seguro':True} })) 

    

#DIVIDO EL DATASET EN 2 PARTES, UNA PARA ENTRENAR Y LA OTRA PARA TESTEAR
from sklearn.model_selection import train_test_split
X_train, X_test = train_test_split(TRAIN_DATA,  test_size=0.20, random_state=0)

X_test_text, X_test_cats = zip(*X_test)
"""
mins=0
ins=0
seg=0
for x in X_test:
    if x[1]['cats']['Muy Inseguro']:
        mins +=1
    else:
        if x[1]['cats']['Inseguro']:
            ins +=1
        else:
             if x[1]['cats']['Seguro']:
                seg +=1

print(mins)
print(ins)
print(seg)
"""


#EVALUA LA PRECISION DEL MODELO
def evaluate(tokenizer, textcat, texts, cats):
    docs = (tokenizer(text) for text in texts)
    tp = 0.0  # True positives
    fp = 1e-8  # False positives
    fn = 1e-8  # False negatives
    tn = 0.0  # True negatives
    for i, doc in enumerate(textcat.pipe(docs)):
        gold = cats[i]['cats']
        for label, score in doc.cats.items():
            if label not in gold:
                continue            
            if score >= 0.5 and gold[label] >= 0.5:
                tp += 1.0
            elif score >= 0.5 and gold[label] < 0.5:
                fp += 1.0
            elif score < 0.5 and gold[label] < 0.5:
                tn += 1
            elif score < 0.5 and gold[label] >= 0.5:
                fn += 1
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    if (precision + recall) == 0:
        f_score = 0.0
    else:
        f_score = 2 * (precision * recall) / (precision + recall)
    return {"textcat_p": precision, "textcat_r": recall, "textcat_f": f_score}


#FUNCION QUE ENTRENA EL TEXTCAT DE UN MODELO
def train_spacy(model,data,iterations):
    TRAIN_DATA = data

    #Verifico si el modelo existe, sino creo uno desde 0
    if model is not None:
        nlp = spacy.load(model)  
        print("Se cargo el modelo '%s'" % model)
    else:
        nlp = spacy.blank('es') 
        print("Se creo un modelo en español")

    #Inicializo textcat 
    if 'textcat' not in nlp.pipe_names:
        textcat = nlp.create_pipe("textcat")
        nlp.add_pipe(textcat, last=True) 
    else:
        textcat = nlp.get_pipe("textcat")   

    #Agrego las categorias
    textcat.add_label('Muy Inseguro')
    textcat.add_label('Inseguro')
    textcat.add_label('Seguro')
    textcat.add_label('Muy Seguro')

    #Solo entreno el textcat del modelo
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'textcat']
    with nlp.disable_pipes(*other_pipes):  # only train textcat
      
        #Si cree el modelo, comienzo a entrenar desde el principio, sino continuo en donde deje
        if model is None:
            optimizer = nlp.begin_training()
        else:
            optimizer = nlp.resume_training()

        #Entreno el modelo en base al numero de iteraciones
        print("Training the model...")
        print("{:^5}\t{:^5}\t{:^5}\t{:^5}".format("LOSS", "P", "R", "F"))
        batch_sizes = compounding(4.0, 32.0, 1.001)
        for i in range(iterations):
            losses = {}
            # batch up the examples using spaCy's minibatch
            random.shuffle(TRAIN_DATA)
            batches = minibatch(TRAIN_DATA, size=batch_sizes)
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(texts, annotations, sgd=optimizer, drop=0.2, losses=losses)
            with textcat.model.use_params(optimizer.averages):
                # evaluate on the dev data split off in load_data()
                scores = evaluate(nlp.tokenizer, textcat, X_test_text, X_test_cats)
            print(
                "{0:.3f}\t{1:.3f}\t{2:.3f}\t{3:.3f}".format(  # print a simple table
                    losses["textcat"],
                    scores["textcat_p"],
                    scores["textcat_r"],
                    scores["textcat_f"],
                )
            )
    return nlp

#LLAMO A LA FUNCION CON EL DATASET QUE TENGO
prdnlp = train_spacy(None, X_train, 30)

# GUARDO EL MODELO EN EL DISCO
prdnlp.to_disk(modelfile)


#<--- OPCIONAL --->

#TESTEO EL MODELO
test_text = input("Enter your testing text: ")
print("TEXTO: ", test_text)
textcat = spacy.load(modelfile)
doc = textcat(test_text)
print(doc.cats)
if doc.cats['Inseguro'] < 0.4:
    print("CATEGORIA: Seguro")
else:
    print("CATEGORIA: Inseguro")

print(doc.cats)
if doc.cats['Seguro'] > doc.cats['Inseguro']:
    print("CATEGORIA: Seguro")
else: 
    print("CATEGORIA: Inseguro")



