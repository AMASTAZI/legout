import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .engine import process_chat_message

def assistant_page(request):
    """Page dédiée d'échange avec le Conseiller Culinaire Le Gout"""
    return render(request, 'chatbot/assistant.html')

@csrf_exempt
def chat_api(request):
    """Endpoint AJAX pour envoyer des questions et recevoir des recommandations en direct"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_msg = data.get('message', '')
        except (ValueError, KeyError):
            user_msg = request.POST.get('message', '')

        if not user_msg:
            return JsonResponse({'reply': "Pose-moi une question sur un plat ou ta commande mon cher !"})

        response_data = process_chat_message(user_msg, user=request.user)
        return JsonResponse(response_data)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
