import json
from tqdm import tqdm
from classes import *
import numpy as np
import random
random.seed(24)
"""
This scrip converts ingredients to paths to do simple proportional analsysis of % of recommend, avoid and caution
It also includes weighted proportional calculation
"""

load_dotenv()
URI = 'bolt://localhost:7687'
USER = os.getenv("NEO4J_USER_NAME")
PASSWORD = os.getenv("NEO4J_PASSWD")
AUTH = (os.getenv("NEO4J_USER_NAME"), os.getenv("NEO4J_PASSWD"))

# Instantiate Neo4j connection
neo4j_obj = Neo4jConnection(uri=URI, 
                    user=USER,
                    pwd=PASSWORD)


import neo4j

# TODO: Handle node duplicates - create a dict of nodes and append them to node list.
def neo4j_to_d3(results):
    """
    Converts a list of Neo4j query results into D3.js format.
    
    Args:
        results (list): A list of Neo4j query results where each result corresponds to nodes and relationships.

    Returns:
        result_d3_graphs (dict): A dictionary with nodes and links suitable for D3.js visualization.
    """
    # Initialize a dictionary to hold nodes and links
    result_d3_graphs = {
        "nodes": [],
        "links": []
    }
    
    # Use sets to avoid duplicates
    nodes_set = set()
    links_set = set()
    # Iterate over each Neo4j result
    for idx, result in enumerate(results):
        for record in result:  # Iterate through each Neo4j record
            # Extract nodes and relationships from the record
            # print(type(re))
            for key in record.keys():
                element = record[key]
                
                # Check if the element is a node
                if isinstance(element, neo4j.graph.Node):
                    #just add ingredient name or something to create unique id for each ingredient diabetes category
                    element_id = str(element.id)+"_"+str(idx)
                    # Check if the node has been processed already
                    if element_id not in nodes_set:
                        nodes_set.add(element_id)
                        element_dict= dict(element)
                        result_d3_graphs["nodes"].append({
                            "id": element_id, 
                            "type": list(element.labels)[0],
                            "name": element_dict['name'],
                            "properties": element_dict  # Convert node properties to a dictionary
                        })
                # Check if the element is a relationship
                elif isinstance(element, neo4j.graph.Relationship):
                    start_node_id = str(element.start_node.id)+"_"+str(idx)
                    end_node_id = str(element.end_node.id)+"_"+str(idx)
                    link_id = (start_node_id, end_node_id, element.type)
                    print(element.type)
                    if link_id not in links_set:
                        links_set.add(link_id)
                        result_d3_graphs["links"].append({
                            "source": start_node_id,
                            "target": end_node_id,
                            "type": element.type,
                            "properties": dict(element)  # Convert relationship properties to a dictionary
                        })

    return result_d3_graphs



# get the ingredient names
macaron_names = ['Flour, almond', 'Butter, stick, unsalted', 'Sugars, powdered', 'Egg, white, raw, fresh']
croissant_names = ['Butter, stick, unsalted', 'Flour, wheat, all-purpose, enriched, unbleached', 'Sugars, granulated', 'Salt, table, iodized', 'Milk, whole, 3.25% milkfat, with added vitamin D', ]
chocolate_name = ['Baking chocolate, unsweetened, squares', 'Butter, stick, unsalted', 'Flour, wheat, all-purpose, enriched, unbleached', 'Sugars, granulated', 'Salt, table, iodized', 'Milk, whole, 3.25% milkfat, with added vitamin D']
samosa_names = ['Flour, wheat, all-purpose, enriched, unbleached', 'Salt, table, iodized',	'Potatoes, mashed, ready-to-eat', 'Peas, green, raw', 'Oil, mustard', 'Onions, raw','Spices, chili powder', 'Spices, cumin seed', 'Spices, coriander seed', 'Spices, turmeric, ground']
fruits_names = ['Melons, cantaloupe, raw', 'Melons, honeydew, raw', 'Pineapple, raw', 'Watermelon, raw', 'Grapes, green, seedless, raw']
# Get those paths from Neo4j
def get_paths(name):
    query_str = """MATCH (n:Ingredient {name:$name})-[r1]-(d:DiabetesCategory)-[r2]-(des:DiabetesDecision) 
    RETURN n,d,des,r1,r2
    """
    parameters = {'name': name}
    results = neo4j_obj.query(query_str, parameters)
    return results

records = []
for name in fruits_names:
    recs = get_paths(name)
    records.append(recs)
print(records)
graph = neo4j_to_d3(records)
# print(graph)

json.dump(graph, open("d3_graph.json", "w"))
    
