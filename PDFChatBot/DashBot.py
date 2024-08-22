import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

# Replace 'your-api-key' with your actual OpenAI API key

load_dotenv()

# Initialize LLM and vectorstore
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.9, max_tokens=500)
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
vectorstore = FAISS.load_local("tempVectorStore", embeddings, allow_dangerous_deserialization=True)
memory = ConversationBufferMemory(output_key="answer")

chain = RetrievalQAWithSourcesChain.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    verbose=True,
    memory=memory
)

# Initialize the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Store(id='store-chat-sessions', data=[]),
    dcc.Store(id='store-current-session', data=[]),
    html.H1("Question and Answer Application"),
    dcc.Input(id='input-question', type='text', placeholder='Type your question here', style={'width': '50%'}),
    html.Button('Submit Question', id='submit-button', n_clicks=0),
    html.Button('New Chat', id='new-chat-button', n_clicks=0),
    html.Div(id='output-answer'),
    html.H2("Chat History"),
    dcc.Dropdown(id='chat-dropdown', options=[
        {'label': f'Chat {i+1}', 'value': i} for i in range(len([]) + 1)
    ], value=None),
    html.Div(id='chat-history')
])

@app.callback(
    Output('output-answer', 'children'),
    Output('chat-history', 'children'),
    Output('chat-dropdown', 'options'),
    Output('store-chat-sessions', 'data'),
    Output('store-current-session', 'data'),
    Input('submit-button', 'n_clicks'),
    Input('new-chat-button', 'n_clicks'),
    Input('chat-dropdown', 'value'),
    State('input-question', 'value'),
    State('output-answer', 'children'),
    State('chat-history', 'children'),
    State('store-chat-sessions', 'data'),
    State('store-current-session', 'data')
)
def update_output(submit_clicks, new_chat_clicks, dropdown_value, query, current_output, chat_history, chat_sessions, current_session):
    ctx = dash.callback_context

    if not ctx.triggered:
        return current_output, chat_history, [{'label': f'Chat {i+1}', 'value': i} for i in range(len(chat_sessions) + 1)], chat_sessions, current_session

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'new-chat-button':
        # if current_session:
        #     chat_sessions.append(current_session)
        current_session = []
        memory.clear()
        print("new chat:")
        print(chat_sessions)
        return "", "", [{'label': f'Chat {i+1}', 'value': i} for i in range(len(chat_sessions) + 1)], chat_sessions, current_session

    if button_id == 'submit-button' and query:
        result = chain({"question": query}, return_only_outputs=False)
        memory.save_context({"question": query}, {"answer": result["answer"]})

        answer = result["answer"]
        sources = result.get("sources", "")
        if sources:
            sources_list = sources.split("\n")
            sources_str = "\n".join(sources_list)
            answer += f"\n\nSources:\n{sources_str}"

        # current_session.append(f"Q: {query}\nA: {answer}")
        # print(current_session)
        if len(current_session) == 0:
            chat_sessions.append(current_session)
        current_session.append(f"Q: {query}\nA: {answer}")    
        new_history = "\n\n".join(current_session)
        print("submit: ")
        print(chat_sessions)
        return answer, new_history, [{'label': f'Chat {i+1}', 'value': i} for i in range(len(chat_sessions) + 1)], chat_sessions, current_session

    if button_id == 'chat-dropdown':
        if dropdown_value is not None and dropdown_value < len(chat_sessions):
            selected_chat = "\n\n".join(chat_sessions[dropdown_value])
            return current_output, selected_chat, [{'label': f'Chat {i+1}', 'value': i} for i in range(len(chat_sessions) + 1)], chat_sessions, current_session

    return current_output, chat_history, [{'label': f'Chat {i+1}', 'value': i} for i in range(len(chat_sessions) + 1)], chat_sessions, current_session

if __name__ == '__main__':
    app.run_server(debug=True)
