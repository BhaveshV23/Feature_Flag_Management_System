import hashlib

def is_user_in_rollout(
    user_id: str,
    flag_id: str,
    rollout_percentage: int
):
    value = f"{user_id}:{flag_id}"
    hash_value = hashlib.md5(value.encode()).hexdigest()
    
    bucket = int(hash_value, 16) % 100
    
    return bucket < rollout_percentage