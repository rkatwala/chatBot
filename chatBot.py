import openai

# Replace 'your-api-key' with your actual OpenAI API key
openai.api_key = ''

def generate_question(temp):
    prompt = "Generate a unique question about basic data science. Each question should be different and cover various aspects of data science. Make sure it is not similar to one of these questions:"+ temp
    print(prompt)
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=50
    )
    question = response.choices[0].message.content
    return question

def evaluate_answer(question, answer):
    prompt = f"Question: {question}\n\nAnswer: {answer}\n\nEvaluate this answer on a scale of 0 to 100 and provide a brief reasoning. Then answer the question yourself that is a 100 out of 100"
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a teacher grading an exam"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )
    evaluation = response.choices[0].message.content
    return evaluation

def save_to_txt(question, answer, evaluation):
    with open("qa_evaluation.txt", "a") as f:
        f.write(f"Question: {question}\n")
        f.write(f"Answer: {answer}\n")
        f.write(f"Evaluation: {evaluation}\n")
        f.write("-" * 40 + "\n")

def main():
    temp = ""
    while True:
        question = generate_question(temp)
        temp = temp + question + "\n"
        print("Question:", question)
        answer = input("Your Answer: ")
        evaluation = evaluate_answer(question, answer)
        print("Evaluation:", evaluation)
        save_to_txt(question, answer, evaluation)
        continue_prompt = input("Do you want to answer another question? (y/n): ")
        if continue_prompt.lower() != 'y':
            break

if __name__ == "__main__":
    main()
