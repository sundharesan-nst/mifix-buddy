## nst-rm-support
A multilingual Chatbot with a purpose to support Relationship Manager in daily tasks.

# Project Setup Instructions

## Prerequisites

1. Ensure the following are in place:
   - All necessary setup is complete.
   - A `.env` file is configured with required environment variables.

---

## Next Steps

1. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Populate the Vector Database**
   - If chunks are already available in the `smart_chunks/` directory:
     ```bash
     python general_utils/just_upsert.py
     ```
   - Otherwise, generate and vectorize the chunks:
     ```bash
     python general_utils/chunk_and_vectorize.py
     ```

4. **Run the Application**
   ```bash
   python app.py
   ```


