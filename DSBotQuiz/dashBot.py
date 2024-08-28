import json
import openai
import os
from dash import Dash, html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Dash app
app = Dash(__name__)

# Function definitions
def read_qa_evaluation(fileName):
    try:
        with open(fileName, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def generate_question(temp):
    prompt = "Generate a unique question about basic data science. Each question should be different and cover various aspects of data science. Only give me the question and no other words. Make sure it is not similar to one of these questions:" + temp
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
    )
    question = response.choices[0].message.content
    return question

def evaluate_answer(question, answer):
    prompt = f"Question: {question}\n\nAnswer: {answer}\n\nEvaluate this answer on a scale of 0 to 100 and provide a brief reasoning. Then answer the question yourself that is a 100 out of 100. Label each thing on a different line, the three categories should be 'Score','Reasoning', and 'Right Answer'"
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a teacher grading an exam"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )
    evaluation = response.choices[0].message.content
    return evaluation

def save_to_txt(question, answer, evaluation, fileName):
    with open(fileName, "a") as f:
        f.write(f"Question: {question}\n")
        f.write(f"Answer: {answer}\n")
        f.write(f"Evaluation: {evaluation}\n")
        f.write("-" * 40 + "\n")

def parse_qa_evaluation(text):
    qa_list = []
    blocks = text.split('----------------------------------------')
    
    for block in blocks:
        block = block.strip()
        if block:
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            qa_dict = {}

            for i, line in enumerate(lines):
                if line.startswith("Question:"):
                    qa_dict['Question'] = line.split(': ', 1)[1].strip()
                elif line.startswith("Answer:"):
                    qa_dict['Answer'] = line.split(': ', 1)[1].strip()
                elif line.startswith("Evaluation: Score:"):
                    qa_dict['Score'] = line.split(': ', 1)[1].strip()
                elif line.startswith("Reasoning:"):
                    qa_dict['Reasoning'] = line.split(': ', 1)[1].strip()
                elif line.startswith("Right Answer:"):
                    # Collect all lines after "Right Answer:" as part of the right answer
                    qa_dict['Right Answer'] = '\n'.join(lines[i+1:]).strip()
                    break
            
            qa_list.append(qa_dict)
    
    return qa_list

def save_to_jsonl(txt_file, jsonl_file):
    temp = read_qa_evaluation(txt_file)
    qa_json = parse_qa_evaluation(temp)
    with open(jsonl_file, 'w') as jsonl_out:
        for record in qa_json:
            jsonl_out.write(json.dumps(record) + '\n')

# Layout of the app
app.layout = html.Div([
    html.H1("Data Science Chatbot"),
    dcc.Input(id='file-name', type='text', placeholder='Enter file name', style={'marginRight': '10px'}),
    html.Br(),
    dcc.Textarea(id='answer', placeholder='Enter your answer here...', style={'width': '100%', 'height': 100}),
    html.Br(),
    html.Button('Submit', id='submit-button', n_clicks=0, style={'marginRight': '10px'}),
    html.Button('New Question', id='new-question-button', n_clicks=0, style={'marginRight': '10px'}),
    html.Button('Start New Chat', id='new-chat-button', n_clicks=0),
    html.Br(),
    html.Div(id='question-display', style={'marginTop': '20px'}),
    html.Div(id='evaluation-display', style={'marginTop': '20px'}),
    html.Div(id='conversion-status', style={'marginTop': '20px'})
])

# Callback to handle user input and interaction
@app.callback(
    [Output('question-display', 'children'),
     Output('evaluation-display', 'children'),
     Output('conversion-status', 'children'),
     Output('answer', 'value')],
    [Input('submit-button', 'n_clicks'),
     Input('new-question-button', 'n_clicks'),
     Input('new-chat-button', 'n_clicks')],
    [State('file-name', 'value'),
     State('answer', 'value')]
)
def handle_interaction(submit_clicks, new_question_clicks, new_chat_clicks, file_name, answer):
    if not file_name:
        raise PreventUpdate

    if new_chat_clicks > submit_clicks and new_chat_clicks > new_question_clicks:
        # Start a new chat
        temp = ""
    else:
        # Continue with the existing chat
        temp = read_qa_evaluation(file_name)
    
    # Generate a question (new question or continuing with the same)
    question = generate_question(temp)
    
    if new_question_clicks > submit_clicks:
        # If "New Question" button is clicked, clear the answer box
        return f"Question: {question}", "", "", ""

    if not answer:
        return f"Question: {question}", "", "", ""

    # Evaluate the answer
    evaluation = evaluate_answer(question, answer)
    
    # Save the conversation to the file
    save_to_txt(question, answer, evaluation, file_name)
    
    # Automatically convert .txt to .jsonl
    jsonl_file_name = file_name.replace('.txt', '.jsonl')
    save_to_jsonl(file_name, jsonl_file_name)
    
    conversion_status = f"Automatically converted {file_name} to {jsonl_file_name} successfully."
    
    return f"Question: {question}", f"Evaluation: {evaluation}", conversion_status, ""

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
