from logics.member_scrapper       import scrapping_task
from logics.display_changer       import display_task
from logics.avatar_changer        import avatar_task
from logics.token_checker         import checking_task
from logics.fast_friender         import fast_friending_task
from logics.server_joiner         import joining_task
from logics.tos_accepter          import tos_task
from logics.bio_changer           import bio_task
from logics.friender              import friending_task
from logics.mass_dm               import dming_task

def soon():
    print("Soon...")

features = {
    'Friender': friending_task,
    'Fast Friender': fast_friending_task,
    
    'Joiner': joining_task,
    'Mass Dm': dming_task,
    'Member Scapper': scrapping_task,


    'Tos Accepter': tos_task,

    'Bio Changer': bio_task,
    'Avatar Changer': avatar_task,
    'Display Changer': display_task,
    'Token Checker': checking_task,
}

def get_features() -> dict:
    max_feature_length = max(len(feature) for feature in features)
    features_str = ''
    count = 0
    count2 = 1
    for feature in features:
        if count != 0:
            features_str += "   "
        features_str += f'[{count2}] {feature.ljust(max_feature_length)}'
        count2 += 1
        count += 1
        if count >= 5:
            features_str += "\n"
            count = 0
    return [features, features_str]