import streamlit as st
import re
import requests

from retriever import GSTRetriever
from goods_retriever import GoodsRetriever
from gst_engine import calculate_gst
from rewriter import rewrite_query

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet



@st.cache_resource
def load_models():
    service_ret = GSTRetriever("gst_services_cleaned.csv")
    goods_ret = GoodsRetriever("GST_Goods_Rates.csv")
    return service_ret, goods_ret

service_retriever, goods_retriever = load_models()



def extract_price(query):
    numbers = re.findall(r'\d+', query)
    return int(numbers[0]) if numbers else None


def extract_rate(row):
    try:
        for col in row.index:
            if "igst" in col.lower():
                val = str(row[col]).replace('%', '').strip()
                if val and val.lower() != "nan":
                    return float(val)

        cgst, sgst = 0, 0

        for col in row.index:
            if "cgst" in col.lower():
                cgst = float(str(row[col]).replace('%', '').strip())
            if "sgst" in col.lower():
                sgst = float(str(row[col]).replace('%', '').strip())

        return cgst + sgst
    except:
        return 0.0


def clean_goods_query(query):
    query = query.lower()

    mapping = {
        "curd": "curd lassi buttermilk yoghurt",
        "milk": "milk cream dairy",
        "rice": "rice grain cereal",
        "paneer": "paneer cheese",
        "kidney": "artificial kidney medical device",
        "stent": "coronary stent medical",
        "charger": "charger charging device",
        "bicycle": "bicycle cycle",
        "car": "motor vehicle automobile",
        "bike": "motorcycle two wheeler",
        "phone": "mobile smartphone",
        "laptop": "computer laptop",
    }

    for key in mapping:
        if key in query:
            return mapping[key]

    query = re.sub(r'\d+', '', query)
    return query.strip()



def generate_invoice(description, rate, price, gst, total):
    file_path = "invoice.pdf"

    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph("GST Invoice", styles['Title']))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"Item: {description}", styles['Normal']))
    content.append(Paragraph(f"GST Rate: {rate}%", styles['Normal']))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"Base Price: ₹{price}", styles['Normal']))
    content.append(Paragraph(f"GST Amount: ₹{gst:.2f}", styles['Normal']))
    content.append(Paragraph(f"Total Amount: ₹{total:.2f}", styles['Normal']))

    doc.build(content)
    return file_path



def get_business_help(query):
    prompt = f"""
You are an expert in Indian GST.

Give a SHORT and CLEAR explanation.

Query: {query}
"""

    try:
        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": "phi3",   
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 120   
                }
            },
            timeout=120
        )

        if response.status_code != 200:
            return f"❌ Error: {response.text}"

        data = response.json()

        if "response" not in data:
            return f"❌ Invalid response: {data}"

        return data["response"]

    except Exception as e:
        return f"❌ Connection error: {str(e)}"



def verify_gst(price, given_gst, rate):
    actual = (price * rate) / 100

    if abs(actual - given_gst) < 1:
        return "✅ GST is correct"
    else:
        return f"❌ Incorrect GST. Expected ₹{actual:.2f}, got ₹{given_gst}"



st.title("💰 AI GST Assistant")

mode = st.selectbox(
    "Select Mode",
    ["GST Calculator", "Business Help", "Customer Verification"]
)



if mode == "GST Calculator":

    query = st.text_input("Enter query (e.g. curd 500)")
    type_ = st.selectbox("Select Type", ["Service", "Goods"])

    if st.button("Calculate GST"):

        if not query:
            st.error("Enter query")
        else:
            price = extract_price(query)

            if price is None:
                st.error("Include price (e.g. 1000)")
            else:

                if type_.lower() == "goods":

                    clean_query = clean_goods_query(query)
                    candidates = goods_retriever.get_top_k(clean_query, k=5)

                    candidates = [
                        c for c in candidates
                        if "nil" not in c["text"].lower()
                        and "all goods" not in c["text"].lower()
                    ]

                    if not candidates:
                        st.error("No goods match found")
                    else:
                        st.write("### 🔍 Top Matches")
                        for i, c in enumerate(candidates[:3]):
                            st.write(f"{i+1}. {c['text']}")

                        best_row = candidates[0]["row"]

                        description = best_row.get("Description of Goods", "Unknown")

                        rate = extract_rate(best_row)
                        gst, total = calculate_gst(price, rate)

                        st.success("✅ Result")
                        st.write(f"**Match:** {description}")
                        st.write(f"**Rate:** {rate}%")
                        st.write(f"Base: ₹{price}")
                        st.write(f"GST: ₹{gst:.2f}")
                        st.write(f"Total: ₹{total:.2f}")

                        path = generate_invoice(description, rate, price, gst, total)
                        with open(path, "rb") as f:
                            st.download_button("📄 Download Invoice", f, "invoice.pdf")

                else:

                    rewritten_query = rewrite_query(query)
                    candidates = service_retriever.get_top_k(rewritten_query, k=3)

                    if not candidates:
                        st.error("No service match found")
                    else:
                        best_row = candidates[0]["row"]

                        rate = extract_rate(best_row)
                        gst, total = calculate_gst(price, rate)

                        st.success("✅ Result")
                        st.write(f"**Match:** {best_row['Description of Service']}")
                        st.write(f"**Rate:** {rate}%")
                        st.write(f"Base: ₹{price}")
                        st.write(f"GST: ₹{gst:.2f}")
                        st.write(f"Total: ₹{total:.2f}")



elif mode == "Business Help":

    q = st.text_input("Ask GST-related question")

    if st.button("Get Guidance"):
        if q:
            st.write(get_business_help(q))



else:

    product = st.text_input("Enter product (e.g. curd)")
    price = st.number_input("Price", min_value=0.0)
    gst_given = st.number_input("GST charged in bill", min_value=0.0)

    if st.button("Verify GST"):

        if product:
            product = clean_goods_query(product)

            candidates = goods_retriever.get_top_k(product, k=5)

            candidates = [
                c for c in candidates
                if "nil" not in c["text"].lower()
                and "all goods" not in c["text"].lower()
            ]

            if not candidates:
                st.error("No match found")
            else:
                row = candidates[0]["row"]
                rate = extract_rate(row)

                st.write(f"Detected Rate: {rate}%")
                st.write(verify_gst(price, gst_given, rate))