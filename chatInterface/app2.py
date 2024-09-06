from flask import Flask, request, Response
from flask_cors import CORS
import json
from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.documents import Document

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load data files
with open("unique_names.json", "r") as file:
    names = json.load(file)
with open("conciseRoom.json", "r") as file:
    temp = json.load(file)
    rooms = {list(i.keys())[0]: i[list(i.keys())[0]] for i in temp}
with open("floors.json", "r") as file:
    floors = json.load(file)

# Load mergedContext JSON and setup Chroma vector store


# Initialize FastEmbedEmbeddings and Chroma vector store
'''
embedding = FastEmbedEmbeddings()
db = Chroma(persist_directory="./rag", embedding_function=embedding)
'''

with open("mergedContext.json", "r") as f:
    data = json.load(f)

# Convert JSON data into LangChain Document format
documents = [
    Document(page_content=str(chunk), metadata={"source": str(chunk["metadata"])}, id=i)
    for i, chunk in enumerate(data)
]
embedding = FastEmbedEmbeddings()
db = Chroma.from_documents(documents=documents, embedding=embedding, persist_directory="rag")
db.persist()


# Define RAG chain (Retrieval-Augmented Generation)
def rag_chain():
    model = ChatOllama(
        model="llama3.1",
        temperature=0.1,
    )
    prompt = PromptTemplate.from_template(
        """
        You are a friendly assistant made by IWAYPlus to help users fin information about the RNI building.
            General information about the building:
            Each floor contains Male, Female and handicapped washroom.
            Each floor also has pantries.
            Every floor is accessible by Lifts and Staircases.
            The building has 3 blocks A,B,C.
            Each floor has room like 1A-1A (1st floor block A Room 1A), 2B-2C(Second floor block B Room 2C), 3A-2B(Third Floor A Block Room 2C) etc.
            Building has eateries like breadbox and cafetaria.
            Auditorium for events.
            Instruction:
            {input}
            Similar Question Answers: {context} 
        """
    )
    
    # Create retriever and document chain
    retriever = db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 10},
    )
    document_chain = create_stuff_documents_chain(model, prompt)
    chain = create_retrieval_chain(retriever, document_chain)
    return chain

# Define the chat function that generates output based on user input
def chat(user_query):
    # Use LangChain to process the user query and generate a response
    chain = rag_chain()
    result = chain.invoke({"input": user_query})
    
    response = {
        "answer": result["answer"],
        "sources": [doc.metadata for doc in result["context"]]
    }
    print(response)
    return response



# Route to handle LangChain queries
@app.route('/langchain_query', methods=['GET'])
def langchain_query():
    user_query = request.args.get('message', '')
    response = chat(user_query)  # Call the chat function here
    
    return Response(json.dumps(response), mimetype='application/json')

# Existing chat route for other functionality
@app.route('/chat', methods=['GET'])
def chat_endpoint():
    user_message = request.args.get('message', '')
    return chat(user_message)  # Now the chat function is called here too

if __name__ == '__main__':
    app.run(debug=True)
