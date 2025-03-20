import os , re
from django.conf import settings
from rest_framework import serializers
from .models import CustomUser
from rest_framework.exceptions import ValidationError
from .utils import generate_random , verify_code
from validators.user_validators import validate_password, validate_name, validate_username

class CustomUserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'password','confirm_password']



    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        user.save()
        return user


class CustomUserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name']

        def validate(self, data):
            validate_name(data["first_name"])
            validate_name(data["last_name"])
            validate_username(data["username"])
            return data

        def update(self, instance, validated_data):
            instance.username = validated_data.get('username', instance.username)
            instance.email = validated_data.get('email', instance.email)
            instance.first_name = validated_data.get('first_name', instance.first_name)
            instance.last_name = validated_data.get('last_name', instance.last_name)
            instance.save()
            return instance

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        if not data.get('username') and not data.get('email'):
            raise serializers.ValidationError("Vous devez fournir soit un nom d'utilisateur soit un email.")
        if not data.get('password'):
            raise serializers.ValidationError("Le mot de passe est requis.")
        return data

class CustomUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name' ,'avatar','is_email_verified' ,'active_2fa' , 'is_online']
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        avatar_url = representation.get('avatar')
        if avatar_url:
            avatar_path = os.path.join(settings.MEDIA_ROOT , avatar_url)
            if not os.path.exists(avatar_path):
                avatar_url = '/media/avatars/default_avatar.png'
            elif not avatar_url.startswith('/media/'):
                avatar_url = f'/media/{avatar_url}'
                representation['avatar'] = self.context['request'].build_absolute_uri(avatar_url).replace('http://', 'https://')
        else:
            default_avatar_url = '/media/avatars/default_avatar.png'
            representation['avatar'] = self.context['request'].build_absolute_uri(default_avatar_url).replace('http://', 'https://')
        return representation



class Login__42Serializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name','avatar']


    def create(self, validated_data):
        validated_data['password'] = generate_random()
        user = CustomUser(**validated_data)
        user.save()
        return user

class verify_otp_Serializer(serializers.ModelSerializer):
    code_otp = serializers.CharField(required=True)
    class Meta:
        model = CustomUser
        fields = ['code_otp']
    def validate_code_otp(self, value):
        if len(value) != 8:
            raise serializers.ValidationError("The verification code must be 8 numbers long.")
        user = self.context['request'].user
        if verify_code(value , user.code_otp) is False :
            raise serializers.ValidationError("The verification code is invalid or does not correspond to the user.")
        return value





