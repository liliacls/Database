def exact_mass_calculation(Precursor_MZ, ion_mode):
    """
    Calcul de la masse exacte à partir du Precursor_MZ et du mode d'ionisation
    """
    
    # Masse du proton en Da
    masse_proton = 1.007276

    # En mode positif, la molécule a gagné un proton donc retrait
    if ion_mode == "Positif":
        return round(Precursor_MZ - masse_proton, 6)
    
    # En mode négatif, la molécule a perdu un proton, donc rajout
    else:
        return round(Precursor_MZ + masse_proton, 6)
