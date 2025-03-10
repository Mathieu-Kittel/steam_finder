from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import mysql.connector
from mysql.connector import Error
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import requests
import random

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_mysql_connection(host, user, mdp, database):
    return mysql.connector.connect(
        host=host,
        user=user,
        password=mdp,
        database=database
    )

load_dotenv()
host     = os.getenv('host')
database = os.getenv('database')
user     = os.getenv('root')
mdp      = os.getenv('mdp')

mongo_client = MongoClient("mongodb://localhost:27017")
mongo_db = mongo_client["steam_finder"]
headers_collection = mongo_db["headers"]

def get_game_details(search_term: str = None):
    try:
        connection = get_mysql_connection(host, user, mdp, database)
        cursor = connection.cursor(dictionary=True)
        if search_term:
            like_pattern = f"%{search_term}%"
            query = """
            SELECT 
                games.game_id,
                games.game_name,
                (SELECT price FROM games_prices WHERE game_id = games.game_id ORDER BY check_date DESC LIMIT 1) as latest_price,
                games_summary.release_date,
                games_summary.review_cnt,
                games_summary.snippet,
                games_summary.metacritic,
                games_summary.link,
                GROUP_CONCAT(DISTINCT languages.language_name SEPARATOR ', ') as languages,
                GROUP_CONCAT(DISTINCT features.feature_name SEPARATOR ', ') as features,
                GROUP_CONCAT(DISTINCT tags.tag_name SEPARATOR ', ') as tags,
                GROUP_CONCAT(DISTINCT genres.genre_name SEPARATOR ', ') as genres,
                GROUP_CONCAT(DISTINCT publishers.publisher_name SEPARATOR ', ') as publishers,
                GROUP_CONCAT(DISTINCT developers.developer_name SEPARATOR ', ') as developers,
                reviews.review_name
            FROM games
            LEFT JOIN games_summary ON games.game_id = games_summary.game_id
            LEFT JOIN reviews ON games_summary.review_id = reviews.review_id
            LEFT JOIN games_languages ON games.game_id = games_languages.game_id
            LEFT JOIN languages ON games_languages.language_id = languages.language_id
            LEFT JOIN games_features ON games.game_id = games_features.game_id
            LEFT JOIN features ON games_features.feature_id = features.feature_id
            LEFT JOIN games_tags ON games.game_id = games_tags.game_id
            LEFT JOIN tags ON games_tags.tag_id = tags.tag_id
            LEFT JOIN games_genres ON games.game_id = games_genres.game_id
            LEFT JOIN genres ON games_genres.genre_id = genres.genre_id
            LEFT JOIN games_publishers ON games.game_id = games_publishers.game_id
            LEFT JOIN publishers ON games_publishers.publisher_id = publishers.publisher_id
            LEFT JOIN games_developers ON games.game_id = games_developers.game_id
            LEFT JOIN developers ON games_developers.developer_id = developers.developer_id
            WHERE games.game_name LIKE %s
            GROUP BY games.game_id, games_summary.release_date, games_summary.review_cnt, games_summary.snippet, games_summary.metacritic, games_summary.link, reviews.review_name
            """
            cursor.execute(query, (like_pattern,))
        else:
            cursor.execute("SELECT * FROM games")
        results = cursor.fetchall()
        for game in results:
            header = headers_collection.find_one({"_id": game["game_id"]})
            game["header"] = header.get("image") if header and "image" in header else None
        return results
    except Error as e:
        print(e)
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_random_game_details(limit: int = 5):
    try:
        connection = get_mysql_connection(host, user, mdp, database)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT game_id FROM games")
        all_ids = [row['game_id'] for row in cursor.fetchall()]
        if not all_ids:
            return []
        sampled_ids = random.sample(all_ids, min(limit, len(all_ids)))
        placeholders = ','.join(['%s'] * len(sampled_ids))
        query = f"""
            SELECT 
                games.game_id,
                games.game_name,
                (SELECT price FROM games_prices WHERE game_id = games.game_id ORDER BY check_date DESC LIMIT 1) as latest_price,
                games_summary.release_date,
                games_summary.review_cnt,
                games_summary.snippet,
                games_summary.metacritic,
                games_summary.link,
                GROUP_CONCAT(DISTINCT languages.language_name SEPARATOR ', ') as languages,
                GROUP_CONCAT(DISTINCT features.feature_name SEPARATOR ', ') as features,
                GROUP_CONCAT(DISTINCT tags.tag_name SEPARATOR ', ') as tags,
                GROUP_CONCAT(DISTINCT genres.genre_name SEPARATOR ', ') as genres,
                GROUP_CONCAT(DISTINCT publishers.publisher_name SEPARATOR ', ') as publishers,
                GROUP_CONCAT(DISTINCT developers.developer_name SEPARATOR ', ') as developers,
                reviews.review_name
            FROM games
            LEFT JOIN games_summary ON games.game_id = games_summary.game_id
            LEFT JOIN reviews ON games_summary.review_id = reviews.review_id
            LEFT JOIN games_languages ON games.game_id = games_languages.game_id
            LEFT JOIN languages ON games_languages.language_id = languages.language_id
            LEFT JOIN games_features ON games.game_id = games_features.game_id
            LEFT JOIN features ON games_features.feature_id = features.feature_id
            LEFT JOIN games_tags ON games.game_id = games_tags.game_id
            LEFT JOIN tags ON games_tags.tag_id = tags.tag_id
            LEFT JOIN games_genres ON games.game_id = games_genres.game_id
            LEFT JOIN genres ON games_genres.genre_id = genres.genre_id
            LEFT JOIN games_publishers ON games.game_id = games_publishers.game_id
            LEFT JOIN publishers ON games_publishers.publisher_id = publishers.publisher_id
            LEFT JOIN games_developers ON games.game_id = games_developers.game_id
            LEFT JOIN developers ON games_developers.developer_id = developers.developer_id
            WHERE games.game_id IN ({placeholders})
            GROUP BY games.game_id, games_summary.release_date, games_summary.review_cnt, games_summary.snippet, games_summary.metacritic, games_summary.link, reviews.review_name
        """
        cursor.execute(query, tuple(sampled_ids))
        results = cursor.fetchall()
        for game in results:
            header = headers_collection.find_one({"_id": game["game_id"]})
            game["header"] = header.get("image") if header and "image" in header else None
        return results
    except Error as e:
        print(e)
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    games = get_random_game_details(limit=5)
    return templates.TemplateResponse("home.html", {"request": request, "games": games})

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str = None):
    if q:
        games = get_game_details(search_term=q)
    else:
        games = []
    return templates.TemplateResponse("results.html", {"request": request, "games": games, "query": q})

@app.get("/steam_search", response_class=HTMLResponse)
async def steam_search(request: Request, q: str):
    country = "fr"
    language = "french"
    url = f"https://store.steampowered.com/api/storesearch/?term={q}&cc={country}&l={language}"
    response = requests.get(url)
    results = response.json()
    return templates.TemplateResponse("steam_results.html", {"request": request, "results": results, "query": q})

@app.post("/search", response_class=HTMLResponse)
async def search_post(request: Request, q: str = Form(...)):
    return RedirectResponse(url=f"/search?q={q}", status_code=303)
