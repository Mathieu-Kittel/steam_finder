from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import Error
import requests
from datetime import date
import time

def price_format(price):
    return f"{price/100}€"

print("Initialisation du script de mise à jour des prix.")

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

host = os.getenv('host')
user = os.getenv('user')
password = os.getenv('mdp')
database = os.getenv('database')

today = date.today().isoformat()

print("Variables importées.")

try:
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    if connection.is_connected():
        cursor = connection.cursor()
        query = "SELECT game_id FROM games"
        cursor.execute(query)
        results = cursor.fetchall()
        print("Identifiants récupérés.")
except Error as e:
    print("Erreur lors de la connexion à MySQL:", e)
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()

t1 = time.time()
total_row = len(results)
loop = 0

print("Début des requêtes Steam api.")

country  = "fr"
language = "french"
tup_prices = []
for row in results:
    term = row[0]
    url = f"https://store.steampowered.com/api/storesearch/?term={term}&cc={country}&l={language}"
    response = requests.get(url)
    res = response.json()
    if res['total'] > 0:
        try:
            price = price_format(res["items"][0]['price']['final'])
        except KeyError:
            price = -1
        app_id = res["items"][0]['id']
        tup_prices.append((app_id, today, price))

    loop += 1
    if loop % 50 == 0:
        print(f"Effectué : {loop}/{total_row}, en {round(time.time() - t1, 2)}")
    
try:
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    if connection.is_connected():
        cursor = connection.cursor()

        try:
            for v in tup_prices:
                q = f"""INSERT IGNORE INTO games_prices(game_id, check_date, price)
                VALUES {v};"""
            
                print(f"Insertion de {v}...")
                cursor.execute(q)
                print("Insertion réussie.")
        
            connection.commit()
            print("Enregistrement des modifications.\n")
    
        except Exception as e:
            print("Une erreur est survenue :\n",e,"\nUn rollback de la base de donnée va être effectué.")
            q="ROLLBACK;"
            cursor.execute(q)
            print("ROLLBACK effectué !")

        
except Error as e:
    print("Erreur lors de la connexion à MySQL:", e)
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Connexion fermée.")

print("Fin du script de mise à jour des prix.")