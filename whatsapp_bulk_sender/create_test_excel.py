import pandas as pd
import random

def create_test_excel(filename="sample_leads.xlsx"):
    data = []
    
    countries = ["Qatar", "Serbia", "Oman", "Malaysia", "UAE", "Saudi Arabia", "", "Kuwait"]
    experiences = ["Plumber", "Forklift Operator", "Rajmistri", "Electrician", "Driver", "Cleaner", "", "Welder"]
    exp_years = ["2+", "5+", "10+", "15+", "", "3+", "7+"]
    
    # Generate 15 dummy leads
    for i in range(15):
        # We need realistic numbers, starting with 880 for Bangladesh
        phone = f"88017{random.randint(1000000, 9999999)}"
        country = random.choice(countries)
        exp = random.choice(experiences)
        year = random.choice(exp_years)
        
        # Link
        link = f"https://wa.me/{phone}"
        
        data.append({
            "Phone Number (Digits)": phone,
            "Work Experience": exp,
            "Experience Year": year,
            "Country / Visa Interest": country,
            "WhatsApp Link (Auto)": link
        })
        
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"Created '{filename}' with {len(data)} test leads.")

if __name__ == "__main__":
    create_test_excel()
