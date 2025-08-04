from dotenv import load_dotenv
import os
from openai import OpenAI
import base64
import json
from library import make_json, send_json
import requests
import re
from neo4j import GraphDatabase, RoutingControl
from neo4j.exceptions import ServiceUnavailable, AuthError, ClientError

load_dotenv()
client = OpenAI()

task_name = "connections"
my_key = os.getenv("MY_KEY")

def send_query(query):
    url = "https://c3ntrala.ag3nts.org/apidb"
    data = { "task": "database", "apikey": my_key, "query": query }
    response = requests.post(url, json=data)
    return response.json()

def add_user(driver, user):
    driver.execute_query(
        "CREATE (u:User {name: $name, userId: $userId})", 
        name=user["username"], 
        userId=user["id"], 
        database_="neo4j"
    )
    print(f"✅ Added user: {user['username']}")

def add_connection(driver, connection):
    driver.execute_query(
        "MERGE (u1:User {userId: $user1_id}) "
        "MERGE (u2:User {userId: $user2_id}) "
        "MERGE (u1)-[:KNOWS]->(u2) ",
        user1_id=connection["user1_id"],
        user2_id=connection["user2_id"],
        database_="neo4j"
    )
    print(f"✅ Added connection: {connection['user1_id']} -> {connection['user2_id']}")

def find_shortest_path(driver, user1_name, user2_name):
    """
    return list of users names creating shortest path between user1 and user2
    """
    # First check if both users exist
    check_users = driver.execute_query(
        "MATCH (u:User) WHERE u.name IN [$user1_name, $user2_name] RETURN u.name as name",
        user1_name=user1_name,
        user2_name=user2_name,
        database_="neo4j",
        routing_control=RoutingControl.READ
    )
    
    found_users = [record["name"] for record in check_users.records]
    if user1_name not in found_users:
        print(f"❌ User '{user1_name}' not found in database")
        return None
    if user2_name not in found_users:
        print(f"❌ User '{user2_name}' not found in database")
        return None
    
    result = driver.execute_query(
        "MATCH (u1:User {name: $user1_name}), (u2:User {name: $user2_name}) "
        "MATCH path = shortestPath((u1)-[:KNOWS*]-(u2)) "
        "RETURN path, length(path) as path_length",
        user1_name=user1_name,
        user2_name=user2_name,
        database_="neo4j",
        routing_control=RoutingControl.READ
    )
    return result

def display_shortest_path(result):
    """
    display shortest path as list of users names separated by comas
    """
    if not result.records:
        print("❌ No path found between users")
        return
    
    path = result.records[0]["path"]
    path_length = result.records[0]["path_length"]
    print(f"🔗 Shortest path (length: {path_length}):")
    path_names = [node["name"] for node in path.nodes]
    print(",".join(path_names))

if __name__ == "__main__":

    driver = GraphDatabase.driver(os.getenv("NEO4J_URI"), auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")))

    # users = send_query("select * from users")["reply"]
    # connections = send_query("select * from connections")["reply"]

    # for user in users:
    #     add_user(driver, user)
    
    # for connection in connections:
    #     add_connection(driver, connection)

    result = find_shortest_path(driver, "Rafał", "Barbara")
    display_shortest_path(result)
    path_names = [node["name"] for node in result.records[0]["path"].nodes]
    json_data = make_json(task_name, ",".join(path_names))
    print(send_json(json_data))

