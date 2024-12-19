from flask import Flask, render_template, request, send_file
from xhtml2pdf import pisa
import matplotlib.pyplot as plt
import os
import io

app = Flask(__name__)

def generate_pie_chart(energy_co2, waste_co2, travel_co2):
    labels = ['ENERGY CO₂', 'WASTE CO₂', 'TRAVEL CO₂']
    values = [energy_co2, waste_co2, travel_co2]
    colors = ['#6A994E', '#FFB703', '#3A86FF']

    plt.figure(figsize=(6, 6))
    wedges, texts, autotexts = plt.pie(
        values, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors,
        textprops={'color': 'black'}, pctdistance=0.86
    )
    plt.setp(autotexts, size=13, weight="bold")
    plt.title('CO₂ Emissions Distribution', fontsize=17)
    plt.gca().set_facecolor('#ffffff')
    chart_path = 'static/pie_chart.png'
    plt.savefig(chart_path, bbox_inches='tight', transparent=True)
    plt.close()
    return chart_path

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Capture form data
        Electricity = float(request.form.get("Electricity", 0))
        Gas = float(request.form.get("Gas", 0))
        Fuel = float(request.form.get("Fuel", 0))
        Waste = float(request.form.get("Waste", 0))
        Recycling = float(request.form.get("Recycling", 0))
        Travel_km = float(request.form.get("Travel_km", 0))
        Fuel_Efficiency = float(request.form.get("Fuel_Efficiency", 1))

        # CO2 calculations
        Energy_co2 = (Electricity * 12 * 0.0005) + (Gas * 12 * 0.0053) + (Fuel * 12 * 2.32)
        Waste_co2 = Waste * 12 * (0.57 - Recycling / 100)
        Travel_co2 = (Travel_km * 1 / Fuel_Efficiency) * 2.31
        total_co2 = Energy_co2 + Waste_co2 + Travel_co2

        # Generate pie chart
        chart_path = generate_pie_chart(Energy_co2, Waste_co2, Travel_co2)

        return render_template(
            "index.html",
            energy_co2=round(Energy_co2, 2),
            waste_co2=round(Waste_co2, 2),
            travel_co2=round(Travel_co2, 2),
            total_co2=round(total_co2, 2),
            chart_path=chart_path,
        )

    return render_template("index.html")

@app.route("/download_pdf", methods=["POST"])
def download_pdf():
    try:
        # Capture results
        energy_co2 = request.form.get("Energy_co2")
        waste_co2 = request.form.get("Waste_co2")
        travel_co2 = request.form.get("Travel_co2")
        total_co2 = request.form.get("Total_co2")
        chart_path = 'static/pie_chart.png'

        # PDF content
        pdf_content = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Times New Roman, sans-serif; margin: 25px; }}
                    h1 {{ color: #663399; text-align: center; }}
                    .summary {{ background: #f4f4f4; padding: 16px; border-radius: 6px; }}
                    img {{ display: block; margin: 20px auto; max-width: 80%; }}
                </style>
            </head>
            <body>
                <h1>CO₂ Emission Reporting</h1>
                <div class="summary">
                    <p><strong>Energy CO₂:</strong> {energy_co2} kgCO₂</p>
                    <p><strong>Waste CO₂:</strong> {waste_co2} kgCO₂</p>
                    <p><strong>Travel CO₂:</strong> {travel_co2} kgCO₂</p>
                    <p><strong>Total CO₂:</strong> {total_co2} kgCO₂</p>
                </div>
                <img src="{chart_path}" alt="CO₂ Distribution">
            </body>
        </html>
        """

        pdf_stream = io.BytesIO()
        pisa.CreatePDF(pdf_content, dest=pdf_stream)
        pdf_stream.seek(0)

        return send_file(pdf_stream, as_attachment=True, download_name="CO2_Emission_Feedback.pdf")

    except Exception as e:
        return f"Error: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)
