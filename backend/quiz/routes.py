import random
import os

from flask import Blueprint, render_template, session, redirect, url_for, request, current_app
from pymongo import MongoClient
from bson import ObjectId

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
    },
    {
        'question': 'Welke kamer is het beste geschikt voor een indoor skelterrace?',
        'choices': ['Woonkamer', 'Gang', 'Keuken + Eetkamer', 'Slaapkamer'],
        'answer': 'Keuken + Eetkamer'
    },
    {
        'question': 'Wat zou je het liefst in de tuin willen tegenkomen?',
        'choices': ['Een trampoline', 'Een zwembad', 'Een pizza-oven', 'Een geheime hut'],
        'answer': 'Een geheime hut'
    },
    {
        'question': 'Wie heeft ooit per ongeluk een muur roze geverfd?',
        'choices': ['Steven', 'Anja', 'Scott', 'Niemand'],
        'answer': 'Niemand'
    },
    {
        'question': 'Wat is het grappigste geluid dat je in huis kunt horen?',
        'choices': ['Scott die lacht', 'De deurbel', 'De stofzuiger', 'Steven die zingt'],
        'answer': 'Steven die zingt'
    },
    {
        'question': 'Wat is het meest onverwachte dat je in de badkamer kunt vinden?',
        'choices': ['Een rubberen eend', 'Een plant', 'Een boek', 'Een radio'],
        'answer': 'Een boek'
    }
    ,
    {
        'question': 'Wat is het gekste dat ooit in de koelkast heeft gelegen?',
        'choices': ['Een watermeloen', 'Schaapje', 'Een pizza', 'Een paar sokken'],
        'answer': 'Schaapje'
    },
    {
        'question': 'Hoeveel bomen hebben wij per saldo verwijderd in de tuinen?',
        'description': 'Nieuwe bomen is plus, omgehakt is min.',
        'choices': ['-3', '0', '3', '4'],
        'answer': '0'
    },
    {
        'question': 'Over hoeveel dagen denk je dat Scott officieel grote broer wordt?',
        'open': True,
        'no_score': True
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

    return render_template('quiz_start.html', error=None, title="Start de House Tour Quiz")

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
        if question.get('no_score'):
            is_correct = None
        else:
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
            'is_correct': is_correct,
            'no_score': question.get('no_score', False)
        })
        session['quiz_answers'] = answers
        return redirect(url_for('quiz.feedback'))

    return render_template(
        'quiz_question.html',
        question=question,
        progress=progress+1,
        total=len(order),
        name=session.get('quiz_name', ''),
        title="Quizvraag"
    )

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
    is_correct = session.get('quiz_last_correct', False)
    if question_obj and question_obj.get('no_score'):
        is_correct = None
        show_correct = False
    elif question_obj and question_obj.get('open') and question_obj.get('answer') is False:
        show_correct = False
    return render_template(
        'quiz_feedback.html',
        is_correct=is_correct,
        selected=last_answer,
        question=last_question,
        correct_answer=correct_answer if show_correct else '',
        next_url=url_for('quiz.question') if progress < total else url_for('quiz.result'),
        title="Quiz Feedback"
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
    return render_template('quiz_result.html', score=score, total=total, title="Quiz Resultaat")

@quiz_blueprint.route('/leaderboard')
def leaderboard():
    results = list(quiz_results.find({}, {'_id': 0, 'name': 1, 'score': 1, 'total': 1, 'answers': 1}))
    results.sort(key=lambda r: r.get('score', 0), reverse=True)
    open_questions = {q['question']: q.get('open', False) for q in QUIZ_QUESTIONS}
    for result in results:
        for answer in result.get('answers', []):
            answer['is_open'] = open_questions.get(answer.get('question'), False)
    return render_template('quiz_leaderboard.html', results=results, title="Quiz Ranglijst")

@quiz_blueprint.route('/leaderboard/edit', methods=['GET', 'POST'])
def leaderboard_edit_auth():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == '13636':
            session['edit_mode'] = True
            return redirect(url_for('quiz.leaderboard_edit'))
        return render_template('quiz_leaderboard_auth.html', error='Wachtwoord onjuist!')
    return render_template('quiz_leaderboard_auth.html', error=None, title="Bewerk Ranglijst Toegang")

@quiz_blueprint.route('/leaderboard/edit/manage', methods=['GET', 'POST'])
def leaderboard_edit():
    if not session.get('edit_mode'):
        return redirect(url_for('quiz.leaderboard_edit_auth'))
    if request.method == 'POST':
        delete_id = request.form.get('delete_id')
        if delete_id:
            quiz_results.delete_one({'_id': ObjectId(delete_id)})
    results = list(quiz_results.find({}, {'name': 1, 'score': 1, 'total': 1}))
    return render_template('quiz_leaderboard_edit.html', results=results, title="Bewerk Ranglijst")
