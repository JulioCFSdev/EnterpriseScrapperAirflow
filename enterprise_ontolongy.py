import json
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import FOAF, DC

def read_json_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_ontology(data, query):
    g = Graph()
    n = Namespace("http://example.org/ontology/")
    g.bind("ex", n)
    
    search_concept = n[query.replace(' ', '_')]
    g.add((search_concept, RDF.type, FOAF.Document))
    g.add((search_concept, DC.title, Literal(query)))

    for item in data:
        title = item['title']
        link = item['link']
        content = item['content']
        
        doc = URIRef(link)
        g.add((doc, RDF.type, FOAF.Document))
        g.add((doc, DC.title, Literal(title)))
        g.add((doc, DC.identifier, URIRef(link)))
        g.add((doc, DC.description, Literal(content[:200] + "...")))

        g.add((search_concept, FOAF.topic, doc))

    return g

def save_ontology(g, filename):
    g.serialize(destination=filename, format='turtle')

def main():
    query = "Petrobras"
    filename = f"search_google_Petrobras.json"
    data = read_json_file(filename)
    
    g = create_ontology(data, query)
    ontology_filename = f"ontology_{query.replace(' ', '_')}.ttl"
    save_ontology(g, ontology_filename)
    
    print(f"Ontologia salva em {ontology_filename}")

if __name__ == "__main__":
    main()
