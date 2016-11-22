from django.core.paginator import Paginator
from django.http import HttpResponse
from django.conf import settings

from polls.models import User, Film
import math, hashlib, datetime, os, json

def make_password(password):
    salt = '&e2g$jR-%/frwR0()2>d#'
    hash = hashlib.md5(bytes(password + salt, encoding = 'utf-8')).hexdigest()
    return hash

def check_password(hash, password):
    generated_hash = make_password(password)
    return hash == generated_hash

def save_file(f, root):
    path = os.path.join(settings.BASE_DIR + settings.MEDIA_URL, root)
    if not os.path.exists(path):
        os.makedirs(path)

    with open(os.path.join(path, f.name), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return str(root + '/' + f.name)

# Create your views here.

def error(request):
    return HttpResponse(json.dumps({'Error': '404 Not Found!'}), content_type = 'application/json')

def signup(request):
    if request.method == 'POST':
        name = ' '.join(request.POST.get('name', '').strip().split()) # убирает пробелы beg-end; несколько пробелов заменяются одним
        mail = request.POST.get('mail', '').replace(' ', '')
        password_1 = request.POST.get('password_1', '').replace(' ', '')
        password_2 = request.POST.get('password_2', '').replace(' ', '')

        if name and mail and password_1 and password_2:
            if password_1 == password_2:
                try:
                    password = make_password(password_1)
                    User.objects.create(name = name, mail = mail, password = password)
                    # user, created = User.objects.get_or_create(mail = mail, defaults = {'name': name, 'password': password_1})

                    return HttpResponse(json.dumps({'Success': 'Registration completed successfully'}), content_type = 'application/json')
                except NotUniqueError:
                    return HttpResponse(json.dumps({'Error': 'Mail уже существует!'}), content_type = 'application/json')
                except ValidationError:
                    return HttpResponse(json.dumps({'Error': 'Некорректный ввод mail!'}), content_type = 'application/json')
                except:
                    return HttpResponse(json.dumps({'Error': 'Неизвестная ошибка!'}), content_type = 'application/json')
            else:
                return HttpResponse(json.dumps({'Error': 'Пароли не совпадают!'}), content_type = 'application/json')
        else:
            return HttpResponse(json.dumps({'Error': '400 Bad Request!'}), content_type = 'application/json')
    else:
        return HttpResponse(json.dumps({'Error': '405 Method Not Allowed!'}), content_type = 'application/json')

#new
def login(request):
    if request.method == 'POST':
        mail = request.POST.get('mail', '').replace(' ', '')
        password = request.POST.get('password', '').replace(' ', '')

        if mail and password:
            try:
                user = User.objects.get(mail = mail)
                if check_password(user.password, password):
                    request.session['id'] = str(user.id)
                    return HttpResponse(json.dumps({'Success': 'Login completed successfully'}), content_type = 'application/json')
                else:
                    return HttpResponse(json.dumps({'Error': 'Неверный пароль!'}), content_type = 'application/json')
            except:
                return HttpResponse(json.dumps({'Error': 'Неверный mail!'}), content_type = 'application/json')
        else:
            return HttpResponse(json.dumps({'Error': '400 Bad Request!'}), content_type = 'application/json')
    else:
        return HttpResponse(json.dumps({'Error': '405 Method Not Allowed!'}), content_type = 'application/json')

#new
def logout(request):
    try:
        del request.session['id']
    except KeyError:
        pass
    return HttpResponse(json.dumps({'Success': 'Logout completed successfully'}), content_type = 'application/json')

# TODO: // json
def films(request, page_number):
    if request.method == 'GET':
        value = ' '.join(request.GET.get('value', '').strip().split())
        count_films_on_page = 4

        if not value:
            films = Film.objects.all()
        else:
            films = Film.objects.filter(name__icontains = value)

        if int(page_number) >= 1 and int(page_number) <= math.ceil(len(films) / count_films_on_page):
            current_page = Paginator(films, count_films_on_page)

            for film in films:
                print(film.__dict__['_data'].pop('id'))

            json.dumps([film.__dict__['_data'] for film in films])
            return HttpResponse(json.dumps([film.__dict__ for film in films]), content_type = 'application/json')
        else:
            return HttpResponse(json.dumps({'Error': '404 Not Found!'}), content_type = 'application/json')
    else:
        return HttpResponse(json.dumps({'Error': '405 Method Not Allowed!'}), content_type = 'application/json')

# TODO: // json
def filminfo(request, name):
    if request.method == 'GET':
        try:
            film = Film.objects.get(name = name)
            print(film.__dict__['_data'].pop('id'))
            return HttpResponse(json.dumps(film.__dict__['_data']), content_type = 'application/json')
        except:
            return HttpResponse(json.dumps({'Error': '404 Not Found!'}), content_type = 'application/json')
    else:
        return HttpResponse(json.dumps({'Error': '405 Method Not Allowed!'}), content_type = 'application/json')

# TODO: json (all)
def rating(request): # переделать
    if request.method == 'POST':
        name = ' '.join(request.POST.get('name', '').strip().split())
        grade = request.POST.get('grade', '').replace(' ', '')

        #film = Film.objects.get(name = name)

        #user = User.objects.get(films = film)
        #user.update(add_to_set__films = {'grade': 12})

        if name and grade:
            if 'id' in request.session:
                try:
                    user_id = request.session.get('id')
                    user = User.objects.get(id = user_id)

                    #user.update(set__films__grade = grade)

                    #Film.objects(name = name).update(set__film = grade) # изменить бд, проверки
                    return redirect('/filminfo/' + name)
                except:
                    return render(request, 'html/Error.html', {'error': '404 Not Found!'})
            else:
                return render(request, 'html/Error.html', {'error': '401 Unauthorized!'})
        else:
            return render(request, 'html/Error.html', {'error': '400 Bad Request!'})
    else:
        return render(request, 'html/Error.html', {'error': '405 Method Not Allowed!'})

# должен работать!!! проверить на уникальность
def add(request):
    if request.method == 'POST':
        name = ' '.join(request.POST.get('name', '').strip().split())

        if name:
            if 'id' in request.session:
                try:
                    user_id = request.session.get('id')
                    user = User.objects.get(id = user_id)
                    film = Film.objects.get(name = name)
                    myfilm = {'film': film, 'grade': 0, 'date': datetime.datetime.now()}
                    user.update(add_to_set__films = myfilm)
                    return HttpResponse(json.dumps({'Success': 'Successfully added'}), content_type = 'application/json')
                except:
                    return HttpResponse(json.dumps({'Error': '404 Not Found!'}), content_type = 'application/json')
            else:
                return HttpResponse(json.dumps({'Error': '401 Unauthorized!'}), content_type = 'application/json')
        else:
            return HttpResponse(json.dumps({'Error': '400 Bad Request!'}), content_type = 'application/json')
    else:
        return HttpResponse(json.dumps({'Error': '405 Method Not Allowed!'}), content_type = 'application/json')

# TODO: json (all)
def sort(request):
    if request.method == 'GET':
        value = ' '.join(request.GET.get('value', '').strip().split())

        if value:
            if 'id' in request.session:
                try:
                    user_id = request.session.get('id')
                    user = User.objects.get(id = user_id)

                    #people = User.objects.order_by('-grade')    # поправить
                    #for p in people:
                        #print(p.name + '   ' + p.mail)

                    return render(request, 'html/Error.html', {'error': 'Ок!'}) # изменить страницу
                except:
                    return render(request, 'html/Error.html', {'error': '404 Not Found!'})
            else:
                return render(request, 'html/Error.html', {'error': '401 Unauthorized!'})
        else:
            return render(request, 'html/Error.html', {'error': '400 Bad Request!'})
    else:
        return render(request, 'html/Error.html', {'error': '405 Method Not Allowed!'})

# должен работать!!!
# TODO: json
def myfilms(request, page_number):
    if request.method == 'GET':
        value = ' '.join(request.GET.get('value', '').strip().split())
        count_films_on_page = 4

        if 'id' in request.session:
            #try:
            user_id = request.session.get('id')
            user = User.objects.get(id = user_id)

            if not value:
                films = user.films
            else:
                films = list(filter(lambda film: film['film'].name == value, user.films))

            if int(page_number) >= 1 and int(page_number) <= math.ceil(len(films) / count_films_on_page):
                current_page = Paginator(films, count_films_on_page)

                """print(films)
                all_films = []
                for film in films:
                    red_id = film['film']['_ref'].id
                    print(red_id)
                    f = Film.objects.get(id = bson.objectid.ObjectId(red_id))
                    print(f)
                    all_films.append(f)
                print (all_films)"""
                return HttpResponse(json.dumps({'Error': 'Сейчас это не работает((('}), content_type = 'application/json')
            else:
                return HttpResponse(json.dumps({'Error': '404 Not Found!'}), content_type = 'application/json')
            #except:
                #return HttpResponse(json.dumps({'Error': '404 Not Found!'}), content_type = 'application/json')
        else:
            return HttpResponse(json.dumps({'Error': '401 Unauthorized!'}), content_type = 'application/json')
    else:
        return HttpResponse(json.dumps({'Error': '405 Method Not Allowed!'}), content_type = 'application/json')

# должен работать!!!
def addfilm(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        name = ' '.join(name.split()) # несколько пробелов заменяются одним
        image = save_file(request.FILES['image'], 'image')
        about = request.POST.get('about', '').replace(' ', '')
        country = request.POST.get('country', '').replace(' ', '')
        year = request.POST.get('year', '').replace(' ', '')
        genre = request.POST.get('genre', '').replace(' ', '')
        duration = request.POST.get('duration', '').replace(' ', '')
        producer = request.POST.get('producer', '').replace(' ', '')
        actors = request.POST.get('actors', '').replace(' ', '')
        video = save_file(request.FILES['video'], 'video')

        if 'id' in request.session:
            user_id = request.session.get('id')
            user = User.objects.get(id = user_id)

            if user.role == 'admin':
                if name and image and about and country and year and genre and duration and producer and actors and video:
                    try:
                        film = Film.objects.create(
                            name = name,
                            image = image,
                            about = about,
                            country = country,
                            year = year,
                            genre = genre,
                            duration = duration,
                            producer = producer,
                            actors = actors,
                            video = video
                        )
                        # get_or_create
                        return HttpResponse(json.dumps({'Success': 'Successfully added'}), content_type = 'application/json')
                    except:
                        return HttpResponse(json.dumps({'Error': 'Неверный ввод!'}), content_type = 'application/json')
                else:
                    return HttpResponse(json.dumps({'Error': '400 Bad Request!'}), content_type = 'application/json')
            else:
                return HttpResponse(json.dumps({'Error': '403 Forbidden!'}), content_type = 'application/json')
        else:
            return HttpResponse(json.dumps({'Error': '401 Unauthorized!'}), content_type = 'application/json')
    else:
        return HttpResponse(json.dumps({'Error': '405 Method Not Allowed!'}), content_type = 'application/json')
