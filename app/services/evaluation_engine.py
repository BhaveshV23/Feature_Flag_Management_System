from sqlalchemy.orm import Session

from app.models.environment import Environment
from app.models.flag import Flag
from app.models.targeting_rule import TargetingRule
from app.models.user_group_membership import UserGroupMembership
from app.cache.redis_client import redis_client

import hashlib

def evaluate_flag(db: Session, flag_key: str, environment_name: str, user_context: dict | None = None):
    
    if user_context is None:
        user_context = {}
    
    # Find Environment
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
      
        
    # Find Flag
    flag = (
        db.query(Flag)
        .filter( 
                Flag.key == flag_key,
                Flag.environment_id == environment.id
        )
        .first()
    )
    
    if flag is None:
        return {
            "success": False,
            "message": "Feature flag not found"
        }
        
    cache_key = f"{environment_name}:{flag_key}"
    cached_value = redis_client.get(cache_key)
    
    if cached_value:
        return {
            "success": True,
            "message": "Returned From Redis Cache",
            "enabled": cached_value == "true",
            "value": cached_value
    }
    
       
    # USER TARGETING 
    if user_context:
        user_id = str(user_context.get("user_id"))
            
        user_rule = (
            db.query(TargetingRule)
            .filter(TargetingRule.user_id == user_id)
            .first()
        )
            
        if user_rule:
            rule = (db.query(TargetingRule)
                    .filter(
                            TargetingRule.flag_id == flag.id,
                            TargetingRule.attribute == "group_name",
                            TargetingRule.operator == "=",
                            TargetingRule.value == group_rule.group_name
                        )
                        .first()
                    )
                
            if rule:
                redis_client.set(
                    cache_key,
                    str(flag.default_value).lower()
                )
                    
                return{
                        "success": True,
                        "message": "Matched User Targeting Rule",
                        "environment": environment.name,
                        "flag": flag.key,
                        "enabled": True,
                        "value": flag.default_value,
                        "user_context": user_context
                    }
                
    
    # Group Targeting Rules
    
    if user_context:
        user_id = str(user_context.get("user_id"))
        
        group_rule = (
            db.query(UserGroupMembership)
            .filter(UserGroupMembership.user_id == user_id)
            .first()
        )
        
        if group_rule:
            rule = (db.query(TargetingRule)
                    .filter(
                        TargetingRule.flag_id == flag.id,
                        TargetingRule.attribute == "group_name",
                        TargetingRule.operator == "=",
                        TargetingRule.value == group_rule.group_name
                    )
                    .first()
                )
            
            if rule:
                redis_client.set(
                    cache_key,
                    str(flag.default_value).lower()
                )
                
                return{
                    "success": True,
                    "message": "Matched Group Targeting Rule",
                    "environment": environment.name,
                    "flag": flag.key,
                    "enabled": True,
                    "value": flag.default_value,
                    "user_context": user_context
                }


    # Percentage Rollout
    if user_id:

        percentage_rules = (
            db.query(TargetingRule)
            .filter(
                TargetingRule.flag_id == flag.id,
                TargetingRule.rule_type == "percentage",
                TargetingRule.enabled == True
            )
            .order_by(TargetingRule.priority)
            .all()
        )
        
        for rule in percentage_rules:

            percentage = rule.percentage

            if percentage is None:
                continue

            # Create deterministic hash from user_id + flag_key
            hash_input = f"{user_id}:{flag_key}"

            hash_value = hashlib.sha256(
                hash_input.encode()
            ).hexdigest()

            # Convert hash into a number between 0 and 99
            bucket = int(hash_value, 16) % 100

            # User falls inside rollout percentage
            if bucket < percentage:
                
                redis_client.set(
                    cache_key,
                    str(flag.default_value).lower()
                )

                return {
                    "success": True,
                    "flag": flag.key,
                    "enabled": True,
                    "value": flag.default_value,
                    "user_context": user_context
                }


    redis_client.set(
        cache_key,
        str(flag.default_value).lower()
    )
    
    
    return {
        "success": True,
        "message": "Default Flag Evaluation",
        "environment": environment.name,
        "flag": flag.key,
        "enabled": flag.enabled,
        "value": flag.default_value,
    }