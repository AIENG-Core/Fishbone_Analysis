#constants.py
FISHBONE = {
    "People": [
        "Lack of Training", "Inadequate Manpower",
        "Improper Motivation", "Lack of Experience",
        "Human Factors", "Eyes not on task",
        "Inadequate Physical Capability", "Fatigue",
        "Drug or Alcohol Abuse", "Mental Stress",
        "Poor Judgement", "Memory Failure",
        "Poor Reaction Time", "Vision Deficiency",
        "Hearing Deficiency", "Restricted body movement",
        "Extreme Boredom", "Aggression",
        "Not using PPE", "Incorrect Instructions"
    ],

    "Process": [
        "Inadequate Management Review",
        "Inadequate Operating Procedure",
        "Inadequate Change Management",
        "Inadequate Supervision",
        "Inadequate hazard identification",
        "Inadequate Assessment of Skills",
        "Lack of Coaching",
        "Lack of Training Need Identification",
        "Inadequate Work Planning",
        "Inadequate Horizontal Deployment of Learnings",
        "Inadequate Display of Information",
        "Inadequate Access Control",
        "Inadequate Warning System"
    ],

    "Material": [
        "Makeshift Tool", "Use of Damaged Tool",
        "Damage / inadequate PPE",
        "Improper Storage of Material",
        "Incorrect part used in assembly",
        "Inadequate Resources",
        "Improper handling of Material",
        "Inadequate Material Packaging",
        "Incompatible Material"
    ],

    "Measurement": [
        "Lack of performance monitoring",
        "Poorly defined KPIs",
        "Rewarding Improper Performance",
        "Inadequate Contractor Performance Evaluation",
        "Inadequate Performance Evaluation",
        "Inadequate monitoring of performance"
    ],

    "Equipment": [
        "Poor Quality",
        "Lack of Preventive Maintenance",
        "Use of Non-Calibrated Equipment",
        "Use of Non-Certified Equipment",
        "Improper Breakdown Maintenance",
        "Bypass Safety Systems",
        "Inadequate Equipment Design",
        "Defective Equipment",
        "Defective Safety Devices"
    ],

    "Environment": [
        "Poor Illumination", "High Wind", "Rain",
        "Congested Workplace", "Slippery Surface",
        "High Temperature", "High Noise",
        "High Vibration", "Inadequate Ventilation",
        "Unprotected height", "Exposure to Radiation"
    ]
}


THRESHOLDS = {
    "People": 0.38,
    "Process": 0.35,
    "Material": 0.32,
    "Measurement": 0.40,
    "Equipment": 0.33,
    "Environment": 0.30
}