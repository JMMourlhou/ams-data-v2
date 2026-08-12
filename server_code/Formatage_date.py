import re
"""
    Formate un numéro français de 10 chiffres :
    0102030405 -> 01-02-03-04-05

    Accepte également :
    01 02 03 04 05
    01.02.03.04.05
    01-02-03-04-05

    Si le numéro n'a pas 10 chiffres,
    il est retourné sans modification.
    """

def telephone_fr(tel):

    if tel is None:
        return ""
    
        tel = str(tel).strip()
    
    # On ne conserve que les chiffres
    chiffres = re.sub(r"\D", "", tel)
    
    if len(chiffres) != 10:
        return tel
    
    return "-".join(
        chiffres[i:i + 2]
        for i in range(0, 10, 2)
    )
