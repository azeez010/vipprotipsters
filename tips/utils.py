from datetime import datetime
import os, random
from django.conf import settings
from tips import mixins, models
from pathlib import Path
# from django.db.transaction import commit_on_success


def handle_uploaded_file(f, name, category):
    if category == "freebet":
        arr = prepare_csv(f)
        folder = str(settings.CSV_STATIC_URL)
    elif category == "paid":
        arr = prepare_forebet_csv(f)
        folder = str(settings.PAID_CSV_STATIC_URL)
    elif category == "paid_results":
        arr = prepare_forebet_csv(f)
        folder = str(settings.RESULT_CSV_STATIC_URL)

    mixins.CSV.addCsv(name, folder, arr)


def prepare_csv(data):
    arr = []
    for line in data:
        _line = [line.get('image'), line.get('league_name'), line.get('team_name'), line.get('tips'), line.get("time"), line.get("odd_1"), line.get("odd_2"), line.get("odd_3")]
        arr.append(_line)
    return arr

def prepare_forebet_csv(data):
    arr = []
    for line in data:
        _line = [False, line.get('image'), line.get('team_name'), line.get('predict'), line.get('odds'), line.get('prediction_true'), line.get('full_time_scores'), line.get('time')]
        arr.append(_line)
    return arr


def delete_outdate_csv(category):
    folder = get_folder(category)
    no_of_csv_allowed = models.Settings.objects.filter(key="no_of_csv_allowed").first() 
    if no_of_csv_allowed:
        _dir = Path(folder)
    else:
        no_of_csv_allowed = settings.NO_OF_CSV_ALLOWED  
        os.chdir(folder)
        all_files = os.listdir()
        all_files = all_files[::-1][no_of_csv_allowed:]

        for file in all_files:
            os.remove(file)

def get_all_csv(category):
    folder = get_folder(category)
    os.chdir(folder)
    all_files = os.listdir()
    return all_files    

def get_folder(category):
    if category == "freebet":
        folder = str(settings.CSV_STATIC_URL)
    elif category == "paid":
        folder = str(settings.PAID_CSV_STATIC_URL)
    elif category == "paid_results":
        folder = str(settings.RESULT_CSV_STATIC_URL)
    
    return folder

def generate_predictions(cur_date):
    minimum_odds = models.Settings.objects.filter(key="minimum_odds").first()
    # if not minimum_odds:
    #     minimum_odds = settings.MINIMUM_ODDS
    # else:
    #     minimum_odds = minimum_odds.value

    # minimum_odds_float = float(minimum_odds)    
    cur_date = cur_date.date()
    tickets = models.Ticket.objects.filter(ticket_date_time=cur_date).all()
    tipsters = models.Tipsters.objects.all()
    
    prep_tickets = []
    for ticket in tickets:
        occurence = ticket.occurence
        if len(tipsters) < occurence:
            occurence = len(tipsters) 
        prep_tickets.append([ticket, occurence])
        
    random.shuffle(prep_tickets)

    for tipster in tipsters:
        total_odds = 1 
        # Delete all the added Tickets to override
        try:
            ticket_with_date, _ = models.TicketWithDate.objects.get_or_create(ticket_date_time=cur_date, tipsters=tipster)
        except models.TicketWithDate.MultipleObjectsReturned:
            ticket_with_date = models.TicketWithDate.objects.filter(ticket_date_time=cur_date, tipsters=tipster).first()
        
        ticket_with_date.ticket.clear()
        
        # Shuffle the tickets before adding 
        random.shuffle(prep_tickets)
        random_games = random.randrange(4, 7)
        for index, ticket_arr in enumerate(prep_tickets[:random_games]):
            ticket, occurence = ticket_arr
            if occurence > 0:
                ticket_with_date.ticket.add(ticket)
                total_odds *= ticket.game_odds
                occurence -= 1
                prep_tickets[index] = [ticket, occurence]

            # if total_odds > minimum_odds_float:
            #     break      