import os
import spacy
from dotenv import load_dotenv
from openai import OpenAI
from langdetect import detect
import deepl


def start_pipeline (df):
    return df.copy()

def lang_detect(text):
    try:
        return detect(text)
    except:
        return None

def add_language_detection(df, text_column = 'text'):
    df['language'] = df[text_column].apply(lang_detect)
    return df

nlp = spacy.load("en_core_web_sm")

def extract_dutch_sentences(text):
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents if 'dutch' in sent.text.lower()]
    return ' '.join(sentences)

# Helper function to get generated outputs from OpenAI model 
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_completion(prompt, model='gpt-4o-mini'):
    messages = [{ "role": "user", "content": prompt }]
    response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
        )
    return response.choices[0].message.content

# Fuction to determine if the text requires dutch language  
def determine_dutch_requirement(text):

    prompt = f"""
              Your task is to determine if the job description {text} requires the Dutch language. 
              You can only choose one from the following list as your response and nothing else:
              ['Dutch required', 'Dutch is an asset', 'Other']
              Please don't enclose your response in single (') or double quotes(")
              """

    try:
        result = get_completion(prompt)
        return result
    except Exception as e:
        print(f"An error occured: {e}")
        return []

def add_dutch_requirement(df):
    # Filter for English language entries and check for 'dutch' mention
    english_mask = df['language'] == 'en'
    df['dutch_mention'] = df.loc[english_mask, 'text'].str.contains('dutch', case=False, na=False)
    
    # For entries with dutch mention, extract sentences and determine requirement
    dutch_mention_mask = df['dutch_mention'] == True
    df['sentences_with_dutch'] = df.loc[dutch_mention_mask, 'text'].apply(extract_dutch_sentences)
    df['dutch_requirement'] = df.loc[dutch_mention_mask, 'sentences_with_dutch'].apply(determine_dutch_requirement)

    return df

def add_is_english(df):
    # Determine if job is english based on 'language' and 'dutch_requirment'
    df['is_english'] = (df['language'] == 'en') & (df['dutch_requirement']!= 'Dutch required')

    return df 

deepl_api_key = os.getenv("DEEPL_API_KEY")

def translate_text(text):
    try:
        translator = deepl.Translator(auth_key=deepl_api_key)
        translation = translator.translate_text(text, target_lang='EN-US').text
        return translation
    except Exception as e:
        print(f"An error occurred: {e}")
        return text
    
def get_english(text):
    language = lang_detect(text)
    if language =='en':
        return text
    else:
        return translate_text(text)

# Function to group job titles
def group_title_ds (title):
    title_lower = title.lower()

    title_categories = {
        'Data Scientist': ['scientist', 'data science'],
        'Machine Learning Engineer': ['machine learning', 'artificial intelligence',' ai ', ' ml '],
        'Software Engineer': ['developer', 'programmer', 'engineer']
    }

    for category, keywords in title_categories.items():
        if any(keyword in title_lower for keyword in keywords):
            return category

    return 'Other'
    
def add_title_ds(df):
    df['english_title'] = df['title'].apply(get_english)
    df['title_group'] = df['english_title'].apply(group_title_ds)

    return df