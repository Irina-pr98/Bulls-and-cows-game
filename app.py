from flask import Flask, render_template, request, redirect, url_for, session
import random
import time

app = Flask(__name__)
app.secret_key = '4\x05"\xb8\xe6\xa7\x8ft@\xe8.\xa9N(\x9bY\x0b3\xe9\xc0\x97\x0b67'


def generate_number(difficulty):
    digits = list(range(10))
    random.shuffle(digits)
    if difficulty == 'easy':
        return ''.join(map(str, digits[:3]))
    elif difficulty == 'medium':
        return ''.join(map(str, digits[:4]))
    else:  # hard
        return ''.join(map(str, digits[:5]))


def get_bulls_and_cows(secret, guess):
    bulls = sum(s == g for s, g in zip(secret, guess))
    cows = sum(g in secret for g in guess) - bulls
    return bulls, cows


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/rules')
def rules():
    return render_template('rules.html')


@app.route('/user_guesses', methods=['GET', 'POST'])
def user_guesses():
    if request.method == 'POST':
        guess = request.form['guess']
        if guess == 'q':
            return redirect(url_for('index'))
        if len(guess) != len(session['secret_number']) or not guess.isdigit() or len(set(guess)) != len(guess):
            return render_template('user_guesses.html', error='Неправильный ввод. Введите число без повторяющихся цифр')

        secret_number = session['secret_number']
        attempts = session['attempts']
        bulls, cows = get_bulls_and_cows(secret_number, guess)
        attempts.append((guess, bulls, cows))

        if bulls == len(secret_number):
            return render_template('user_guesses.html', secret_number=secret_number,
                                   attempts=attempts, success=True, attempts_count=len(attempts))

        session['attempts'] = attempts
        return render_template('user_guesses.html', secret_number=secret_number, attempts=attempts)

    difficulty = request.args.get('difficulty', 'medium')
    session['secret_number'] = generate_number(difficulty)
    session['attempts'] = []
    return render_template('user_guesses.html', secret_number=session['secret_number'], attempts=[],
                           difficulty=difficulty)


@app.route('/computer_guesses', methods=['GET', 'POST'])
def computer_guesses():
    if request.method == 'POST':
        bulls = int(request.form['bulls'])
        cows = int(request.form['cows'])
        guess = request.form['guess']
        possible_numbers = eval(request.form['possible_numbers'])
        attempts = eval(request.form['attempts'])

        if bulls == len(guess):
            return render_template('computer_guesses.html', guess=guess, attempts=attempts, success=True)

        attempts.append((guess, bulls, cows))
        possible_numbers = [num for num in possible_numbers if get_bulls_and_cows(num, guess) == (bulls, cows)]

        if not possible_numbers:
            return render_template('computer_guesses.html', error='Нет возможных чисел. Начните заново.')

        guess = random.choice(possible_numbers)
        return render_template('computer_guesses.html', guess=guess,
                               possible_numbers=possible_numbers, attempts=attempts)

    possible_numbers = [str(i).zfill(4) for i in range(10000) if len(set(str(i))) == 4]
    guess = random.choice(possible_numbers)
    return render_template('computer_guesses.html', guess=guess, possible_numbers=possible_numbers, attempts=[])


if __name__ == '__main__':
    app.run(debug=True)
