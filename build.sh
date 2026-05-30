pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
# Create a superuser using environment variables (Add this to your build.sh)
if [[ $CREATE_SUPERUSER ]];
then
    python manage.py createsuperuser --no-input
    echo "Superuser creation attempted."
fi