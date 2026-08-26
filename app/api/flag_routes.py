from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.flag import Flag
from app.services.evaluation_engine import evaluate_flag
from app.schemas.evaluation import EvaluationRequest
from app.schemas.feat_flag import FlagCreate, FlagUpdate
from app.models.targeting_rule import TargetingRule
from app.schemas.targeting_rule import TargetingRuleCreate, TargetingRuleUpdate
from app.models.environment import Environment
from app.schemas.environment import CreateEnvironment, UpdateEnvironment
from app.cache.redis_client import redis_client
from app.core.security import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])

# Flags

@router.get("/flags")
def get_all_flags(db: Session = Depends(get_db)):
    return db.query(Flag).all()


@router.get("/flags/{flag_id}")
def get_flag(flag_id: int, db: Session = Depends(get_db)):
    return(
        db.query(Flag)
        .filter(Flag.id == flag_id)
        .first()
    )
   
    
@router.post("/evaluate")
def evaluate(
    request: EvaluationRequest,
    db: Session = Depends(get_db)
):
    return evaluate_flag(
        db=db,
        flag_key=request.flag_key,
        environment_name=request.environment_name,
        user_context=request.user_context
    )
    

@router.post("/flags")
def create_flag(
    request: FlagCreate,
    db: Session = Depends(get_db)
):
    flag = Flag(
        environment_id=request.environment_id,
        key=request.key,
        name=request.name,
        type=request.type,
        default_value=request.default_value,
        enabled=request.enabled,
        description=request.description,
        owner_team=request.owner_team        
    )
    db.add(flag)
    db.commit()
    db.refresh(flag)
    
    return flag


@router.put("/flags/{flag_id}")
def update_flag(
    flag_id: int,
    request: FlagUpdate,
    db: Session = Depends(get_db)
):
    flag = (db.query(Flag)
            .filter(Flag.id == flag_id)
            .first()
            )  

    if flag is None:
        return {
            "message": "Feature flag not found"
        }
        
    flag.key = request.key
    flag.type = request.type
    flag.default_value = request.default_value
    flag.enabled = request.enabled
    flag.description = request.description
    flag.owner_team = request.owner_team
    
    db.commit()
    cache_key = f"{flag.environment.name}:{flag.key}"
    redis_client.delete(cache_key)
    db.refresh(flag)
    
    return flag
    
    
@router.delete("/flags/{flag_id}")
def delete_flag(
    flag_id: int,
    db: Session = Depends(get_db)
):
    flag = (
        db.query(Flag)
        .filter(Flag.id == flag_id)
        .first()
    )
    
    if flag is None:
        return {
            "message": "Feature flag not found"
        }
        
    db.delete(flag)
    db.commit()
    cache_key = f"{flag.environment.name}:{flag.key}"
    redis_client.delete(cache_key)

    return {
        "message": "Feature flag deleted successfully",
        "flag_id": flag_id
    }
    

# Targeting Rules
  
@router.get("/targeting-rules")
def get_all_targeting_rules(
    db:Session = Depends(get_db)
):
    return db.query(TargetingRule).all()


@router.get("/targeting-rules/{rule_id}")
def get_targeting_rules_by_id(
    rule_id:int, db:Session = Depends(get_db)
):
    rule = (db.query(TargetingRule)
            .filter(TargetingRule.id == rule_id)
            .first()
            )
    
    if rule is None:
        return{
            "message": "Targeting rule not found"
        }
        
    return rule
    
    
@router.post("/targeting-rules")
def create_targeting_rule(
    request: TargetingRuleCreate,
    db: Session = Depends(get_db)
):
    rule = TargetingRule(
        flag_id=request.flag_id,
        priority=request.priority,
        rule_type=request.rule_type,
        operator=request.operator,
        value=request.value,
        percentage=request.percentage,
        enabled=request.enabled
    )

    db.add(rule)
    db.commit()
    db.refresh(rule)

    return rule


@router.put("/targeting-rules/{rule_id}")
def update_targeting_rule(
    rule_id: int,
    request: TargetingRuleUpdate,
    db: Session = Depends(get_db)
):
    rule = (db.query(TargetingRule)
            .filter(TargetingRule.id == rule_id)
            .first()
            )
    
    if rule is None:
        return{
            "message": "Targeting rule not found"
        }
        
    rule.flag_id = request.flag_id
    rule.priority = request.priority
    rule.rule_type = request.rule_type
    rule.operator = request.operator
    rule.value = request.value
    rule.percentage = request.percentage
    rule.enabled = request.enabled   
    
    db.commit()
    db.refresh(rule)
    
    return rule


@router.delete("/targeting-rules/{rule_id}")
def delete_targeting_rule(
    rule_id: int,
    db: Session = Depends(get_db)
):
    rule = (
        db.query(TargetingRule)
        .filter(TargetingRule.id == rule_id)
        .first()
    )
    
    if rule is None:
        return{
            "message": "Targeting rule not found"
        }
        
    db.delete(rule)
    db.commit()
    
    return {
        "message": "Targeting rule deleted successfully",
        "rule_id": rule_id
    }
    
    
# Environments

@router.get("/environment")
def get_all_environments(
    db: Session = Depends(get_db)
):
    return db.query(Environment).all()


@router.get("/environment/{environment_id}")
def get_environment_by_id(
    environment_id: int,
    db: Session = Depends(get_db)
):
    environment_id = (
        db.query(Environment)
        .filter(Environment.id == environment_id)
        .first()
    )
    
    if environment_id is None:
        return{
            "message": "Environment not found."
        }
        
    return environment_id


@router.post("/environment")
def create_environment(
    request: CreateEnvironment,
    db:Session = Depends(get_db)
):
    environment = Environment(
        name=request.name,
        description=request.description,
        is_active=request.is_active
    )
    
    db.add(environment)
    db.commit()
    db.refresh(environment)
    
    return environment


@router.put("/environment/{environment_id}")
def update_environment(
    environment_id: int,
    request: UpdateEnvironment,
    db:Session = Depends(get_db)
):
    environment = (db.query(Environment)
                   .filter(Environment.id == environment_id)
                   .first()
                   )
    
    if environment is None:
        return {
            "message": "Environment not found."
        }
        
    environment.name=request.name
    environment.description=request.description
    environment.is_active=request.is_active
    
    db.commit()
    db.refresh(environment)
    
    return environment


@router.delete("/environment/{environment_id}")
def delete_environment(
    environment_id: int,
    db:Session = Depends(get_db)
):
    environment = (
        db.query(Environment)
        .filter(Environment.id == environment_id)
        .first()
    )
    
    if environment is None:
        return {
            "message": "Environment not found."
        }
        
    db.delete(environment)
    db.commit()
        
    return {
        "message": "Environment is deleted successfully."
    }
    
    
