from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, Game, User, Complaint
from . import db
import json

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html", notes=Note.query.all(), user=current_user)

@views.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("notes.html", user=current_user)

@views.route('/delete-note', methods=['POST'])
def delete_note():
    data = json.loads(request.data)
    noteId = data['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    
    return jsonify({})

@views.route('/dashboard', methods=['POST', 'GET'])
@login_required
def dashboard():
    if current_user.role == "admin":
        users = User.query.all()
        complaints = Complaint.query.all()

        admin_info_dict = {
            "users": len(users),
            "unsolved_complaints": len([c for c in complaints if not c.solved])
        }
    else:
        admin_info_dict = dict()

    library_games = current_user.library_games.all()
    reviews = current_user.reviews.all()
    complaints = current_user.complaints.all()
    complaints_solved = [c.solved for c in complaints]
    complaints_solved_dict = {
        "solved": sum(complaints_solved),
        "unsolved": len(complaints_solved) - sum(complaints_solved)
    }

    return render_template("dashboard.html", user=current_user, library_games=library_games, reviews=reviews, complaints_solved=complaints_solved_dict, admin_info=admin_info_dict)