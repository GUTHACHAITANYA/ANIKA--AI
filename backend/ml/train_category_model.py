import os
import sys
import random
from pathlib import Path
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support, confusion_matrix

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.config import Config

CATEGORIES = [
    "Food & Dining",
    "Groceries",
    "Shopping",
    "Transport",
    "Fuel",
    "Healthcare",
    "Entertainment",
    "Utilities",
    "Travel",
    "Education",
    "Bills",
    "Other"
]

CATEGORY_TEMPLATES = {
    "Food & Dining": {
        "merchants": ["Swiggy", "Zomato", "McDonald's", "Dominos Pizza", "Starbucks", "Barbeque Nation", "Haldiram's", "KFC", "Burger King", "Cafe Coffee Day", "Subway", "Chai Point", "Bikanervala", "Dhaba Express", "Punjab Grill"],
        "descriptions": ["Dinner with friends", "Lunch delivery", "Coffee and croissant", "Friday night pizza", "Family buffet dinner", "Burger meal with fries", "Afternoon chai and snacks", "Office lunch", "Late night dessert delivery", "Sushi dinner", "Tandoori chicken meal", "Pasta and mocktail"],
        "keywords": ["food, restaurant, meal, dinner, lunch, snack, cafe, beverage, pizza, burger, dining"],
        "amount_range": (150, 4500)
    },
    "Groceries": {
        "merchants": ["Blinkit", "Zepto", "Instamart", "BigBasket", "DMart", "Reliance Fresh", "Nature's Basket", "More Supermarket", "Local Kirana Store", "Spencer's", "Heritage Fresh"],
        "descriptions": ["Weekly grocery restock", "Fresh vegetables and fruits", "Milk, eggs, and bread", "Cooking oil, rice, and pulses", "Household kitchen essentials", "Dairy supplies", "Snacks and breakfast cereals", "Gourmet cheese and pasta", "Spices and masala ingredients", "Organic honey and oats"],
        "keywords": ["grocery, vegetables, fruits, milk, dairy, supermarket, kitchen, provisions, pulses, food items"],
        "amount_range": (200, 7500)
    },
    "Shopping": {
        "merchants": ["Amazon", "Flipkart", "Myntra", "Zara", "H&M", "Ajio", "Uniqlo", "Decathlon", "Lifestyle", "Westside", "Nike Store", "Shoppers Stop", "Croma", "Reliance Digital"],
        "descriptions": ["Running shoes purchase", "Summer cotton shirts", "Denim jeans and jacket", "Sports backpack and gear", "Casual sneakers", "Wireless earbuds", "Mechanical keyboard", "Gym wear t-shirts", "Formal blazer", "Winter hoodie", "Home decor lamp", "Sunglasses and watch"],
        "keywords": ["shopping, apparel, clothing, shoes, fashion, electronics, retail, accessories, gadget"],
        "amount_range": (500, 25000)
    },
    "Transport": {
        "merchants": ["Uber", "Ola Cabs", "Rapido", "Metro Rail", "Auto Rickshaw", "BluSmart", "RedBus", "MakeMyTrip Cabs", "QuickRide", "Local Taxi Service"],
        "descriptions": ["Cab ride to airport", "Office commute ride", "Auto ride to metro station", "Late night cab home", "Intercity shared cab", "Bike taxi ride", "Monthly metro card recharge", "Taxi ride to railway station", "Morning peak hour cab", "Weekend city travel ride"],
        "keywords": ["transport, cab, taxi, ride, auto, metro, commute, transit, travel, fare"],
        "amount_range": (50, 2800)
    },
    "Fuel": {
        "merchants": ["Indian Oil", "Bharat Petroleum", "HPCL", "Shell Petrol Station", "Nayara Energy", "Reliance Petroleum", "Essar Fuel Station", "TotalEnergies"],
        "descriptions": ["Petrol tank refill", "Diesel for SUV", "Full tank petrol", "Scooter fuel refill", "Power petrol refill", "Speed diesel fuel", "Highway petrol stop", "Car fuel top-up", "Shell V-Power petrol", "CNG cylinder filling"],
        "keywords": ["fuel, petrol, diesel, gas, cng, refill, pump, station, energy, tank"],
        "amount_range": (300, 6000)
    },
    "Healthcare": {
        "merchants": ["Apollo Pharmacy", "MedPlus", "1mg", "Netmeds", "Practo Clinic", "Dr Lal PathLabs", "Fortis Hospital", "Max Healthcare", "Care Diagnostics", "Apollo Spectra"],
        "descriptions": ["Prescription medicine refill", "Doctor consultation fee", "Annual health checkup blood test", "Vitamins and protein supplements", "Dental checkup and cleaning", "Eye examination and drops", "Skin ointment and dermat care", "Blood sugar diagnostic panel", "Physiotherapy session fee", "Emergency clinic visit"],
        "keywords": ["healthcare, pharmacy, medicine, doctor, clinic, hospital, diagnostic, lab, pills, medical"],
        "amount_range": (150, 15000)
    },
    "Entertainment": {
        "merchants": ["Netflix", "BookMyShow", "PVR Cinemas", "INOX", "Spotify", "Amazon Prime Video", "Hotstar", "SonyLIV", "Steam Games", "PlayStation Store", "Smaaash Arcade", "Bowling Alley"],
        "descriptions": ["Weekend IMAX movie tickets", "Monthly Netflix subscription", "Spotify premium yearly", "Standup comedy show passes", "Music concert tickets", "Video game digital purchase", "Arcade bowling evening", "Theater play tickets", "OTT streaming annual renewal", "Gaming zone credits"],
        "keywords": ["entertainment, movies, cinema, subscription, streaming, concert, gaming, music, theater, fun"],
        "amount_range": (199, 5000)
    },
    "Utilities": {
        "merchants": ["Tata Power", "BSES Yamuna", "Bescom Electricity", "Adani Gas", "Mahanagar Gas", "Water Supply Board", "JioFiber", "Airtel Xstream Broadband", "ACT Fibernet", "Urban Company Waste Management"],
        "descriptions": ["Monthly electricity bill", "High-speed broadband internet", "Piped natural gas PNG bill", "Apartment water charges", "Fiber optic wifi bill", "Municipal water tax", "Gas cylinder refill payment", "Home maintenance society fee", "Summer AC power bill", "Internet router renewal"],
        "keywords": ["utilities, electricity, water, internet, wifi, broadband, gas, power, connection, bill"],
        "amount_range": (400, 8500)
    },
    "Travel": {
        "merchants": ["MakeMyTrip", "Goibibo", "IRCTC", "IndiGo Airlines", "Air India", "Airbnb", "Booking.com", "Agoda", "Taj Hotels", "Treebo Hotels", "Zostel"],
        "descriptions": ["Roundtrip flight tickets to Goa", "Train reservation AC 2 Tier", "Himalayan boutique resort stay", "Backpacker hostel booking", "Weekend getaway Airbnb villa", "Domestic flight to Mumbai", "Hotel accommodation 3 nights", "Airport lounge access fee", "Heritage resort booking in Jaipur", "Train tatkal ticket booking"],
        "keywords": ["travel, flight, airline, hotel, irctc, train, booking, resort, vacation, holiday, stay"],
        "amount_range": (800, 45000)
    },
    "Education": {
        "merchants": ["Coursera", "Udemy", "edX", "Oxford Bookstore", "Crossword Books", "Skillshare", "Byju's", "Unacademy", "Simplilearn", "College Tuition Portal", "AWS Certification Portal"],
        "descriptions": ["Python data science course certification", "Machine learning masterclass", "Cloud architect exam fee", "University semester tuition fee", "Competitive exam study books", "Frontend React bootcamp access", "Language learning app subscription", "Reference textbook for engineering", "Design UI/UX workshop pass", "Academic journal subscription"],
        "keywords": ["education, course, learning, tuition, books, certification, exam, university, class, bootcamp"],
        "amount_range": (499, 35000)
    },
    "Bills": {
        "merchants": ["Airtel Prepaid/Postpaid", "Jio Telecom", "Vodafone Idea", "Tata Play DTH", "Dish TV", "HDFC Credit Card Bill", "ICICI Card Pay", "LIC Premium", "HDFC Life Insurance", "SBI Card Payment"],
        "descriptions": ["Monthly mobile phone postpaid plan", "DTH satellite TV recharge", "Credit card statement bill payment", "Term life insurance premium", "Vehicle insurance renewal", "Mobile data add-on pack", "Annual credit card fee payment", "Health policy premium installment", "Family mobile plan recharge", "Quarterly insurance premium"],
        "keywords": ["bills, recharge, mobile, postpaid, dth, credit card, insurance, premium, payment, telecom"],
        "amount_range": (299, 25000)
    },
    "Other": {
        "merchants": ["India Post", "DHL Courier", "Local Laundry", "Dry Cleaners", "Pet Store & Vet", "Car Wash Express", "Key Maker", "Community Donation", "Hardware Tool Store", "Notary Legal Services"],
        "descriptions": ["Express document courier", "Dry cleaning suit and blazer", "Dog food and grooming treats", "Car foam wash and interior polish", "Donation to local animal shelter", "Apartment key duplicate making", "Plumbing repair spare parts", "Legal stamp paper fee", "Watch battery replacement", "Charity contribution"],
        "keywords": ["other, miscellaneous, courier, laundry, pet, maintenance, donation, service, general"],
        "amount_range": (100, 6000)
    }
}

def generate_synthetic_dataset(num_records: int = 1500) -> pd.DataFrame:
    """Generates a realistic synthetic dataset for financial expense category classification."""
    records = []
    records_per_category = num_records // len(CATEGORIES) + 15

    for category, data in CATEGORY_TEMPLATES.items():
        merchants = data["merchants"]
        descriptions = data["descriptions"]
        keywords_pool = data["keywords"][0].split(", ")
        min_amt, max_amt = data["amount_range"]

        for _ in range(records_per_category):
            merchant = random.choice(merchants)
            desc_base = random.choice(descriptions)
            
            # Combine variations
            variations = [
                f"{merchant} - {desc_base}",
                f"{desc_base} at {merchant}",
                f"Paid {merchant} for {desc_base.lower()}",
                f"{merchant} bill: {desc_base}",
                f"{desc_base}",
                f"Purchase at {merchant}",
                f"{merchant} payment"
            ]
            full_desc = random.choice(variations)
            
            # Pick 2-4 keywords
            k_sample = random.sample(keywords_pool, k=min(len(keywords_pool), random.randint(2, 4)))
            keywords_str = ", ".join(k_sample)
            
            amount = round(random.uniform(min_amt, max_amt), 2)
            
            records.append({
                "description": full_desc,
                "merchant": merchant,
                "amount": amount,
                "keywords": keywords_str,
                "category": category
            })

    df = pd.DataFrame(records)
    # Shuffle
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    return df

def train_and_evaluate_model():
    """Trains the scikit-learn model and saves serialized artifacts."""
    print("=" * 60)
    print("ANIKA-AI: Training Financial Category Classification Model")
    print("=" * 60)

    # 1. Generate or load dataset
    dataset_path = Config.DATASET_PATH
    os.makedirs(os.path.dirname(dataset_path), exist_ok=True)
    
    print("Generating synthetic financial dataset (1,400+ samples across 12 categories)...")
    df = generate_synthetic_dataset(num_records=1440)
    df.to_csv(dataset_path, index=False)
    print(f"Dataset successfully saved to: {dataset_path}")
    print(f"Dataset shape: {df.shape}")

    # Combine text features: merchant + description + keywords
    df["combined_text"] = df["merchant"] + " " + df["description"] + " " + df["keywords"]
    
    X = df["combined_text"]
    y = df["category"]

    # 2. Train / Test Split (80% train, 20% test, stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"Training samples: {len(X_train)} | Test samples: {len(X_test)}")

    # 3. Model Pipeline: TF-IDF + LogisticRegression with balanced weights
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
            lowercase=True
        )),
        ('clf', LogisticRegression(
            C=2.0,
            max_iter=1000,
            class_weight='balanced',
            random_state=42
        ))
    ])

    print("Fitting TF-IDF Vectorizer and Logistic Regression classifier...")
    pipeline.fit(X_train, y_train)

    # 4. Evaluation
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')

    print("\n--- MODEL PERFORMANCE EVALUATION ---")
    print(f"Accuracy:  {accuracy * 100:.2f}%")
    print(f"Precision: {precision * 100:.2f}%")
    print(f"Recall:    {recall * 100:.2f}%")
    print(f"F1 Score:  {f1 * 100:.2f}%")
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, digits=3))

    cm = confusion_matrix(y_test, y_pred)
    print("Confusion Matrix shape:", cm.shape)

    # 5. Save model bundle
    model_path = Config.CATEGORY_MODEL_PATH
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    artifact_bundle = {
        'pipeline': pipeline,
        'categories': CATEGORIES,
        'metrics': {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1)
        }
    }

    joblib.dump(artifact_bundle, model_path)
    print(f"\nTrained category classification model successfully saved to: {model_path}")
    print("=" * 60)

    # Sanity checks
    test_cases = [
        "Shell petrol station refill",
        "Pizza Hut dinner with friends",
        "Amazon shoes and sneakers",
        "Apollo pharmacy antibiotics",
        "Uber ride to airport"
    ]
    print("\nSanity Check Predictions:")
    for query in test_cases:
        probs = pipeline.predict_proba([query])[0]
        pred_idx = np.argmax(probs)
        pred_cat = pipeline.classes_[pred_idx]
        conf = probs[pred_idx] * 100
        print(f"  '{query}' -> {pred_cat} ({conf:.1f}% confidence)")

    return artifact_bundle

if __name__ == "__main__":
    train_and_evaluate_model()
