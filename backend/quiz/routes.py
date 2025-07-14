import random
import os
from flask import Blueprint, render_template, session, redirect, url_for, request, current_app
from pymongo import MongoClient

quiz_blueprint = Blueprint('quiz', __name__, template_folder='../templates', url_prefix='/quiz')

QUIZ_QUESTIONS = [
    {
        'question': 'Wat is de hoofdstad van Nederland?',
        'choices': ['Amsterdam', 'Rotterdam', 'Utrecht', 'Den Haag'],
        'answer': 'Amsterdam'
    },
    {
        'question': 'Welke kleur heeft de Nederlandse vlag NIET?',
        'choices': ['Rood', 'Blauw', 'Geel', 'Wit'],
        'answer': 'Geel'
    },
    {
        'question': 'Hoeveel provincies heeft Nederland?',
        'choices': ['10', '12', '11', '9'],
        'answer': '12'
    },
    # ...meer vragen...
]

MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://stevendejong:<db_password>@housetour.ge5znlo.mongodb.net/?retryWrites=true&w=majority&appName=Housetour"
)
client = MongoClient(MONGO_URI)
db = client["housetour"]
quiz_results = db["quiz_results"]

@quiz_blueprint.route('/start', methods=['GET', 'POST'])
def start_quiz():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            return render_template('quiz_start.html', error="Vul je naam in a.u.b.")
        session['quiz_name'] = name
        session['quiz_progress'] = 0
        session['quiz_score'] = 0
        session['quiz_order'] = random.sample(range(len(QUIZ_QUESTIONS)), len(QUIZ_QUESTIONS))
        return redirect(url_for('quiz.question'))
    return render_template('quiz_start.html', error=None)

@quiz_blueprint.route('/question', methods=['GET', 'POST'])
def question():
    progress = session.get('quiz_progress', 0)
    order = session.get('quiz_order', list(range(len(QUIZ_QUESTIONS))))
    if progress >= len(order):
        return redirect(url_for('quiz.result'))

    q_idx = order[progress]
    question = QUIZ_QUESTIONS[q_idx]

    if request.method == 'POST':
        selected = request.form.get('choice')
        correct = question['answer']
        is_correct = selected == correct
        session['quiz_progress'] = progress + 1
        if is_correct:
            session['quiz_score'] = session.get('quiz_score', 0) + 1
        session['quiz_last_correct'] = is_correct
        session['quiz_last_answer'] = selected
        session['quiz_last_question'] = question['question']
        session['quiz_last_correct_answer'] = correct
        return redirect(url_for('quiz.feedback'))

    return render_template('quiz_question.html', question=question, progress=progress+1, total=len(order), name=session.get('quiz_name', ''))

@quiz_blueprint.route('/feedback')
def feedback():
    progress = session.get('quiz_progress', 0)
    total = len(session.get('quiz_order', QUIZ_QUESTIONS))
    if progress > total:
        return redirect(url_for('quiz.result'))
    return render_template(
        'quiz_feedback.html',
        is_correct=session.get('quiz_last_correct', False),
        selected=session.get('quiz_last_answer', ''),
        question=session.get('quiz_last_question', ''),
        correct_answer=session.get('quiz_last_correct_answer', ''),
        next_url=url_for('quiz.question') if progress < total else url_for('quiz.result')
    )

@quiz_blueprint.route('/result')
def result():
    score = session.get('quiz_score', 0)
    total = len(session.get('quiz_order', QUIZ_QUESTIONS))
    name = session.get('quiz_name', '')
    # Sla resultaat op in MongoDB
    if name:
        quiz_results.insert_one({
            "name": name,
            "score": score,
            "total": total
        })
    return render_template('quiz_result.html', score=score, total=total, name=name)
