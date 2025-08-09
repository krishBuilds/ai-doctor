import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'rest_framework',
    'corsheaders',
    'avatar',
    'voice',
    'chat',
    'animation',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ai_doctor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ASGI_APPLICATION = 'ai_doctor.asgi.application'
# WSGI_APPLICATION = 'ai_doctor.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# OpenAI Configuration (Using GPT-4o mini for best cost/performance ratio)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# Using GPT-4o mini - cheapest and latest model with great performance
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')  # Cheapest GPT-4 class model
OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '1000'))  # Increased for better medical responses

# OpenAI Voice Models (TTS-1 is cheaper than TTS-1-HD)
OPENAI_TTS_MODEL = os.getenv('OPENAI_TTS_MODEL', 'tts-1')  # Cheaper model
OPENAI_TTS_VOICE = os.getenv('OPENAI_TTS_VOICE', 'alloy')  # Good quality, standard voice
OPENAI_WHISPER_MODEL = os.getenv('OPENAI_WHISPER_MODEL', 'whisper-1')  # Only Whisper model available

# Medical AI Configuration
MEDICAL_AI_SYSTEM_PROMPT = os.getenv('MEDICAL_AI_SYSTEM_PROMPT', 
    'You are Dr. AI, a professional virtual medical assistant. Provide helpful, accurate medical information while always recommending users consult with qualified healthcare professionals for medical advice.')
MAX_CONVERSATION_HISTORY = int(os.getenv('MAX_CONVERSATION_HISTORY', '10'))
ENABLE_VOICE_RESPONSES = os.getenv('ENABLE_VOICE_RESPONSES', 'True') == 'True'
ENABLE_GESTURE_RESPONSES = os.getenv('ENABLE_GESTURE_RESPONSES', 'True') == 'True'

# Feature Flags
ENABLE_OPENAI_INTEGRATION = os.getenv('ENABLE_OPENAI_INTEGRATION', 'True') == 'True'
ENABLE_AVATAR_INTEGRATION = os.getenv('ENABLE_AVATAR_INTEGRATION', 'True') == 'True'
ENABLE_VOICE_CHAT = os.getenv('ENABLE_VOICE_CHAT', 'True') == 'True'
ENABLE_TEXT_TO_SPEECH = os.getenv('ENABLE_TEXT_TO_SPEECH', 'True') == 'True'
ENABLE_SPEECH_TO_TEXT = os.getenv('ENABLE_SPEECH_TO_TEXT', 'True') == 'True'

# Rate Limiting
OPENAI_RATE_LIMIT_RPM = int(os.getenv('OPENAI_RATE_LIMIT_RPM', '60'))
OPENAI_RATE_LIMIT_TPM = int(os.getenv('OPENAI_RATE_LIMIT_TPM', '10000'))

# Other API Keys
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'