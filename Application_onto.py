import streamlit as st
from rdf_handler import initialize_graph, execute_sparql_query
from langchain.llms import OpenAI
import re
import os

# Configurer la clé API OpenAI
os.environ["OPENAI_API_KEY"] = " "

# Fonction pour générer une réponse en utilisant OpenAI
def generate_response(prompt):
    llm = OpenAI(openai_api_key=os.environ["OPENAI_API_KEY"], temperature=0.7, max_tokens=1024, timeout=60)
    response = llm(prompt)
    return response

# Fonction pour corriger ou reformuler la question avec le LLM
def refine_question_with_llm(question):
    prompt = f"Reformule la question suivante pour qu'elle soit plus claire et précise : {question}"
    refined_question = generate_response(prompt)
    return refined_question

# Fonction pour extraire le cours, la classe, et l'année à partir de la question
def extract_details_from_question(question):
    course_pattern = r"(Mathématiques|Science|Géographie|Histoire|Chimie|Technologie|Français|Anglais|Trigonométrie)"
    class_pattern = r"(Première Année|Deuxième Année|Troisième Année|Quatrième Année|Cinquième Année|Sixième Année)"
    year_pattern = r"\b(2019|2020|2021|2022|2023)\b"

    course = re.search(course_pattern, question)
    class_name = re.search(class_pattern, question)
    year = re.search(year_pattern, question)

    return (course.group(0) if course else None, 
            class_name.group(0) if class_name else None, 
            year.group(0) if year else None)

# Application Streamlit
def main():
    # Initialiser l'état de session pour conserver l'historique
    if "history" not in st.session_state:
        st.session_state.history = []

    # Appliquer des styles CSS pour le design
    st.markdown(
        """
        <style>
        /* Style de fond principal */
        .stApp {
            background-color: #eaf4fc;
        }
        /* Style du panneau latéral */
        .sidebar .sidebar-content {
            background-color: #fdfdfd;
            padding: 20px;
            color: white; /* Texte en blanc */
        }
        
        /* Appliquer la couleur blanche au texte dans la barre latérale */
        .sidebar .sidebar-content h1, .sidebar .sidebar-content h2, .sidebar .sidebar-content h3, 
        .sidebar .sidebar-content h4, .sidebar .sidebar-content h5, .sidebar .sidebar-content h6, 
        .sidebar .sidebar-content p, .sidebar .sidebar-content ul, .sidebar .sidebar-content li {
            color: white;
        }
        
        /* Style du titre principal */
        h1 {
            font-size: 2rem;
            color: #333;
            font-family: 'Arial', sans-serif;
        }
        /* Style des titres de sous-sections */
        h2, h3, h4, h5, h6 {
            color: #0056b3;
            font-family: 'Arial', sans-serif;
        }
        /* Style des textes */
        li {
            color: #fff;
            font-family: 'Arial', sans-serif;
        }

        p, ul {
            color: #000;
            font-family: 'Arial', sans-serif;
        }


        /* Style des boîtes de texte */
        .stTextInput input {
            border: 2px solid #0056b3;
            padding: 0.5rem;
            border-radius: 8px;
            font-size: 1rem;
            background-color: #fff;
            color: #333;
        }
        
        .stTextInput, .stMarkdown {
            color: black;
        }
        
        .stTextInput p {
            color: #000;
            }
        
        /* Style des boutons */
        .stButton button {
            background-color: #0056b3;
            color: ;
            padding: 0.5rem 1rem;
            font-size: 1rem;
            border-radius: 8px;
            border: none;
            font-family: 'Arial', sans-serif;
        }
        </style>
        """, unsafe_allow_html=True
    )
    
    st.sidebar.write("---")
    st.sidebar.header("Aperçu de l'application")
    st.sidebar.write("""
     - Cette application permet d'analyser les performances éducatives des étudiants 
     en fonction de différents critères tels que le cours, la classe, et l'année. 
     Vous pouvez poser une question pour obtenir des insights détaillés.
    """)

    st.sidebar.write("---")
    st.sidebar.subheader("Propositions de questions")
    st.sidebar.write("""
    - Quel est le score moyen en Mathématiques pour la Sixième Année en 2022 ?
    - Pouvez-vous me donner le score moyen en Chimie pour la Troisième Année en 2021 ?
    - Je voudrais connaître la moyenne des scores en Géographie pour la Cinquième Année en 2019.
    """)

    st.title("Suivi de la Performance Éducative")

    # Initialiser le graphe RDF
    g = initialize_graph()

    # Entrée utilisateur pour la question
    question = st.text_input("Entrez votre question :")

    if question:
        # Corriger ou reformuler la question avec le LLM
        refined_question = refine_question_with_llm(question)
        st.write(f"Question reformulée : {refined_question}")

        # Extraire les détails de la question reformulée
        course, class_name, year = extract_details_from_question(refined_question)

        if course and class_name and year:
            # Définir la requête SPARQL en fonction des détails extraits
            sparql_query = f"""
            PREFIX edu: <http://example.org/education/>
            PREFIX cube: <http://purl.org/linked-data/cube#>

            SELECT (AVG(?score) as ?averageScore)
            WHERE {{
              ?observation a cube:Observation ;
                           edu:Year "{year}"^^<http://www.w3.org/2001/XMLSchema#gYear> ;
                           edu:Subject "{course}" ;
                           edu:Class "{class_name}" ;
                           edu:Score ?score .
            }}
            """
            
            # Exécuter la requête SPARQL
            average_score = execute_sparql_query(g, sparql_query)
            st.write(f"Le score moyen en {course} pour la {class_name} en {year} est : {average_score}")
            
            # Générer un prompt pour le modèle de langage
            prompt = f"La requête en langage naturel est : {refined_question}\n\nLa réponse obtenue est : {average_score}\n\n" \
                     "Peux-tu fournir une analyse de cette donnée et des recommandations pour améliorer la performance de cette classe ?"
            
            # Générer la réponse
            response = generate_response(prompt)
            st.write(response)
            
            # Ajouter la question et la réponse à l'historique
            st.session_state.history.append({
                "question": refined_question,
                "response": response,
                "average_score": average_score
            })
        else:
            st.write("Le LLM n'a pas pu extraire toutes les informations nécessaires. Veuillez reformuler votre question.")

    # Afficher l'historique des questions et réponses sous forme de menu cliquable
    if st.session_state.history:
        st.write("### Historique des Questions et Réponses")
        for idx, item in enumerate(st.session_state.history, 1):
            with st.expander(f"Question {idx}: {item['question']}"):
                st.write(f"**Question**: {item['question']}")
                st.write(f"**Réponse**: {item['response']}")
                st.write(f"**Score moyen**: {item['average_score']}")

if __name__ == "__main__":
    main()