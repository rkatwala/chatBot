import openai

# Replace 'your-api-key' with your actual OpenAI API key
openai.api_key = ""


def read_qa_evaluation(fileName):
    try:
        with open(fileName, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def generate_question(temp):
    prompt = "Generate a unique question about basic data science. Each question should be different and cover various aspects of data science. Only give me the question and no other words. Make sure it is not similar to one of these questions:"+ temp
    #print(prompt)
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
    prompt = f"Question: {question}\n\nAnswer: {answer}\n\nEvaluate this answer on a scale of 0 to 100 and provide a brief reasoning. Then answer the question yourself that is a 100 out of 100"
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

def main():
    import os
    
    def display_file_names():
        if os.path.exists("fileNames.txt"):
            with open("fileNames.txt", "r") as f:
                file_names = f.readlines()
                if not file_names:
                    print("No files found.")
                else:
                    for i, name in enumerate(file_names):
                        print(f"{i + 1}. {name.strip()}")
                return file_names
        else:
            print("No files found.")
            return []

    def write_file_name(file_name):
        with open("fileNames.txt", "a") as f:
            f.write(file_name + "\n")

    fileName = ""
    user_choice = input("Choose 'n' for New Chat or 'o' for Old Chat: ").lower()
    
    if user_choice == 'n':
        fileName = input("Enter the new file name: ")
        write_file_name(fileName)
    elif user_choice == 'o':
        file_names = display_file_names()
        if file_names:
            try:
                file_index = int(input("Enter the number associated with the file name: ")) - 1
                if 0 <= file_index < len(file_names):
                    fileName = file_names[file_index].strip()
                else:
                    print("Invalid number entered.")
                    return
            except ValueError:
                print("Invalid input. Please enter a number.")
                return
    else:
        print("Invalid choice.")
        return

    print(f"Using file: {fileName}")
    
    while True:
        temp = read_qa_evaluation(fileName)  # Replace with your actual function
        question = generate_question(temp)  # Replace with your actual function
        print("Question:", question)
        answer = input("Your Answer: ")
        evaluation = evaluate_answer(question, answer)  # Replace with your actual function
        print("Evaluation:", evaluation)
        save_to_txt(question, answer, evaluation, fileName)  # Replace with your actual function
        continue_prompt = input("Do you want to answer another question? (y/n): ")
        if continue_prompt.lower() != 'y':
            break


if __name__ == "__main__":
    main()
