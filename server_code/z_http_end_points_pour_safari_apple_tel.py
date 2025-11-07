"""
Safari (ou plus probablement l’appareil photo Apple de l'utilisateur + son navigateur intégré au QR code, Safari) envoie des requêtes automatiques comme :
/security.txt
/traffic-advice
/apple-app-site-association
avant d’autoriser le chargement réel de la page.

Quand ces requêtes tombent sur mon app Anvil locale, le serveur les rejette (404) — ce qui n’est pas grave, mais certains navigateurs iOS interprètent ça comme une erreur réseau et stoppent le chargement principal.
C’est une particularité d’iOS 17+

Je supprime complètement ces erreurs et restaure la compatibilité iPhone en ajoutant deux endpoints “neutres”
"""
import anvil.server

@anvil.server.http_endpoint("/security.txt")
def security_txt(**params):
    return """Contact: mailto:jmarc@jmm-formation-et-services.fr
Preferred-Languages: fr, en
Expires: 2026-12-31T23:59:59Z
"""

@anvil.server.http_endpoint("/traffic-advice")
def traffic_advice(**params):
    """
    Réponse neutre pour requêtes automatiques de Safari/iOS.
    Sans ce endpoint, certains iPhones bloquent l’ouverture du site.
    """
    return anvil.server.HttpResponse(
        200,
        "OK",
        headers={"Content-Type": "text/plain"}
    )
