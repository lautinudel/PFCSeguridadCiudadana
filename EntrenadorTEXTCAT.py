from __future__ import unicode_literals, print_function
import plac
import random
from pathlib import Path
import thinc.extra.datasets
import spacy
from spacy.util import minibatch, compounding
import pandas as pd
from sklearn.model_selection import train_test_split
from spacy.gold import GoldParse
from spacy.scorer import Scorer

class EntrenadorTEXTCAT(object):
    modelo = "TEXTCATModel"
    datasetDeEntrenamiento = pd.read_csv('Datasets\TEXTCAT dataset - 1000 datos - 261120.csv', usecols=['label', 'text'])
    
    def __init__(self):
        super(EntrenadorTEXTCAT, self).__init__()

        train_data_aux = []

        for index, data in self.datasetDeEntrenamiento.iterrows():
            if data['label'] == 108: #muy inseguro
                train_data_aux.append((data['text'],{'cats': {'Muy Inseguro': True, 'Inseguro': False, 'Seguro':False, 'Muy Seguro':False} })) 
            else: 
                if data['label'] == 107: #inseguro
                    train_data_aux.append((data['text'],{'cats': {'Muy Inseguro': False, 'Inseguro': True, 'Seguro':False, 'Muy Seguro':False} }))  
                else :
                    if data['label'] == 109: #seguro
                        train_data_aux.append((data['text'],{'cats': {'Muy Inseguro': False, 'Inseguro': False, 'Seguro':True, 'Muy Seguro':False} })) 
                    else: 
                        if data['label'] == 110: #muy seguro
                            train_data_aux.append((data['text'],{'cats': {'Muy Inseguro': False, 'Inseguro': False, 'Seguro':False, 'Muy Seguro':True} })) 
            pass

        X_train, X_test = train_test_split(train_data_aux,  test_size=0.20, random_state=0)
        X_test_text, X_test_cats = zip(*X_test)
        self.datasetDeEntrenamientoTexto = X_test_text
        self.datasetDeEntrenamientoEtiquetas = X_test_cats

        prdnlp = self.entrenarModeloTextcat(None, X_train, 30)

        prdnlp.to_disk(self.modelo)

        self.obtenerPrecisionPorCategoria(prdnlp,X_test)

        #<--- OPCIONAL --->

        #TESTEO EL MODELO
        test_text = input("Ingrese texto de prueba: ")
        print("TEXTO: ", test_text)
        textcat = spacy.load(self.modelo)
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
        pass

    def entrenarModeloTextcat(self, model, data, iterations):
        TRAIN_DATA = data

        if model is not None:
            nlp = spacy.load(model)  
            print("Se cargo el modelo '%s'" % model)
        else:
            nlp = spacy.blank('es') 
            print("Se creo un modelo en español")

        if 'textcat' not in nlp.pipe_names:
            textcat = nlp.create_pipe("textcat", config={"exclusive_classes": True})
            nlp.add_pipe(textcat, last=True) 
        else:
            textcat = nlp.get_pipe("textcat")   

        textcat.add_label('Muy Inseguro')
        textcat.add_label('Inseguro')
        textcat.add_label('Seguro')
        textcat.add_label('Muy Seguro')

        other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'textcat']
        with nlp.disable_pipes(*other_pipes):
        
            if model is None:
                optimizer = nlp.begin_training()
            else:
                optimizer = nlp.resume_training()

            print("Entrenando el modelo...")
            print("{:^5}\t{:^5}\t{:^5}\t{:^5}".format("LOSS", "P", "R", "F"))
            batch_sizes = compounding(1.0, 32.0, 1.001)
            for i in range(iterations):
                losses = {}
                random.shuffle(TRAIN_DATA)
                batches = minibatch(TRAIN_DATA, size=batch_sizes)
                for batch in batches:
                    texts, annotations = zip(*batch)
                    nlp.update(texts, annotations, sgd=optimizer, drop=0.2, losses=losses)
                with textcat.model.use_params(optimizer.averages):
                    scores = self.obtenerPrecisionGeneral(nlp.tokenizer, textcat, self.datasetDeEntrenamientoTexto, self.datasetDeEntrenamientoEtiquetas)
                print(
                    "{0:.3f}\t{1:.3f}\t{2:.3f}\t{3:.3f}".format(
                        losses["textcat"],
                        scores["textcat_p"],
                        scores["textcat_r"],
                        scores["textcat_f"],
                    )
                )
        return nlp

    def obtenerPrecisionGeneral(tokenizer, textcat, texts, cats):
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
    
    def obtenerPrecisionPorCategoria(nlp, test_data):
        eval_input = [(nlp.make_doc(text), GoldParse(nlp.make_doc(text), cats=label["cats"])) for text, label in test_data]
        scorer = nlp.evaluate(eval_input)
 
        return scorer.scores
    
entrenador = EntrenadorTEXTCAT()


