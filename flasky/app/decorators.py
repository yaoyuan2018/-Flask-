from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission

def permission_required(permission):     #这个修饰器用于检查常规权限，使用Python标准库重的functools包，如果用户不具有指定权限，则返回403错误代码
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):                   #这个修饰器用于检查管理员权限
    return permission_required(Permission.ADMINISTER)(f)


