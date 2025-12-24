import re
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import JobDescriptionForm, SignUpForm,UploadCVForm
from .models import JobOffre,CV, MatchingScore
from django.http import FileResponse, Http404
import os
from django.views.decorators.clickjacking import xframe_options_exempt
from .cv_extractor import extract_text_from_file
from .match import analyze_resume_jd
import time
import ast




	
def loginregister(request):
    if request.method == 'POST':
        if 'login' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "You Have Been Logged In!")
                # redirection selon le rôle
                if user.role == 'jobseeker':
                    return redirect('profil')
                elif user.role == 'recruiter':
                    return redirect('profil2')
            else:
                messages.error(request, "Login failed. Please check your credentials.")

        elif 'register' in request.POST:
            form = SignUpForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(request, "You Have Successfully Registered!")
                # redirection selon le rôle
                if user.role == 'jobseeker':
                    return redirect('profil')
                elif user.role == 'recruiter':
                    return redirect('profil')
            else:
                messages.error(request, "Registration failed. Please correct the errors.")
    else:
        form = SignUpForm()

    return render(request, 'loginregister.html', {'form': form})

	

def logout_user(request):
	logout(request)
	messages.success(request, "You Have Been Logged Out...")
	return redirect('home')

def home(request):
    offres = JobOffre.objects.all().order_by('-id')  # ou par date si dispo
    return render(request, 'home.html', {'offres': offres})








@xframe_options_exempt
def pdf_view(request, pdfSlug):
    try:
        cv = CV.objects.get(pdf_slug=pdfSlug)
        file_path = cv.fichier.path
        print(file_path)

        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="' + file_path + '"'
            print(response)
            return response
        else:
            raise Http404("Fichier introuvable.")
    except CV.DoesNotExist:
        raise Http404("CV introuvable.")
    
@login_required
def jobs(request) :
    last_cv = CV.objects.filter(user=request.user).order_by('-id').first()

    if not last_cv:
        return render(request, 'jobs.html', {
            'job_scores': [],
            'message': "Vous n'avez pas encore déposé de CV."
        })

    job_scores = MatchingScore.objects.filter(cv=last_cv).select_related('job_offer').order_by('-score')

    # Ajouter un attribut 'color' selon le score
    for job in job_scores:
        if job.score >= 80:
            job.color = "#28a745"  # vert
        elif job.score >= 50:
            job.color = "#ffc107"  # jaune
        else:
            job.color = "#dc3545"  # rouge

    return render(request, 'jobs.html', {
        'job_scores': job_scores,
        'last_cv': last_cv
    })

@login_required
def offre_detail(request, offre_id):
    job = get_object_or_404(JobOffre, id=offre_id)
    last_cv = CV.objects.filter(user=request.user).last()

    correspend = []
    manque = []
    score = None

    if last_cv:
        try:
            matching = MatchingScore.objects.get(cv=last_cv, job_offer=job)
            
            ch1=""
            for i in matching.correspend :
                if i != ',' :
                    ch1 += i

            ch2=""
            for i in matching.manque :
                if i != ',' :
                    ch2 += i





            
            correspend = nettoyer_et_separer(ch1)
            manque = nettoyer_et_separer(ch2)
            score = matching.score

        except MatchingScore.DoesNotExist:
            pass

    return render(request, 'offre_detail.html', {
        'job': job,
        'correspend': correspend,
        'manque': manque,
        'score': score,
    })


import json

def try_parse_list(text):
    try:
        return ast.literal_eval(text)
    except (ValueError, SyntaxError):
        try:
            return json.loads(text)
        except (ValueError, json.JSONDecodeError):
            return [text] if isinstance(text, str) else []
        
def nettoyer_et_separer(ch):
    # Étape 1 : supprimer une des deux espaces consécutives
    ch = re.sub(r'(?<=\S)  (?=\S)', ' ', ch)

    # Étape 2 : supprimer les espaces simples entre les lettres
    ch = re.sub(r'(?<=\S) (?=\S)', '', ch)

    # Étape 3 : séparer les phrases à partir du caractère '*'
    phrases = [phrase.strip() for phrase in ch.split('*') if phrase.strip()]

    return phrases


@login_required
def profil2(request):
    from .models import DescriptionJobOffer, MatchingScore2, CV, DomainCV
    from .cv_extractor import extract_text_from_file
    from .match import analyze_resume_jd
    import time

    if request.method == "POST":
        form = JobDescriptionForm(request.POST)
        if form.is_valid():
            job_desc = form.save(commit=False)
            job_desc.recruiter = request.user
            job_desc.save()

            # Récupérer tous les CVs qui ont ce domaine
            cvs = CV.objects.filter(domains=job_desc.domain)

            for cv in cvs:
                try:
                    cv_text = extract_text_from_file(cv.fichier.path, lang="eng", dpi=300)
                    result, _ = analyze_resume_jd(cv_text, job_desc.description)
                    ch1=", ".join(result["matches"]),
                    ch2=", ".join(result["misses"]),
                    ch3=""
                    for i in ch1 :
                        if i != ',' :
                            ch3 += i

                    ch4=""
                    for i in ch2 :
                        if i != ',' :
                            ch4 += i

                    MatchingScore2.objects.create(
                        job_offer_desc=job_desc,
                        cv=cv,
                        correspend=nettoyer_et_separer(ch3),
                        manque=nettoyer_et_separer(ch4),
                        score=result["percentage"]
                    )
                    time.sleep(4.2)  # éviter quota API
                    print(f"✅ Match calculé pour CV {cv.id}")

                except Exception as e:
                    print("❌ Erreur matching :", e)

            return redirect("profil2")

    else:
        form = JobDescriptionForm()

    # Historique des offres + résultats
    offres = DescriptionJobOffer.objects.filter(recruiter=request.user).order_by("-id")
    results = MatchingScore2.objects.filter(job_offer_desc__in=offres).select_related("cv", "job_offer_desc")

    return render(request, "profil2.html", {
        "form": form,
        "offres": offres,
        "results": results
    })

@login_required
def profil(request):
    if request.method == 'POST':
        form = UploadCVForm(request.POST, request.FILES)
        if form.is_valid():
            cv = form.save(commit=False)
            cv.user = request.user
            cv.save()

            # Ajouter les domaines sélectionnés (ManyToMany)
            form.save_m2m()

            print("✅ CV sauvegardé avec domaines")

            # === Étape 1 : Extraire le texte du CV
            try:
                from .cv_extractor import extract_text_from_file
                from .match import analyze_resume_jd

                cv_text = extract_text_from_file(cv.fichier.path, lang="eng", dpi=300)
                print("✅ Texte extrait")

                # === Étape 2 : Comparer avec chaque offre d’emploi
                for offer in JobOffre.objects.all():
                    result, _ = analyze_resume_jd(cv_text, offer.description)

                    MatchingScore.objects.create(
                        cv=cv,
                        job_offer=offer,
                        correspend=", ".join(result["matches"]),
                        manque=", ".join(result["misses"]),
                        score=result["percentage"]
                    )
                    time.sleep(4.2)  # éviter quota API
                    print(f"✅ Matching enregistré pour {offer.title}")

            except Exception as e:
                print("❌ Erreur analyse matching :", e)

            return redirect('profil')
    else:
        form = UploadCVForm()
    from .models import DomainCV
    last_cv = CV.objects.filter(user=request.user).order_by('-id').first()
    user_cvs = CV.objects.filter(user=request.user).order_by('-id')
    domaines = DomainCV.objects.filter()
    print(domaines)
    print(last_cv)
    return render(request, 'profil.html', {
        'form': form,
        'last_cv': last_cv,
        'user_cvs': user_cvs,
        'domaines': domaines
    })


