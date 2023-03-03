import spacy
import contextualSpellCheck

nlp = spacy.load('en_core_web_sm')
contextualSpellCheck.add_to_pipe(nlp)
doc = nlp('It is not allways easy , but there are rules in each home and you have to respect them .')

print(doc._.outcome_spellCheck)
