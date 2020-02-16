import re
COOK_TOOL = {
    # complex word
    'baking dish':      re.compile(r'(^|\W)baking\s?dish($|\W)'),
    'beanpot':          re.compile(r'(^|\W)bean\s?pan($|\W)'),
    'broiler tray':     re.compile(r'(^|\W)broiler\s?tray($|\W)'),
    'dutch oven':       re.compile(r'(^|\W)dutch\s?oven($|\W)'),
    'food processor':   re.compile(r'(^|\W)food\s?processor($|\W)'),
    'frying pan':       re.compile(r'(^|\W)frying\s?pan($|\W)'),
    'loaf pan':         re.compile(r'(^|\W)loaf\s?pan($|\W)'),
    'meat mallet':      re.compile(r'(^|\W)meat\s?mallet($|\W)'),
    'mixing bowl':      re.compile(r'(^|\W)mixing\s?bowl($|\W)'),
    'rolling pin':      re.compile(r'(^|\W)rolling\s?pin($|\W)'),
    'saucepan':         re.compile(r'(^|\W)sauce\s?pan($|\W)'),
    'slow cooker':      re.compile(r'(^|\W)slow\s?cooker($|\W)'),
    'stockpan':         re.compile(r'(^|\W)stock\s?pan($|\W)'),

    # simple word
    'baster':       re.compile(r'(^|\W)baster($|\W)'),
    'bowl':         re.compile(r'(^|\W)bowl($|\W)'),
    'dish':         re.compile(r'(^|\W)dish($|\W)'),
    'fork':         re.compile(r'(^|\W)fork($|\W)'),
    'foil':         re.compile(r'(^|\W)foil($|\W)'),
    'grater':       re.compile(r'(^|\W)grater($|\W)'),
    'knife':        re.compile(r'(^|\W)knife($|\W)'),
    'microwave':    re.compile(r'(^|\W)microwave($|\W)'),
    'oven':         re.compile(r'(^|\W)oven($|\W)'),
    'pan':          re.compile(r'(^|\W)pan($|\W)'),
    'plate':        re.compile(r'(^|\W)plate($|\W)'),
    'plastic':      re.compile(r'(^|\W)plastic($|\W)'),
    'pot':          re.compile(r'(^|\W)pot($|\W)'),
    'skillet':      re.compile(r'(^|\W)skillet($|\W)'),
    'spider':       re.compile(r'(^|\W)spider($|\W)'),
    'spoon':        re.compile(r'(^|\W)spoon($|\W)'),
    'thermometer':  re.compile(r'(^|\W)thermometer($|\W)'),
    'wok':          re.compile(r'(^|\W)wok($|\W)'),
    'whisk':        re.compile(r'(^|\W)whisk($|\W)')
}