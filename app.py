from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from models.models import db, User, Card, Deck

app = Flask(__name__)
app.config['SECRET_KEY'] = 'x5UXtdnNeKZN'   # Add your own unique secret key here
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskflash.db'
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    user_decks = Deck.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', user=current_user, decks=user_decks)

@app.route('/new_deck', methods=['GET', 'POST'])
@login_required
def new_deck():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        # Create the new deck
        new_deck = Deck(title=title, description=description, user_id=current_user.id)
        db.session.add(new_deck)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('new_deck.html')

@app.route('/decks/<int:deck_id>/add_cards', methods=['GET', 'POST'])
@login_required
def add_cards_to_deck(deck_id):
    if request.method == 'POST':
        # Handle adding cards to the deck
        card_title = request.form['card_title']
        card_description = request.form['card_description']
        
        # Create a new card object
        new_card = Card(title=card_title, description=card_description, deck_id=deck_id, user_id=current_user.id)
        
        # Add the card to the database
        db.session.add(new_card)
        db.session.commit()
        
        flash('Card added to the deck successfully!', 'success')
        
        # Redirect back to the same page
        return redirect(url_for('add_cards_to_deck', deck_id=deck_id))
    
    else:
        # Display form to add cards to the deck
        return render_template('add_cards.html', deck_id=deck_id)
    
@app.route('/decks/<int:deck_id>/delete', methods=['POST'])
@login_required
def delete_deck(deck_id):
    deck_to_delete = Deck.query.get_or_404(deck_id)
    if deck_to_delete.user_id != current_user.id:
        flash("You don't have permission to delete this deck.", 'error')
        return redirect(url_for('dashboard'))
    
    db.session.delete(deck_to_delete)
    db.session.commit()
    flash('Deck deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/decks/<int:deck_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_deck(deck_id):
    deck_to_edit = Deck.query.get_or_404(deck_id)
    if deck_to_edit.user_id != current_user.id:
        flash("You don't have permission to edit this deck.", 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        deck_to_edit.title = request.form['title']
        deck_to_edit.description = request.form['description']
        db.session.commit()
        flash('Deck edited successfully!', 'success')
        return redirect(url_for('dashboard'))
    else:
        # Display form to edit the deck
        return render_template('edit_deck.html', deck=deck_to_edit)
    
@app.route('/decks/<int:deck_id>/view_cards', methods=['GET'])
@login_required
def view_cards(deck_id, current_card_id=0):
    # Retrieve the cards associated with the selected deck
    deck = Deck.query.get_or_404(deck_id)
    cards = deck.cards
    current_card = cards[0]

    # Check if 'next' and 'prev' parameters are present in the query string
    next_card_requested = 'next' in request.args
    prev_card_requested = 'prev' in request.args

    if prev_card_requested:
        current_card = cards[0]
    if next_card_requested:
        current_card = cards[1]

    return render_template('view_cards.html', deck=deck, card=current_card)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check your username and password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)