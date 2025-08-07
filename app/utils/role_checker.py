from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
from flask import jsonify

def roles_required(*allowed_roles):
  def wrapper(fn):
    @wraps(fn)
    def roles_checker(*args, **kwargs):
      verify_jwt_in_request()
      identity = get_jwt_identity()

      if not identity or 'user_type' not in identity:
        return jsonify({"error": "Unauthorized"}), 401
      
      user_type = identity.get('user_type')
      
      if user_type not in allowed_roles:
        return jsonify({"error": "Insufficient permissions"}), 403
      
      return fn(*args, **kwargs)
    return roles_checker
  return wrapper