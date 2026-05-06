def lipid_category_calc(lipid_class):
    """Retourne la catégorie lipidique à partir de la classe lipidique.
    
    :param lipid_class: Classe lipidique
    :type lipid_class: str
    :return: Catégorie lipidique ou None si inconnue
    :rtype: str
    """
    if not lipid_class:
        return ""
    
    categories = {
        "Glycerophospholipids": [
            "PE",
            "PG",
            "PA",
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
        ],
        "Cardiolipins": [
            "CL",
            "CLox",
            "DLCL",
            "MLCL",
            "MLCLox",
        ],
        "Lipopolysaccharides": [
            "LipA5P2",
            "LipA5P2PE",
            "LipA6P",
            "LipA6P2",
            "LipA6P2PE",
            "LipA6P2-KDO",
            "LipA6PPE",
            "LipA7P",
            "LipA7P2",
            "LipA7P2PE",
            "LipA7PPE",
            "LipIVA",
            "LipX3",
            "LipX4",
        ],
    }
    
    for category, classes in categories.items():
        if lipid_class in classes:
            return category
    return ""