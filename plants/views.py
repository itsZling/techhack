from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import UserPlant
from .utils import to_artist_key, get_plant_for_artist
# Create your views here.

@login_required
def index(request):
    return render(request, 'plants/index.html')

def results(request):
    artist_key = "" #to_artist_key(artist_name), wherever artist_name comes from
    score = 0  # calculate score based on game results

    plant_name = get_plant_for_artist(artist_key)
    if plant_name:
        record, created = UserPlant.objects.get_or_create(
            user=request.user,
            plant_name=plant_name,
            defaults={"experience": 0}
        )
        record.experience += score
        record.save()

    return render(request, 'lobby/results.html')