# Create your views here.
from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import UserRegistrationModel
from django.conf import settings
import pandas as pd
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC, LinearSVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import string
import logging

logger = logging.getLogger(__name__)

# File paths
DATASET_PATH = os.path.join(settings.MEDIA_ROOT, 'twitter sentiment analysis.csv')
MODEL_PATH = os.path.join(settings.MEDIA_ROOT, 'svm_model.pkl')
VECTORIZER_PATH = os.path.join(settings.MEDIA_ROOT, 'tfidf_vectorizer.pkl')


# Create your views here.
def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            print('Data is Valid')
            form.save()
            messages.success(request, 'You have been successfully registered')
            form = UserRegistrationForm()
            return render(request, 'UserRegistrations.html', {'form': form})
        else:
            # Fixed: Changed from messages.success() to messages.error()
            messages.error(request, 'Registration failed. Email or Mobile may already exist.')
            print("Invalid form", form.errors)
    else:
        form = UserRegistrationForm()
    return render(request, 'UserRegistrations.html', {'form': form})


def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        print("Login ID = ", loginid, ' Password = ', pswd)
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            status = check.status
            print('Status is = ', status)
            if status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                print("User id At", check.id, status)
                return redirect('UserHome')
            else:
                messages.warning(request, 'Your account has not been activated yet. Please contact administrator.')
                return render(request, 'UserLogin.html')
        except UserRegistrationModel.DoesNotExist:
            messages.error(request, 'Invalid login ID or password')
            logger.warning(f'Failed login attempt for user: {loginid}')
        except Exception as e:
            messages.error(request, 'An error occurred during login. Please try again.')
            logger.error(f'Unexpected error during login: {str(e)}')
    
    return render(request, 'UserLogin.html', {})


def UserHome(request):
    if not request.session.get('id'):
        messages.warning(request, 'Please login first')
        return redirect('UserLogin')
    return render(request, 'users/UserHomePage.html', {})


def DatasetView(request):
    if not request.session.get('id'):
        messages.warning(request, 'Please login first')
        return redirect('UserLogin')
    
    if not os.path.exists(DATASET_PATH):
        return render(request, 'users/viewdataset.html', {'error': 'Dataset not found'})

    try:
        df = pd.read_csv(DATASET_PATH)
        data = df.head(50).to_html(classes='table table-bordered table-striped', index=False)
        return render(request, 'users/viewdataset.html', {'data': data})
    except Exception as e:
        logger.error(f'Error loading dataset: {str(e)}')
        return render(request, 'users/viewdataset.html', {'error': f'Error loading dataset: {str(e)}'})


import numpy as np
import warnings
warnings.filterwarnings('ignore')


def preprocess_text(text):
    """Ultra-fast preprocessing"""
    if pd.isna(text):
        return ""
    text = str(text).lower()
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)
    return text


def training(request):
    if not request.session.get('id'):
        messages.warning(request, 'Please login first')
        return redirect('UserLogin')
    
    if not os.path.exists(DATASET_PATH):
        return render(request, 'users/training.html', {'error': 'Dataset not found'})

    try:
        print("Loading dataset...")
        df = pd.read_csv(DATASET_PATH, dtype={'Text': 'string', 'Label': 'category'})
        print(f"Dataset loaded: {len(df)} rows")
        
        print("Preprocessing...")
        df['Text'] = df['Text'].apply(preprocess_text)
        df = df[df['Text'].str.len() > 0]
        print(f"Cleaned: {len(df)} rows")

        X = df['Text'].values
        y = df['Label'].values

        print("Splitting...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        print("Vectorizing...")
        vectorizer = TfidfVectorizer(
            max_features=800,
            stop_words='english',
            ngram_range=(1, 1),
            min_df=3,
            max_df=0.9,
            sublinear_tf=True
        )
        
        X_train_vec = vectorizer.fit_transform(X_train)
        X_test_vec = vectorizer.transform(X_test)
        print(f"Features: {X_train_vec.shape[1]}")

        print("Training SVM...")
        from sklearn.multiclass import OneVsRestClassifier
        base_svm = SVC(
            kernel='linear',
            C=1.0,
            probability=False,
            random_state=42,
            max_iter=1000
        )
        model = OneVsRestClassifier(base_svm, n_jobs=1)
        
        model.fit(X_train_vec, y_train)

        print("Evaluating...")
        y_pred = model.predict(X_test_vec)
        accuracy = round(accuracy_score(y_test, y_pred) * 100, 2)
        print(f"✅ Accuracy: {accuracy}%")

        print("Saving...")
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model, f)
        with open(VECTORIZER_PATH, 'wb') as f:
            pickle.dump(vectorizer, f)

        context = {
            'accuracy': accuracy,
            'report': classification_report(y_test, y_pred, output_dict=True),
            'matrix': confusion_matrix(y_test, y_pred).tolist(),
            'status': f'Training complete! Accuracy: {accuracy}%'
        }
        messages.success(request, f'Model trained successfully with {accuracy}% accuracy')
        return render(request, 'users/training.html', context)
        
    except Exception as e:
        logger.error(f'Error during training: {str(e)}')
        messages.error(request, f'Training error: {str(e)}')
        return render(request, 'users/training.html', {'error': str(e)})


def prediction(request):
    if not request.session.get('id'):
        messages.warning(request, 'Please login first')
        return redirect('UserLogin')
    
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        
        if not text:
            return render(request, 'users/prediction.html', {
                'error': 'Please enter some text!'
            })
        
        try:
            # Load trained model and vectorizer
            with open(MODEL_PATH, 'rb') as f:
                model = pickle.load(f)
            with open(VECTORIZER_PATH, 'rb') as f:
                vectorizer = pickle.load(f)
            
            # Preprocess input text
            processed_text = preprocess_text(text)
            
            # Vectorize and predict
            text_vec = vectorizer.transform([processed_text])
            prediction_result = model.predict(text_vec)[0]
            
            context = {
                'prediction': prediction_result,
                'input_text': text,
                'status': 'Prediction complete!'
            }
            return render(request, 'users/prediction.html', context)
            
        except FileNotFoundError:
            logger.warning('Model files not found')
            return render(request, 'users/prediction.html', {
                'error': 'Please train the model first!'
            })
        except Exception as e:
            logger.error(f'Prediction error: {str(e)}')
            return render(request, 'users/prediction.html', {
                'error': f'Prediction error: {str(e)}'
            })
    
    return render(request, 'users/prediction.html')
