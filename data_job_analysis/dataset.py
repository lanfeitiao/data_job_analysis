import os
from urllib.request import urlopen
from dotenv import load_dotenv
import pickle
import pandas as pd

# Access the url using the variable name defined in the .env file
load_dotenv()
db_file_path = os.getenv('DB_FILE_PATH')

# Load pickle file from url 
with urlopen(db_file_path) as db:
    pickle_db = pickle.load(db)

def get_jobs_by_keyword(keyword):
    
    job_list =[]
    job_ids = pickle_db['jobs_by_search_keyword'].get(keyword, set())
    for job_id in job_ids:
        job_details = pickle_db['jobs_by_id'][job_id]
        job_list.append(job_details)
    
    return pd.DataFrame(job_list)


def get_all_jobs():
    job_list = []
    # Assuming that your pickle_db dictionary correctly contains 'jobs_by_search_keyword'
    # and 'jobs_by_id' as keys.
    jobs_by_keyword = pickle_db.get('jobs_by_search_keyword', {})
    jobs_by_id = pickle_db.get('jobs_by_id', {})

    for keyword, job_ids in jobs_by_keyword.items():
        print(f"{keyword}")
        for job_id in job_ids:
            job_details = jobs_by_id.get(job_id)
            if job_details:
                job_list.append(job_details)
    
    return pd.DataFrame(job_list)



