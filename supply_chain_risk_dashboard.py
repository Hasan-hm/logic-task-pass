# Colab setup: uncomment the line below on first run
# !pip install -q gradio anthropic pandas

import json
import os
import pandas as pd
import gradio as gr
import anthropic

# --- LLM engine ---------------------------------------------------------
# Default: Haiku, to keep dev iteration cheap and avoid rate/token limits.
# Swap to "claude-sonnet-5" (or "claude-opus-5" for max quality) for production runs.
MODEL_ID = "claude-haiku-4-5"
MAX_TOKENS = 800

os.environ.setdefault("ANTHROPIC_API_KEY", "")  # set your key here or via env/Colab secret
client = anthropic.Anthropic()

SYSTEM_PROMPT = (
    "You are a supply-chain risk analyst. Given supplier data as compact JSON, "
    "produce a CONCISE, STRUCTURED bullet-point assessment. No prose paragraphs. "
    "For EACH supplier output:\n"
    "- **Risk Score**: Low/Medium/High (one word, with a 1-line quantitative justification)\n"
    "- **Bottleneck Prediction**: the most likely operational failure point\n"
    "- **Cost-Reduction Action**: one specific, actionable step\n"
    "Keep total output under 700 words. Use markdown bullets, no filler."
)

# --- Mock data -----------------------------------------------------------
oil_gas_df = pd.DataFrame([
    {"Supplier_ID": "OG-101", "Name": "DesertValve Industries", "On_Time_Rate": 0.91,
     "Defect_Rate": 0.018, "Compliance": "API Q1", "Field_Notes": "Occasional gasket failures in high-heat wellheads"},
    {"Supplier_ID": "OG-102", "Name": "SandRunner Logistics", "On_Time_Rate": 0.78,
     "Defect_Rate": 0.03, "Compliance": "ISO 9001", "Field_Notes": "Convoy delays during sandstorm season, single-route dependency"},
    {"Supplier_ID": "OG-103", "Name": "RigForce Workforce Solutions", "On_Time_Rate": 0.95,
     "Defect_Rate": 0.005, "Compliance": "API Q1 / ISO 45001", "Field_Notes": "Crew rotation gaps during peak heat months"},
])

aerospace_df = pd.DataFrame([
    {"Supplier_ID": "AS-201", "Name": "OrbitLink CubeSat Comms", "On_Time_Rate": 0.88,
     "Defect_Rate": 0.012, "Compliance": "AS9100D", "Field_Notes": "RF module yield drops on rush orders"},
    {"Supplier_ID": "AS-202", "Name": "Apex Propulsion Systems", "On_Time_Rate": 0.82,
     "Defect_Rate": 0.021, "Compliance": "AS9100D", "Field_Notes": "Single-source rare-earth magnet supplier, long lead times"},
    {"Supplier_ID": "AS-203", "Name": "Helios Precision Components", "On_Time_Rate": 0.93,
     "Defect_Rate": 0.008, "Compliance": "AS9100D / ITAR", "Field_Notes": "Strong QA but limited surge capacity"},
])


# --- AI assessment ---------------------------------------------------------
def run_risk_assessment(df: pd.DataFrame, industry: str) -> str:
    payload = json.dumps(df.to_dict(orient="records"), separators=(",", ":"))
    try:
        response = client.messages.create(
            model=MODEL_ID,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": f"Industry: {industry}\nSupplier data (JSON): {payload}"}],
        )
        return "".join(b.text for b in response.content if b.type == "text")
    except anthropic.APIError as e:
        return f"**Error calling Claude API:** {e}"


# --- UI ---------------------------------------------------------------
with gr.Blocks(title="AI Supply Chain Risk Evaluator") as demo:
    gr.Markdown("# AI Supply Chain Risk Evaluator")

    with gr.Tab("Oil & Gas"):
        og_table = gr.Dataframe(value=oil_gas_df, interactive=False)
        og_button = gr.Button("Run AI Risk Assessment")
        og_output = gr.Markdown()
        og_button.click(fn=lambda: run_risk_assessment(oil_gas_df, "Oil & Gas"), outputs=og_output)

    with gr.Tab("Aerospace"):
        as_table = gr.Dataframe(value=aerospace_df, interactive=False)
        as_button = gr.Button("Run AI Risk Assessment")
        as_output = gr.Markdown()
        as_button.click(fn=lambda: run_risk_assessment(aerospace_df, "Aerospace"), outputs=as_output)

demo.launch(debug=True)
