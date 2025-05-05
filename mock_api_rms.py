from flask import Flask, request, jsonify
from datetime import datetime
import random


app = Flask(__name__)

# Collection Based APIs ------------------------------------------------------------------------------------------------------

# Attendance Data
attendance_data = {
    "demo_user1": {
        "employeeId": "EMP00123",
        "employeeName": "Ram",
        "designation": "Field Executive",
        "status": "COMPLETED",
        "clockInTime": "2025-05-04T09:15:00+05:30",
        "remarks": "Already clocked in today at 09:15 AM IST",
        "latitude": 37,
        "longitude": 123
    },
    "demo_user2": {
        "employeeId": "EMP00456",
        "employeeName": "Rahul",
        "designation": "Relationship Manager",
        "status": "PENDING",
        "clockInTime": None,
        "remarks": None,
        "latitude": None,
        "longitude": None
    }
}

# Mock data for the target
targets_data = {
    "demo_user1": {
        "collectionPending": "6000.00",
        "groupsPending": "4",
        "customersPending": "12",
        "collectionCompleted": "11000.00",
        "groupsCompleted": "8",
        "customersCompleted": "20",
        "cashAmount": "6000.00",
        "upiAmount": "3000.00",
        "emiAmount": "1200.00",
        "extraAmount": "500.00",
        "rescheduledAmount": "200.00"
    },
    "demo_user2": {
        "collectionPending": "5000.00",
        "groupsPending": "5",
        "customersPending": "15",
        "collectionCompleted": "12000.00",
        "groupsCompleted": "10",
        "customersCompleted": "25",
        "cashAmount": "7000.00",
        "upiAmount": "3000.00",
        "emiAmount": "1500.00",
        "extraAmount": "500.00",
        "rescheduledAmount": "200.00"
    }
}

# Mock data for group schedules
group_schedule_data = {
    "demo_user1": [
        {
            "id": "group_001",
            "bankName": "Federal Bank",
            "bankId": "fbl_123",
            "bankIcon": "https://example.com/bank_icon.png",
            "collectedAmount": "2000.00",
            "depositToBm": True,
            "dpdDays": "3",
            "emiAmount": "1500.00",
            "healthStatus": "Healthy",
            "isRescheduled": False,
            "isVisited": True,
            "latitude": "12.971598",
            "longitude": "77.594566",
            "name": "Ram",
            "nextVisit": "2025-05-02T14:00:00Z",
            "overDue": "500.00",
            "phoneNumber": "+1234567890",
            "pincode": "560001",
            "productType": "Home Loan",
            "profileIcon": "https://example.com/profile_icon.png",
            "remainingAmount": "500.00",
            "transactionStatus": "Completed",
            "isRescheduleAllowed": True,
            "isIncompleteTransaction": False,
            "losProspectId": "prospect_456",
            "losGroupId": "group_789",
            "groupName": "Golden Group",
            "status": "Active",
            "amount": "5000.00"
        }
    ],
    "demo_user2": [
        {
            "id": "group_002",
            "bankName": "KVB",
            "bankId": "KVB_123",
            "bankIcon": "https://example.com/xyz_bank_icon.png",
            "collectedAmount": "500.00",
            "depositToBm": False,
            "dpdDays": "0",
            "emiAmount": "1000.00",
            "healthStatus": "At Risk",
            "isRescheduled": True,
            "isVisited": False,
            "latitude": "13.082680",
            "longitude": "80.270718",
            "name": "Jane Doe",
            "nextVisit": "2025-05-03T10:00:00Z",
            "overDue": "300.00",
            "phoneNumber": "+9876543210",
            "pincode": "600001",
            "productType": "Personal Loan",
            "profileIcon": "https://example.com/jane_doe_profile_icon.png",
            "remainingAmount": "800.00",
            "transactionStatus": "Pending",
            "isRescheduleAllowed": False,
            "isIncompleteTransaction": True,
            "losProspectId": "prospect_789",
            "losGroupId": "group_123",
            "groupName": "Silver Group",
            "status": "Inactive",
            "amount": "2000.00"
        }
    ]
}

# Mock data for incomplete transactions
incomplete_transactions_data = {
    "demo_user1": [
        {
            "bankIcon": "https://example.com/bank_icon1.png",
            "bankId": "bank_001",
            "bankName": "Federal Bank",
            "collectedAmount": "1500.00",
            "depositToBm": True,
            "dpdDays": "5",
            "emiAmount": "1000.00",
            "healthStatus": "At Risk",
            "id": "transaction_001",
            "isAdvanceTransaction": False,
            "isRescheduleAllowed": True,
            "isRescheduled": False,
            "isVisited": False,
            "latitude": "12.971598",
            "longitude": "77.594566",
            "name": "Ram",
            "nextVisit": "2025-05-10T10:00:00Z",
            "overDue": "200.00",
            "phoneNumber": "+1234567890",
            "pincode": "560001",
            "productType": "Home Loan",
            "profileIcon": "https://example.com/profile_icon1.png",
            "remainingAmount": "800.00",
            "transactionStatus": "Pending",
            "customerId": "customer_001",  # Changed from losProspectId
            "losGroupId": "group_001"
        }
    ],
    "demo_user2": [
        {
            "bankIcon": "https://example.com/bank_icon2.png",
            "bankId": "bank_002",
            "bankName": "KVB",
            "collectedAmount": "2000.00",
            "depositToBm": False,
            "dpdDays": "10",
            "emiAmount": "1500.00",
            "healthStatus": "Critical",
            "id": "transaction_002",
            "isAdvanceTransaction": True,
            "isRescheduleAllowed": False,
            "isRescheduled": True,
            "isVisited": True,
            "latitude": "13.082680",
            "longitude": "80.270718",
            "name": "Rahul",
            "nextVisit": "2025-05-11T15:00:00Z",
            "overDue": "300.00",
            "phoneNumber": "+9876543210",
            "pincode": "600002",
            "productType": "Personal Loan",
            "profileIcon": "https://example.com/profile_icon2.png",
            "remainingAmount": "1200.00",
            "transactionStatus": "Incomplete",
            "customerId": "customer_002",  # Changed from losProspectId
            "losGroupId": "group_002"
        }
    ]
}
# Mock data for deposit details
deposit_details_data = {
    "demo_user1": {
        "cmsDeposited": "50000.00",
        "cashInHand": "20000.00",
        "cashDeposited": "30000.00",
        "verifiedAmount": "48000.00",
        "deposits": [
            {
                "bankId": "bank_001",
                "bankName": "Federal Bank",
                "depositAmount": "10000.00",
                "depositDate": "2025-05-04T10:00:00Z",
                "receiptId": "receipt_001"
            },
            {
                "bankId": "bank_002",
                "bankName": "KVB",
                "depositAmount": "20000.00",
                "depositDate": "2025-05-04T12:00:00Z",
                "receiptId": "receipt_002"
            }
        ]
    },
    "demo_user2": {
        "cmsDeposited": "60000.00",
        "cashInHand": "15000.00",
        "cashDeposited": "45000.00",
        "verifiedAmount": "58000.00",
        "deposits": [
            {
                "bankId": "bank_003",
                "bankName": "DLXB",
                "depositAmount": "25000.00",
                "depositDate": "2025-05-03T15:00:00Z",
                "receiptId": "receipt_003"
            },
            {
                "bankId": "bank_004",
                "bankName": "FBL",
                "depositAmount": "20000.00",
                "depositDate": "2025-05-03T18:00:00Z",
                "receiptId": "receipt_004"
            }
        ]
    }
}

# Mock data for group prospects
group_prospect_data = {
    "group_001": {
        "productId": "P12345",
        "id": "G001",
        "bankName": "Bank of India",
        "bankId": "B123",
        "bankIcon": "https://example.com/bank-icon.png",
        "collectionDueDate": "2025-05-01",
        "emiAmount": 5000.0,
        "isRescheduled": True,
        "location": "Mumbai, Maharashtra",
        "name": "Group ABC",
        "overDue": 2000.0,
        "pincode": 400001,
        "productType": "Loan",
        "profileIcon": "https://example.com/profile-icon.png",
        "remainingAmount": 15000.0,
        "rescheduledDate": "2025-05-20",
        "totalAmount": 20000.0,
        "members": [
            {
                "productId": "P12345",
                "productName": "Loan Product A",
                "loanAccountNumber": "LAC123456",
                "isPaidEarlier": True,
                "amountToBePaid": "5000",
                "id": "M001",
                "bankName": "Bank of India",
                "bankId": "B123",
                "amountPaid": "10000",
                "emi": "2500",
                "healthStatus": "Good",
                "isPaid": True,
                "isRescheduled": False,
                "name": "Ram",
                "overdue": "0",
                "paymentType": "Online",
                "phoneNumber": "9876543210",
                "profileIcon": "https://example.com/member-profile-icon.png",
                "rescheduledDate": "null",
                "totalAmount": "15000",
                "isPartiallyPaid": False,
                "isGroupHead": True,
                "losProspectId": "P1234567",
                "losLoanId": "L1234567",
                "losGroupId": "G001",
                "totalOutstanding": "5000",
                "isEligibleForLoanRenewal": True,
                "isEligibleForLoanClosure": False,
                "initiatedLoanRenewal": False,
                "paidEarlier": "Yes",
                "paymentStatusString": "Paid",
                "currentTenure": "12 months",
                "loanDisbursalDate": "2024-01-01",
                "isEnabaleClosure": True,
                "paymentLinkStatus": "Active"
            },
            {
                "productId": "P12345",
                "productName": "Loan Product B",
                "loanAccountNumber": "LAC654321",
                "isPaidEarlier": False,
                "amountToBePaid": "7000",
                "id": "M002",
                "bankName": "State Bank of India",
                "bankId": "SBI123",
                "amountPaid": "0",
                "emi": "3000",
                "healthStatus": "Poor",
                "isPaid": False,
                "isRescheduled": True,
                "name": "RajKumari",
                "overdue": "7000",
                "paymentType": "Cash",
                "phoneNumber": "9123456789",
                "profileIcon": "https://example.com/member-profile-icon-2.png",
                "rescheduledDate": "2025-05-10",
                "totalAmount": "7000",
                "isPartiallyPaid": True,
                "isGroupHead": False,
                "losProspectId": "P7654321",
                "losLoanId": "L7654321",
                "losGroupId": "G002",
                "totalOutstanding": "7000",
                "isEligibleForLoanRenewal": False,
                "isEligibleForLoanClosure": True,
                "initiatedLoanRenewal": True,
                "paidEarlier": "No",
                "paymentStatusString": "Pending",
                "currentTenure": "6 months",
                "loanDisbursalDate": "2024-07-01",
                "isEnabaleClosure": True,
                "paymentLinkStatus": "Inactive"
            }
        ],
        "upiAmount": "5000",
        "cashAmount": "1000",
        "total": "6000",
        "isRescheduleAllowed": True,
        "paidEarlier": "Yes",
        "losGroupId": "G001"
    }
}

#Checking Attendance Status
@app.route('/api/v1/attendance/status', methods=['GET'])
def get_attendance_status():
    user_id = request.args.get('user_id')
    if user_id in attendance_data:
        user_status = attendance_data[user_id]
        response = {
            "status": "200",
            "message": "Attendance status fetched successfully",
            "data": {
                "success": True,
                "message": "Data retrieval successful",
                "employeeDetails": user_status
            },
            "error": None
        }
        return jsonify(response)
    return jsonify({"error": "User ID not found"}), 404


# Attendence Marking API
@app.route('/api/v1/attendance/mark', methods=['PUT'])
def mark_attendance():
    user_id = request.json.get('user_id')
    latitude = request.json.get('eventData', {}).get('latitude')
    longitude = request.json.get('eventData', {}).get('longitude')
    
    if user_id not in attendance_data:
        return jsonify({"error": "User ID not found"}), 404

    user_status = attendance_data[user_id]

    # Check if already marked
    if user_status["status"] == "COMPLETED":
        return jsonify({
            "status": "400",
            "message": "Attendance already marked",
            "data": {
                "success": False,
                "remarks": f"Already clocked in today at {user_status['clockInTime']} IST"
            }
        }), 400

    # Update attendance status
    current_time = datetime.now().isoformat()
    user_status["status"] = "COMPLETED"
    user_status["clockInTime"] = current_time
    user_status["latitude"] = latitude
    user_status["longitude"] = longitude
    user_status["remarks"] = f"Clock-in successful at {current_time.split('T')[1]} IST"

    response = {
        "status": "200",
        "message": "Attendance marked successfully",
        "data": {
            "success": True,
            "message": "Attendance event logged successfully",
            "attendanceDetails": user_status
        },
        "error": None
    }
    return jsonify(response)


@app.route('/dms/1.0/collection-target', methods=['GET'])
def get_collection_target():
    try:
        # Extract user_id and date from query parameters
        user_id = request.args.get('user_id')

        # Validate user_id
        if not user_id:
            return jsonify({
                "statusCode": "400",
                "message": "User ID is required.",
                "data": None
            }), 400

        # Retrieve data for the given user_id
        target_data = targets_data.get(user_id)
        if not target_data:
            return jsonify({
                "statusCode": "404",
                "message": f"No collection target data found for user ID: {user_id}",
                "data": None
            }), 404

        # Build response
        response = {
            "statusCode": "200",
            "message": "Collection target retrieved successfully",
            "data": target_data
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            "statusCode": "500",
            "message": "An error occurred while fetching collection target data.",
            "data": None,
            "error": str(e)
        }), 500


@app.route('/dms/1.0/group-scheduled', methods=['GET'])
def get_group_schedule():
    try:
        # Extract user_id from query parameters
        user_id = request.args.get('user_id')

        # Validate user_id
        if not user_id:
            return jsonify({
                "statusCode": "400",
                "message": "User ID is required.",
                "data": None
            }), 400

        # Default to today's date
        date = datetime.now().strftime('%Y-%m-%d')

        # Fetch group schedule data for the user
        user_data = group_schedule_data.get(user_id)
        if not user_data:
            return jsonify({
                "statusCode": "404",
                "message": f"No group schedule data found for user ID: {user_id}",
                "data": None
            }), 404

        # Construct response
        response = {
            "statusCode": "200",
            "message": f"Group schedule retrieved successfully for {date}",
            "data": user_data
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            "statusCode": "500",
            "message": "An error occurred while fetching group schedule data.",
            "data": None,
            "error": str(e)
        }), 500
    

@app.route('/dms/1.0/incomplete_transactions', methods=['GET'])
def get_incomplete_transactions():
    try:
        # Extract user_id
        user_id = request.args.get('user_id')

        # Validate user_id
        if not user_id:
            return jsonify({
                "statusCode": "400",
                "message": "User ID is required.",
                "data": None
            }), 400

        # Retrieve incomplete transactions for the user
        user_data = incomplete_transactions_data.get(user_id)
        if not user_data:
            return jsonify({
                "statusCode": "404",
                "message": f"No incomplete transactions found for user ID: {user_id}",
                "data": None
            }), 404

        # Build response
        response = {
            "statusCode": "200",
            "message": "Incomplete transactions retrieved successfully",
            "data": user_data
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            "statusCode": "500",
            "message": "An error occurred while fetching incomplete transactions.",
            "data": None,
            "error": str(e)
        }), 500

@app.route('/cts/1.0/deposit_details', methods=['GET'])
def get_deposit_details():
    try:
        # Extract user_id from query parameters
        user_id = request.args.get('user_id')

        # Validate user_id
        if not user_id:
            return jsonify({
                "statusCode": "400",
                "message": "User ID is required.",
                "data": None
            }), 400

        # Retrieve deposit details for the user
        user_data = deposit_details_data.get(user_id)
        if not user_data:
            return jsonify({
                "statusCode": "404",
                "message": f"No deposit details found for user ID: {user_id}",
                "data": None
            }), 404

        # Build response
        response = {
            "statusCode": "200",
            "message": "Deposit details retrieved successfully.",
            "data": user_data
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            "statusCode": "500",
            "message": "An error occurred while fetching deposit details.",
            "data": None,
            "error": str(e)
        }), 500


@app.route('/dms/1.0/group-prospect-detail', methods=['GET'])
def get_group_prospect_details():
    try:
        # Retrieve data for the given group ID
        group_id = request.json.get('group_id')
        group_data = group_prospect_data.get(group_id)

        # Handle invalid group ID
        if not group_data:
            return jsonify({
                "status": "failure",
                "message": f"No details found for group ID: {group_id}",
                "data": None
            }), 404

        # Construct response
        response = {
            "status": "success",
            "message": "Group prospect details fetched successfully",
            "data": group_data
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            "status": "failure",
            "message": "An error occurred while fetching group prospect details.",
            "data": None,
            "error": str(e)
        }), 500

# Endpoint: Generate Digital Transaction
@app.route('/cts/1.0/generate-digital-transaction', methods=['POST'])
def generate_digital_transaction():
    try:
        # Parse request data
        data = request.json
        customer_id = data.get('customer_id')
        amount = data.get('amount')
        print(customer_id, amount)
        
        if not customer_id or not amount:
            return jsonify({
                "statusCode": "400",
                "message": "Missing required fields: customer_id or amount",
                "data": None
            }), 400
        
        # Generate random transaction details
        transaction_id = f"txn-{random.randint(100000000, 999999999)}"
        deep_link = f"https://example.com/qr?transaction={transaction_id}"
        short_link = f"https://short.link/{transaction_id}"

        response = {
            "statusCode": "200",
            "message": "QR Code generated successfully.",
            "data": {
                "deep_link": deep_link,
                "pg_upi_unique_request_id": f"pg-qr-{random.randint(10000, 99999)}",
                "pine_pg_transaction_id": random.randint(100000000, 999999999),
                "response_code": 200,
                "response_message": "Success",
                "short_link": short_link,
                "uniqueMerchantTxnId": transaction_id
            }
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            "statusCode": "500",
            "message": "An error occurred while generating the QR code.",
            "data": None,
            "error": str(e)
        }), 500


# Endpoint: Update Proof Of Transaction
@app.route('/cts/1.0/update_proof_of_transaction', methods=['POST'])
def update_proof_of_transaction():
    try:
        # Parse request data
        data = request.json
        cust_id = data.get('custId')
        proof_of_transactions = data.get('proofOfTransactions', [])
        transaction_date = data.get('transactionDate', datetime.now().strftime('%Y-%m-%d'))
        group_name = data.get('groupName', "Unknown Group")
        
        # Validate input
        if not cust_id or not proof_of_transactions:
            return jsonify({
                "statusCode": "400",
                "message": "Missing required fields: groupId or proofOfTransactions",
                "data": None
            }), 400

        if len(proof_of_transactions) == 0:
            return jsonify({
                "statusCode": "400",
                "message": "At least one proof of transaction is required.",
                "data": None
            }), 400
        
        # Generate mock transaction details
        transactions = [
            {
                "transactionId": f"txn-{i+1}",
                "transactionAmount": "5000.00",
                "transactionDate": transaction_date
            } for i in range(len(proof_of_transactions))
        ]

        response = {
            "statusCode": "200",
            "message": "Proof of transaction updated successfully.",
            "data": {
                "location": "123, Some Street, City",
                "name": "Ram",
                "pincode": "560001",
                "productType": "Loan",
                "cashAmount": "5000.00",
                "totalAmount": "10000.00",
                "upiAmount": "5000.00",
                "transactions": transactions
            }
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            "statusCode": "500",
            "message": "An error occurred while updating proof of transaction.",
            "data": None,
            "error": str(e)
        }), 500

@app.route('/dms/1.0/schedule/reschedule-customer', methods=['PUT'])
def reschedule_customer():
    try:
        # Parse request data
        data = request.json
        customer_id = data.get('customer_id')
        reason = data.get('reason')
        date = data.get('date') 
        remark = data.get('remark', "No remark provided")
        text_feedback = data.get('textFeedback', "No feedback provided")
        reschedule_type = data.get('type', "General")
        voice_feedback_url = data.get('voiceFeedbackUrl', None)
        
         # Validate input
        if not customer_id:
            return jsonify({
                "statusCode": "400",
                "message": "customer_id is required.",
                "data": None
            }), 400
    
        # Validate input
        if not reason:
            return jsonify({
                "statusCode": "400",
                "message": "Reason for rescheduling is required.",
                "data": None
            }), 400

        # Construct the response
        response = {
            "statusCode": "200",
            "message": "Customer rescheduled successfully.",
            "data": {
                "customerId": customer_id,
                "date": date,
                "reason": reason,
                "remark": remark,
                "textFeedback": text_feedback,
                "type": reschedule_type,
                "voiceFeedbackUrl": voice_feedback_url
            }
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            "statusCode": "500",
            "message": "An error occurred while rescheduling the customer.",
            "data": None,
            "error": str(e)
        }), 500


# JLG APIs ------------------------------------------------------------------------------------------------------------------

# Dummy data for demo purposes
customers_db = ["CUST0", "CUST1", "CUST2", "CUST3", "CUST4", "CUST5"]

# Mock IFSC database
ifsc_database = {
    "SBIN0000123": {
        "bankName": "State Bank of India",
        "ifsc": "SBIN0000123",
        "branch": "Hebbal",
        "address": "123 Raj street, Hebbal",
        "city1": "Banglore",
        "city2": "Metro City",
        "stdCode": "011",
        "phone": "81234567890"
    },
    "HDFC0000456": {
        "bankName": "HDFC Bank",
        "ifsc": "HDFC0000456",
        "branch": "Corporate Branch",
        "address": "456 Corporate Street, BTM Layout",
        "city1": "Bengaluru",
        "city2": "Capital City",
        "stdCode": "022",
        "phone": "9876543210"
    }
}

mock_customers_l1 = [
    {
        "custId": "CUST0",
        "stage": "L1",
        "demographics": {
            "mobileNumber": "9876543210",
            "name": "Latha"
        },
        "loanDetails": {
            "amount": "50000"
        },
        "bankAccountDetails": {
            "id": "BANK001",
            "ifsc": "SBIN0000123",
            "disbursementPreference": "Direct Transfer",
            "dedupe": True,
            "isActive": True,
            "errorMessage": None
        },
        "documents": {
            "keys": ["doc1", "doc2"],
            "type": "Verification"
        },
        "level": "Stage 1",
        "status": "Pending",
        "isEditable": True,
        "isDeletable": False,
        "isEkycExpiry": False,
        "isDedupeExpiry": False,
        "verification": {
            "reasons": ["Incomplete documents"],
            "comments": "Pending verification"
        },
        "currentAddress": {
            "houseNo": "123",
            "street": "Main Street",
            "locality": "BTM Layout",
            "landmark": "BTM Water Tank",
            "vtc": "Tech City",
            "state": "Karnataka",
            "district": "Banglore",
            "city": "Banglore",
            "stateCode": "ST01",
            "cityCode": "CT01",
            "districtCode": "DT01",
            "pincode": "123456",
            "id": "ADDR001",
            "type": "Residential",
            "updated_at": "2024-11-15T12:00:00Z",
            "created_at": "2024-11-01T10:00:00Z",
            "natureOfResidence": "Owned"
        },
        "creditReports": {
            "id": "CREDIT001",
            "isNew": True,
            "isExpired": False
        },
        "stageUpdatedAt": "2024-11-25T15:00:00Z",
        "summary": {
            "custId": "CUST0",
            "name": "Latha",
            "loanAmount": "50000",
            "status": "Pending",
            "stage": "L1"
        }
    },
    {
        "custId": "CUST1",
        "stage": "L1",
        "demographics": {
            "mobileNumber": "9876543211",
            "name": "Rajee"
        },
        "loanDetails": {
            "amount": "75000"
        },
        "bankAccountDetails": {
            "id": "BANK002",
            "ifsc": "SBIN0000123",
            "disbursementPreference": "Cheque",
            "dedupe": False,
            "isActive": True,
            "errorMessage": None
        },
        "documents": {
            "keys": ["doc3", "doc4"],
            "type": "Verification"
        },
        "level": "Stage 1",
        "status": "Completed",
        "isEditable": False,
        "isDeletable": False,
        "isEkycExpiry": False,
        "isDedupeExpiry": False,
        "verification": {
            "reasons": [],
            "comments": "All documents verified"
        },
        "currentAddress": {
            "houseNo": "124",
            "street": "Second Street",
            "locality": "Suburbs",
            "landmark": "Near Mall",
            "vtc": "Tech City",
            "state": "Karnataka",
            "district": "Banglore",
            "city": "Banglore",
            "stateCode": "ST01",
            "cityCode": "CT01",
            "districtCode": "DT01",
            "pincode": "123457",
            "id": "ADDR002",
            "type": "Residential",
            "updated_at": "2024-11-14T12:00:00Z",
            "created_at": "2024-11-01T11:00:00Z",
            "natureOfResidence": "Rented"
        },
        "creditReports": {
            "id": "CREDIT002",
            "isNew": False,
            "isExpired": False
        },
        "stageUpdatedAt": "2024-11-25T15:30:00Z",
        "summary": {
            "custId": "CUST1",
            "name": "Rajee",
            "loanAmount": "75000",
            "status": "Completed",
            "stage": "L1"
        }
    }
]

mock_customers_l2 = [
    {
        "custId": "CUST2",
        "stage": "L2",
        "demographics": {
            "mobileNumber": "9876543210",
            "name": "Manju"
        },
        "loanDetails": {
            "amount": "100000"
        },
        "bankAccountDetails": {
            "id": "BANK001",
            "ifsc": "SBIN0000123",
            "disbursementPreference": "Direct Transfer",
            "dedupe": True,
            "isActive": True,
            "errorMessage": None
        },
        "documents": {
            "keys": ["doc5", "doc6"],
            "type": "Final Verification"
        },
        "level": "Stage 2",
        "status": "Completed",
        "isEditable": False,
        "isDeletable": False,
        "isEkycExpiry": False,
        "isDedupeExpiry": False,
        "verification": {
            "reasons": [],
            "comments": "All details verified successfully"
        },
        "currentAddress": {
            "houseNo": "123A",
            "street": "Main Street",
            "locality": "BTM Layout",
            "landmark": "BTM Water Tank",
            "vtc": "Tech City",
            "state": "Karnataka",
            "district": "Banglore",
            "city": "Banglore",
            "stateCode": "ST01",
            "cityCode": "CT01",
            "districtCode": "DT01",
            "pincode": "123456",
            "id": "ADDR001",
            "type": "Residential",
            "updated_at": "2024-11-20T10:00:00Z",
            "created_at": "2024-11-10T08:00:00Z",
            "natureOfResidence": "Owned"
        },
        "creditReports": {
            "id": "CREDIT001",
            "isNew": False,
            "isExpired": False
        },
        "stageUpdatedAt": "2024-11-25T15:45:00Z",
        "summary": {
            "custId": "CUST2",
            "name": "Manju",
            "loanAmount": "100000",
            "status": "Completed",
            "stage": "L2"
        }
    }
]

mock_customers_l3 = [
    {
        "custId": "CUST3",
        "stage": "L3",
        "demographics": {
            "mobileNumber": "9876543215",
            "name": "Kumari"
        },
        "loanDetails": {
            "amount": "200000"
        },
        "bankAccountDetails": {
            "id": "BANK005",
            "ifsc": "SBIN0000123",
            "disbursementPreference": "Direct Transfer",
            "dedupe": True,
            "isActive": True,
            "errorMessage": None
        },
        "documents": {
            "keys": ["doc10", "doc11"],
            "type": "Final Verification"
        },
        "level": "Stage 3",
        "status": "Completed",
        "isEditable": False,
        "isDeletable": False,
        "isEkycExpiry": False,
        "isDedupeExpiry": False,
        "verification": {
            "reasons": [],
            "comments": "Final verification completed"
        },
        "currentAddress": {
            "houseNo": "505",
            "street": "Fifth Avenue",
            "locality": "City Center",
            "landmark": "Near Library",
            "vtc": "Tech City",
            "state": "Karnataka",
            "district": "Banglore",
            "city": "Banglore",
            "stateCode": "ST01",
            "cityCode": "CT01",
            "districtCode": "DT01",
            "pincode": "654321",
            "id": "ADDR005",
            "type": "Residential",
            "updated_at": "2025-05-15T12:00:00Z",
            "created_at": "2025-05-01T10:00:00Z",
            "natureOfResidence": "Owned"
        },
        "creditReports": {
            "id": "CREDIT003",
            "isNew": False,
            "isExpired": False
        },
        "stageUpdatedAt": "2025-05-20T10:00:00Z",
        "summary": {
            "custId": "CUST3",
            "name": "Kumari",
            "loanAmount": "200000",
            "status": "Completed",
            "stage": "L3"
        }
    }
]



@app.route('/main/customer/generateOTP', methods=['POST'])
def generate_mobile_otp():
    try:
        # Parse request data
        data = request.json
        phone_number = data.get('phoneNumber')
        otp_type = data.get('type', 'ONBOARDING')  # Default to ONBOARDING if not provided

        # Validate input
        if not phone_number:
            return jsonify({
                "payload": {
                    "message": "Phone number is required",
                    "code": "400"
                }
            }), 400

        # Validate phone number length and characters
        if len(phone_number) != 10 or not phone_number.isdigit():
            return jsonify({
                "payload": {
                    "message": "Invalid phone number. It must be a 10-digit numeric value.",
                    "code": "400"
                }
            }), 400

        # Generate a random OTP
        otp = '111111'

        # Build response
        response = {
            "payload": {
                "data": {
                    "response": "OTP generated successfully",
                    "otp": otp
                },
                "message": f"OTP has been sent to your registered mobile number {phone_number}",
                "code": "200"
            }
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            "payload": {
                "message": "An error occurred while generating OTP",
                "code": "500",
                "error": str(e)
            }
        }), 500

@app.route('/main/customer/validateOTP', methods=['POST'])
def validate_mobile_otp():
    try:
        # Parse request data
        data = request.json

        print('data', data)

        phone_number = data.get('payload', {}).get('mobile')
        otp = data.get('payload', {}).get('otp')

        # Validate input
        if not phone_number or not otp:
            return jsonify({
                "payload": {
                    "message": "Phone number and OTP are required.",
                    "code": "400"
                }
            }), 400

        # Validate phone number
        if len(phone_number) != 10 or not phone_number.isdigit():
            return jsonify({
                "payload": {
                    "message": "Invalid phone number. It must be a 10-digit numeric value.",
                    "code": "400"
                }
            }), 400

        # Validate OTP (static OTP for simplicity)
        STATIC_OTP = "111111"
        if otp != STATIC_OTP:
            return jsonify({
                "payload": {
                    "data": False,
                    "message": "Invalid OTP.",
                    "code": "401"
                }
            }), 401

        # Successful OTP validation
        response = {
            "payload": {
                "data": True,
                "message": "OTP validated successfully",
                "code": "200"
            }
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            "payload": {
                "message": "An error occurred while validating OTP.",
                "code": "500",
                "error": str(e)
            }
        }), 500

# Uploading Images
#   
# Customer Document Upload (L1):
#   For uploading applicant photos, PAN card images, and address proofs.
# Household Member Document Upload (L2):
#   For uploading KYC and asset-related images.
# Bank Account Document Upload (L3):
#   For uploading proof of account images.

@app.route('/main/customer/upload', methods=['POST'])
def upload_customer_documents():
    try:
        # Parse metadata from form-data
        customer_id = request.form.get("customerId")
        doc_type = request.form.get("type")
        files = request.files.getlist("files")

        # Validate inputs
        if not customer_id or not doc_type or not files:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Missing required fields (customerId, type, or files)",
                    "code": "400",
                    "error": "Invalid Input"
                }
            }), 400

        # Simulate file upload and return URLs
        uploaded_urls = []
        for file in files:
            uploaded_urls.append(f"https://cdn.example.com/images/{file.filename}")

        # Mock response
        return jsonify({
            "payload": {
                "code": "200",
                "message": "Images uploaded successfully",
                "data": {
                    "id": "IMG123456",
                    "metadata": f"{doc_type} Documents",
                    "name": f"Upload Batch for {customer_id}",
                    "urls": uploaded_urls,
                    "message": "Upload completed"
                },
                "error": None
            }
        })

    except Exception as e:
        return jsonify({
            "payload": {
                "data": None,
                "message": "Error occurred during upload",
                "code": "500",
                "error": str(e)
            }
        }), 500


@app.route('/main/household/upload', methods=['POST'])
def upload_household_documents():
    try:
        # Parse metadata from form-data
        customer_id = request.form.get("customerId")
        member_id = request.form.get("memberId")
        doc_type = request.form.get("type")
        files = request.files.getlist("files")

        # Validate inputs
        if not customer_id or not member_id or not doc_type or not files:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Missing required fields (customerId, memberId, type, or files)",
                    "code": "400",
                    "error": "Invalid Input"
                }
            }), 400

        # Simulate file upload and return URLs
        uploaded_urls = []
        for file in files:
            uploaded_urls.append(f"https://cdn.example.com/images/{file.filename}")

        # Mock response
        return jsonify({
            "payload": {
                "code": "200",
                "message": "Images uploaded successfully",
                "data": {
                    "id": "IMG789101",
                    "metadata": f"{doc_type} Documents for Member {member_id}",
                    "name": f"Upload Batch for Household {customer_id}",
                    "urls": uploaded_urls,
                    "message": "Upload completed"
                },
                "error": None
            }
        })

    except Exception as e:
        return jsonify({
            "payload": {
                "data": None,
                "message": "Error occurred during upload",
                "code": "500",
                "error": str(e)
            }
        }), 500

@app.route('/main/bank/upload', methods=['POST'])
def upload_bank_documents():
    try:
        # Parse metadata from form-data
        customer_id = request.form.get("customerId")
        doc_type = request.form.get("type")
        files = request.files.getlist("files")

        # Validate inputs
        if not customer_id or not doc_type or not files:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Missing required fields (customerId, type, or files)",
                    "code": "400",
                    "error": "Invalid Input"
                }
            }), 400

        # Simulate file upload and return URLs
        uploaded_urls = []
        for file in files:
            uploaded_urls.append(f"https://cdn.example.com/images/{file.filename}")

        # Mock response
        return jsonify({
            "payload": {
                "code": "200",
                "message": "Images uploaded successfully",
                "data": {
                    "id": "IMG654321",
                    "metadata": f"{doc_type} Documents",
                    "name": f"Upload Batch for Customer {customer_id}",
                    "urls": uploaded_urls,
                    "message": "Upload completed"
                },
                "error": None
            }
        })

    except Exception as e:
        return jsonify({
            "payload": {
                "data": None,
                "message": "Error occurred during upload",
                "code": "500",
                "error": str(e)
            }
        }), 500


@app.route('/main/customer/submitDetails', methods=['POST'])
def submit_l1_additional_details():
    try:
        # Parse request data
        request_data = request.get_json()

        if not request_data or "payload" not in request_data:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Missing payload in the request",
                    "code": "400",
                    "error": "Payload must include customerId and demographics"
                }
            }), 400

        payload = request_data["payload"]
        customer_id = payload.get("customerId")  # Include customerId
        demographics = payload.get("demographics", {})

        # Validate customerId
        if not customer_id:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Missing customerId in the payload",
                    "code": "400",
                    "error": "Customer ID is required"
                }
            }), 400

        # Validate mandatory demographics fields
        required_fields = ["fullName", "dob", "gender", "mobileNumber", "maritalStatus", "educationalQualification", "natureOfResidence"]
        missing_fields = [field for field in required_fields if field not in demographics]

        if missing_fields:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": f"Missing demographic fields: {', '.join(missing_fields)}",
                    "code": "400",
                    "error": "Validation Error"
                }
            }), 400

        # Simulate data submission
        response_data = {
            "customerId": customer_id,
            "demographics": demographics
        }

        return jsonify({
            "payload": {
                "data": response_data,
                "message": "L1 additional details submitted successfully",
                "code": "200",
                "error": None
            }
        })

    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            "payload": {
                "data": None,
                "message": "Error occurred while submitting L1 details",
                "code": "500",
                "error": str(e)
            }
        }), 500

@app.route('/main/customer/singleList', methods=['POST'])
def get_l1_submitted_customers_list():
    try:
        # Parse request data
        # Parse request data
        user_id = request.args.get('userId')

        if not user_id:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Missing user_id in the request payload",
                    "code": "400",
                    "error": "Invalid Input"
                }
            }), 400


        # Filter mock customers based on user_id
        # Assuming `user_id` is linked to all customers in the mock data
        filtered_customers = [
            customer for customer in mock_customers_l1
        ]

        # Construct response
        response_data = {
            "count": len(filtered_customers),
            "customers": filtered_customers
        }

        return jsonify({
            "payload": {
                "data": response_data,
                "message": "Customer list fetched successfully",
                "code": "200",
                "error": None
            }
        }), 200

    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            "payload": {
                "data": None,
                "message": "Error occurred while fetching the customer list",
                "code": "500",
                "error": str(e)
            }
        }), 500

@app.route('/main/customer/members', methods=['PUT'])
def submit_update_household_member_details():
    try:
        # Parse request data
        request_data = request.get_json()

        if not request_data or "payload" not in request_data:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Missing payload in the request",
                    "code": "400",
                    "error": "Payload must include household member details"
                }
            }), 400

        payload = request_data["payload"]
        customer_id = payload.get("customerId")  # Explicitly include customerId

        # Validate customerId
        if not customer_id:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Missing customerId in the payload",
                    "code": "400",
                    "error": "Customer ID is required"
                }
            }), 400

        members = payload.get("members", [])

        # Validate members array
        if not isinstance(members, list) or not members:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Invalid or empty members list",
                    "code": "400",
                    "error": "Members must be a non-empty list"
                }
            }), 400

        # Validate required fields for each member
        required_fields = ["id", "fullName", "gender", "dob", "relationship"]
        invalid_members = []

        for member in members:
            missing_fields = [field for field in required_fields if field not in member or not member[field]]
            if missing_fields:
                invalid_members.append({"member": member.get("id", "UNKNOWN"), "missingFields": missing_fields})

        if invalid_members:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Validation failed for some members",
                    "code": "400",
                    "error": invalid_members
                }
            }), 400

        # Simulate submission/update process
        updated_members = []
        for member in members:
            # Mock response with essential details
            updated_members.append({
                "id": member["id"],
                "custId": customer_id,  # Associate with customerId
                "tempId": member.get("tempId"),
                "fullName": member["fullName"],
                "gender": member["gender"],
                "dob": member["dob"],
                "age": member.get("age"),
                "relationship": member["relationship"],
                "isNominee": member.get("isNominee", False),
                "incomeDetails": [
                    {
                        "id": income["id"],
                        "type": income["type"],
                        "employmentType": income["employmentType"],
                        "occupation": income["occupation"],
                        "designation": income["designation"],
                        "income": income["income"]
                    } for income in member.get("incomeDetails", [])
                ],
                "documents": {
                    "kycDocuments": member.get("documents", {}).get("kycDocuments"),
                    "customerPhoto": member.get("documents", {}).get("customerPhoto"),
                }
            })

        # Success response
        return jsonify({
            "payload": {
                "data": updated_members,
                "message": "Household member details submitted successfully",
                "code": "200",
                "error": None
            }
        })

    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            "payload": {
                "data": None,
                "message": "Error occurred while submitting/updating household member details",
                "code": "500",
                "error": str(e)
            }
        }), 500

@app.route('/main/customer/household/submit', methods=['POST'])
def submit_household_details():
    try:
        # Parse request data
        request_data = request.get_json()

        if not request_data or "payload" not in request_data:
            return jsonify({
                "payload": {
                    "message": "Missing payload in the request",
                    "code": "400",
                    "error": "Payload must include customerId, consent, and loan details"
                }
            }), 400

        payload = request_data["payload"]
        customer_id = payload.get("customerId")  # Include customerId explicitly
        consent = payload.get("consent")
        opted_loan = payload.get("optedLoan", {})

        # Validate required fields
        if not customer_id:
            return jsonify({
                "payload": {
                    "message": "Missing customerId in the payload",
                    "code": "400",
                    "error": "Customer ID is required"
                }
            }), 400

        if consent is None:
            return jsonify({
                "payload": {
                    "message": "Consent is required",
                    "code": "400",
                    "error": "Missing Consent"
                }
            }), 400

        required_loan_fields = ["amount", "tenure", "purpose", "netWorth"]
        missing_loan_fields = [field for field in required_loan_fields if field not in opted_loan]

        if missing_loan_fields:
            return jsonify({
                "payload": {
                    "message": f"Missing loan details: {', '.join(missing_loan_fields)}",
                    "code": "400",
                    "error": "Validation Error"
                }
            }), 400

        # Simulate data processing and response
        return jsonify({
            "payload": {
                "message": "Household details submitted successfully for customerId: " + customer_id,
                "code": "200",
                "error": None
            }
        }), 200

    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            "payload": {
                "message": "Error occurred while submitting household details",
                "code": "500",
                "error": str(e)
            }
        }), 500

@app.route('/main/customer/amenities', methods=['POST'])
def submit_amenities():
    try:
        # Parse request data
        request_data = request.get_json()

        if not request_data or "payload" not in request_data:
            return jsonify({
                "payload": {
                    "message": "Missing payload in the request",
                    "code": "400",
                    "error": "Payload must include customerId and amenities list"
                }
            }), 400

        payload = request_data["payload"]
        customer_id = payload.get("customerId")  # Include customerId explicitly
        amenities = payload.get("amenities", [])

        # Validate customerId
        if not customer_id:
            return jsonify({
                "payload": {
                    "message": "Missing customerId in the payload",
                    "code": "400",
                    "error": "Customer ID is required"
                }
            }), 400

        # Validate amenities list
        if not isinstance(amenities, list) or not amenities:
            return jsonify({
                "payload": {
                    "message": "Invalid or empty amenities list",
                    "code": "400",
                    "error": "Amenities must be a non-empty list"
                }
            }), 400

        # Validate required fields in each amenity
        required_fields = ["code", "value"]
        invalid_amenities = []

        for amenity in amenities:
            missing_fields = [field for field in required_fields if field not in amenity]
            if missing_fields:
                invalid_amenities.append({"amenity": amenity.get("code", "UNKNOWN"), "missingFields": missing_fields})

        if invalid_amenities:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Validation failed for some amenities",
                    "code": "400",
                    "error": invalid_amenities
                }
            }), 400

        # Simulate amenity creation
        created_amenities = []
        for idx, amenity in enumerate(amenities):
            created_amenities.append({
                "id": f"AMEN{str(idx + 1).zfill(3)}",
                "code": amenity["code"],
                "value": amenity["value"],
                "error": None
            })

        return jsonify({
            "payload": {
                "code": "200",
                "message": "Amenities created successfully",
                "data": created_amenities,
                "error": None
            }
        }), 200

    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            "payload": {
                "message": "Error occurred while submitting amenities",
                "code": "500",
                "error": str(e)
            }
        }), 500

@app.route('/main/customer/assets', methods=['POST'])
def submit_assets():
    try:
        # Parse request data
        request_data = request.get_json()

        if not request_data or "payload" not in request_data:
            return jsonify({
                "payload": {
                    "message": "Missing payload in the request",
                    "code": "400",
                    "error": "Payload must include customerId and asset details"
                }
            }), 400

        payload = request_data["payload"]
        customer_id = payload.get("customerId")  # Include customerId explicitly
        assets = payload.get("assets", [])

        # Validate customerId
        if not customer_id:
            return jsonify({
                "payload": {
                    "message": "Missing customerId in the payload",
                    "code": "400",
                    "error": "Customer ID is required"
                }
            }), 400

        # Validate assets list
        if not isinstance(assets, list) or not assets:
            return jsonify({
                "payload": {
                    "message": "Invalid or empty assets list",
                    "code": "400",
                    "error": "Assets must be a non-empty list"
                }
            }), 400

        # Validate required fields in each asset
        required_fields = ["category", "code", "value"]
        invalid_assets = []

        for asset in assets:
            missing_fields = [field for field in required_fields if field not in asset]
            if missing_fields:
                invalid_assets.append({"asset": asset.get("code", "UNKNOWN"), "missingFields": missing_fields})

        if invalid_assets:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Validation failed for some assets",
                    "code": "400",
                    "error": invalid_assets
                }
            }), 400

        # Simulate asset submission
        submitted_assets = []
        for idx, asset in enumerate(assets):
            submitted_assets.append({
                "id": f"ASSET{str(idx + 1).zfill(3)}",
                "custId": customer_id,
                "category": asset["category"],
                "type": asset.get("type", asset["code"].capitalize()),  # Default to code if type is missing
                "code": asset["code"],
                "value": asset["value"]
            })

        return jsonify({
            "payload": {
                "code": "200",
                "message": "Asset information submitted successfully",
                "error": None,
                "data": submitted_assets
            }
        }), 200

    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            "payload": {
                "message": "Error occurred while submitting asset information",
                "code": "500",
                "error": str(e)
            }
        }), 500

@app.route('/main/customer/expenses', methods=['POST'])
def submit_expenses():
    try:
        # Parse request data
        request_data = request.get_json()

        if not request_data or "payload" not in request_data:
            return jsonify({
                "payload": {
                    "message": "Missing payload in the request",
                    "code": "400",
                    "error": "Payload must include customerId and expense details"
                }
            }), 400

        payload = request_data["payload"]
        customer_id = payload.get("customerId")  # Include customerId explicitly
        expenses = payload.get("expenses", [])

        # Validate customerId
        if not customer_id:
            return jsonify({
                "payload": {
                    "message": "Missing customerId in the payload",
                    "code": "400",
                    "error": "Customer ID is required"
                }
            }), 400

        # Validate expenses list
        if not isinstance(expenses, list) or not expenses:
            return jsonify({
                "payload": {
                    "message": "Invalid or empty expenses list",
                    "code": "400",
                    "error": "Expenses must be a non-empty list"
                }
            }), 400

        # Validate required fields in each expense
        required_fields = ["type", "code", "value"]
        invalid_expenses = []

        for expense in expenses:
            missing_fields = [field for field in required_fields if field not in expense]
            if missing_fields:
                invalid_expenses.append({"expense": expense.get("code", "UNKNOWN"), "missingFields": missing_fields})

        if invalid_expenses:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Validation failed for some expenses",
                    "code": "400",
                    "error": invalid_expenses
                }
            }), 400

        # Simulate expense submission
        submitted_expenses = []
        current_time = datetime.now().isoformat()
        for idx, expense in enumerate(expenses):
            submitted_expenses.append({
                "tid": f"TID{str(idx + 1).zfill(3)}",
                "id": f"EXP{str(idx + 1).zfill(3)}",
                "custId": customer_id,
                "type": expense["type"],
                "code": expense["code"],
                "expenseType": "Fixed" if expense["type"] in ["Rent"] else "Variable",
                "value": expense["value"],
                "created_at": current_time,
                "updated_at": current_time,
                "deleted_at": None,
                "recurring": expense["type"] in ["Rent", "Utilities"]  # Example recurring logic
            })

        return jsonify({
            "payload": {
                "data": submitted_expenses,
                "message": "Expenses created successfully",
                "error": None,
                "code": "200"
            }
        }), 200

    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            "payload": {
                "message": "Error occurred while submitting expenses",
                "code": "500",
                "error": str(e)
            }
        }), 500
    
@app.route('/main/customer/eligibility', methods=['POST'])
def eligibility_check():
    try:
        # Parse request arguments
        customer_id = request.args.get('customerId')  # Include customerId in query parameters

        # Validate customerId
        if not customer_id:
            return jsonify({
                "payload": {
                    "error": "Customer ID is required",
                    "code": "400",
                    "message": "Missing customerId in the request",
                    "data": None
                }
            }), 400

        # Mock eligibility data
        eligibility_data = {
            "monthlyIncome": 50000.0,
            "monthlyLiabilities": 15000,
            "eligibleLoanAmount": 1000000,
            "loanAmounts": [500000, 750000, 1000000],
            "interestRate": 8,
            "tenure": 24,
            "purpose": "Home Renovation",
            "optedLoanAmount": 750000,
            "annualCustomerIncome": 600000,
            "netWorth": 2000000
        }

        # Simulate successful response
        return jsonify({
            "payload": {
                "error": None,
                "code": "200",
                "message": "Eligibility data fetched successfully",
                "data": eligibility_data
            }
        }), 200

    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            "payload": {
                "error": str(e),
                "code": "500",
                "message": "Error occurred while fetching eligibility data",
                "data": None
            }
        }), 500


@app.route('/main/customer/calculate', methods=['POST'])
def calculate_emi():
    try:
        # Parse request data
        request_data = request.get_json()

        if not request_data or "payload" not in request_data:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Missing payload in the request",
                    "code": "400",
                    "error": "Payload with customerId, amount, and tenure must be provided"
                }
            }), 400

        payload = request_data["payload"]
        customer_id = payload.get("customerId")
        amount = payload.get("amount")
        tenure = payload.get("tenure")

        # Validate inputs
        if not customer_id:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Missing customer ID",
                    "code": "400",
                    "error": "Customer ID must be provided"
                }
            }), 400

        if not amount or not isinstance(amount, (int, float)) or amount <= 0:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Invalid amount",
                    "code": "400",
                    "error": "Amount must be a positive number"
                }
            }), 400

        if not tenure or not isinstance(tenure, int) or tenure <= 0:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Invalid tenure",
                    "code": "400",
                    "error": "Tenure must be a positive integer"
                }
            }), 400

        # Assumed interest rate (for demonstration purposes)
        interest_rate = 5.5  # Annual interest rate in percentage
        monthly_rate = interest_rate / (12 * 100)  # Convert to monthly interest rate

        # EMI Calculation Formula
        emi = (amount * monthly_rate * pow(1 + monthly_rate, tenure)) / (pow(1 + monthly_rate, tenure) - 1)
        emi = round(emi, 2)

        # Success response
        return jsonify({
            "payload": {
                "data": {
                    "customerId": customer_id,
                    "emi": emi,
                    "interest": interest_rate,
                    "principle": amount
                },
                "message": "EMI and interest calculated successfully",
                "code": "200",
                "error": None
            }
        })

    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            "payload": {
                "data": None,
                "message": "Error occurred while calculating EMI",
                "code": "500",
                "error": str(e)
            }
        }), 500

@app.route('/main/customer/l2List', methods=['GET'])
def get_l2_submitted_customers_list():
    try:
        # Parse request data
        user_id = request.args.get('userId')

        if not user_id:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Missing user_id in the request payload",
                    "code": "400",
                    "error": "Invalid Input"
                }
            }), 400

        # # Validate user_id
        # if not isinstance(user_id, str) or not user_id.startswith("USER"):
        #     return jsonify({
        #         "payload": {
        #             "data": None,
        #             "message": "Invalid user_id format",
        #             "code": "400",
        #             "error": "Validation Error"
        #         }
        #     }), 400

        # Filter mock customers by user_id (this logic simulates a relationship mapping)
        # Assuming all L2 customers belong to the user
        filtered_customers = mock_customers_l2  # Replace with actual filtering logic if needed

        # Construct response
        response_data = {
            "customers": filtered_customers,
            "total_count": len(filtered_customers)
        }

        return jsonify({
            "payload": {
                "data": response_data,
                "message": "L2 customer list fetched successfully",
                "code": "200",
                "error": None
            }
        }), 200

    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            "payload": {
                "data": None,
                "message": "Error occurred while fetching the L2 customer list",
                "code": "500",
                "error": str(e)
            }
        }), 500

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
        bank_details = ifsc_database.get(ifsc)

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
                "data": bank_details,
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

@app.route('/main/customer/account', methods=['POST'])
def submit_bank_details():
    try:
        # Parse request data
        request_data = request.get_json()

        if not request_data or "payload" not in request_data:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Missing payload in the request",
                    "code": "400",
                    "error": "Payload must include customerId and account details"
                }
            }), 400

        payload = request_data["payload"]
        customer_id = payload.get("customerId")  # Fetch customerId from payload

        # Validate customerId
        if not customer_id:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Missing customerId in the payload",
                    "code": "400",
                    "error": "Customer ID is required"
                }
            }), 400

        # Validate required fields in the payload
        required_fields = ["disbursementPreference", "consent", "bankDetails"]
        missing_fields = [field for field in required_fields if field not in payload]

        if missing_fields:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": f"Missing fields: {', '.join(missing_fields)}",
                    "code": "400",
                    "error": "Validation Error"
                }
            }), 400

        bank_details = payload["bankDetails"]

        # Validate mandatory fields in bankDetails
        required_bank_fields = [
            "accountHolderName", "accountNumber", "reAccNumber",
            "ifsc", "branchName", "branchAddress", "proofOfAccount"
        ]
        missing_bank_fields = [field for field in required_bank_fields if field not in bank_details]

        if missing_bank_fields:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": f"Missing fields in bank details: {', '.join(missing_bank_fields)}",
                    "code": "400",
                    "error": "Validation Error"
                }
            }), 400

        # Simulate processing and validate account number matching
        if bank_details["accountNumber"] != bank_details["reAccNumber"]:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Account numbers do not match",
                    "code": "400",
                    "error": "Account Number Mismatch"
                }
            }), 400

        # Simulate success response
        return jsonify({
            "payload": {
                "data": bank_details,
                "message": "Account details submitted successfully",
                "error": None,
                "code": "200"
            }
        }), 200

    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            "payload": {
                "data": None,
                "message": "Error occurred while submitting account details",
                "code": "500",
                "error": str(e)
            }
        }), 500

@app.route('/main/customer/l3List', methods=['GET'])
def get_l3_submitted_customers_list():
    try:
        # Parse request data
        user_id = request.args.get('userId')

        if not user_id:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Missing user_id in the request payload",
                    "code": "400",
                    "error": "Invalid Input"
                }
            }), 400

        # # Validate user_id
        # if not isinstance(user_id, str):
        #     return jsonify({
        #         "payload": {
        #             "data": None,
        #             "message": "Invalid user_id format",
        #             "code": "400",
        #             "error": "Validation Error"
        #         }
        #     }), 400

        # Filter mock customers by user_id (this logic simulates a relationship mapping)
        # Assuming all L3 customers belong to the user
        filtered_customers = mock_customers_l3  # Replace with actual filtering logic if needed

        # Construct response
        response_data = {
            "customers": filtered_customers,
            "total_count": len(filtered_customers)
        }

        return jsonify({
            "payload": {
                "data": response_data,
                "message": "L3 customer list fetched successfully",
                "code": "200",
                "error": None
            }
        }), 200

    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            "payload": {
                "data": None,
                "message": "Error occurred while fetching the L3 customer list",
                "code": "500",
                "error": str(e)
            }
        }), 500

@app.route('/main/customer/retriggerEKYC', methods=['POST'])
def retrigger_ekyc():
    try:
        # Parse request data
        request_data = request.get_json()

        if not request_data or "payload" not in request_data:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Missing payload in the request",
                    "code": "400",
                    "error": "Payload must include customerId and EKYC details"
                }
            }), 400

        payload = request_data["payload"]
        customer_id = payload.get("customerId")  # Include customerId
        ekyc_requests = payload.get("ekycRequests", [])

        # Validate customerId
        if not customer_id:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Missing customerId in the payload",
                    "code": "400",
                    "error": "Customer ID is required"
                }
            }), 400

        # Validate ekycRequests list
        if not isinstance(ekyc_requests, list) or not ekyc_requests:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Invalid or empty EKYC requests list",
                    "code": "400",
                    "error": "EKYC requests must be a non-empty list"
                }
            }), 400

        # Validate required fields in each EKYC request
        required_fields = ["id", "aadharNumber", "transactionId"]
        invalid_requests = []

        for ekyc_request in ekyc_requests:
            missing_fields = [field for field in required_fields if field not in ekyc_request or not ekyc_request[field]]
            if missing_fields:
                invalid_requests.append({"request": ekyc_request.get("id", "UNKNOWN"), "missingFields": missing_fields})

        if invalid_requests:
            return jsonify({
                "payload": {
                    "data": None,
                    "message": "Validation failed for some EKYC requests",
                    "code": "400",
                    "error": invalid_requests
                }
            }), 400

        # Simulate EKYC retrigger
        return jsonify({
            "payload": {
                "data": {
                    "customerId": customer_id,
                    "status": "EKYC retriggered successfully"
                },
                "message": "EKYC retriggered successfully",
                "code": "200",
                "error": None
            }
        })

    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            "payload": {
                "data": None,
                "message": "Error occurred while retriggering EKYC",
                "code": "500",
                "error": str(e)
            }
        }), 500


@app.route('/main/customer/credit-check', methods=['POST'])
def retry_credit_check():
    try:
        # Mock logic to randomly select a customer for the credit check (demo purpose)
        customer_id = customers_db[0]  # Assuming CUST0 is the one being checked

        # Generate mock response
        response = {
            "payload": {
                "data": {
                    "custId": customer_id,
                    "level": "Level 2",
                    "label": "Credit Eligibility Check",
                    "status": "Approved"  # For simplicity, always return "Approved"
                },
                "message": "Credit check retried successfully",
                "code": "200",
                "error": None
            }
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({
            "payload": {
                "data": None,
                "message": "Error occurred during credit check retry",
                "code": "500",
                "error": str(e)
            }
        }), 500
    

@app.route('/main/group/create', methods=['POST'])
def create_group():
    try:
        data = request.json.get("payload", {})
        customers = data.get("customers", [])
        group_head = data.get("groupHead", "")
        village_name = data.get("villageName", "")

        # Validations
        if not customers:
            return jsonify({"payload": {"code": "400", "message": "Customers list is required", "error": "Invalid Input"}}), 400
        
        if len(customers) < 4:
            return jsonify({"payload": {"code": "400", "message": "At least 4 customers are required to create a group", "error": "Insufficient Customers"}}), 400
        
        if len(customers) > 7:
            return jsonify({"payload": {"code": "400", "message": "Maximum of 7 customers allowed without special permission", "error": "Exceeds Limit"}}), 400
        
        if group_head not in customers:
            return jsonify({"payload": {"code": "400", "message": "Group head must be included in the customers list", "error": "Invalid Group Head"}}), 400
        
        if not village_name:
            return jsonify({"payload": {"code": "400", "message": "Village name is required", "error": "Missing Village Name"}}), 400

        # Generate a unique group ID and group name
        group_id = f"GRP{random.randint(10000, 99999)}"
        group_name = f"{village_name} Group"

        # Success response
        return jsonify({
            "payload": {
                "code": "200",
                "message": "Group created successfully",
                "error": None,
                "data": {
                    "groupId": group_id,
                    "groupName": group_name
                }
            }
        })

    except Exception as e:
        return jsonify({"payload": {"code": "500", "message": "Internal Server Error", "error": str(e)}}), 500


if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)