import streamlit as st
import re
import requests

from retriever import GSTRetriever
from goods_retriever import GoodsRetriever
from gst_engine import calculate_gst
from llm import generate_response
from rewriter import rewrite_query
from selector import select_best

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


# ======================
# 🔹 LOAD MODELS
# ======================
@st.cache_resource
def load_models():
    service_ret = GSTRetriever("gst_services_cleaned.csv")
    goods_ret = GoodsRetriever("GST_Goods_Rates.csv")
    return service_ret, goods_ret

service_retriever, goods_retriever = load_models()


# ======================
# 🔹 HELPERS
# ======================
def extract_price(query):
    numbers = re.findall(r'\d+', query)
    return int(numbers[0]) if numbers else None


def extract_rate(row):
    try:
        igst = str(row.get("IGST Rate (%)", "")).replace('%', '').strip()
        if igst and igst.lower() != "nan":
            return float(igst)

        cgst = float(str(row.get("CGST Rate (%)", 0)).replace('%', '').strip())
        sgst = float(str(row.get("SGST/UTGST Rate (%)", 0)).replace('%', '').strip())

        return cgst + sgst
    except:
        return 18.0


# ======================
# 🔹 INVOICE
# ======================
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


# ======================
# 🔹 BUSINESS HELP
# ======================
def get_business_help(query):
    prompt = f"""
You are an expert in Indian GST.

Explain clearly:
- GST rules
- Legal terms
- Business guidance

Query: {query}
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt, "stream": False}
        )
        return response.json()["response"]
    except:
        return "⚠️ Could not fetch guidance."


# ======================
# 🔹 VERIFY GST
# ======================
def verify_gst(price, given_gst, rate):
    actual = (price * rate) / 100

    if abs(actual - given_gst) < 1:
        return "✅ GST is correct"
    else:
        return f"❌ Incorrect GST. Expected ₹{actual:.2f}, got ₹{given_gst}"


# ======================
# 🔥 UI
# ======================
st.title("💰 AI GST Assistant (Goods + Services)")

mode = st.selectbox(
    "Select Mode",
    ["GST Calculator", "Business Help", "Customer Verification"]
)


# ======================
# 🔥 GST CALCULATOR
# ======================
if mode == "GST Calculator":

    query = st.text_input("Enter query (e.g. restaurant service 1200)")
    type_ = st.selectbox("Select Type", ["Service", "Goods"])

    if st.button("Calculate GST"):

        if not query:
            st.error("Enter query")
        else:
            price = extract_price(query)

            if price is None:
                st.error("Include price (e.g. 1000)")
            else:

                # 🔹 GOODS
                if type_.lower() == "goods":

                    clean_query = re.sub(r'\d+', '', query).lower()
                    clean_query = clean_query.replace("rupees", "").strip()

                    candidates = goods_retriever.get_top_k(clean_query, k=5)

                    if not candidates:
                        st.error("No goods match found")
                    else:
                        best_row = candidates[0]["row"]

                        rate = extract_rate(best_row)
                        gst, total = calculate_gst(price, rate)

                        st.success("✅ Result")

                        st.write(f"**Match:** {best_row.iloc[0]}")
                        st.write(f"**Rate:** {rate}%")

                        st.write(f"Base: ₹{price}")
                        st.write(f"GST: ₹{gst:.2f}")
                        st.write(f"Total: ₹{total:.2f}")

                        # invoice
                        path = generate_invoice(str(best_row.iloc[0]), rate, price, gst, total)
                        with open(path, "rb") as f:
                            st.download_button("📄 Download Invoice", f, "invoice.pdf")

                # 🔹 SERVICES
                else:

                    rewritten_query = rewrite_query(query)

                    candidates = service_retriever.get_top_k(rewritten_query, k=3)

                    if not candidates:
                        st.error("No service match found")
                    else:
                        best_row = candidates[0]["row"]

                        rate = extract_rate(best_row)
                        gst, total = calculate_gst(price, rate)

                        explanation = generate_response(
                            query,
                            best_row['Description of Service'],
                            rate,
                            price,
                            gst,
                            total
                        )

                        st.success("✅ Result")

                        st.write(f"**Match:** {best_row['Description of Service']}")
                        st.write(f"**Rate:** {rate}%")

                        st.write(f"Base: ₹{price}")
                        st.write(f"GST: ₹{gst:.2f}")
                        st.write(f"Total: ₹{total:.2f}")

                        st.write("### 🤖 Explanation")
                        st.write(explanation)

                        path = generate_invoice(
                            best_row['Description of Service'],
                            rate,
                            price,
                            gst,
                            total
                        )
                        with open(path, "rb") as f:
                            st.download_button("📄 Download Invoice", f, "invoice.pdf")


# ======================
# 🔥 BUSINESS HELP
# ======================
elif mode == "Business Help":

    q = st.text_input("Ask GST question")

    if st.button("Get Guidance"):
        if q:
            res = get_business_help(q)
            st.write(res)


# ======================
# 🔥 CUSTOMER VERIFY
# ======================
else:

    product = st.text_input("Enter product")
    price = st.number_input("Price", min_value=0.0)
    gst_given = st.number_input("GST charged in bill", min_value=0.0)

    if st.button("Verify GST"):

        if product:
            candidates = goods_retriever.get_top_k(product, k=3)

            if not candidates:
                st.error("No match found")
            else:
                row = candidates[0]["row"]
                rate = extract_rate(row)

                result = verify_gst(price, gst_given, rate)

                st.write(f"Detected Rate: {rate}%")
                st.write(result)