from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import openai
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from dotenv import load_dotenv

#
load_dotenv()

app = Flask(__name__)
CORS(app)
 
# Retrieve the API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

type_of_person = (
    "You are a bot that generates SAT problems. "
    "You should write answers for them as the options A, B, C, D."
)

@app.route('/generate-sat-problem', methods=['POST'])
def generate_sat_problem():
    data = request.json
    section = data.get('section')
    difficulty = data.get('difficulty')

    if not section or not difficulty:
        return jsonify({"error": "Section and difficulty are required"}), 400

    if difficulty == "easy":
        num_questions = 30
        prompt = (
            f"You are a bot that generates SAT problems. "
            f"The section is {section} and the difficulty is {difficulty}. "
            f"Generate {num_questions} SAT problems with multiple choice answers. "
            "Please return your response in JSON format as a list of questions with the following structure:\n"
            "["
            "  {"
            "    \"question\": \"Generate the SAT question\","
            "    \"choices\": [\"Option A\", \"Option B\", \"Option C\", \"Option D\"],"
            "    \"answer\": \"Correct answer\""
            "  },"
            "  ..."
            "]"
        )
    elif difficulty == "medium":
        if section == "math":
            num_questions = 12
            prompt = (
                f"You are a bot that generates SAT problems. "
                f"The section is {section} and the difficulty is {difficulty}. "
                f"Generate {num_questions} slightly harder SAT math problems. "
                "Please return your response in JSON format as a list of questions with the following structure:\n"
                "["
                "  {"
                "    \"question\": \"Generate the SAT question\","
                "    \"choices\": [\"Option A\", \"Option B\", \"Option C\", \"Option D\"],"
                "    \"answer\": \"Correct answer\""
                "  },"
                "  ..."
                "]"
            )
        elif section == "verbal":
            num_questions = 10
            prompt = (
                f"You are a bot that generates SAT problems. "
                f"The section is {section} and the difficulty is {difficulty}. "
                f"Generate a short reading passage followed by {num_questions} SAT verbal questions. "
                "Please return your response in JSON format as a list of questions with the following structure:\n"
                "["
                "  {"
                "    \"passage\": \"Provide a short reading passage\","
                "    \"questions\": ["
                "      {"
                "        \"question\": \"Generate the SAT question\","
                "        \"choices\": [\"Option A\", \"Option B\", \"Option C\", \"Option D\"],"
                "        \"answer\": \"Correct answer\""
                "      },"
                "      ..."
                "    ]"
                "  }"
                "]"
            )
        else:
            return jsonify({"error": "Unsupported section"}), 400
    elif difficulty == "hard":
        if section == "math":
            num_questions = 8
            prompt = (
                f"You are a bot that generates SAT problems. "
                f"The section is {section} and the difficulty is {difficulty}. "
                f"Generate {num_questions} challenging word problems for SAT math. "
                "These problems should require critical thinking and problem-solving skills. "
                "Please return your response in JSON format as a list of questions with the following structure:\n"
                "["
                "  {"
                "    \"question\": \"Generate the SAT math word problem\","
                "    \"choices\": [\"Option A\", \"Option B\", \"Option C\", \"Option D\"],"
                "    \"answer\": \"Correct answer\""
                "  },"
                "  ..."
                "]"
            )
        elif section == "verbal":
            num_questions = 15
            prompt = (
                f"You are a bot that generates SAT problems. "
                f"The section is {section} and the difficulty is {difficulty}. "
                f"Generate {num_questions} challenging verbal questions for SAT. "
                "These questions should involve skimming and scanning through complex information. "
                "Please return your response in JSON format as a list of questions with the following structure:\n"
                "["
                "  {"
                "    \"passage\": \"Provide a complex reading passage\","
                "    \"questions\": ["
                "      {"
                "        \"question\": \"Generate the SAT question\","
                "        \"choices\": [\"Option A\", \"Option B\", \"Option C\", \"Option D\"],"
                "        \"answer\": \"Correct answer\""
                "      },"
                "      ..."
                "    ]"
                "  }"
                "]"
            )
        else:
            return jsonify({"error": "Unsupported section"}), 400
    else:
        return jsonify({"error": "Unsupported difficulty"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": type_of_person},
                {"role": "user", "content": prompt}
            ]
        )

        print("OpenAI response:", response.choices[0].message['content'])

        res = json.loads(response.choices[0].message['content'])

        if difficulty == "easy" and all('question' in q and 'choices' in q and 'answer' in q for q in res):
            return jsonify(res), 200
        elif difficulty == "medium" and section == "math" and all('question' in q and 'choices' in q and 'answer' in q for q in res):
            return jsonify(res), 200
        elif difficulty == "medium" and section == "verbal" and 'passage' in res[0] and all('question' in q and 'choices' in q and 'answer' in q for q in res[0]['questions']):
            return jsonify(res[0]), 200
        elif difficulty == "hard" and section == "math" and all('question' in q and 'choices' in q and 'answer' in q for q in res):
            return jsonify(res), 200
        elif difficulty == "hard" and section == "verbal" and 'passage' in res[0] and all('question' in q and 'choices' in q and 'answer' in q for q in res[0]['questions']):
            return jsonify(res[0]), 200
        else:
            return jsonify({"error": "Incomplete response from OpenAI"}), 500

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    data = request.json
    section = data.get('section')
    difficulty = data.get('difficulty')

    if not section or not difficulty:
        return jsonify({"error": "Section and difficulty are required"}), 400

    # Fetch the generated SAT problems first
    sat_problem_response = generate_sat_problem()
    if sat_problem_response[1] != 200:
        return sat_problem_response

    problems = sat_problem_response[0].json
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y = height - 40
    p.drawString(100, y, f"SAT {section.capitalize()} Problems - {difficulty.capitalize()} Difficulty")
    y -= 30

    if section == "verbal" and 'passage' in problems:
        p.drawString(100, y, "Passage:")
        y -= 20
        for line in problems['passage'].split('\n'):
            if y < 40:
                p.showPage()
                y = height - 40
            p.drawString(100, y, line)
            y -= 20
        for i, question in enumerate(problems['questions']):
            y -= 30
            if y < 40:
                p.showPage()
                y = height - 40
            p.drawString(100, y, f"Question {i + 1}: {question['question']}")
            y -= 20
            for choice in question['choices']:
                if y < 40:
                    p.showPage()
                    y = height - 40
                p.drawString(120, y, choice)
                y -= 20
            p.drawString(100, y, f"Answer: {question['answer']}")
    else:
        for i, question in enumerate(problems):
            y -= 30
            if y < 40:
                p.showPage()
                y = height - 40
            p.drawString(100, y, f"Question {i + 1}: {question['question']}")
            y -= 20
            for choice in question['choices']:
                if y < 40:
                    p.showPage()
                    y = height - 40
                p.drawString(120, y, choice)
                y -= 20
            p.drawString(100, y, f"Answer: {question['answer']}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='sat_problems.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)