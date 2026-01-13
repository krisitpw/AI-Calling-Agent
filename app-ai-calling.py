import logging
logging.basicConfig(level=logging.DEBUG)
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
import os

app = Flask(__name__)

# Use environment variables for safety in production
TWILIO_SID = os.environ.get("TWILIO_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "")

# 🔧 Replace this with your live Ngrok or Heroku URL!
PUBLIC_URL = os.environ.get("PUBLIC_URL", "")  # <-- Change this!

@app.route("/")
def index():
    return "Real Estate Calling Agent is running."

@app.route("/voice", methods=['POST'])
def voice():
    response = VoiceResponse()
    gather = Gather(input='speech dtmf', timeout=5, num_digits=1, action='/gather', method='POST')

    gather.say(
        "Hi, this is Priya from DreamNest Realty. "
        "We have a 3 bedroom apartment available in Noida Sector 137. "
        "It's semi-furnished with 2 balconies, priced at 65 lakh rupees. "
        "If you're interested, press 1 or say Yes. If not, press 2 or say No.",
        voice='Polly.Amy', language='en-IN'
    )

    response.append(gather)
    response.say("No input received. Goodbye!", voice='Polly.Amy')
    return Response(str(response), mimetype='text/xml')

@app.route("/gather", methods=['POST'])
def gather():
    user_speech = request.values.get('SpeechResult', '').lower()
    digit = request.values.get('Digits', '')
    response = VoiceResponse()

    if 'yes' in user_speech or digit == '1':
        response.say("Great! We'll send you more details on WhatsApp. Thank you!", voice='Polly.Amy')
        print("Lead interested. Follow-up needed.")
    elif 'no' in user_speech or digit == '2':
        response.say("No problem. Have a great day!", voice='Polly.Amy')
        print("Lead not interested.")
    else:
        response.say("Sorry, I didn't catch that. We'll follow up later. Goodbye!", voice='Polly.Amy')

    return Response(str(response), mimetype='text/xml')

@app.route("/make-call", methods=["GET"])
def make_call():
    lead_number = request.args.get("to", "+919113115450")  # Replace default if needed
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

    call = client.calls.create(
        to=lead_number,
        from_=TWILIO_PHONE_NUMBER,
        url=f"{PUBLIC_URL}/voice"  # ✅ Use public URL
    )

    return f"Calling {lead_number}... Call SID: {call.sid}"

if __name__ == "__main__":
    app.run(port=5000, debug=True)
