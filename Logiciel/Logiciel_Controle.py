import Logicielroutage as lr
import Routage_Vent as rv
import Paramètres as p  
p.position_initiale, p.position_finale = rv.point_ini_fin(p.loc_nav)

p.enable_prints()

lr.itere_jusqua_dans_enveloppe(
    p.position_initiale, p.position_finale, 
    p.pas_temporel, p.pas_angle, p.tolerance_arrivée, 
    p.loc_nav, live = p.live, 
    enregistrement = p.enregistrement
    )