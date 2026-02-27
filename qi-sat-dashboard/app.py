from flask import Flask, render_template, request, redirect
from store import add_submission, get_averages, submissions
from datetime import datetime

app = Flask(__name__)


@app.route('/rate', methods=['GET'])
def rate_form():
    # simply render the page, optionally with an error message
    error = request.args.get('error')
    return render_template('rate.html', error=error)


@app.route('/rate', methods=['POST'])
def rate_submit():
    visit_date = request.form.get('visit_date', '').strip()
    nurse = request.form.get('nurse', '').strip()
    physician = request.form.get('physician', '').strip()

    # basic validation
    error = None
    if not visit_date:
        error = 'Visit date is required.'
    else:
        try:
            # validate date format
            datetime.strptime(visit_date, '%Y-%m-%d')
        except ValueError:
            error = 'Invalid date format.'

    try:
        nurse_val = int(nurse)
        if nurse_val < 1 or nurse_val > 5:
            raise ValueError
    except ValueError:
        error = 'Nurse courtesy rating must be an integer between 1 and 5.'

    try:
        phys_val = int(physician)
        if phys_val < 1 or phys_val > 5:
            raise ValueError
    except ValueError:
        error = 'Physician courtesy rating must be an integer between 1 and 5.'

    if error:
        # redirect back to form with error (simple approach)
        return redirect(f"/rate?error={error}")

    add_submission(visit_date, nurse_val, phys_val)
    # stay on the form so users can enter multiple submissions;
    # provide a success flag so the template can show confirmation
    return redirect('/rate?success=1')


@app.route('/dashboard', methods=['GET'])
def dashboard():
    dates, nurse_avgs, phys_avgs = get_averages()
    return render_template(
        'dashboard.html',
        dates=dates,
        nurse_avgs=nurse_avgs,
        phys_avgs=phys_avgs,
    )


@app.route('/', methods=['GET'])
def index():
    # default route redirects to the rating form
    return redirect('/rate')


if __name__ == '__main__':
    app.run(debug=True)
