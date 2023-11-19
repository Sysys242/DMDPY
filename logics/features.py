from .avatar_changer        import avatar_task
from .fast_friender         import fast_friending_task
from .server_joiner         import joining_task
from .tos_accepter          import tos_task
from .friender              import friending_task

features = {
    'Friender': friending_task,
    'Fast Friender': fast_friending_task,
    
    'Joiner': joining_task,

    'Tos Accepter': tos_task,

    'Avatar Changer': avatar_task,
}

def get_features() -> dict:
    features_str = ''
    count = 0
    count2 = 1
    for feature in features:
        if count != 0:
            features_str += "           "
        features_str += f'[{count2}] {feature}'
        count2 += 1
        count += 1
        if count >= 5:
            features_str += "\n"
            count = 0
    return [features, features_str]