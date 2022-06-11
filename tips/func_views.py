import datetime 
from tips import models, mixins
from django.shortcuts import render
from tips import utils
from django.views.decorators.csrf import csrf_exempt
import orjson

@csrf_exempt
def save_csv(request):
    if request.method == "POST":
        games = request.POST.get("games")
        name = request.POST.get("name")
        category = request.POST.get("category")
        games = orjson.loads(games)
        utils.handle_uploaded_file(games, name, category)
        utils.delete_outdate_csv(category)
        return render(request, 'free_tips.html', {})

@csrf_exempt
def result(request, *args, **kwargs):
    cur_date_time = datetime.datetime.now()
    if request.method == "POST":
        games = request.POST.get("games")
        games = orjson.loads(games)
        today_games = models.Ticket.objects.filter(date_added=cur_date_time).all()
        team_names = {}
        
        for game in today_games:
            team_names[f"{game.team_name}-{game.tips}"] = game 
        games_with_result =  utils.prepare_forebet_csv(games)
        
        for game in games_with_result:
            key = f"{game[2]}-{game[3]}"
            if key in team_names.keys() and game[6]:
                if game[5]:
                    ticket = team_names.get(key)
                    ticket.success = True
                    ticket.played = True
                    ticket.save()
                else:
                    ticket = team_names.get(key)
                    ticket.played = True
                    ticket.save() 
            elif key in team_names.keys() and not game[6]:
                ticket = team_names.get(key)
                ticket.postponed = True
                ticket.save()
                

    return render(request, 'free_tips.html', {})
