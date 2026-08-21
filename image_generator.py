import requests
import os
import datetime
from google import genai 
import json

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

def get_news():
    # retrieves raw data 
    url = os.environ.get("NEWS_API_URL")
    key = os.environ.get("NEWS_API_KEY")
    if not url or not key:
        return print(" ----------- *****  CANNOT ACCESS API KEY AND URL ***** --------- ")
    
    response = requests.get(url + key)
    response = response.json()
    
    if response['status'] == 'ok': 
        return response
    else: 
        print(f"Request failed with status code: {response.status_code}")
    

def parse_news(news_raw):
    # extracts news data from raw
    parsed_news = {}
    number = 1
    para_counter = 0

    print("Entry: ", news_raw['articles'][0])

    for entry in news_raw['articles']: 
        source = entry["source"]["name"]
        headline = entry["title"].split(" - ")[0] # removes source from headline
        description = entry["description"]
        url = entry["url"]
        urlToImage = entry["urlToImage"]
        paragraph = entry["content"]

        if paragraph is not None: 
            para_counter += 1
        
        raw_article_data = [source, headline, description, url, urlToImage, paragraph]

        clean_article_data = [item for item in raw_article_data if item is not None]
        parsed_news[number] = clean_article_data
        number += 1

    print("PARA COUNTER: ", para_counter)
    return parsed_news

def get_prompt(file):
    image_prompt = None
    with open(f'prompts/{file}', 'r') as f:
        image_prompt = f.read()

    return image_prompt

def image_context(news_data):
    # joins human prompt with news data
    prompt = get_prompt("main_image.txt")

    for key, value in news_data.items(): 
        context_string = str(key) + ". "
        context_string += ', '.join(value)
        prompt += context_string + "; "

    # Print first third of the prompt in "output" section
    # first_third = prompt[:len(prompt) // 3]
    # print("FIRST THIRD: " + first_third)

    return prompt

def gemini_request(prompt_text):
    # makes gemini request and saves resulting image
    prompt = f"{prompt_text}\n{prompt_text}"
    response = client.models.generate_content(
        model="gemini-3.1-flash-image-preview",
        contents=[prompt],
    )
    return response

def retrieve_image(gemini_response):
    #retrieves image from gemini response
    if not gemini_response.parts:
        raise ValueError("No parts found in the response")

    for part in gemini_response.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = part.as_image()
            # add timestamp to image name so that in the future, we can delete it
            # image.save(f"images/{todays_date}.png")
            return image 

def generate_image():
    # sequence to generate one image
    # gets articles, makes prompt, sends prompt to gemini, saves result

    raw_data = get_news()
    parsed_data = parse_news(raw_data)
    prompt = image_context(parsed_data)
    response = gemini_request(prompt)
    image = retrieve_image(response)

    return image
