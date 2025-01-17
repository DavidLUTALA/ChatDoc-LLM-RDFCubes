# rdf_handler.py

# rdf_handler.py

from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD

def initialize_graph():
    g = Graph()

    # Définition des namespaces
    EX = Namespace("http://example.org/")
    CUBE = Namespace("http://purl.org/linked-data/cube#")
    EDU = Namespace("http://example.org/education/")

    g.bind("ex", EX)
    g.bind("cube", CUBE)
    g.bind("edu", EDU)

    # Définir les dimensions
    g.add((EDU.Year, RDF.type, CUBE.DimensionProperty))
    g.add((EDU.Subject, RDF.type, CUBE.DimensionProperty))
    g.add((EDU.Class, RDF.type, CUBE.DimensionProperty))

    # Définir les mesures
    g.add((EDU.Score, RDF.type, CUBE.MeasureProperty))
    g.add((EDU.AttendanceRate, RDF.type, CUBE.MeasureProperty))

    # Ajouter plusieurs observations sur 5 ans, différents cours et classes
    courses = ["Mathématiques", "Science", "Géographie", "Histoire", "Chimie", "Technologie", "Français", "Anglais", "Trigonométrie"]
    classes = ["Première Année", "Deuxième Année", "Troisième Année", "Quatrième Année", "Cinquième Année", "Sixième Année"]
    
    observations = []

    for year in range(2019, 2024):  # Période de 5 ans (2019-2023)
        for course in courses:
            for class_name in classes:
                score = round(70 + 30 * (hash(f"{year}{course}{class_name}") % 10) / 9, 2)
                attendance = round(85 + 15 * (hash(f"{year}{course}{class_name}") % 10) / 9, 2)
                observations.append({"year": year, "subject": course, "class": class_name, "score": score, "attendance": attendance})

    for i, obs in enumerate(observations, start=1):
        obs_uri = URIRef(f"http://example.org/observation{i}")
        g.add((obs_uri, RDF.type, CUBE.Observation))
        g.add((obs_uri, EDU.Year, Literal(obs["year"], datatype=XSD.gYear)))
        g.add((obs_uri, EDU.Subject, Literal(obs["subject"])))
        g.add((obs_uri, EDU.Class, Literal(obs["class"])))
        g.add((obs_uri, EDU.Score, Literal(obs["score"], datatype=XSD.integer)))
        g.add((obs_uri, EDU.AttendanceRate, Literal(obs["attendance"], datatype=XSD.float)))

    # Sauvegarder le graphe RDF dans un fichier
    g.serialize(destination='education_performance.ttl', format='turtle')
    return g



def execute_sparql_query(g, sparql_query):
    qres = g.query(sparql_query)
    for row in qres:
        return row.averageScore
