import sys
import re

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel,
    QPushButton, QVBoxLayout,
    QLineEdit, QTextEdit, QComboBox
)

from retriever import GSTRetriever
from goods_retriever import GoodsRetriever
from gst_engine import calculate_gst
from llm import generate_response
from rewriter import rewrite_query
from selector import select_best


class GSTApp(QWidget):
    def __init__(self):
        super().__init__()

        # 🔥 Load retrievers
        self.service_retriever = GSTRetriever("data/gst_services_cleaned.csv")
        self.goods_retriever = GoodsRetriever("data/GST_Goods_Rates.csv")

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Neural GST Assistant (Goods + Services)")
        self.setGeometry(200, 200, 600, 600)

        layout = QVBoxLayout()

        # 🔹 Input
        layout.addWidget(QLabel("Enter your query:"))
        self.input_box = QLineEdit()
        layout.addWidget(self.input_box)

        # 🔹 Dropdown
        layout.addWidget(QLabel("Select Type:"))
        self.type_selector = QComboBox()
        self.type_selector.addItems(["Service", "Goods"])
        layout.addWidget(self.type_selector)

        # 🔹 Button
        self.btn = QPushButton("Process")
        self.btn.clicked.connect(self.process)
        layout.addWidget(self.btn)

        # 🔹 Output
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.setLayout(layout)

    # 🔥 Correct GST extraction (fixes wrong column issue)
    def extract_rate(self, row):
        try:
            igst = str(row.get("IGST Rate (%)", "")).replace('%', '').strip()
            if igst and igst.lower() != "nan":
                return float(igst)

            cgst = float(str(row.get("CGST Rate (%)", 0)).replace('%', '').strip())
            sgst = float(str(row.get("SGST/UTGST Rate (%)", 0)).replace('%', '').strip())

            return cgst + sgst
        except:
            return 0.0

    def process(self):
        query = self.input_box.text().strip()
        if not query:
            return

        type_ = self.type_selector.currentText().lower()

        # 🔹 Extract price
        price = self.service_retriever.extract_price(query)
        if price is None:
            self.output.setText("❌ Could not detect price.")
            return

        # ======================
        # 🔥 GOODS PIPELINE
        # ======================
        if type_ == "goods":

            # 🔹 Retrieve top candidates
            candidates = self.goods_retriever.get_top_k(query, k=7)

            # 🔥 Remove generic junk like "Nil rate"
            candidates = [
                c for c in candidates
                if "nil rate" not in c["text"].lower()
            ]

            if not candidates:
                self.output.setText("❌ No goods match found.")
                return

            # 🔹 LLM selection (mode = goods)
            best_row = select_best(query, candidates, mode="goods")

            if best_row is None:
                self.output.setText("❌ Could not determine best goods category.")
                return

            # 🔹 Extract GST rate correctly
            rate = self.extract_rate(best_row)

            # 🔹 Calculate GST
            amt, total = calculate_gst(price, rate)

            # 🔹 Display
            self.output.setText(f"""
CATEGORY: Goods

MATCH: {best_row.iloc[0]}
RATE: {rate}%

-------------------
BASE: ₹{price:,.2f}
GST: ₹{amt:,.2f}
TOTAL: ₹{total:,.2f}
""")
            return

        # ======================
        # 🔥 SERVICE PIPELINE
        # ======================

        # 🔹 Rewrite query
        rewritten_query = rewrite_query(query)
        rewritten_query = rewritten_query.replace('"', '').strip()

        print("Original:", query)
        print("Rewritten:", rewritten_query)

        # 🔹 Retrieve candidates
        candidates = self.service_retriever.get_top_k(rewritten_query, k=3)

        if not candidates:
            self.output.setText("❌ No service match found.")
            return

        # 🔹 LLM selection (mode = service)
        best_row = select_best(rewritten_query, candidates, mode="service")

        if best_row is None:
            self.output.setText("❌ Could not determine best service category.")
            return

        gst_info = {
            "description": best_row['Description of Service'],
            "chapter": best_row['Chapter / Section / Heading']
        }

        # 🔹 Extract rate
        rate = self.extract_rate(best_row)

        # 🔹 Calculate GST
        amt, total = calculate_gst(price, rate)

        # 🔹 Explanation
        explanation = generate_response(
            query, gst_info["description"], rate, price, amt, total
        )

        # 🔥 Clean weird terminal characters
        explanation = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', explanation)

        # 🔹 Display
        res = f"ORIGINAL: {query}\n"
        res += f"INTERPRETED: {rewritten_query}\n\n"
        res += f"MATCH: {gst_info['description']}\n"
        res += f"HSN: {gst_info['chapter']}\n"
        res += f"RATE: {rate}%\n"
        res += f"-------------------\n"
        res += f"BASE: ₹{price:,.2f}\n"
        res += f"GST: ₹{amt:,.2f}\n"
        res += f"TOTAL: ₹{total:,.2f}\n"
        res += f"-------------------\n"
        res += f"AI EXPLANATION:\n{explanation}"

        self.output.setText(res)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GSTApp()
    window.show()
    sys.exit(app.exec_())