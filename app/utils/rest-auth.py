def default_create_jwt_token(token_model, user, serializer):
    access, refresh = token_model.objects.get_or_create(user=user)
    return access, refresh