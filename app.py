import os
import psycopg2
from flask import Flask
from dotenv import load_dotenv

# Load the secret database URL from the .env file
load_dotenv() 

app = Flask(__name__)

@app.route('/')
def home():
    try:
        # 1. Connect to the Railway Database
        conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
        cursor = conn.cursor()

        # 2. Ask the database our Traceability Question
        query = """
        SELECT 
            public.jurisdictions.name AS state,
            public.material_types.name AS material,
            public.base_fee_rates.rate_per_kg AS base_cost
        FROM public.material_types
        JOIN public.base_fee_rates ON public.material_types.id = public.base_fee_rates.material_type_id
        JOIN public.legislations ON public.base_fee_rates.legislation_id = public.legislations.id
        JOIN public.jurisdictions ON public.legislations.jurisdiction_id = public.jurisdictions.id;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        # 3. Close the doors
        cursor.close()
        conn.close()

        # 4. Format the results as basic HTML to prove it works
        html_output = "<h1>EPR Traceability Engine: Active</h1>"
        for row in results:
            html_output += f"<p><strong>State:</strong> {row[0]} | <strong>Material:</strong> {row[1]} | <strong>Base Cost:</strong> ${row[2]:.4f}/kg</p>"
            
        return html_output

    except Exception as e:
        return f"Database Connection Failed: {e}"

if __name__ == '__main__':
    # Get Railway's assigned port, or default to 5000 locally
    port = int(os.environ.get("PORT", 5000))
    # host='0.0.0.0' tells Flask to listen for outside internet traffic
    app.run(host='0.0.0.0', port=port)
