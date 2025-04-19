# scripts/MappingHelperMethods.py

# Helper methods to clean and prepare active ingredient data

def clean_active_ingredient(active_ingred):
    """Clean active ingredient string."""
    if not isinstance(active_ingred, str):
        return ""
    active_ingred = active_ingred.lower()
    active_ingred = active_ingred.replace(',', '')
    active_ingred = active_ingred.replace('.', '')
    active_ingred = active_ingred.replace('/', ' ')
    active_ingred = active_ingred.replace('(', '')
    active_ingred = active_ingred.replace(')', '')
    active_ingred = active_ingred.replace('  ', ' ')
    return active_ingred.strip()


def split_active_ingredients(active_ingred):
    """Split multiple active ingredients into list."""
    if not isinstance(active_ingred, str):
        return []
    active_ingred = active_ingred.lower()
    separators = [' and ', ' with ', ' plus ', '+']
    for sep in separators:
        active_ingred = active_ingred.replace(sep, '|')
    return [part.strip() for part in active_ingred.split('|') if part.strip()]


# Additional helper methods can be added here as needed
