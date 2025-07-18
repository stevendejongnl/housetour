import random
import os
from flask import Blueprint, render_template, session, redirect, url_for, request, current_app
from pymongo import MongoClient

quiz_blueprint = Blueprint('quiz', __name__, template_folder='../templates', url_prefix='/quiz')

QUIZ_QUESTIONS = [
    {
        'question': 'Hoeveel dagen heeft Steven gebruik kunnen maken van het kleine kamertje boven als kantoor?',
        'choices': ['6 dagen', '36 dagen', '60 dagen', '123 dagen'],
        'answer': '123 dagen'
    },
    {
        'question': 'Waar kun je de hand afdruk van Scott in de muur vinden?',
        'choices': ['Eetkamer', 'WC', 'Scott\'s slaapkamer', 'In de achtertuin'],
        'answer': 'Eetkamer'
    },
    {
        'question': 'Hoeveel lampen zijn er in de woonkamer?',
        'choices': ['4', '5', '6', '9'],
        'answer': '5'
    },
    {
        'question': 'Waar had Steven beter zijn best kunnen doen met klussen?',
        'open': True,
        'answer': False
    },
    {
        'question': 'Wat is de kleur van de muur in de woonkamer?',
        'choices': ['Sandy Beach', 'Serene Sandstone', 'Intuitive', 'Sand Drift'],
        'answer': 'Intuitive'
    },
    {
        'question': 'Waar heeft Steven door de muur heen geschroefd?',
        'choices': ['Woonkamer', 'Badkamer', 'WC', 'Scott zijn kamer'],
        'answer': 'WC'
    },
    {
        'question': 'Hoeveel kurken hebben Anja En Steven verzameld en bewaard door de jaren heen?',
        'choices': ['86', '154', '173', '243'],
        'answer': '173'
    }
]

MONGO_URI = os.environ.get("MONGO_URI")
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
        session['quiz_answers'] = []
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
        if question.get('open'):
            selected = request.form.get('open_answer', '').strip()
        if not question.get('open'):
            selected = request.form.get('choice')

        correct = question.get('answer')
        is_correct = selected == correct

        if is_correct:
            session['quiz_score'] = session.get('quiz_score', 0) + 1

        session['quiz_progress'] = progress + 1
        session['quiz_last_correct'] = is_correct
        session['quiz_last_answer'] = selected
        session['quiz_last_question'] = question['question']
        session['quiz_last_correct_answer'] = correct
        answers = session.get('quiz_answers', [])
        answers.append({
            'question': question['question'],
            'selected': selected,
            'correct': correct,
            'is_correct': is_correct
        })
        session['quiz_answers'] = answers
        return redirect(url_for('quiz.feedback'))

    return render_template('quiz_question.html', question=question, progress=progress+1, total=len(order), name=session.get('quiz_name', ''))

@quiz_blueprint.route('/feedback')
def feedback():
    progress = session.get('quiz_progress', 0)
    total = len(session.get('quiz_order', QUIZ_QUESTIONS))
    if progress > total:
        return redirect(url_for('quiz.result'))
    last_question = session.get('quiz_last_question', '')
    last_answer = session.get('quiz_last_answer', '')
    correct_answer = session.get('quiz_last_correct_answer', '')
    question_obj = next((q for q in QUIZ_QUESTIONS if q['question'] == last_question), None)
    show_correct = True
    if question_obj and question_obj.get('open') and question_obj.get('answer') is False:
        show_correct = False
    return render_template(
        'quiz_feedback.html',
        is_correct=session.get('quiz_last_correct', False),
        selected=last_answer,
        question=last_question,
        correct_answer=correct_answer if show_correct else '',
        next_url=url_for('quiz.question') if progress < total else url_for('quiz.result')
    )

@quiz_blueprint.route('/result')
def result():
    score = session.get('quiz_score', 0)
    total = len(session.get('quiz_order', QUIZ_QUESTIONS))
    name = session.get('quiz_name', '')
    answers = session.get('quiz_answers', [])
    if name:
        current_app.logger.info(f"Connected to MongoDB at {MONGO_URI}, database: {db.name}, collection: {quiz_results.name}")

        quiz_results.insert_one({
            "name": name,
            "score": score,
            "total": total,
            "answers": answers
        })
    return render_template('quiz_result.html', score=score, total=total, name=name)
