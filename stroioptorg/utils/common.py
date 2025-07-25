from datetime import datetime
from typing import Optional, TypeVar, Type

from django.db.models import Model
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request

T = TypeVar('T', bound=Model)


def get_object_by_user_or_session_key(request: Request, model_type: Type[T], auth_fields: list[str] = None,
                                      get_by_auth: bool = True, **params) -> Optional[T]:
    """
    :param request: Request object
    :param model_type: Model type
    :param auth_fields: Names of nested fields for foreign key where we will search by user or session_key
    :param get_by_auth: Boolean for searching by user or session key in model, by default True
    :param params: Additional params for searching
    :return: Model instance or None
    """

    if request.user.is_authenticated:
        if auth_fields:
            auth_params = {f'{field}__user': request.user for field in auth_fields}
        else:
            auth_params = {}

        if get_by_auth:
            obj = get_object_or_404(model_type, user=request.user, **auth_params, **params)
        else:
            obj = get_object_or_404(model_type, **auth_params, **params)

    elif request.session.session_key:
        if auth_fields:
            auth_params = {f'{field}__session_key': request.session.session_key for field in auth_fields}
        else:
            auth_params = {}

        if get_by_auth:
            obj = get_object_or_404(model_type, session_key=request.session.session_key, **auth_params, **params)
        else:
            obj = get_object_or_404(model_type, **auth_params, **params)
    else:
        raise ValidationError(f'{model_type} не найдена')

    return obj

def get_objects_by_user_or_session_key(request: Request, model_type: Type[T], auth_fields: list[str] = None,
                                      get_by_auth: bool = True, **params) -> Optional[list[T]]:
    """
    :param request: Request object
    :param model_type: Model type
    :param auth_fields: Names of nested fields for foreign key where we will search by user or session_key
    :param get_by_auth: Boolean for searching by user or session key in model, by default True
    :param params: Additional params for searching
    :return: List of Model instances or None
    """

    if request.user:
        if auth_fields:
            auth_params = {f'{field}__user': request.user for field in auth_fields}
        else:
            auth_params = {}

        if get_by_auth:
            objs = model_type.objects.filter(user=request.user, **auth_params, **params)
        else:
            objs = model_type.objects.filter(**auth_params, **params)
    elif request.session.session_key:
        if auth_fields:
            auth_params = {f'{field}__session_key': request.session.session_key for field in auth_fields}
        else:
            auth_params = {}

        if get_by_auth:
            objs = model_type.objects.filter(session_key=request.session.session_key, **auth_params, **params)
        else:
            objs = model_type.objects.filter(**auth_params, **params)
    else:
        raise ValidationError(f'{model_type} не найдена')

    return objs

def format_russian_date(dt):
    months = {
        1: 'Января', 2: 'Февраля', 3: 'Марта', 4: 'Апреля',
        5: 'Мая', 6: 'Июня', 7: 'Июля', 8: 'Августа',
        9: 'Сентября', 10: 'Октября', 11: 'Ноября', 12: 'Декабря'
    }
    return f"{dt.day} {months[dt.month]} {dt.year}"