import random
import json
import os
import re
import nlpaug.augmenter.char as nac
import nlpaug.augmenter.word as naw
import nlpaug.augmenter.sentence as nas
import nlpaug.flow as nafc
from nlpaug.util import Action

dirname = os.path.dirname(__file__)         #path de la carpeta actual
filename1 = "marginal.json1"   #nombre del archivo
filepath1 = os.path.join(dirname, filename1)  #path del dataset  1  


#CARGO EL DATASET 1
train_data = []
for line in open(filepath1, encoding="utf8"):
    train_data.append(json.loads(line))

#OCR Augmenter
ocr = []
ocr += train_data.copy()
aug = nac.OcrAug()
for data in ocr:
    augmented_texts = aug.augment(data['text'], n=2)
    if len(augmented_texts) > 1:
        data['text'] = augmented_texts[1]

print(train_data[1])
print(ocr[1])


#Keyboard Augmenter
key = train_data.copy()
aug = nac.KeyboardAug()
for data in key:    
    augmented_text = aug.augment(data['text'])
    data['text'] = augmented_text

#Random Augmenter
random = train_data.copy()
aug = nac.RandomCharAug(action="substitute")
for data in random:
    augmented_text = aug.augment(data['text'])
    data['text'] = augmented_text

print(ocr[1])
print(key[1])
print(random[1])
