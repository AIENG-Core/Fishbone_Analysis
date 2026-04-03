

"""
Fishbone Incident Analyser — Free Cause Analysis
=================================================
AI-powered root cause analysis using local Ollama LLM.

SETUP:
1. Install Ollama:   https://ollama.com/download
2. Pull model:       ollama pull gemma3:4b
3. Install deps:     pip install fastapi uvicorn
4. Run:              python api.py
5. Open:             http://localhost:8001/docs
"""


# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import json
# import re
# import urllib.request
# import urllib.error

# # ================= CONFIG =================

# OLLAMA_HOST  = "http://localhost:11434"
# OLLAMA_MODEL = "gemma3:4b"

# # ================= CAUSE LIBRARY =================

# CATEGORIES: dict[str, list[str]] = {
#     "People": [
#         "Inadequate Knowledge Transfer (7.1)",
#         "Inadequate recall of Training Material (7.2)",
#         "Inadequate Training Effort (7.3)",
#         "No Training Provided (7.4)",
#         "Other Permanent Physical Capability (1.5)",
#         "Temporary Disability (1.6)",
#         "Personal Protective Equipment not used (3.2)",
#         "Improper Position for Task (1.5)",
#         "Fatigue (2.2)",
#         "Use of Drug or Alcohol Abuse (4.7)",
#         "Poor Judgement (3.1)",
#         "Memory Failure (3.2)",
#         "Poor Coordination (3.3)",
#         "Restricted body movement (1.8)",
#         "Inappropriate Aggression (5.5)",
#         "Incorrect Instructions (15.8)",
#         "Operation of Equipment without Authority (11.4)",
#     ],
#     "Process": [
#         "Inadequate development of PSP (14.2)",
#         "Inadequate Evaluation of Change (10.8)",
#         "Inadequate Management of Change System (8.5)",
#         "Inadequate Supervisory example (5.2)",
#         "Inadequate identification of worksite / job hazards (8.4)",
#         "Inadequate assessment of required skills (6.1)",
#         "Lack of Coaching on skill (6.4)",
#         "Inadequate Work Planning (11.1)",
#         "Inadequate horizontal communication between peers (15.1)",
#         "Inadequate Contractor Selection (9.3)",
#         "Inadequate Warning System (5.5)",
#     ],
#     "Material": [
#         "Inadequate Tools (6.5)",
#         "Defective Tools (6.4)",
#         "Defective personal protective equipment (5.4)",
#         "Improper Storage of Material or Spare (12.5)",
#         "Inadequate Repair (11.3)",
#         "Improper handling of Material (12.4)",
#         "Inadequate Material Packaging (12.6)",
#     ],
#     "Measurement": [
#         "Inadequate Performance Measurement (8.8)",
#         "Inadequate monitoring of initial operation (10.7)",
#         "Improper performance is rewarded (5.1)",
#         "Inadequate contractor pre qualifications (9.2)",
#     ],
#     "Equipment": [
#         "Improper use of Equipment (2.1)",
#         "Inadequate Preventive Maintenance (11.2)",
#         "Operation of equipment at improper speed (2.6)",
#         "Inadequate Equipment (6.2)",
#         "Use of defective Equipment (2.3)",
#         "Inadequate Safety Devices (5.8)",
#         "Defective Safety Devices (5.9)",
#         "Inadequate adjustment / repair / maintenance (13.5)",
#     ],
#     "Environment": [
#         "Inadequate or excessive Illumination (8.1)",
#         "Congestion or Restricted Movement (7.8)",
#         "Slippery floors or walkway (7.7)",
#         "Temperature Extremes (7.6)",
#         "Exposure to Noise (7.2)",
#         "Inadequate Ventilation (8.3)",
#         "Unprotected height (8.4)",
#         "Exposure to Radiation (7.5)",
#     ],
# }

# # ================= CAUSE VALIDATOR =================

# def _match_cause(raw: str, category: str) -> str | None:
#     """Match LLM-returned cause name to official library. Prevents hallucination."""
#     name    = raw.strip()
#     lower   = name.lower()
#     official = CATEGORIES.get(category, [])

#     for c in official:
#         if c.lower() == lower:
#             return c

#     for c in official:
#         if lower in c.lower() or c.lower() in lower:
#             return c

#     name_words = set(w for w in lower.split() if len(w) > 2)
#     for c in official:
#         c_words = set(w for w in c.lower().split() if len(w) > 2)
#         if len(name_words & c_words) >= 2:
#             return c

#     return None

# # ================= PROMPT =================

# def _build_prompt(incident: str) -> str:
#     blocks = []
#     for cat, causes in CATEGORIES.items():
#         lines = "\n".join(f"  {i+1}. {c}" for i, c in enumerate(causes))
#         blocks.append(f"{cat}:\n{lines}")
#     cause_list = "\n\n".join(blocks)

#     return f"""You are an industrial safety analyst. Perform a fishbone root cause analysis.

# INCIDENT:
# {incident}

# CAUSE LIST — select ONLY from these exact cause names:

# {cause_list}

# RULES:
# - Select causes clearly supported by the incident description.
# - Use the EXACT cause name as written in the list above.
# - For each cause write 2 sentences explaining how it applies to this incident.
# - Rate relevance: HIGH, MEDIUM, or LOW.
# - If a category has no relevant causes return an empty list [].
# - Do NOT invent causes not in the list.
# - Output JSON only.

# JSON FORMAT:
# {{
#   "summary": "1-2 sentences summarizing the root causes.",
#   "categories": {{
#     "People":      [ {{ "cause": "exact name from list", "description": "2 sentences.", "relevance": "HIGH" }} ],
#     "Process":     [],
#     "Material":    [],
#     "Measurement": [],
#     "Equipment":   [],
#     "Environment": []
#   }}
# }}

# JSON:"""

# # ================= JSON EXTRACTOR =================

# def _extract_json(text: str) -> dict:
#     text = text.strip()
#     text = re.sub(r"^```(?:json)?", "", text, flags=re.MULTILINE).strip()
#     text = re.sub(r"```$",          "", text, flags=re.MULTILINE).strip()

#     try:
#         return json.loads(text)
#     except json.JSONDecodeError:
#         pass

#     start = text.find("{")
#     if start != -1:
#         depth, end = 0, -1
#         for i, ch in enumerate(text[start:], start=start):
#             if   ch == "{": depth += 1
#             elif ch == "}":
#                 depth -= 1
#                 if depth == 0:
#                     end = i + 1
#                     break
#         if end != -1:
#             try:
#                 return json.loads(text[start:end])
#             except json.JSONDecodeError:
#                 pass

#         frag = text[start:].rstrip().rstrip(",")
#         if len(re.findall(r'(?<!\\)"', frag)) % 2 != 0:
#             frag += '"'
#         frag += "]" * (frag.count("[") - frag.count("]"))
#         frag += "}" * (frag.count("{") - frag.count("}"))
#         try:
#             return json.loads(frag)
#         except json.JSONDecodeError:
#             pass

#     raise ValueError(f"No valid JSON found:\n{text[:300]}")

# # ================= OLLAMA CALL =================

# def _call_ollama(prompt: str) -> str:
#     payload = json.dumps({
#         "model":  OLLAMA_MODEL,
#         "prompt": prompt,
#         "stream": False,
#         "options": {
#             "temperature":    0,
#             "num_predict":    2000,
#             "top_k":          1,
#             "top_p":          1.0,
#             "repeat_penalty": 1.1,
#         }
#     }).encode("utf-8")

#     req = urllib.request.Request(
#         url     = f"{OLLAMA_HOST}/api/generate",
#         data    = payload,
#         headers = {"Content-Type": "application/json"},
#         method  = "POST",
#     )

#     try:
#         with urllib.request.urlopen(req, timeout=180) as resp:
#             return json.loads(resp.read().decode())["response"]
#     except urllib.error.URLError as exc:
#         raise HTTPException(
#             status_code = 503,
#             detail      = f"Ollama not reachable: {exc}\nFix: ollama serve && ollama pull {OLLAMA_MODEL}"
#         )

# # ================= RESPONSE BUILDER =================

# def _build_response(incident: str, llm: dict) -> dict:
#     summary  = str(llm.get("summary", "")).strip() or "No summary provided."
#     raw_cats = llm.get("categories", {})
#     order    = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}

#     by_category: dict[str, list[dict]] = {}

#     for cat in CATEGORIES:
#         raw_list = raw_cats.get(cat, [])
#         if not isinstance(raw_list, list):
#             raw_list = []

#         clean: list[dict] = []
#         seen:  set[str]   = set()

#         for item in raw_list:
#             if not isinstance(item, dict):
#                 continue

#             matched = _match_cause(str(item.get("cause", "")), cat)
#             if not matched or matched in seen:
#                 continue
#             seen.add(matched)

#             rel = str(item.get("relevance", "MEDIUM")).upper()
#             if rel not in {"HIGH", "MEDIUM", "LOW"}:
#                 rel = "MEDIUM"

#             clean.append({
#                 "cause":       matched,
#                 "description": str(item.get("description", "")).strip(),
#                 "relevance":   rel,
#             })

#         clean.sort(key=lambda x: order.get(x["relevance"], 1))
#         by_category[cat] = clean

#     return {
#         "incident":               incident,
#         "summary":                summary,
#         "categories_with_causes": [k for k, v in by_category.items() if v],
#         "categories_empty":       [k for k, v in by_category.items() if not v],
#         "by_category":            by_category,
#     }

# # ================= PYDANTIC =================

# class IncidentRequest(BaseModel):
#     incident: str

# class CauseItem(BaseModel):
#     cause:       str
#     description: str
#     relevance:   str

# class FishboneResponse(BaseModel):
#     incident:               str
#     summary:                str
#     categories_with_causes: list[str]
#     categories_empty:       list[str]
#     by_category:            dict[str, list[CauseItem]]

# # ================= FASTAPI =================

# app = FastAPI(
#     title       = "Fishbone Incident Analyser",
#     description = (
#         "Root cause analysis using predefined cause library.\n\n"
#         "Returns causes **by category only**.\n\n"
#         f"Model: `{OLLAMA_MODEL}` via Ollama.\n\n"
#         "```bash\nollama pull gemma3:4b\npython api.py\n```"
#     ),
#     version = "5.0",
# )

# @app.post("/analyse", response_model=FishboneResponse)
# def analyse_incident(req: IncidentRequest):
#     """
#     Analyse a safety incident using 6M fishbone framework.
#     Returns causes grouped by category. Empty categories return [].

#     Example:
#     ```json
#     { "incident": "Worker fell from scaffold. No harness worn. Wet surface." }
#     ```
#     """
#     if not req.incident.strip():
#         raise HTTPException(status_code=400, detail="Incident cannot be empty.")

#     try:
#         raw      = _call_ollama(_build_prompt(req.incident.strip()))
#         llm_data = _extract_json(raw)
#     except ValueError as exc:
#         raise HTTPException(status_code=500, detail=str(exc))

#     return _build_response(req.incident.strip(), llm_data)




# if __name__ == "__main__":
#     import uvicorn
#     print(f"\n{'='*50}")
#     print(f"  Fishbone Analyser  |  {OLLAMA_MODEL}")
#     print(f"  Docs   : http://localhost:8001/docs")
#     print(f"  Health : http://localhost:8001/health")
#     print(f"{'='*50}\n")
#     uvicorn.run("api:app", host="localhost", port=8001, reload=False)



from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
import re
import urllib.request
import urllib.error
import os

# ================= CONFIG =================

OLLAMA_HOST  = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:4b")

# ================= CAUSE LIBRARY =================

CATEGORIES: dict[str, list[str]] = {
    "People": [
        "Inadequate Knowledge Transfer (7.1)",
        "Inadequate recall of Training Material (7.2)",
        "Inadequate Training Effort (7.3)",
        "No Training Provided (7.4)",
        "Other Permanent Physical Capability (1.5)",
        "Temporary Disability (1.6)",
        "Personal Protective Equipment not used (3.2)",
        "Improper Position for Task (1.5)",
        "Fatigue (2.2)",
        "Use of Drug or Alcohol Abuse (4.7)",
        "Poor Judgement (3.1)",
        "Memory Failure (3.2)",
        "Poor Coordination (3.3)",
        "Restricted body movement (1.8)",
        "Inappropriate Aggression (5.5)",
        "Incorrect Instructions (15.8)",
        "Operation of Equipment without Authority (11.4)",
    ],
    "Process": [
        "Inadequate development of PSP (14.2)",
        "Inadequate Evaluation of Change (10.8)",
        "Inadequate Management of Change System (8.5)",
        "Inadequate Supervisory example (5.2)",
        "Inadequate identification of worksite / job hazards (8.4)",
        "Inadequate assessment of required skills (6.1)",
        "Lack of Coaching on skill (6.4)",
        "Inadequate Work Planning (11.1)",
        "Inadequate horizontal communication between peers (15.1)",
        "Inadequate Contractor Selection (9.3)",
        "Inadequate Warning System (5.5)",
    ],
    "Material": [
        "Inadequate Tools (6.5)",
        "Defective Tools (6.4)",
        "Defective personal protective equipment (5.4)",
        "Improper Storage of Material or Spare (12.5)",
        "Inadequate Repair (11.3)",
        "Improper handling of Material (12.4)",
        "Inadequate Material Packaging (12.6)",
    ],
    "Measurement": [
        "Inadequate Performance Measurement (8.8)",
        "Inadequate monitoring of initial operation (10.7)",
        "Improper performance is rewarded (5.1)",
        "Inadequate contractor pre qualifications (9.2)",
    ],
    "Equipment": [
        "Improper use of Equipment (2.1)",
        "Inadequate Preventive Maintenance (11.2)",
        "Operation of equipment at improper speed (2.6)",
        "Inadequate Equipment (6.2)",
        "Use of defective Equipment (2.3)",
        "Inadequate Safety Devices (5.8)",
        "Defective Safety Devices (5.9)",
        "Inadequate adjustment / repair / maintenance (13.5)",
    ],
    "Environment": [
        "Inadequate or excessive Illumination (8.1)",
        "Congestion or Restricted Movement (7.8)",
        "Slippery floors or walkway (7.7)",
        "Temperature Extremes (7.6)",
        "Exposure to Noise (7.2)",
        "Inadequate Ventilation (8.3)",
        "Unprotected height (8.4)",
        "Exposure to Radiation (7.5)",
    ],
}

# ================= REQUEST MODEL =================

class IncidentRequest(BaseModel):
    incident: str
    location: Optional[str] = None
    department: Optional[str] = None
    equipment_involved: Optional[str] = None
    material_involved: Optional[str] = None
    personnel_involved: Optional[str] = None
    witnesses: Optional[str] = None
    time_of_incident: Optional[str] = None
    reported_by: Optional[str] = None
    incident_type: Optional[str] = None
    nature_of_injury: Optional[str] = None
    shift: Optional[str] = None
    activity_at_time_of_incident: Optional[str] = None
    sequential_occurrence: Optional[str] = None
    observations: Optional[str] = None
    immediate_action_taken: Optional[str] = None

# ================= CONTEXT BUILDER =================

def _build_context(req: IncidentRequest) -> str:
    fields = {
        "Incident": req.incident,
        "Location": req.location,
        "Department": req.department,
        "Equipment": req.equipment_involved,
        "Material": req.material_involved,
        "Personnel": req.personnel_involved,
        "Witnesses": req.witnesses,
        "Time": req.time_of_incident,
        "Reported By": req.reported_by,
        "Incident Type": req.incident_type,
        "Injury": req.nature_of_injury,
        "Shift": req.shift,
        "Activity": req.activity_at_time_of_incident,
        "Sequence": req.sequential_occurrence,
        "Observations": req.observations,
        "Immediate Action": req.immediate_action_taken,
    }

    return "\n".join(f"{k}: {v}" for k, v in fields.items() if v)

# ================= CAUSE VALIDATOR =================

def _match_cause(raw: str, category: str) -> str | None:
    name = raw.strip()
    lower = name.lower()
    official = CATEGORIES.get(category, [])

    for c in official:
        if c.lower() == lower:
            return c

    for c in official:
        if lower in c.lower() or c.lower() in lower:
            return c

    name_words = set(w for w in lower.split() if len(w) > 2)
    for c in official:
        c_words = set(w for w in c.lower().split() if len(w) > 2)
        if len(name_words & c_words) >= 2:
            return c

    return None

# ================= PROMPT =================

def _build_prompt(req: IncidentRequest) -> str:
    context = _build_context(req)

    blocks = []
    for cat, causes in CATEGORIES.items():
        lines = "\n".join(f"  {i+1}. {c}" for i, c in enumerate(causes))
        blocks.append(f"{cat}:\n{lines}")
    cause_list = "\n\n".join(blocks)

    return f"""You are an industrial safety analyst. Perform a fishbone root cause analysis.

INCIDENT DETAILS:
{context}

CAUSE LIST — select ONLY from these exact cause names:

{cause_list}

RULES:
- Select causes clearly supported by the incident description.
- Use the EXACT cause name.
- Explain each cause in 2 sentences.
- If none, return [].
- Do NOT invent causes.
- Output JSON only.

JSON FORMAT:
{{
  "summary": "1-2 sentences summarizing the root causes.",
  "categories": {{
    "People": [{{ "cause": "exact name", "description": "text" }}],
    "Process": [],
    "Material": [],
    "Measurement": [],
    "Equipment": [],
    "Environment": []
  }}
}}

JSON:"""

# ================= JSON EXTRACTOR =================

def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text, flags=re.MULTILINE).strip()
    text = re.sub(r"```$", "", text, flags=re.MULTILINE).strip()

    return json.loads(text)

# ================= OLLAMA CALL =================

def _call_ollama(prompt: str) -> str:
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "num_predict": 2000,
            "top_k": 1,
            "top_p": 1.0,
            "repeat_penalty": 1.1,
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        url=f"{OLLAMA_HOST}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())["response"]

# ================= RESPONSE BUILDER =================

def _build_response(req: IncidentRequest, llm: dict) -> dict:
    raw_cats = llm.get("categories", {})

    by_category: dict[str, list[dict]] = {}

    for cat in CATEGORIES:
        raw_list = raw_cats.get(cat, [])
        if not isinstance(raw_list, list):
            raw_list = []

        clean = []
        seen = set()

        for item in raw_list:
            if not isinstance(item, dict):
                continue

            matched = _match_cause(str(item.get("cause", "")), cat)
            if not matched or matched in seen:
                continue
            seen.add(matched)

            clean.append({
                "cause": matched,
                "description": str(item.get("description", "")).strip(),
            })

        by_category[cat] = clean

    return {
        "incident": req.incident,
        "summary": str(llm.get("summary", "")).strip(),
        "categories_with_causes": [k for k, v in by_category.items() if v],
        "categories_empty": [k for k, v in by_category.items() if not v],
        "by_category": by_category,
    }

# ================= PYDANTIC =================

class CauseItem(BaseModel):
    cause: str
    description: str

class FishboneResponse(BaseModel):
    incident: str
    summary: str
    categories_with_causes: list[str]
    categories_empty: list[str]
    by_category: dict[str, list[CauseItem]]

# ================= FASTAPI =================

app = FastAPI(title="Fishbone Incident Analyser", version="6.0")

@app.post("/analyse", response_model=FishboneResponse)
def analyse_incident(req: IncidentRequest):
    if not req.incident.strip():
        raise HTTPException(status_code=400, detail="Incident cannot be empty.")

    raw = _call_ollama(_build_prompt(req))
    llm_data = _extract_json(raw)

    return _build_response(req, llm_data)

# ================= RUN =================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="localhost", port=8001, reload=False)