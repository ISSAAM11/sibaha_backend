from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import User, Coach

class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user_type = request.data.get('user_type', 'user')
        experience = request.data.get('experience', [])

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Utilisateur existe déjà'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username,
            password=password,
            user_type=user_type
        )

        if user_type == 'coach':
            coach = Coach.objects.create(user=user)
            coach.set_experience(experience)
            coach.save()

        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user_type': user.user_type,
            'username': user.username
        })

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            response_data = {
                'token': token.key,
                'user_type': user.user_type,
                'username': user.username
            }

            if user.user_type == 'coach':
                try:
                    coach = user.coach_profile
                    response_data['experience'] = coach.get_experience()
                except Coach.DoesNotExist:
                    response_data['experience'] = []

            return Response(response_data)

        return Response({'error': 'Identifiants invalides'}, status=status.HTTP_401_UNAUTHORIZED)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            'username': user.username,
            'user_type': user.user_type
        }

        if user.user_type == 'coach':
            try:
                coach = user.coach_profile
                data['experience'] = coach.get_experience()
            except Coach.DoesNotExist:
                data['experience'] = []

        return Response(data)

class AddExperienceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.user_type != 'coach':
            return Response({'error': 'Seuls les coachs peuvent ajouter des expériences'}, status=status.HTTP_403_FORBIDDEN)

        new_experience = request.data.get('experience')
        if not new_experience:
            return Response({'error': 'Expérience requise'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            coach = request.user.coach_profile
            coach.add_experience(new_experience)
            return Response({'experience': coach.get_experience()})
        except Coach.DoesNotExist:
            return Response({'error': 'Profil coach non trouvé'}, status=status.HTTP_404_NOT_FOUND)
