SECRET_KEY = 'fake-key'

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "flexible_permissions",
    "tests",
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'tests',
    }
}
