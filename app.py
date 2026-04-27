from flask import Flask, render_template, request, jsonify
import os
import json

app = Flask(__name__)

# Load crop data safely
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(BASE_DIR, "data", "crops.json")

try:
    with open(data_path, "r", encoding="utf-8") as f:
        crop_data = json.load(f)
    print(f"✅ Successfully loaded crop data with {len(crop_data)} crops.")
except FileNotFoundError:
    print(f"❌ Error: crops.json not found at {data_path}")
    crop_data = {}
except json.JSONDecodeError as e:
    print(f"❌ JSON Decode Error in crops.json: {e}")
    crop_data = {}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    # Get user message safely
    data = request.get_json(silent=True) or {}
    user_input = data.get("message", "").strip().lower()

    if not user_input:
        return jsonify({
            "reply": "🌾 Please type a message about your crop or symptoms."
        })

    # ================== IMPROVED CROP DETECTION ==================
    detected_crop = None
    user_words = user_input.split()

    # Common variations for better matching
    crop_variations = {
        "lentils": "lentil",
        "grapes": "grapes",
        "grape": "grapes",
        "potatoes": "potato",
        "maize": "maize",
        "corn": "maize"
    }

    # First check for common variations
    for var, actual_crop in crop_variations.items():
        if var in user_input:
            if actual_crop in crop_data:
                detected_crop = actual_crop
                break

    # If no variation matched, check normal crop names
    if not detected_crop:
        for crop in crop_data.keys():
            crop_lower = crop.lower()
            if (crop_lower in user_input or 
                crop_lower + "s" in user_input or 
                crop_lower + "es" in user_input or
                any(crop_lower in word for word in user_words)):
                detected_crop = crop
                break

    if not detected_crop:
        return jsonify({
            "reply": "🌾 Please mention a crop name like **tomato**, **rice**, **wheat**, **potato**, **maize**, **lentil**, **grapes**, **onion**, **banana**, etc."
        })

    # ================== DISEASE MATCHING ==================
    diseases = crop_data[detected_crop].get("diseases", {})

    # 1. Exact disease name match (Highest priority)
    for disease in diseases.keys():
        if disease.lower() in user_input:
            info = diseases[disease]
            response = f"""🌱 **Crop**: {detected_crop.title()}

🦠 **Disease**: {disease.title()}

🔍 **Symptoms**:
{info.get('symptoms', 'Not available')}

⚠️ **Cause**:
{info.get('cause', 'Not available')}

💊 **Recommended Solution**:
{info.get('solution', 'Not available')}
"""
            return jsonify({"reply": response.strip()})

    # 2. Symptom-based matching
    user_words_set = set(user_input.split())

    for disease, info in diseases.items():
        symptoms_text = info.get("symptoms", "").lower()
        symptom_words = set(symptoms_text.split())

        if user_words_set & symptom_words:   # if any common word found
            response = f"""⚠️ **Possible Disease Detected**

🌱 **Crop**: {detected_crop.title()}

🦠 **Disease**: {disease.title()}

🔍 **Symptoms**:
{info.get('symptoms', 'Not available')}

⚠️ **Cause**:
{info.get('cause', 'Not available')}

💊 **Recommended Solution**:
{info.get('solution', 'Not available')}
"""
            return jsonify({"reply": response.strip()})

    # 3. Fallback - Show available diseases
    disease_list = ", ".join(d.title() for d in diseases.keys())

    fallback = f"""🌱 **Crop Detected**: {detected_crop.title()}

I couldn't identify the exact disease from your description.

**Available diseases for {detected_crop.title()}:**
{disease_list}

Try describing the symptoms, for example:
• yellow leaves
• dark spots
• white powder
• wilting
• pustules
"""

    return jsonify({"reply": fallback.strip()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)