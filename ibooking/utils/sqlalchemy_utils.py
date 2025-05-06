from typing import Dict


def get_dict_from_sqlalchemy(sqlalchemy_model) -> Dict | None:
    if sqlalchemy_model is None:
        return None
    dict_data = sqlalchemy_model.__dict__.copy()
    dict_data.pop("_sa_instance_state")
    return dict_data
