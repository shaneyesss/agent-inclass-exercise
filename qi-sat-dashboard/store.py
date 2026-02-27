from collections import defaultdict
from datetime import datetime

# in-memory list of submissions
# each entry is a dict: {'date': date_obj, 'nurse': int, 'physician': int}
submissions = []


def add_submission(date_str: str, nurse: int, physician: int):
    """Add a rating. date_str should be YYYY-MM-DD."""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    submissions.append({'date': date_obj, 'nurse': nurse, 'physician': physician})


def get_averages():
    """Return (dates, nurse_avg, phys_avg) lists sorted by date."""
    # group by date
    data = defaultdict(lambda: {'nurse': [], 'physician': []})
    for entry in submissions:
        d = entry['date']
        data[d]['nurse'].append(entry['nurse'])
        data[d]['physician'].append(entry['physician'])

    sorted_dates = sorted(data.keys())
    dates = [d.isoformat() for d in sorted_dates]
    nurse_avgs = []
    phys_avgs = []
    for d in sorted_dates:
        nurse_list = data[d]['nurse']
        phys_list = data[d]['physician']
        nurse_avgs.append(sum(nurse_list) / len(nurse_list))
        phys_avgs.append(sum(phys_list) / len(phys_list))
    return dates, nurse_avgs, phys_avgs
