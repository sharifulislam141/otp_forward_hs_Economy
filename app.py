from flask import Flask, request, jsonify
import re
import threading
import time

app = Flask(__name__)

latest_sms = None
otp_timestamp = None
lock = threading.Lock()

def reset_otp():
    global latest_sms, otp_timestamp
    with lock:
        latest_sms = None
        otp_timestamp = None
        print("OTP value reset to None")

@app.route('/')
def home():
    return "This app developed by Tanvir Mahamud Shariful"

@app.route('/forward_sms', methods=['POST'])
def forward_sms():
    global latest_sms, otp_timestamp
    data = request.get_json()
    message = data.get('message', '')

    if "H.S Economics Academy" in message:
        otp_match = re.search(r'\b\d{4}\b', message)
        if otp_match:
            with lock:
                latest_sms = otp_match.group()
                otp_timestamp = time.time()

            print(f"(H.S Economics Academy) Your OTP is: {latest_sms}\nUse this PIN within 3 minutes to verify. Do not forward or share this PIN with anyone.")

            timer = threading.Timer(180, reset_otp)
            timer.start()

            return jsonify({'status': 'success', 'message': 'OTP received and processed!'}), 200
        else:
            return jsonify({'status': 'error', 'message': '4-digit OTP not found.'}), 400
    else:
        return jsonify({'status': 'error', 'message': "Invalid source."}), 400

@app.route('/otp', methods=['GET'])
def get_sms():
    with lock:
        if latest_sms and otp_timestamp:
            time_left = int(180 - (time.time() - otp_timestamp))
            if time_left <= 0:
                reset_otp()
                return "<html><body><h2>OTP expired</h2><p>Please wait for a new OTP.</p></body></html>", 404

            return f"""
            <html>
            <head>
                <title>OTP Viewer</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: 'Poppins', sans-serif;
                        background: linear-gradient(to right, #dbeafe, #eff6ff);
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        padding: 10px;
                    }}
                    .card {{
                        background-color: #ffffff;
                        padding: 30px;
                        border-radius: 16px;
                        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
                        text-align: center;
                        max-width: 400px;
                        width: 100%;
                        box-sizing: border-box;
                    }}
                    .otp {{
                        font-size: 36px;
                        font-weight: 600;
                        color: #1e3a8a;
                        margin-bottom: 20px;
                    }}
                    .msg {{
                        font-size: 16px;
                        color: #333;
                        margin-bottom: 20px;
                    }}
                    #countdown {{
                        font-size: 14px;
                        color: #ef4444;
                        margin-bottom: 20px;
                        font-weight: 500;
                    }}
                    .btn {{
                        display: inline-block;
                        padding: 10px 16px;
                        margin: 5px;
                        font-size: 14px;
                        border: none;
                        border-radius: 8px;
                        cursor: pointer;
                        transition: all 0.2s ease-in-out;
                        text-decoration: none;
                        color: white;
                        width: 100%;
                        box-sizing: border-box;
                    }}
                    .btn-refresh {{ background-color: #3b82f6; }}
                    .btn-refresh:hover {{ background-color: #2563eb; }}
                    .btn-call {{ background-color: #10b981; }}
                    .btn-call:hover {{ background-color: #059669; }}
                    .btn-copy {{ background-color: #f59e0b; }}
                    .btn-copy:hover {{ background-color: #d97706; }}
                    .copied-msg {{
                        display: none;
                        margin-top: 10px;
                        font-size: 13px;
                        color: #16a34a;
                        font-weight: 500;
                    }}
                    @media (max-width: 480px) {{
                        .otp {{
                            font-size: 30px;
                        }}
                        .msg {{
                            font-size: 14px;
                        }}
                        .btn {{
                            font-size: 13px;
                            padding: 10px;
                        }}
                    }}
                </style>
                <script>
                    let timeLeft = {time_left};
                    function startCountdown() {{
                        const countdownElem = document.getElementById("countdown");
                        const interval = setInterval(() => {{
                            if (timeLeft <= 0) {{
                                countdownElem.innerHTML = "OTP expired";
                                clearInterval(interval);
                                setTimeout(() => window.location.reload(), 1000);
                            }} else {{
                                let minutes = Math.floor(timeLeft / 60);
                                let seconds = timeLeft % 60;
                                countdownElem.innerHTML = "⏳ OTP expires in: " + 
                                    minutes.toString().padStart(2, '0') + ":" + 
                                    seconds.toString().padStart(2, '0');
                                timeLeft--;
                            }}
                        }}, 1000);
                    }}

                    function copyOTP() {{
                        const otpText = document.getElementById("otp-value").innerText;
                        navigator.clipboard.writeText(otpText).then(() => {{
                            const msg = document.getElementById("copied-msg");
                            msg.style.display = "block";
                            setTimeout(() => msg.style.display = "none", 1500);
                        }});
                    }}

                    window.onload = startCountdown;
                </script>
            </head>
            <body>
                <div class="card">
                    <div class="otp" id="otp-value">{latest_sms}</div>
                    <div class="msg">
                        Use this PIN within 3 minutes to verify.<br>
                        Do not forward or share this PIN with anyone.
                    </div>
                    <div id="countdown"></div>
                    <button class="btn btn-copy" onclick="copyOTP()">📋 Copy OTP</button>
                    <div id="copied-msg" class="copied-msg">✅ OTP Copied!</div>
                    <br>
                    <a href="/otp" class="btn btn-refresh">🔄 Refresh</a>
                    <a href="tel:+8801571022152" class="btn btn-call">📞 Call Lamia</a>
                </div>
            </body>
            </html>
            """
        else:
            return  """
                    <html>
                    <head>
                        <title>No OTP Available</title>
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <meta http-equiv="refresh" content="5"> <!-- Auto-refresh every 5 seconds -->
                        <style>
                            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

                            body {
                                font-family: 'Poppins', sans-serif;
                                background: linear-gradient(to right, #fef9f9, #ffecec);
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                height: 100vh;
                                margin: 0;
                                padding: 20px;
                            }

                            .card {
                                background: #ffffff;
                                padding: 30px 25px;
                                border-radius: 16px;
                                text-align: center;
                                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
                                animation: fadeIn 0.8s ease;
                                max-width: 400px;
                                width: 100%;
                            }

                            .card h2 {
                                color: #b91c1c;
                                font-size: 24px;
                                margin-bottom: 10px;
                            }

                            .card p {
                                font-size: 16px;
                                color: #6b7280;
                            }

                            .icon {
                                font-size: 50px;
                                color: #f87171;
                                margin-bottom: 15px;
                            }

                            @keyframes fadeIn {
                                from { opacity: 0; transform: translateY(20px); }
                                to { opacity: 1; transform: translateY(0); }
                            }

                            @media (max-width: 480px) {
                                .card {
                                    padding: 25px 20px;
                                }

                                .card h2 {
                                    font-size: 20px;
                                }

                                .icon {
                                    font-size: 40px;
                                }
                            }
                        </style>
                    </head>
                    <body>
                        <div class="card">
                            <div class="icon">📭</div>
                            <h2>No OTP Available</h2>
                            <p>We're checking for new OTPs.<br>This page refreshes every 5 seconds.</p>
                        </div>
                    </body>
                    </html>
                    """, 404

if __name__ == '__main__':
    app.run(debug=True)
