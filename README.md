## # Grocery-Store-in-Django-with-Content-Based-Recommendation
An Online Grocery Store using HTML, CSS, Bootstrap, Python Django, SQLite, featuring a content-based recommendation system based on cosine similarity using product descriptions. Kaggle Grocery Store Dataset used.

## Features
- **Grocery Store Functionality**: 
  - View products by category
  - Add to cart and manage orders
  - Product recommendations
- **Content-Based Recommendation**:
  - Uses cosine similarity to recommend products based on their descriptions.
- **Dataset**: 
  - Sourced from Kaggle **Grocery Store Dataset**.
- **Tech Stack**:
  - HTML, CSS, Bootstrap
  - Python, Django
  - SQLite

## Dataset Structure
- **Dataset Path**: `dataset/`
  - `classes.csv`: Contains coarse class names, IDs, and paths to images/descriptions.
  - `iconic-images-and-descriptions/`: Contains product images and descriptions organized by categories (`fruit`, `vegetables`, `packages`).

Note: Please connect to the internet as most of the styling is handled by Bootstrap, which requires an internet connection for correct rendering.

### ## Installation[Note-- Please connect to internet as most of te styling is in bootstrap so it requires internet for correct displaying]
##### Step 1. Clone the repository:
`git clone https://github.com/your-username/Grocery-Store-in-Django-with-Content-Based-Recommendation.git`


##### Step 2: Unzip the Dataset
Unzip the **dataset.zip** file and place the **dataset** folder in the **same directory** as your project.
**Optional:** You can delete the dataset.zip file after unzipping, as its no longer required.

##### Step 3: Create a Virtual Environment
To create a virtual environment, run:
   ` python -m venv myenv`
##### Step 4: Activate the Virtual Environment
Activate the virtual environment depending on your operating system:
On Windows:
    `myenv\Scripts\activate`
On macOS/Linux:
    `source myenv/bin/activate`

Once activated, your terminal should show (myenv) in the prompt, indicating the virtual environment is active.

##### Step 5: Install Required Packages
With the virtual environment active, install all necessary dependencies by running:
`pip install -r requirements.txt`

##### Step 6: Make Database Migrations
To create and apply the migrations for the database:

Create migrations:
`python manage.py makemigrations`

Apply the migrations:
`python manage.py migrate`

##### Step 7: Load all Products from dataset into the Database
Use the custom management command to load product data into the database:
`python manage.py load_products`

##### Step 8: Create Admin Account
To create a superuser account that will allow you to manage the application via the Django admin panel, run:
`python manage.py createsuperuser`
Follow the prompts to set up a username, email (optional), and password. Once the account is created, you can log in to the admin panel.
