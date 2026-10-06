import random
import pandas as pd
from pathlib import Path
from typing import List, Tuple
from schemas import RequirementRecord, ClarityLabel, AmbiguityType

# --- Configuration ---
DOMAINS = [
    "E-commerce", "Banking", "Healthcare", "Education", 
    "Transportation", "Food Delivery", "IoT", "Social Media", 
    "Cloud Systems", "Mobile Applications"
]

SYSTEM_NOUNS = ["application", "system", "platform", "software", "module", "service"]

# Templates: (template_string, [ambiguity_types], [filler_words])
AMBIGUOUS_TEMPLATES = [
    ("The {system} shall respond {adv}.", [AmbiguityType.PERFORMANCE], ["quickly", "fast", "rapidly", "instantly", "without delay"]),
    ("The {system} must support {adj} users.", [AmbiguityType.QUANTITY], ["many", "a large number of", "several", "numerous", "multiple"]),
    ("The {system} shall be highly {adj}.", [AmbiguityType.SUBJECTIVE], ["user-friendly", "intuitive", "beautiful", "efficient", "effective"]),
    ("The {system} should handle {adj} data.", [AmbiguityType.SIZE], ["large", "massive", "huge", "substantial", "significant"]),
    ("The {system} must be {adj}.", [AmbiguityType.SECURITY], ["secure", "safe", "protected", "unhackable", "impenetrable"]),
    ("The {system} shall process requests {adv}.", [AmbiguityType.TEMPORAL], ["soon", "regularly", "periodically", "frequently", "occasionally"]),
    ("The {system} needs to be {adj}.", [AmbiguityType.VAGUE_TERMINOLOGY], ["good", "better", "adequate", "sufficient", "appropriate"]),
]

CLEAR_TEMPLATES = [
    "The {system} shall process the payment transaction within {num} seconds.",
    "The {system} must support up to {num} concurrent users without performance degradation.",
    "Users shall be able to reset their password via email within {num} minutes.",
    "The database shall automatically back up every {num} hours.",
    "The {system} shall limit failed login attempts to {num} before locking the account for {num} minutes.",
    "The {system} shall encrypt all user passwords using SHA-256.",
    "The {system} must load the dashboard in under {num} seconds on a 4G network.",
]

INCOMPLETE_TEMPLATES = [
    ("The {system} shall generate reports.", [AmbiguityType.MISSING_CONSTRAINT]),
    ("Users can export data.", [AmbiguityType.MISSING_CONSTRAINT]),
    ("The {system} shall send notifications.", [AmbiguityType.MISSING_CONDITION]),
    ("The {system} must validate user input.", [AmbiguityType.MISSING_CONDITION]),
    ("The {system} should backup data.", [AmbiguityType.MISSING_CONSTRAINT]),
    ("The {system} shall integrate with third-party services.", [AmbiguityType.MISSING_CONSTRAINT]),
]

NON_TESTABLE_TEMPLATES = [
    "The {system} shall be user-friendly.",
    "The {system} should have an intuitive interface.",
    "The {system} must be robust and reliable.",
    "The {system} should be easy to maintain.",
    "The {system} shall provide a seamless user experience.",
    "The {system} must be highly scalable.",
    "The {system} should be architecturally sound.",
]

def generate_clear(system: str) -> RequirementRecord:
    template = random.choice(CLEAR_TEMPLATES)
    # Replace {num} with realistic numbers
    text = template.format(system=system, num=random.randint(2, 60))
    return RequirementRecord(
        requirement_text=text,
        domain=random.choice(DOMAINS),
        clarity_label=ClarityLabel.CLEAR,
        completeness_label="Complete",
        testability_label="Testable"
    )

def generate_ambiguous(system: str) -> RequirementRecord:
    template, amb_types, fillers = random.choice(AMBIGUOUS_TEMPLATES)
    filler = random.choice(fillers)
    
    # Determine which placeholder to use based on the template
    if "{adv}" in template:
        text = template.format(system=system, adv=filler)
    elif "{adj}" in template:
        text = template.format(system=system, adj=filler)
    else:
        text = template.format(system=system)

    return RequirementRecord(
        requirement_text=text,
        domain=random.choice(DOMAINS),
        clarity_label=ClarityLabel.AMBIGUOUS,
        ambiguity_types=amb_types,
        completeness_label="Complete",
        testability_label="Testable" # Ambiguous requirements can technically be tested, but poorly
    )

def generate_incomplete(system: str) -> RequirementRecord:
    template, amb_types = random.choice(INCOMPLETE_TEMPLATES)
    text = template.format(system=system)
    
    return RequirementRecord(
        requirement_text=text,
        domain=random.choice(DOMAINS),
        clarity_label=ClarityLabel.INCOMPLETE,
        ambiguity_types=amb_types,
        completeness_label="Incomplete",
        testability_label="Non-testable"
    )

def generate_non_testable(system: str) -> RequirementRecord:
    template = random.choice(NON_TESTABLE_TEMPLATES)
    text = template.format(system=system)
    
    return RequirementRecord(
        requirement_text=text,
        domain=random.choice(DOMAINS),
        clarity_label=ClarityLabel.NON_TESTABLE,
        ambiguity_types=[AmbiguityType.SUBJECTIVE],
        completeness_label="Complete",
        testability_label="Non-testable"
    )

def generate_dataset(num_samples: int = 1000) -> pd.DataFrame:
    records = []
    samples_per_class = num_samples // 4
    
    print(f"Generating {num_samples} synthetic requirements...")
    
    for _ in range(samples_per_class):
        system = random.choice(SYSTEM_NOUNS)
        records.append(generate_clear(system).model_dump())
        
        system = random.choice(SYSTEM_NOUNS)
        records.append(generate_ambiguous(system).model_dump())
        
        system = random.choice(SYSTEM_NOUNS)
        records.append(generate_incomplete(system).model_dump())
        
        system = random.choice(SYSTEM_NOUNS)
        records.append(generate_non_testable(system).model_dump())

    df = pd.DataFrame(records)
    # Shuffle the dataset
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    return df

if __name__ == "__main__":
    # Ensure output directory exists
    output_dir = Path("data/synthetic")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate and save
    df = generate_dataset(1000)
    output_path = output_dir / "synthetic_requirements.csv"
    df.to_csv(output_path, index=False)
    
    print(f"Successfully generated {len(df)} records.")
    print(f"Saved to: {output_path}")
    print("\nClass Distribution:")
    print(df['clarity_label'].value_counts())