import re

def lipid_category_calculation(lipid_class):
    """Retourne la catégorie lipidique à partir de la classe lipidique.
    
    :param lipid_class: Classe lipidique
    :type lipid_class: str
    :return: Catégorie lipidique ou None si inconnue
    :rtype: str
    """
    if not lipid_class:
        return None

    if not isinstance(lipid_class, str):
        lipid_class = str(lipid_class)

    lipid_class = lipid_class.strip()
    
    # Extraction du premier mot, arrêt lors d'un espace
    m = re.match(r'^[A-Za-z0-9\-]+', lipid_class)
    key = m.group(0) if m else lipid_class

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
    return None


def lipid_class_calculation(lipid_name):
    """lipid_class_calc _summary_

    :param lipid_name: _description_
    :type lipid_name: _type_
    :return: _description_
    :rtype: _type_
    """

    if lipid_name is None:
        return None

    lipid_name = str(lipid_name).strip()
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

    # Tri des prefixes du plus long au plus cours
    prefixes = sorted(prefixes, key=len, reverse=True)
    
    # Le nom des lipides est mis en majuscules pour éviter les erreurs de casse
    lipid_name_upper = lipid_name.upper()

    # Test de tous les préfixes du plus grand au plus petit
    for prefix in prefixes:
        # Les préfixes sont mis en majuscules pour éviter les erreurs de casse
        if lipid_name_upper.startswith(prefix.upper()):
            return prefix
    return None

