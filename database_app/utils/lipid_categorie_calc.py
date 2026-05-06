def lipid_class_calc(lipid_name):
    """lipid_class_calc _summary_

    :param lipid_name: _description_
    :type lipid_name: _type_
    :return: _description_
    :rtype: _type_
    """
    if not lipid_name:
        return None

    prefixes = [
        # Glycerophospholipides
        "LPE",
        "LPG",
        "LPA",
        "LcycPGP",
        "NAPE",
        "PAGPE",
        "PGox",
        "PPA",
        "aPG",
        "DaPG",
        "PE",
        "PG",
        "PA",

        # Cardiolipines
        "CLox", 
        "DLCL", 
        "MLCL", 
        "MLCLox", 
        "CL",

        # Lipides A
        "LipA5P2PE", 
        "LipA6P2PE", 
        "LipA6PPE", 
        "LipA7P2PE", 
        "LipA7PPE",
        "LipA5P2", 
        "LipA6P2-KDO", 
        "LipA6P2", 
        "LipA6P", 
        "LipA7P2", 
        "LipA7P",
        "LipIVA", 
        "LipX3", 
        "LipX4",

    ]

    for prefix in prefixes:
        if lipid_name.startswith(prefix):
            return prefix
    return ""