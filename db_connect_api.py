from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import uuid
from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://darwinadmin:DarwinAdmin2023@65.0.116.9:5431/darwinqa'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# ifsc_database = {
#     "SBIN0000123": {
#         "bankName": "State Bank of India",
#         "ifsc": "SBIN0000123",
#         "branch": "Main Branch",
#         "address": "123 Main Street, Example City",
#         "city1": "Example City",
#         "city2": "Metro City",
#         "stdCode": "011",
#         "phone": "1234567890"
#     },
#     "HDFC0000456": {
#         "bankName": "HDFC Bank",
#         "ifsc": "HDFC0000456",
#         "branch": "Corporate Branch",
#         "address": "456 Corporate Street, Example City",
#         "city1": "Example City",
#         "city2": "Capital City",
#         "stdCode": "022",
#         "phone": "9876543210"
#     }
# }
# Define model (mapped to your schema and table)
class mastersCec(db.Model):
    __tablename__ = 'masters_cec'  # Replace with your actual table name
    __table_args__ = {'schema': 'data'}  # Replace with your actual schema name

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state_id = db.Column(db.String)
    region_id = db.Column(db.String)
    name = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    area_type = db.Column(db.String)
    ams_office_id = db.Column(db.String)

class mastersIfscs(db.Model):
    __tablename__ = 'masters_ifscs'
    __table_args__ = {'schema': 'data'} 

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bank_name = db.Column(db.String)
    ifsc = db.Column(db.String)
    branch = db.Column(db.String)
    address = db.Column(db.String)
    city_1 = db.Column(db.String)
    city_2 = db.Column(db.String)
    state = db.Column(db.String)
    std_code = db.Column(db.String)
    phone = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    

# Route to read data
@app.route('/read_table')
def read_table():
    try:
        results = mastersCec.query.all()
        data = [
            {
                'id': str(r.id),
                'state_id': str(r.state_id),
                'region_id': str(r.region_id),
                'name': r.name,
                'created_at': r.created_at.isoformat() if r.created_at else None,
                'updated_at': r.updated_at.isoformat() if r.updated_at else None,
                'area_type': r.area_type,
                'ams_office_id': str(r.ams_office_id)
            }
            for r in results
        ]
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# @app.route('/data/v1/master/ifsc', methods=['GET'])
# def get_bank_details():
#     try:
#         # Fetch bank details for the provided IFSC
#         bank_details = ifsc_database.get("SBIN0000123")

#         if not bank_details:
#             return jsonify({
#                 "payload": {
#                     "data": None,
#                     "message": "IFSC code not found",
#                     "code": "404",
#                     "error": "No details found for the provided IFSC code"
#                 }
#             }), 404

#         # Successful response
#         return jsonify({
#             "payload": {
#                 "data": bank_details,
#                 "message": "IFSC details fetched successfully",
#                 "code": "200",
#                 "error": None
#             }
#         })

#     except Exception as e:
#         # Handle unexpected errors
#         return jsonify({
#             "payload": {
#                 "data": None,
#                 "message": "Error occurred while fetching IFSC details",
#                 "code": "500",
#                 "error": str(e)
#             }
#         }), 500



@app.route('/data/v1/master/ifsc', methods=['POST'])
def get_bank_details():
    try:
        # Parse request data
        request_data = request.get_json()
        if not request_data or "ifsc" not in request_data:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Missing IFSC code in the request",
                    "code": "400",
                    "error": "IFSC code must be provided in the request body"
                }
            }), 400

        # Extract IFSC code
        ifsc = request_data["ifsc"]

        # Validate IFSC format
        if not ifsc or len(ifsc) != 11 or not ifsc.isalnum():
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Invalid IFSC code",
                    "code": "400",
                    "error": "IFSC code must be an 11-character alphanumeric string"
                }
            }), 400

        # Fetch bank details for the provided IFSC
        # bank_details = mastersIfscs.get(ifsc)
        bank_details = db.session.query(mastersIfscs).filter_by(ifsc=ifsc).first()


        if not bank_details:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "IFSC code not found",
                    "code": "404",
                    "error": "No details found for the provided IFSC code"
                }
            }), 404

        # Successful response
        return jsonify({
            "payload": {
                "data": bank_details.as_dict(),
                "message": "IFSC details fetched successfully",
                "code": "200",
                "error": None
            }
        })

    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            "payload": {
                "data": None,
                "message": "Error occurred while fetching IFSC details",
                "code": "500",
                "error": str(e)
            }
        }), 500
    

# Run the app
if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)
