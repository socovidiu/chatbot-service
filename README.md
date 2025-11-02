# Resume Chatbot API

This project is a chatbot application designed to assist users in creating resumes by providing AI-generated suggestions and guidance. The chatbot interacts with users to gather information and offers tailored advice based on their profiles.



## Features

- **Chatbot Interaction**: Users can interact with the chatbot to receive suggestions for their resumes.
- **AI Suggestions**: The chatbot utilizes LLM operators to generate relevant suggestions based on user input.
- **Resume Models**: Data models are defined to handle resume-related information effectively.
- **API Endpoints**: The application exposes API endpoints for chatbot functionality.

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd chatbot-service
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Copy `.env.example` to `.env` and fill in the necessary values.

5. Run the application:
   ```
   python src/chatbot_servic/main.py
   ```

## Testing

To run the tests, use the following command:
```
pytest tests/test_chat.py
```

## License

This project is licensed under the MIT License. See the LICENSE file for more details.