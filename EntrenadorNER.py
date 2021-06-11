import spacy
import random
import json
import os
import unidecode
import re
from spacy.gold import GoldParse
from spacy.scorer import Scorer
from spacy.util import minibatch, compounding
import warnings

class EntrenadorNER(object):
    modelo = "NERModel"
    ubicacionArchivo = os.path.dirname(__file__)
    nombreArchivo = "Datasets\marginal031220.json1"
    direccionCompletaArchivo = os.path.join(ubicacionArchivo, nombreArchivo)

    def __init__(self):
        super(EntrenadorNER, self).__init__()
        train_data = []
        for line in open(self.direccionCompletaArchivo, encoding="utf8"):
            train_data.append(json.loads(line))

        train_data_aux = []
        for data in train_data:
            ents = [tuple(entity) for entity in data['labels']]
            train_data_aux.append((data['text'],{'entities':ents} )) 
            
        train_data_final=[]
        for data in train_data_aux:
            if len(data[1]['entities'])!=0:
                train_data_final.append(data)

        train_data_final = self.limpiarDataset(train_data_final)

        #DIVIDO EL DATASET EN 2 PARTES, UNA PARA ENTRENAR Y LA OTRA PARA TESTEAR
        from sklearn.model_selection import train_test_split
        X_train, X_test = train_test_split(train_data_final,  test_size=0.20)

        ner = self.entrenarModeloNer(None, X_train, 10)

        ner.to_disk(self.modelo)

        self.obtenerPrecision(ner,X_test)

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

        f= open("NER_Output.txt","a+")
        f.write(salida) 
        f.close()

        
    def limpiarDataset(self, data: list) -> list:
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

    def entrenarModeloNer(self,model,data,iterations):
        train_data = data

        #Verifico si el modelo existe, sino creo uno desde 0
        if model is not None:
            nlp = spacy.load(model)  
            print("Se cargo el modelo '%s'" % model)
        else:
            nlp = spacy.blank('es')  
            print("Se creo un modelo en español")
        
        if 'ner' not in nlp.pipe_names:
            ner = nlp.create_pipe('ner')
            nlp.add_pipe(ner, last=True)
        else:
            ner = nlp.get_pipe("ner")   

        #Agrego las etiquetas
        for _, annotations in train_data:
            for ent in annotations.get('entities'):
                ner.add_label(ent[2])

        #Si cree el modelo, comienzo a entrenar desde el principio, sino continuo en donde deje
        if model is None:
            optimizer = nlp.begin_training()
        else:
            optimizer = nlp.resume_training()

        other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
        with nlp.disable_pipes(*other_pipes) and warnings.catch_warnings():  
            warnings.filterwarnings("once", category=UserWarning, module='spacy')

            #Entreno el modelo segun el numero de iteraciones
            sizes = compounding(4.0, 32, 1.001)
            for itn in range(iterations):
                print("Starting iteration " + str(itn))
                random.shuffle(train_data)
                losses = {}
                batches = minibatch(train_data, size=sizes)
                for batch in batches:
                    text, annotations = zip(*batch)
                    nlp.update(
                        text,
                        annotations,
                        drop=0.30,
                        sgd=optimizer,
                        losses=losses)
                print(losses)
        return nlp

    def obtenerPrecision(ner_model, examples):
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

entrenador = EntrenadorNER()