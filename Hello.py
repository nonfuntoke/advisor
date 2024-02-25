from dotenv import load_dotenv
import streamlit as st
import os
# Load environment variables from .env file
load_dotenv()
# Now you can access your API keys (and other environment variables)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

import openai
import pandas as pd

# Set your OpenAI API key here
#openai.api_key = 'your-api-key'

def ask_question(prompt):
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # you can replace this with your preferred model
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    return completion.choices[0].message.content

def interact_with_ai(message, model="gpt-3.5-turbo"):
    prompt = f"You are a hosting advisor and you role is to reply in few words to the {message} just to keep the user engaged and make him feel that he is interacting with someone. Please use 1 emoji per answer max."
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # you can replace this with your preferred model
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )
    return completion.choices[0].message.content


def recommend_hosting_with_ai(dialog, data_csv):
    # Read the CSV data into a string format suitable for the prompt
    hosting_data = pd.read_csv(data_csv)
    hosting_data_string = hosting_data.to_string(index=False)

    # Construct the prompt
    prompt = (f"Based on the following user answers:\n{dialog}\n\n"
              f"And the following hosting service data:\n{hosting_data_string}\n\n"
              "Suggest the best hosting service and return the name, link, and explanation in separate lines.")

    # Call the OpenAI API
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",  
        messages=[{"role": "user", "content": prompt}]
    )

    return completion.choices[0].message.content

# Define the main function of the application
# Define the main function of the application
def main():
    # Set page config
    st.set_page_config(page_title="Hosting Service Advisor", page_icon=":computer:")

    # Define the color of the heading
    heading_color = "#FF5A60"  # You can adjust this color as needed

    # Styling for the title and selectable options
    st.markdown(
        f"""
        <style>
        .title {{
            font-size: 42px;
            font-weight: bold;
            color: {heading_color};
            padding-bottom: 20px;
            text-align: center;
        }}
        .subtitle {{
            font-size: 24px;
            font-weight: bold;
            color: #53A586;
            text-align: center;
        }}
        .footer {{
            background-color: #fff;
            padding: 10px 0;
            text-align: center;
            font-size: 14px;
            color: #666666;
        }}
        .selectable-option {{
            display: inline-block;
            width: 45%; /* Adjust the width of each option */
            margin: 10px;
            padding: 20px;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            text-align: center;
            background-color: {heading_color};
            color: white;
            font-size: 30px;
        }}
        .selectable-option:hover {{
            background-color: #FF7E82; /* Lighter shade of heading color */
        }}
        </style>
        """
        , unsafe_allow_html=True
    )

    # Title with styling
    st.markdown('<p class="title">Hosting Service Advisor</p>', unsafe_allow_html=True)

    # Load hosting data from CSV
    file_path = 'data.csv'  # Update this with the path to your CSV file

    # Define the questions you're going to ask the user
    questions = [
        "What is your monthly budget for web hosting?",
        "How much traffic do you expect your website to have?",
        "What is the primary purpose of your website? (e.g., blog, e-commerce, portfolio)",
        "Do you plan using any of these CMS?",
        "Do you have a preference for where your server is located geographically?"
    ]

    # Display a welcome message
    st.write("Welcome to the Hosting Service Advisor!")

    # Retrieve the index of the current question from session state
    question_index = st.session_state.get('question_index', 0)

    # Check if there are more questions to ask
    if question_index < len(questions):
        question = questions[question_index]  # Get the current question
        dialog = ""  # Initialize an empty string to hold the dialog

        # Display the question as a subheader
        st.subheader(f"{question_index + 1}: {question}")

        # Check if it's the second question to provide selectable choices
        if question_index == 1:
            selected_choice = st.radio("Please select from the list below:", options=["Low Traffic", "Medium", "Moderate", "High Traffic"], index=None, help="Click to select your answer")  # Use HTML to format options
            user_answer = selected_choice if selected_choice else None  # If none selected, set answer to None
        elif question_index == 3:
            selected_choice = st.radio("Please select from the list below:", options=["PrestaShop", "Magento", "Wordpress", "OpenCart", "Other"], index=None, help="Click to select your answer")  # Use HTML to format options
            user_answer = selected_choice if selected_choice else None  # If none selected, set answer to None
        else:
            # Input box for the user's answer with styling
            user_answer = st.text_input("Your Answer:", key=f"answer_{question_index}", 
                                        help="Type your answer here and press Enter")

        # Check if the user has provided an answer
        if user_answer:
            dialog += f"{question}\n {user_answer}\n"  # Append the question and answer to the dialog

            # Get a brief reply from the AI regarding the user's answer
            # Note: for actual deployment, consider adding conditions to prevent excessive API calls
            brief_reply = interact_with_ai(dialog)
            
            # Display the brief reply from the AI as a centered subtitle
            st.markdown(f"<h2 class='subtitle'>{brief_reply}</h2>", unsafe_allow_html=True)

        # Button to proceed to the next question with styling
        if st.button('Next', key=f"next_button_{question_index}", on_click=next_question, 
                     help="Click to go to the next question"):  # <- Colon added here
            pass

    else:  # Last question
        # Centering the button
        col1, col2, col3 = st.columns([1, 3, 1])  # Adjust column ratios as needed
        with col2:
            if st.button('Get Hosting Recommendation', 
                         help="Click to get hosting recommendation",
                         key="get_recommendation_button"):
                dialog = ""
                # Gather all dialogues from previous questions
                for i in range(len(questions)):
                    dialog += st.session_state.get(f"reply_{i}", "")

                # Get hosting recommendation based on gathered dialogues and file path
                recommended_hosting = recommend_hosting_with_ai(dialog, file_path)
                # Display the recommended hosting service
                st.text_area("Recommended Hosting Service", value=recommended_hosting, height=300,
                             key="recommended_hosting_text_area",
                             )

    # Footer
    st.markdown('<div class="footer"><p>Powered by AI Gsepp Solutions</p></div>', unsafe_allow_html=True)

# Function to move to the next question
def next_question():
    if 'question_index' not in st.session_state:
        st.session_state['question_index'] = 0
    else:
        st.session_state['question_index'] += 1

# Call the main function when the script is run
if __name__ == "__main__":
    main()