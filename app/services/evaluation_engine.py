from sqlalchemy.orm import Session

from app.models.environment import Environment
from app.models.flag import Flag

def evaluate_flag(db: Session, flag_key: str, environment_name: str):
    
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
    if flag.enabled:
        return {
            "success": True,
            "flag": flag.key,
            "enabled": True,
            "value": flag.default_value
        }
    return {
        "success": True,
        "flag": flag.key,
        "enabled": False,
        "value": flag.default_value
    }