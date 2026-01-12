cat > Procfile << 'EOF'
web: python manage.py migrate --noinput && python manage.py collectstatic --noinput && python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='Danchik').exists():
    User.objects.create_superuser('Danchik', 'danchik@example.com', 'color2dir/s')
    print('✅ Суперпользователь создан')
else:
    print('⚠️ Суперпользователь уже существует')
" && gunicorn hackathon_site.wsgi:application --bind 0.0.0.0:\$PORT
EOF
