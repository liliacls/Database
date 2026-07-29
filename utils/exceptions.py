class PostIntegrationError(Exception):
    """
    Erreur levée lors de l'echec de création d'une sauvegarde ou de l'écriture de l'historique.
    Ce n'est pas un échec d'intégration, les données sont déjà stockées dans la base de données.

    :param message: message décrivant l'échec de la sauvegarde ou de l'écriture de l'historique.
    :type message: str
    :param detection_ids: identifiants des ``Detection`` déjà validées (commit) en base avant l'échec.
    :type detection_ids: list[int]
    """
    def __init__(self, message: str, detection_ids: list[int]):
        super().__init__(message)
        self.detection_ids = detection_ids