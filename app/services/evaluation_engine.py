from sqlalchemy.orm import Session

from app.models.environment import Environment
from app.models.flag import Flag

def evaluate_flag(db: Session, flag_key: str, environment_name: str, user_context: dict | None = None):
    
    environment = (
    db.query(Environment)
    .filter(Environment.name == environment_name)
    .first()
    )
    if environment is None:
        return {
            "success": False,
            "message": "Environment not found"
        }
    
    flag = (
        db.query(Flag).filter( Flag.key == flag_key,
            Flag.environment_id == environment.id)
        .first()
    )
    
    #Check if Feature Exists
    if flag is None:
        return {
            "success": False,
            "message": "Feature flag not found"
        }
    return {
        "success": True,
        "flag": flag.key,
        "enabled": flag.enabled,
        "value": flag.default_value,
        "user_context": user_context
    }