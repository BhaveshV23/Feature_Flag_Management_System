from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.flag import Flag
from app.services.evaluation_engine import evaluate_flag, invalidate_flag_cache
from app.schemas.evaluation import EvaluationRequest
from app.schemas.feat_flag import FlagCreate, FlagUpdate
from app.models.targeting_rule import TargetingRule
from app.schemas.targeting_rule import TargetingRuleCreate, TargetingRuleUpdate
from app.models.environment import Environment
from app.schemas.environment import CreateEnvironment, UpdateEnvironment
from app.core.security import AuthenticatedUser, get_current_user
from app.services.audit_service import create_audit_log, flag_to_dict, targeting_rule_to_dict

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
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
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
    db.flush()
    create_audit_log(db, flag_id=flag.id, environment_id=flag.environment_id, actor=current_user.username, action="CREATE", new_state=flag_to_dict(flag))
    db.commit()
    db.refresh(flag)
    invalidate_flag_cache(flag.environment.name, flag.key)
    
    return flag


@router.put("/flags/{flag_id}")
def update_flag(
    flag_id: int,
    request: FlagUpdate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    flag = (db.query(Flag)
            .filter(Flag.id == flag_id)
            .first()
            )  

    if flag is None:
        return {
            "message": "Feature flag not found"
        }
        
    previous_environment_name = flag.environment.name
    previous_key = flag.key
    old_state = flag_to_dict(flag)

    flag.key = request.key
    flag.type = request.type
    flag.default_value = request.default_value
    flag.enabled = request.enabled
    flag.description = request.description
    flag.owner_team = request.owner_team
    db.flush()
    new_state = flag_to_dict(flag)
    action = "UPDATE" if old_state["enabled"] == new_state["enabled"] else ("ENABLE" if new_state["enabled"] else "DISABLE")
    create_audit_log(db, flag_id=flag.id, environment_id=flag.environment_id, actor=current_user.username, action=action, old_state=old_state, new_state=new_state)
    db.commit()
    db.refresh(flag)
    invalidate_flag_cache(previous_environment_name, previous_key)
    if (previous_environment_name, previous_key) != (flag.environment.name, flag.key):
        invalidate_flag_cache(flag.environment.name, flag.key)
    
    return flag
    
    
@router.delete("/flags/{flag_id}")
def delete_flag(
    flag_id: int,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
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
        
    environment_name = flag.environment.name
    flag_key = flag.key
    create_audit_log(db, flag_id=flag.id, environment_id=flag.environment_id, actor=current_user.username, action="DELETE", old_state=flag_to_dict(flag))
    db.delete(flag)
    db.commit()
    invalidate_flag_cache(environment_name, flag_key)

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
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    rule = TargetingRule(
        flag_id=request.flag_id,
        priority=request.priority,
        rule_type=request.rule_type,
        operator=request.operator,
        value=request.value,
        percentage=request.percentage,
        enabled=request.enabled,
        is_active=request.is_active,
    )

    flag = db.query(Flag).filter(Flag.id == rule.flag_id).first()
    db.add(rule)
    db.flush()
    if flag is not None:
        create_audit_log(db, flag_id=flag.id, environment_id=flag.environment_id, actor=current_user.username, action="TARGETING_RULE_CREATE", new_state=targeting_rule_to_dict(rule, flag.environment_id))
    db.commit()
    db.refresh(rule)
    flag = db.query(Flag).filter(Flag.id == rule.flag_id).first()
    if flag is not None:
        invalidate_flag_cache(flag.environment.name, flag.key)

    return rule


@router.put("/targeting-rules/{rule_id}")
def update_targeting_rule(
    rule_id: int,
    request: TargetingRuleUpdate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    rule = (db.query(TargetingRule)
            .filter(TargetingRule.id == rule_id)
            .first()
            )
    
    if rule is None:
        return{
            "message": "Targeting rule not found"
        }
        
    previous_flag = db.query(Flag).filter(Flag.id == rule.flag_id).first()
    previous_cache_namespace = (
        (previous_flag.environment.name, previous_flag.key)
        if previous_flag is not None
        else None
    )
    old_state = targeting_rule_to_dict(rule, previous_flag.environment_id) if previous_flag is not None else None
    current_flag = db.query(Flag).filter(Flag.id == request.flag_id).first()

    rule.flag_id = request.flag_id
    rule.priority = request.priority
    rule.rule_type = request.rule_type
    rule.operator = request.operator
    rule.value = request.value
    rule.percentage = request.percentage
    rule.enabled = request.enabled
    if request.is_active is not None:
        rule.is_active = request.is_active
    db.flush()
    if current_flag is not None:
        create_audit_log(db, flag_id=current_flag.id, environment_id=current_flag.environment_id, actor=current_user.username, action="TARGETING_RULE_UPDATE", old_state=old_state, new_state=targeting_rule_to_dict(rule, current_flag.environment_id))
    db.commit()
    db.refresh(rule)
    if previous_cache_namespace is not None:
        invalidate_flag_cache(*previous_cache_namespace)
    if current_flag is not None:
        current_cache_namespace = (current_flag.environment.name, current_flag.key)
        if current_cache_namespace != previous_cache_namespace:
            invalidate_flag_cache(*current_cache_namespace)
    
    return rule


@router.delete("/targeting-rules/{rule_id}")
def delete_targeting_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
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
        
    flag = db.query(Flag).filter(Flag.id == rule.flag_id).first()
    cache_namespace = (
        (flag.environment.name, flag.key)
        if flag is not None
        else None
    )
    if flag is not None:
        create_audit_log(db, flag_id=flag.id, environment_id=flag.environment_id, actor=current_user.username, action="TARGETING_RULE_DELETE", old_state=targeting_rule_to_dict(rule, flag.environment_id))
    db.delete(rule)
    db.commit()
    if cache_namespace is not None:
        invalidate_flag_cache(*cache_namespace)
    
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
    
    
