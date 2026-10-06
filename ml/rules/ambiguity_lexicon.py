# A configurable, domain-agnostic lexicon of vague terms, their categories, and refinement templates.
# This ensures the system is 100% explainable and deterministic.

AMBIGUITY_LEXICON = {
    # Performance Ambiguity
    "quickly": {
        "category": "Performance Ambiguity",
        "severity": "High",
        "question": "What is the maximum acceptable response time?",
        "unit": "seconds",
        "template": "The {system} shall respond within [VALUE] seconds."
    },
    "fast": {
        "category": "Performance Ambiguity",
        "severity": "High",
        "question": "What is the maximum acceptable response time?",
        "unit": "seconds",
        "template": "The {system} shall respond within [VALUE] seconds."
    },
    "rapidly": {
        "category": "Performance Ambiguity",
        "severity": "High",
        "question": "What is the maximum acceptable response time?",
        "unit": "seconds",
        "template": "The {system} shall respond within [VALUE] seconds."
    },
    
    # Quantity Ambiguity
    "many": {
        "category": "Quantity Ambiguity",
        "severity": "High",
        "question": "What is the minimum number of concurrent users the system must support?",
        "unit": "users",
        "template": "The {system} shall support at least [VALUE] concurrent users."
    },
    "several": {
        "category": "Quantity Ambiguity",
        "severity": "Medium",
        "question": "What is the exact number required?",
        "unit": "units",
        "template": "The {system} shall support exactly [VALUE] units."
    },
    "few": {
        "category": "Quantity Ambiguity",
        "severity": "Medium",
        "question": "What is the maximum number allowed?",
        "unit": "units",
        "template": "The {system} shall support no more than [VALUE] units."
    },
    
    # Temporal Ambiguity
    "soon": {
        "category": "Temporal Ambiguity",
        "severity": "Medium",
        "question": "What is the specific deadline or timeframe?",
        "unit": "days/hours",
        "template": "The {system} shall complete this action within [VALUE] days/hours."
    },
    "regularly": {
        "category": "Temporal Ambiguity",
        "severity": "Medium",
        "question": "What is the exact frequency of this action?",
        "unit": "hours/days",
        "template": "The {system} shall perform this action every [VALUE] hours/days."
    },
    "frequently": {
        "category": "Temporal Ambiguity",
        "severity": "Medium",
        "question": "How often should this occur?",
        "unit": "times/day",
        "template": "The {system} shall perform this action [VALUE] times per day."
    },
    
    # Subjective / Vague Terminology
    "user-friendly": {
        "category": "Subjective Language",
        "severity": "High",
        "question": "What specific, measurable metric defines 'user-friendly' (e.g., max clicks, task completion time)?",
        "unit": "metric",
        "template": "The user shall be able to complete [TASK] within [VALUE] interactions/seconds."
    },
    "secure": {
        "category": "Security Ambiguity",
        "severity": "High",
        "question": "What specific security standard or protocol must be implemented?",
        "unit": "standard",
        "template": "The {system} shall encrypt data using [VALUE] standard."
    },
    "efficient": {
        "category": "Vague Terminology",
        "severity": "Medium",
        "question": "What specific resource constraint defines 'efficient' (e.g., CPU usage, memory)?",
        "unit": "metric",
        "template": "The {system} shall operate using no more than [VALUE]% of CPU/memory."
    },
    "easy": {
        "category": "Subjective Language",
        "severity": "Medium",
        "question": "What specific criteria define 'easy' for the user?",
        "unit": "steps",
        "template": "The user shall be able to complete the task in no more than [VALUE] steps."
    },
    
    # Missing Specifics / Incomplete Requirements (NEW!)
    "reports": {
        "category": "Missing Specifics",
        "severity": "High",
        "question": "What type of reports? What format? How often?",
        "unit": "details",
        "template": "The {system} shall generate [TYPE] reports in [FORMAT] format every [FREQUENCY]."
    },
    "data": {
        "category": "Missing Specifics",
        "severity": "Medium",
        "question": "What specific data fields should be included?",
        "unit": "fields",
        "template": "The {system} shall include the following data fields: [FIELDS]."
    },
    "information": {
        "category": "Missing Specifics",
        "severity": "Medium",
        "question": "What specific information is required?",
        "unit": "info_type",
        "template": "The {system} shall provide [INFO_TYPE] information to the user."
    },
    "notifications": {
        "category": "Missing Specifics",
        "severity": "Medium",
        "question": "How should notifications be delivered? When?",
        "unit": "channel",
        "template": "The {system} shall send [TYPE] notifications via [CHANNEL] when [EVENT] occurs."
    },
    "backup": {
        "category": "Missing Specifics",
        "severity": "High",
        "question": "How often? Where? What retention policy?",
        "unit": "schedule",
        "template": "The {system} shall backup data every [FREQUENCY] to [LOCATION] with a retention period of [DURATION]."
    }
}