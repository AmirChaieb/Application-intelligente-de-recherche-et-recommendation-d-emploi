from cv_extractor import extract_text_from_file  # fichier OCR précédent
from match import analyze_resume_jd    # script d'analyse Gemini

# === 1. Extraire le texte depuis le CV (PDF) ===
cv_path = "CV2.pdf"  # Assure-toi que ce fichier est bien dans le même dossier
try:
    cv_text = extract_text_from_file(cv_path, lang="eng", dpi=300)
except Exception as e:
    print(f"Erreur lors de l'extraction du texte OCR : {e}")
    exit(1)

# === 2. Texte de l’offre d’emploi (Fourni) ===
job_description = """
Lieu de travailAbidjan, Côte d'ivoire
Date d'expiration22 Septembre
Niveau de posteStagiaire / Etudiant| Jeune diplômé
Secteur d'activitéBanque, Assurance, Finance
Niveau d'étude (diplome)Master 2, Ingéniorat, Bac + 5
Nombre de postes01
Type de contratStage – Temps partiel
MISSIONS DU POSTE :

. Participer à la conception et au développement de solutions automatisées à l'aide de la suite MS365 (Power automate, Power apps, sharepoint, etc.);

. Créer et maintenir des applications personnalisées avec MS365;

. Collaborer avec les équipes pour identifier et automatiser les processus métier.

FONCTIONS DETAILLEES :

·     Analyser les processus métiers existants, les besoins des utilisateurs et identifier les opportunités d'automatisation en vue de proposer des solutions adaptées.

·     Concevoir et développer des flux de travail automatisés avec Microsoft 365.

·     Créer des applications personnalisées avec Power Apps pour répondre aux besoins spécifiques des utilisateurs.

·     Implémenter des solutions RPA pour automatiser les tâches répétitives et améliorer l'efficacité opérationnelle.

·     Tester et déployer des applications et des flux de travail.

·     Collaborer avec les équipes internes pour assurer l'intégration et le déploiement des solutions.

·     Assurer le suivi évaluation, la maintenance et le support des solutions développées.

·     Rédiger la documentation technique et les guides utilisateurs des solutions développées

·     Assurer l’accompagnement et la formation des utilisateurs finaux

·     Garantir la qualité et la fiabilité des solutions développées.

·     Assurer une communication efficace avec les parties prenantes.
"""

# === 3. Analyser la compatibilité entre le CV et le poste ===
try:
    result, full_response = analyze_resume_jd(cv_text, job_description)

    print("\n===== RÉSUMÉ DU CV =====")
    print(result["resume_summary"])

    print("\n===== RÉSUMÉ DE L'OFFRE D'EMPLOI =====")
    print(result["jd_summary"])

    print("\n===== COMPÉTENCES CORRESPONDANTES =====")
    print(result["matches"])

    print("\n===== COMPÉTENCES MANQUANTES OU FLOUES =====")
    print(result["misses"])

    print("\n===== POURCENTAGE DE CORRESPONDANCE =====")
    print(f"{result['percentage']} %")

except Exception as e:
    print(f"\nErreur d'analyse avec Gemini : {e}")
