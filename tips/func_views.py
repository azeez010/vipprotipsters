from django.http import JsonResponse
import datetime, git
from requests import request
from tips import models, mixins
from django.shortcuts import render
from tips import utils
from django.views.decorators.csrf import csrf_exempt
import orjson, os

@csrf_exempt
def save_csv(request):
    if request.method == "POST":
        games = request.POST.get("games")
        name = request.POST.get("name")
        category = request.POST.get("category")
        games = orjson.loads(games)
        utils.handle_uploaded_file(games, name, category)
        # utils.delete_outdate_csv(category)
        return render(request, 'free_tips.html', {})

#Route for the GitHub webhook
@csrf_exempt
def git_update(request):
    if request.method == "POST":
        os.chdir("/home/turkeyapp")
        repo = git.Repo('./vipprotipsters')
        origin = repo.remotes.origin
        repo.create_head('master',
        origin.refs.master).set_tracking_branch(origin.refs.master).checkout()
        #repo.heads.master.set_tracking_branch(origin.refs.master)
        #all note
        origin.pull()
        # return 'success', 200
        return JsonResponse({'success':'True'})


@csrf_exempt
def result(request, *args, **kwargs):
    if datetime.datetime.now().hour > 6:
        cur_date_time = datetime.datetime.now()
    else:
        today_date = datetime.datetime.now()
        cur_date_time = today_date - datetime.timedelta(days=1) 

    if request.method == "POST":
        games = request.POST.get("games")
        games = orjson.loads(games)
        today_games = models.Ticket.objects.filter(date_added=cur_date_time).all()
        prepare_result = {}

        games_with_result =  utils.prepare_forebet_csv(games)
        
        for game in games_with_result:
            team_name = game[2]
            scores = game[6]
            prepare_result[team_name] = scores

        for game in today_games:
            scores = prepare_result[game.team_name]
            _game_result = score_calc(scores, game.tips)    
            if _game_result:
                game.success = True
                game.played = True
                game.save()
            else:
                game.played = True
                game.save()

    return render(request, 'free_tips.html', {})

def score_calc(score_line, pred):
    actual_score = score_line.split("-")
    home_score = int(actual_score[0])
    away_score = int(actual_score[1])
    total_score = home_score + away_score
    if pred == "1":
        if home_score > away_score:
            return True
        else:
            return False
    elif pred == "X":
        if home_score == away_score:
            return True
        else:
            return False
    elif pred == "2":
        if away_score > home_score:
            return True
        else:
            return False
    
    elif pred == "Over":
        if total_score > 2:
            return True
        else:
            return False
    
    elif pred == "Under":
        if total_score < 3:
            return True
        else:
            return False

    elif pred == "Yes":
        if home_score > 0 and away_score > 0:
            return True
        else:
            return False
        
    elif pred == "No":
        if home_score < 1 or away_score < 0:
            return True
        else:
            return False