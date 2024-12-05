from flask import Flask, render_template, request, jsonify
import ipaddress
import sqlite3

app = Flask(__name__)

def is_valid_ip(ip_parts, subnet_mask):
    print ("ip_parts: ", ip_parts)
    if len(ip_parts) != 4:
        return False
    for part in ip_parts:
        if not part.isdigit():
            return False
        num = int(part)
        if num < 0 or num > 255:
            return False
    return True


def is_valid_subnet_mask(mask):
    if mask.isdigit():
        mask_num = int(mask)
        return 0 <= mask_num <= 32
    return False

def validate_ip_subnet(ip_address, subnet_mask):
    ip_parts = ip_address.split(".")
    if not is_valid_ip(ip_parts, subnet_mask):
        return "Invalid IP address. Please enter values between 0 and 255 for each part."
    if not is_valid_subnet_mask(subnet_mask):
        return "Invalid subnet mask. Please enter a value between 0 and 32."
    return "Valid IP subnet."

@app.route('/', methods=['GET', 'POST'])
def home():
    validation_message = ""
    ip_address = ""
    subnet_mask = ""

    # If the request is POST, process the form data
    if request.method == 'POST':
        ip_address = f"{request.form['ip_address_part1']}.{request.form['ip_address_part2']}." \
                     f"{request.form['ip_address_part3']}.{request.form['ip_address_part4']}"
        subnet_mask = request.form['subnet_mask']
        validation_message = validate_ip_subnet(ip_address, subnet_mask)
    
        print ("ip address is ", ip_address)
        print ("subnet mask is ", subnet_mask)
        print (ip_address + "/" + subnet_mask)
        print ()

        subnet = ip_address + "/" + subnet_mask

        conn = sqlite3.connect('ip.db')
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS IP (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value TEXT NOT NULL
        )
        ''')

        cursor.execute('INSERT INTO IP (value) VALUES (?)', (subnet,))

        conn.commit()
        conn.close()

    # Pass empty values to the template on GET request to clear the form on page refresh
    return render_template('index.html', validation_message=validation_message,
                           ip_address=ip_address if request.method == 'POST' else "",
                           subnet_mask=subnet_mask if request.method == 'POST' else "")

@app.route('/clear-field', methods=['GET', 'POST'])
def clear_field():
    conn = sqlite3.connect('ip.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM IP')
    conn.commit()
    conn.close()

    return render_template('index.html', clear_message="Cleared Input")

@app.route('/clear-events', methods=['GET', 'POST'])
def clear_events():
    conn = sqlite3.connect('ip.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM Events')
    conn.commit()
    conn.close()

    return render_template('index.html', clear_message="Cleared Events")

@app.route('/clear-ips', methods=['GET', 'POST'])
def clear_ips():
    conn = sqlite3.connect('ip.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM IP')
    conn.commit()
    conn.close()

    return render_template('index.html', clear_message="Cleared IPs")

@app.route('/events', methods=['GET'])
def get_events():
    try:
        # Connect to the SQLite database
        db_path = 'ip.db'
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # Query to fetch the events
        query = "SELECT timestamp, username, source_ip, event_type FROM events"
        cursor.execute(query)

        # Fetch all the results
        events = [[row[0], row[1], row[2], row[3]] for row in cursor.fetchall()]

        # Close the connection
        connection.close()

        # Return the events as a JSON response
        return jsonify(events), 200

    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
