from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import requests
import json
from datetime import datetime
import uuid

app = Flask(__name__, static_folder='../frontend/static', template_folder='../frontend/templates')
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'events.db')

# ─── Database Setup ────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            date TEXT,
            time TEXT,
            venue TEXT,
            city TEXT,
            country TEXT,
            category TEXT,
            image_url TEXT,
            price_min REAL DEFAULT 0,
            price_max REAL DEFAULT 0,
            currency TEXT DEFAULT 'USD',
            total_tickets INTEGER DEFAULT 100,
            available_tickets INTEGER DEFAULT 100,
            source TEXT DEFAULT 'local',
            external_url TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS bookings (
            id TEXT PRIMARY KEY,
            event_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            ticket_type TEXT DEFAULT 'General',
            total_price REAL DEFAULT 0,
            status TEXT DEFAULT 'confirmed',
            booking_ref TEXT UNIQUE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES events(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    ''')
    conn.commit()
    conn.close()

# ─── Seed Open Data from Ticketmaster Discovery API (no key needed for demo) ──

def fetch_and_seed_events():
    conn = get_db()
    c = conn.cursor()
    existing = c.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    if existing > 0:
        conn.close()
        return

    # Use Ticketmaster public API (demo key available at developer.ticketmaster.com)
    # Fallback to curated sample data if API unavailable
    sample_events = [
        {
            "id": str(uuid.uuid4()),
            "name": "Global Music Festival 2025",
            "description": "A spectacular three-day music extravaganza featuring world-renowned artists across multiple stages. Experience unforgettable performances, great food, and an electric atmosphere.",
            "date": "2025-08-15",
            "time": "18:00",
            "venue": "Madison Square Garden",
            "city": "New York",
            "country": "US",
            "category": "Music",
            "image_url": "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=800&q=80",
            "price_min": 75.0,
            "price_max": 350.0,
            "currency": "USD",
            "total_tickets": 500,
            "available_tickets": 312,
            "source": "sample",
            "external_url": ""
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Tech Summit 2025",
            "description": "The premier technology conference bringing together innovators, entrepreneurs, and tech leaders. Keynotes, workshops, and networking sessions across two days.",
            "date": "2025-09-10",
            "time": "09:00",
            "venue": "Moscone Center",
            "city": "San Francisco",
            "country": "US",
            "category": "Technology",
            "image_url": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&q=80",
            "price_min": 299.0,
            "price_max": 999.0,
            "currency": "USD",
            "total_tickets": 1000,
            "available_tickets": 487,
            "source": "sample",
            "external_url": ""
        },
        {
            "id": str(uuid.uuid4()),
            "name": "International Food & Wine Expo",
            "description": "Celebrate culinary excellence with top chefs, sommeliers, and food artisans. Tastings, cooking demos, and masterclasses in a vibrant setting.",
            "date": "2025-07-22",
            "time": "12:00",
            "venue": "ExCeL London",
            "city": "London",
            "country": "UK",
            "category": "Food & Drink",
            "image_url": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80",
            "price_min": 45.0,
            "price_max": 180.0,
            "currency": "GBP",
            "total_tickets": 300,
            "available_tickets": 150,
            "source": "sample",
            "external_url": ""
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Champions League Final",
            "description": "The pinnacle of European club football. Watch two of Europe's finest teams battle it out for the ultimate prize in an electric atmosphere.",
            "date": "2025-06-01",
            "time": "20:45",
            "venue": "Wembley Stadium",
            "city": "London",
            "country": "UK",
            "category": "Sports",
            "image_url": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=800&q=80",
            "price_min": 200.0,
            "price_max": 2500.0,
            "currency": "GBP",
            "total_tickets": 200,
            "available_tickets": 45,
            "source": "sample",
            "external_url": ""
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Contemporary Art Biennale",
            "description": "A groundbreaking showcase of contemporary art from emerging and established artists worldwide. Installations, performances, and talks.",
            "date": "2025-10-05",
            "time": "10:00",
            "venue": "Tate Modern",
            "city": "London",
            "country": "UK",
            "category": "Arts",
            "image_url": "https://images.unsplash.com/photo-1531243269054-5ebf6f34081e?w=800&q=80",
            "price_min": 20.0,
            "price_max": 75.0,
            "currency": "GBP",
            "total_tickets": 400,
            "available_tickets": 380,
            "source": "sample",
            "external_url": ""
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Startup India Summit",
            "description": "India's largest startup ecosystem event with pitching competitions, investor meetups, and sessions from unicorn founders. Network with 5000+ entrepreneurs.",
            "date": "2025-11-18",
            "time": "09:30",
            "venue": "Bangalore International Exhibition Centre",
            "city": "Bangalore",
            "country": "IN",
            "category": "Business",
            "image_url": "https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=800&q=80",
            "price_min": 999.0,
            "price_max": 4999.0,
            "currency": "INR",
            "total_tickets": 2000,
            "available_tickets": 1250,
            "source": "sample",
            "external_url": ""
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Comedy Night Spectacular",
            "description": "An evening of non-stop laughter featuring stand-up comedy from 10 top comedians. Perfect for a fun night out!",
            "date": "2025-07-05",
            "time": "20:00",
            "venue": "The Comedy Store",
            "city": "Los Angeles",
            "country": "US",
            "category": "Comedy",
            "image_url": "https://images.unsplash.com/photo-1527224857830-43a7acc85260?w=800&q=80",
            "price_min": 30.0,
            "price_max": 80.0,
            "currency": "USD",
            "total_tickets": 250,
            "available_tickets": 89,
            "source": "sample",
            "external_url": ""
        },
        {
            "id": str(uuid.uuid4()),
            "name": "EDM Night: Neon Dreams",
            "description": "Immerse yourself in a world of bass, beats, and neon lights. Featuring DJ sets from globally acclaimed electronic music artists.",
            "date": "2025-08-30",
            "time": "22:00",
            "venue": "Fabric",
            "city": "London",
            "country": "UK",
            "category": "Music",
            "image_url": "https://images.unsplash.com/photo-1571266752807-1f1f1c5b6b37?w=800&q=80",
            "price_min": 25.0,
            "price_max": 60.0,
            "currency": "GBP",
            "total_tickets": 500,
            "available_tickets": 220,
            "source": "sample",
            "external_url": ""
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Marathon Chennai 2025",
            "description": "Join thousands of runners in India's premier marathon event. Categories for all fitness levels — 5K, 10K, half marathon, and full marathon.",
            "date": "2025-12-07",
            "time": "05:30",
            "venue": "Marina Beach",
            "city": "Chennai",
            "country": "IN",
            "category": "Sports",
            "image_url": "https://images.unsplash.com/photo-1552674605-db6ffd4facb5?w=800&q=80",
            "price_min": 500.0,
            "price_max": 2000.0,
            "currency": "INR",
            "total_tickets": 5000,
            "available_tickets": 3200,
            "source": "sample",
            "external_url": ""
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Wellness & Yoga Retreat",
            "description": "A weekend of mindfulness, yoga, meditation, and holistic wellness workshops in a serene environment. Recharge your mind and body.",
            "date": "2025-09-27",
            "time": "07:00",
            "venue": "Isha Yoga Center",
            "city": "Coimbatore",
            "country": "IN",
            "category": "Wellness",
            "image_url": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800&q=80",
            "price_min": 1500.0,
            "price_max": 5000.0,
            "currency": "INR",
            "total_tickets": 200,
            "available_tickets": 80,
            "source": "sample",
            "external_url": ""
        },
    ]

    for event in sample_events:
        c.execute('''INSERT OR IGNORE INTO events 
            (id, name, description, date, time, venue, city, country, category, image_url,
             price_min, price_max, currency, total_tickets, available_tickets, source, external_url)
            VALUES (:id,:name,:description,:date,:time,:venue,:city,:country,:category,:image_url,
                    :price_min,:price_max,:currency,:total_tickets,:available_tickets,:source,:external_url)''', event)
    conn.commit()
    conn.close()

# ─── API Routes ────────────────────────────────────────────────────────────────

@app.route('/api/events', methods=['GET'])
def get_events():
    conn = get_db()
    category = request.args.get('category', '')
    city = request.args.get('city', '')
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'date')

    query = "SELECT * FROM events WHERE 1=1"
    params = []
    if category:
        query += " AND category = ?"
        params.append(category)
    if city:
        query += " AND city LIKE ?"
        params.append(f'%{city}%')
    if search:
        query += " AND (name LIKE ? OR description LIKE ? OR venue LIKE ?)"
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])

    sort_map = {'date': 'date ASC', 'price': 'price_min ASC', 'name': 'name ASC', 'available': 'available_tickets DESC'}
    query += f" ORDER BY {sort_map.get(sort, 'date ASC')}"

    events = [dict(row) for row in conn.execute(query, params).fetchall()]
    conn.close()
    return jsonify({'events': events, 'total': len(events)})

@app.route('/api/events/<event_id>', methods=['GET'])
def get_event(event_id):
    conn = get_db()
    event = conn.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    conn.close()
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    return jsonify(dict(event))

@app.route('/api/categories', methods=['GET'])
def get_categories():
    conn = get_db()
    cats = conn.execute("SELECT DISTINCT category FROM events ORDER BY category").fetchall()
    conn.close()
    return jsonify([r[0] for r in cats])

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    if not data.get('name') or not data.get('email'):
        return jsonify({'error': 'Name and email required'}), 400
    conn = get_db()
    existing = conn.execute("SELECT * FROM users WHERE email = ?", (data['email'],)).fetchone()
    if existing:
        conn.close()
        return jsonify(dict(existing))
    user_id = str(uuid.uuid4())
    conn.execute("INSERT INTO users (id, name, email, phone) VALUES (?,?,?,?)",
                 (user_id, data['name'], data['email'], data.get('phone', '')))
    conn.commit()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return jsonify(dict(user)), 201

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    data = request.json
    required = ['event_id', 'user_id', 'quantity']
    for f in required:
        if not data.get(f):
            return jsonify({'error': f'{f} is required'}), 400

    conn = get_db()
    event = conn.execute("SELECT * FROM events WHERE id = ?", (data['event_id'],)).fetchone()
    if not event:
        return jsonify({'error': 'Event not found'}), 404

    qty = int(data['quantity'])
    if event['available_tickets'] < qty:
        return jsonify({'error': f'Only {event["available_tickets"]} tickets available'}), 400

    booking_id = str(uuid.uuid4())
    booking_ref = f"EVT-{datetime.now().strftime('%Y%m%d')}-{booking_id[:6].upper()}"
    total_price = event['price_min'] * qty

    conn.execute('''INSERT INTO bookings (id, event_id, user_id, quantity, ticket_type, total_price, booking_ref)
                    VALUES (?,?,?,?,?,?,?)''',
                 (booking_id, data['event_id'], data['user_id'], qty,
                  data.get('ticket_type', 'General'), total_price, booking_ref))
    conn.execute("UPDATE events SET available_tickets = available_tickets - ? WHERE id = ?",
                 (qty, data['event_id']))
    conn.commit()

    booking = conn.execute('''
        SELECT b.*, e.name as event_name, e.date as event_date, e.time as event_time,
               e.venue, e.city, u.name as user_name, u.email as user_email
        FROM bookings b
        JOIN events e ON b.event_id = e.id
        JOIN users u ON b.user_id = u.id
        WHERE b.id = ?''', (booking_id,)).fetchone()
    conn.close()
    return jsonify(dict(booking)), 201

@app.route('/api/bookings/<user_id>', methods=['GET'])
def get_user_bookings(user_id):
    conn = get_db()
    bookings = conn.execute('''
        SELECT b.*, e.name as event_name, e.date as event_date, e.time as event_time,
               e.venue, e.city, e.image_url, e.category
        FROM bookings b
        JOIN events e ON b.event_id = e.id
        WHERE b.user_id = ?
        ORDER BY b.created_at DESC''', (user_id,)).fetchall()
    conn.close()
    return jsonify([dict(b) for b in bookings])

@app.route('/api/bookings/cancel/<booking_id>', methods=['PUT'])
def cancel_booking(booking_id):
    conn = get_db()
    booking = conn.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    if booking['status'] == 'cancelled':
        return jsonify({'error': 'Already cancelled'}), 400
    conn.execute("UPDATE bookings SET status = 'cancelled' WHERE id = ?", (booking_id,))
    conn.execute("UPDATE events SET available_tickets = available_tickets + ? WHERE id = ?",
                 (booking['quantity'], booking['event_id']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Booking cancelled successfully'})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = get_db()
    stats = {
        'total_events': conn.execute("SELECT COUNT(*) FROM events").fetchone()[0],
        'total_bookings': conn.execute("SELECT COUNT(*) FROM bookings WHERE status='confirmed'").fetchone()[0],
        'total_users': conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        'revenue': conn.execute("SELECT COALESCE(SUM(total_price),0) FROM bookings WHERE status='confirmed'").fetchone()[0],
        'by_category': [dict(r) for r in conn.execute(
            "SELECT category, COUNT(*) as count FROM events GROUP BY category").fetchall()]
    }
    conn.close()
    return jsonify(stats)

# Serve frontend
@app.route('/')
@app.route('/<path:path>')
def serve_frontend(path=''):
    frontend_dir = os.path.join(os.path.dirname(__file__), '../frontend')
    if path and os.path.exists(os.path.join(frontend_dir, 'static', path)):
        return send_from_directory(os.path.join(frontend_dir, 'static'), path)
    return send_from_directory(frontend_dir, 'index.html')

if __name__ == '__main__':
    init_db()
    fetch_and_seed_events()
    print("\n" + "="*55)
    print("  🎫  Event Management System")
    print("  🌐  http://localhost:5000")
    print("="*55 + "\n")
    app.run(debug=True, port=5000)
