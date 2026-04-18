import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SENDER_EMAIL = "nahashon.mwendwa@student.moringaschool.com"
APP_PASSWORD  = "ouxh hxgt flpv zdny"
RECEIVER_EMAIL = "nahashon.mwendwa@student.moringaschool.com"


def build_email_body(data):
    products_text = ""
    if data.get("customDuty") and data.get("products"):
        products_text = "\nPRODUCT DETAILS\n" + ("-" * 40) + "\n"
        for i, p in enumerate(data["products"], 1):
            products_text += (
                f"  Item {i}:\n"
                f"    Description : {p.get('description', 'N/A')}\n"
                f"    Weight      : {p.get('weight', 'N/A')}\n"
                f"    Dimensions  : {p.get('dimensions', 'N/A')}\n"
                f"    Quantity    : {p.get('qty', 'N/A')}\n"
                f"    Price       : {p.get('price', 'N/A')}\n"
            )

    return f"""
{'=' * 40}
NEW SHIPMENT QUOTE REQUEST
{'=' * 40}

COMPANY / PERSONAL INFORMATION
{'-' * 40}
Company : {data.get('company') or 'N/A'}
Person  : {data.get('person') or 'N/A'}
Email   : {data.get('email')}
Phone   : {data.get('phone') or 'N/A'}

SHIPMENT DETAILS
{'-' * 40}
Service       : {data.get('service')}
InCO Term     : {data.get('incoterm')}
Origin        : {data.get('origin')}
Shipment Mode : {data.get('shipmentType')}
Destination   : {data.get('destination')}
Goods Desc.   : {data.get('goodsDescription') or 'N/A'}

CARGO DETAILS
{'-' * 40}
Weight : {data.get('weight') or 'N/A'} KGS
Volume : {data.get('volume') or 'N/A'} CBM

CONTAINER DETAILS
{'-' * 40}
Container Type : {data.get('containerType') or 'N/A'}
Quantity       : {data.get('containerQty') or 'N/A'}

QUOTE INCLUDES
{'-' * 40}
Insurance   : {'Yes' if data.get('insurance') else 'No'}
Last Mile   : {'Yes' if data.get('lastMile') else 'No'}
Custom Duty : {'Yes' if data.get('customDuty') else 'No'}
{products_text}
{'=' * 40}
""".strip()


def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECEIVER_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())


@app.route("/send", methods=["POST"])
def send_quote():
    data = request.get_json()

    # Basic validation
    if not data.get("email"):
        return jsonify({"success": False, "message": "Email is required."}), 400

    if not data.get("company") and not data.get("person"):
        return jsonify({"success": False, "message": "Company or Person name is required."}), 400

    required_fields = ["service", "incoterm", "origin", "shipmentType", "destination"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"success": False, "message": f"{field} is required."}), 400

    subject = (
        f"New Shipment Quote — {data.get('service')} | "
        f"{data.get('origin')} → {data.get('destination')}"
    )

    try:
        body = build_email_body(data)
        send_email(subject, body)
        print(f"[OK] Email sent for: {data.get('email')}")
        return jsonify({"success": True, "message": "Quote submitted successfully."})

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"success": False, "message": "Failed to send email. Please try again."}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"success": True, "message": "Server is running."})


if __name__ == "__main__":
    app.run(port=3000, debug=True)