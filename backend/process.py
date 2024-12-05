import sqlite3
import json
import ipaddress

db_path = 'ip.db'  # Update the path if the database is located elsewhere
connection = sqlite3.connect(db_path)

cursor = connection.cursor()

query = "SELECT value FROM IP"

cursor.execute(query)

subnet_values = [row[0] for row in cursor.fetchall()]

connection.close()

file_path = "events.jsonl"

suspicious_ip = {}
suspicious_user = {}
with open(file_path, 'r') as file:
    conn = sqlite3.connect('ip.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Events (
        timestamp TIMESTAMP,
        username VARCHAR(255),
        source_ip VARCHAR(45),
        event_type VARCHAR(255),
        file_size_mb DECIMAL(10, 2),
        application VARCHAR(255),
        success BOOLEAN
    );    
    ''')

    conn.commit()
    conn.close()
    
    for line in file:
        event = json.loads(line.strip())
        if event['source_ip'] in suspicious_ip or ('username' in event and event['username'] in suspicious_user):
            suspicious_ip[event['source_ip']] = 1

            conn = sqlite3.connect('ip.db')
            cursor = conn.cursor()

            if 'username' not in event:
                    event['username'] = "NaN"
                    
            cursor.execute('''
                INSERT INTO Events (timestamp, username, source_ip, event_type, application, success)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (event['timestamp'], event['username'], event['source_ip'], event['event_type'], event['application'], event['success']))

            conn.commit()
            conn.close()

            if event['username'] not in suspicious_user:
                suspicious_ip[event['source_ip']] = 1
            else:
                suspicious_ip[event['source_ip']] += 1

            if event['username'] not in suspicious_user:
                suspicious_user[event['username']] = 1
            else:
                suspicious_user[event['username']] += 1

        else:
            ip_obj = ipaddress.ip_address(event['source_ip'])

            found = False

            for subnet in subnet_values:
                subnet_obj = ipaddress.ip_network(subnet, strict=False)

                if ip_obj in subnet_obj:
                    found = True
                    break
            if found:
                conn = sqlite3.connect('ip.db')
                cursor = conn.cursor()

                if 'username' not in event:
                    event['username'] = "NaN"
                cursor.execute('''
                    INSERT INTO Events (timestamp, username, source_ip, event_type, application, success)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (event['timestamp'], event['username'], event['source_ip'], event['event_type'], event['application'], event['success']))

                conn.commit()
                conn.close()

                if event['source_ip'] not in suspicious_ip:
                    suspicious_ip[event['source_ip']] = 1
                else:
                    suspicious_ip[event['source_ip']] += 1

                if event['username'] not in suspicious_user:
                    suspicious_user[event['username']] = 1
                else:
                    suspicious_user[event['username']] += 1
            


print ("There are ", len(suspicious_ip.keys()), " suspicious IP's")
print ("There are ", len(suspicious_user.keys()), " suspicious Users")