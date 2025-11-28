import os
import time
import requests  # <-- We need this new library
from ddgs import DDGS

# 1. Define the "Other" folder
DATASET_DIR = "dataset/Other"

# 2. Create the list of search queries for non-yoga images
NEGATIVE_QUERIES = [
    "people standing on street",
    "person walking in park",
    "person sitting in chair",
    "people at business meeting",
    "running in a park",
    "gym workout",
    "people dancing",
    "playing soccer",
    "playing basketball",
    "group of friends talking"
]
MAX_IMAGES_PER_QUERY = 100 # Set how many images to try for each query

# 3. Make sure the "dataset/Other" directory exists
os.makedirs(DATASET_DIR, exist_ok=True)
print(f"Downloading images into: {os.path.abspath(DATASET_DIR)}")

# 4. Create a DuckDuckGo Search instance and download
with DDGS() as ddgs:
    for query in NEGATIVE_QUERIES:
        print(f"\nSearching for '{query}'...")
        downloaded_count = 0
        
        # 1. Search for image URLs. This does not download.
        results = ddgs.images(query, max_results=MAX_IMAGES_PER_QUERY)
        
        if not results:
            print(f"No results found for {query}.")
            continue

        # 2. Loop through results and download each image
        for i, r in enumerate(results):
            image_url = r.get('image')
            if not image_url:
                continue
            
            try:
                # 3. Get the image content
                response = requests.get(image_url, timeout=5) # 5 second timeout
                
                # 4. Check if the download was successful
                if response.status_code == 200 and response.content:
                    
                    # 5. Create a clean filename (e.g., people_standing_on_street_1.jpg)
                    extension = os.path.splitext(image_url.split("?")[0])[-1]
                    if not extension or extension.lower() not in ['.jpg', '.jpeg', '.png']:
                        extension = '.jpg' # Default to .jpg
                        
                    filename = f"{query.replace(' ', '_')}_{i+1}{extension}"
                    file_path = os.path.join(DATASET_DIR, filename)
                    
                    # 6. Save the image
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    downloaded_count += 1
                
            except Exception as e:
                # If one image fails, just skip it and move to the next
                print(f"Skipping {image_url} (Error: {e})")
                continue

        print(f"Successfully downloaded {downloaded_count} images for {query}.")
        time.sleep(2) # Be polite and wait before the next search

print(f"\n\nAll 'Other' images downloaded!")
print("IMPORTANT: Please go to the folder and MANUALLY DELETE any images that are actually yoga.")