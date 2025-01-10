import streamlit as st

QUERY_PARAM_SEPARATOR = "|"

def update_query_param(param, selector, multiitem=False):
    """Assign the value in `selector` to the `param` query parameter.
    
    For lists, will concatenate items together.
    """
    if selector not in st.session_state:
        raise ValueError(f"Selector \"{selector}\" not found")

    if multiitem:
        new_value = QUERY_PARAM_SEPARATOR.join(st.session_state[selector])
    else:
        new_value = st.session_state[selector]

    st.query_params[param] = new_value

def extract_query_param_list(param, allowed_items, default=None):
    """Fetch a list of items from a query param"""
    selected = []
    if param in st.query_params:
        for identifier in st.query_params[param].split(QUERY_PARAM_SEPARATOR):
            if identifier in allowed_items:
                selected.append(identifier)

    if default is not None and len(selected) == 0:
        return default

    return selected

def retrieve_query_value_with_default(query_param, allowed, default):
    """Fetch a single value from a query value"""
    if query_param in st.query_params and int(st.query_params[query_param]) in allowed:
        chosen_index = allowed.index(int(st.query_params[query_param]))
    else:
        chosen_index = default

    return chosen_index
