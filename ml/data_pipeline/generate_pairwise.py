import random
import pandas as pd
from pathlib import Path

DOMAINS = ["E-commerce", "Banking", "Healthcare", "IoT"]
SYSTEM_NOUNS = ["application", "system", "platform", "software"]

def generate_pairwise_dataset(num_pairs_per_class=200):
    pairs = []
    
    # 1. DUPLICATES (High similarity, exact same meaning, different wording)
    dup_bases = [
        ("The {sys} shall process payments within 2 seconds.", "The {sys} must process payment transactions in under 2 seconds."),
        ("Users must reset their password via email.", "Users are required to recover their password through email."),
        ("The {sys} shall encrypt all data using AES-256.", "All data must be encrypted by the {sys} using AES-256."),
        ("The database must backup every 12 hours.", "Database backups shall occur automatically every 12 hours."),
        ("The {sys} shall limit login attempts to 5.", "The {sys} should restrict failed logins to a maximum of 5 attempts.")
    ]
    for _ in range(num_pairs_per_class):
        sys1, sys2 = random.choice(SYSTEM_NOUNS), random.choice(SYSTEM_NOUNS)
        a, b = random.choice(dup_bases)
        pairs.append({"requirement_a": a.format(sys=sys1), "requirement_b": b.format(sys=sys2), "relationship": "Duplicate"})

    # 2. SIMILAR (Same intent, but distinct requirements)
    sim_bases = [
        ("The {sys} shall allow users to export reports to PDF.", "The {sys} must provide a feature to download reports in PDF format."),
        ("Users can filter search results by price.", "The {sys} shall enable filtering of search results based on price range."),
        ("The {sys} shall send an email upon registration.", "Users must receive an email confirmation after signing up.")
    ]
    for _ in range(num_pairs_per_class):
        sys1, sys2 = random.choice(SYSTEM_NOUNS), random.choice(SYSTEM_NOUNS)
        a, b = random.choice(sim_bases)
        pairs.append({"requirement_a": a.format(sys=sys1), "requirement_b": b.format(sys=sys2), "relationship": "Similar"})

    # 3. CONTRADICTORY (Mutually exclusive logic)
    cont_bases = [
        ("The {sys} shall require users to change passwords every 30 days.", "Users shall never be required to change their passwords."),
        ("The {sys} must be accessible 24/7 without downtime.", "The {sys} will be offline for maintenance every Sunday."),
        ("The {sys} shall allow anonymous access to all features.", "Users must authenticate to access any feature."),
        ("The {sys} must store data locally on the device.", "All user data shall be stored exclusively in the cloud."),
        ("The {sys} shall support only English language.", "The {sys} must support multiple languages including Spanish and French.")
    ]
    for _ in range(num_pairs_per_class):
        sys1, sys2 = random.choice(SYSTEM_NOUNS), random.choice(SYSTEM_NOUNS)
        a, b = random.choice(cont_bases)
        pairs.append({"requirement_a": a.format(sys=sys1), "requirement_b": b.format(sys=sys2), "relationship": "Contradictory"})

    # 4. NEUTRAL (Completely unrelated)
    neut_a = [
        "The {sys} shall process payments within 2 seconds.",
        "The database must backup every 12 hours.",
        "Users shall be able to filter search results by price.",
        "The {sys} shall send an email notification upon registration.",
        "The API shall return data in JSON format."
    ]
    neut_b = [
        "The user profile must display a profile picture.",
        "The {sys} shall calculate shipping costs based on weight.",
        "Admins can export sales reports to CSV.",
        "The {sys} shall support dark mode.",
        "Passwords must contain at least one special character."
    ]
    for _ in range(num_pairs_per_class):
        sys1, sys2 = random.choice(SYSTEM_NOUNS), random.choice(SYSTEM_NOUNS)
        a, b = random.choice(neut_a), random.choice(neut_b)
        pairs.append({"requirement_a": a.format(sys=sys1), "requirement_b": b.format(sys=sys2), "relationship": "Neutral"})

    df = pd.DataFrame(pairs)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    return df

if __name__ == "__main__":
    output_dir = Path("data/synthetic")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    df = generate_pairwise_dataset(200)
    output_path = output_dir / "pairwise_requirements.csv"
    df.to_csv(output_path, index=False)
    
    print(f"Generated {len(df)} pairwise records.")
    print(f"Saved to: {output_path}")
    print("\nRelationship Distribution:")
    print(df['relationship'].value_counts())