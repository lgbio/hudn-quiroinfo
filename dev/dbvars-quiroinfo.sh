export PGDATABASE="quiroinfo"
export PGUSER="postgres"
export PGPASSWORD="postgres"
export PGHOST=localhost
export PGPORT=5432

export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/quiroinfo"
export DATABASE_PUBLIC_URL=$DATABASE_URL

#-- Django superuser
export DJANGO_SUPERUSER_USERNAME=lgx
export DJANGO_SUPERUSER_PASSWORD=lge
export DJANGO_SUPERUSER_EMAIL="lgx@gmail.com"

#-- Django project dir
export DJANGO_PROJECT_ROOT=/home/lg/APPS/EcuapassDocs/edocsapp
export PGURL="postgresql://$PGUSER:$PGPASSWORD@$PGHOST:$PGPORT/$PGDATABASE"
