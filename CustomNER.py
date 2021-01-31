import spacy
import random
import json
import os
import unidecode
import re
from spacy.gold import GoldParse
from spacy.scorer import Scorer
from spacy.util import decaying
from spacy.util import minibatch, compounding
import warnings

#FUNCION QUE LIMPIA EL DATASET
def trim_entity_spans(data: list) -> list:
    """Removes leading and trailing white spaces from entity spans.

    Args:
        data (list): The data to be cleaned in spaCy JSON format.

    Returns:
        list: The cleaned data.
    """
    invalid_span_tokens = re.compile(r'\s')

    cleaned_data = []
    for text, annotations in data:
        entities = annotations['entities']
        valid_entities = []
        for start, end, label in entities:
            valid_start = start
            valid_end = end
            while valid_start < len(text) and invalid_span_tokens.match(
                    text[valid_start]):
                valid_start += 1
            while valid_end > 1 and invalid_span_tokens.match(
                    text[valid_end - 1]):
                valid_end -= 1
            valid_entities.append([valid_start, valid_end, label])
        cleaned_data.append([text, {'entities': valid_entities}])

    return cleaned_data

#NOMBRE DEL MODELO A CREAR
modelfile = "NERModel"

#DEFINO EL PATH DEL DATASET
dirname = os.path.dirname(__file__)         #path de la carpeta actual
filename1 = "Datasets\marginal031220.json1"   #nombre del archivo
filepath1 = os.path.join(dirname, filename1)  #path del dataset  1     

#CARGO EL DATASET
train_data = []
for line in open(filepath1, encoding="utf8"):
    train_data.append(json.loads(line))

#ME QUEDO CON LAS PARTES DEL DATASET QUE QUIERO (TEXT Y LABELS)
TRAIN_DATA = []
for data in train_data:
	ents = [tuple(entity) for entity in data['labels']]
	TRAIN_DATA.append((data['text'],{'entities':ents} )) 
       
#DESCARTO LAS FRASES QUE NO TIENEN ETIQUETA
TRAIN_DATA_FINAL=[]
for data in TRAIN_DATA:
    if len(data[1]['entities'])!=0:
        TRAIN_DATA_FINAL.append(data)

#LIMPIO EL DATASET PARA QUE SPACY PUEDA USARLO CORRECTAMENTE
TRAIN_DATA_FINAL = trim_entity_spans(TRAIN_DATA_FINAL)

#DIVIDO EL DATASET EN 2 PARTES, UNA PARA ENTRENAR Y LA OTRA PARA TESTEAR
from sklearn.model_selection import train_test_split
X_train, X_test = train_test_split(TRAIN_DATA_FINAL,  test_size=0.20)

#FUNCION QUE ENTRENA EL NER DE UN MODELO
def train_spacy(model,data,iterations):
    TRAIN_DATA = data

    #Verifico si el modelo existe, sino creo uno desde 0
    if model is not None:
        nlp = spacy.load(model)  
        print("Se cargo el modelo '%s'" % model)
    else:
        nlp = spacy.blank('es')  
        print("Se creo un modelo en español")
    
    # create the built-in pipeline components and add them to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner, last=True)
    else:
        ner = nlp.get_pipe("ner")   

    #agrego las etiquetas
    for _, annotations in TRAIN_DATA:
         for ent in annotations.get('entities'):
            ner.add_label(ent[2])

    #Si cree el modelo, comienzo a entrenar desde el principio, sino continuo en donde deje
    if model is None:
      optimizer = nlp.begin_training()
    else:
      optimizer = nlp.resume_training()

    # solo entreno el ner del modelo
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes) and warnings.catch_warnings():  
        warnings.filterwarnings("once", category=UserWarning, module='spacy')

        #Entreno el modelo segun el numero de iteraciones
        sizes = compounding(4.0, 32, 1.001)
        for itn in range(iterations):
            print("Starting iteration " + str(itn))
            random.shuffle(TRAIN_DATA)
            losses = {}
            batches = minibatch(TRAIN_DATA, size=sizes)
            for batch in batches:
                text, annotations = zip(*batch)
                nlp.update(
                    text,  # batch of texts
                    annotations,  # batch of annotations
                    drop=0.30,  # dropout - make it harder to memorise data
                    sgd=optimizer,  # callable to update weights
                    losses=losses)
            print(losses)
    return nlp


#LLAMO A LA FUNCION QUE ENTRENA EL NER CON EL DATASET CARGADO
ner = train_spacy(None, X_train, 10)

# GUARDO EL MODELO EN EL DISCO
ner.to_disk(modelfile)

#VEO QUE TAN PRECISO ES EL ALGORITMO
def evaluate(ner_model, examples):
    """
    Params
    ner_model : Spacy ner model
    examples : test data to evaluate on
    Returns
    scores : dict containing precision, reacall and f-score
    count : count of total test_data that was evaluate on
    """
    scorer = Scorer()
    count_error_data = 0
    for input_, annot in examples:
        try:
            doc_gold_text = ner_model.make_doc(input_)
            gold = GoldParse(doc_gold_text, entities=annot['entities'])
            pred_value = ner_model(input_)
            scorer.score(pred_value, gold)
            
        except ValueError as e:
            count_error_data +=1
            pass
    return scorer.scores, len(examples)-count_error_data

evaluate(ner,X_test)












#<--- OPCIONAL -->

#TESTEO EL MODELO
test_text = input("Enter your testing text: ")
print("TEXTO: ", test_text)
doc = prdnlp(nlp(test_text))
salida="["
salida2=[]
for ent in doc.ents:
    print("ENTIDAD: ", ent.text)
    print("TIPO: ", ent.label_)
    salida+=ent.label_+", "
    salida2.append(ent.label_)
salida+="]\n"

#Guardo la salida en un txt
f= open("NER_Output.txt","a+")
f.write(salida) 
f.close()




