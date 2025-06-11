from django import template

register = template.Library()

@register.filter
def lookup(dict_data, key):
    """
    Template filter để truy cập dictionary với key dynamic
    Usage: {{ dict|lookup:key }}
    """
    if dict_data and isinstance(dict_data, dict):
        result = dict_data.get(key, '')
        # If the result is a dict with 'value' and 'unit', format it properly
        if isinstance(result, dict) and 'value' in result:
            value = result.get('value', '')
            unit = result.get('unit', '')
            if unit:
                return f"{value} {unit}"
            return value
        return result
    return ''

@register.filter
def get_item(dictionary, key):
    """
    Alternative filter để lấy item từ dictionary
    """
    return dictionary.get(key) if dictionary else None

@register.filter
def format_requirement(req_data):
    """
    Format admission requirement data properly
    Usage: {{ requirement_dict|format_requirement }}
    """
    if isinstance(req_data, dict) and 'value' in req_data:
        value = req_data.get('value', '')
        unit = req_data.get('unit', '')
        if unit and unit != 'points':
            return f"{value} {unit}"
        return str(value)
    return str(req_data) if req_data else ''