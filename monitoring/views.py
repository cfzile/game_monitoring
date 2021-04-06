import hashlib
import json
from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader

import monitoring.events as events
from monitoring.apps import *
from monitoring.constance_private import ROBOKASSA_PASS1, ROBOKASSA_PASS2
from monitoring.forms import UserForm, AddServerForm
from monitoring.models import Server, Profile, Order, Place
from siteroot import settings
import logging

logger = logging.getLogger('monigorin_css_v34')


def get_full_context(request, context):
    cur_user_profile = None
    if request.user.is_authenticated and request.user.is_superuser and Profile.objects.filter(
            user_id=request.user.id).count() == 0:
        Profile.objects.create(user=request.user).save()
    if request.user.is_authenticated:
        cur_user_profile = Profile.objects.get(user_id=request.user.id)
    general_context = {"events": events.get(request), 'constance': constance, 'premium_servers': get_premium_servers(),
                       'cur_user_profile': cur_user_profile}
    return {**context, **general_context}


def monitoring_table(request, page=1):
    pages, servers = get_servers_by_page(page)
    context = get_full_context(request, {'Title': constance.SITE_MONITORING_CSS_V_34_NAME,
                                         'selected_monitoring': 'selected',
                                         'page': page,
                                         'pages': pages,
                                         'servers': servers})

    return render(request, 'monitoring/monitoring_table.html', get_full_context(request, context))


def sign_up(request):
    if request.user.is_authenticated:
        return redirect('/')

    user_form = UserForm()

    if request.method == 'POST':

        user_form = UserForm(request.POST)

        if user_form.is_valid():

            if request.POST.get('password') == request.POST.get('password_repeat'):
                user = user_form.save(commit=False)
                user.set_password(user_form.cleaned_data['password'])
                user.save()
                Profile.objects.create(user=user, servers=[])

                events.add_event(request, {constance.EVENT_INFO: ['Регистация прошла успешно.']})

                return redirect("sign_in")
            else:
                events.add_event(request, {constance.EVENT_ERROR: ['Пароли не совпадают.']})

        else:
            events.add_event(request, user_form.errors)

    return render(request, "monitoring/sign_up.html", get_full_context(request, {'Title': constance.SITE_SIGN_UP_NAME,
                                                                                 'user_form': user_form}))


def sign_in(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('/')
        else:
            events.add_event(request, {constance.EVENT_ERROR: [constance.NON_CORRECT_DATA]})

    template = loader.get_template('monitoring/sign_in.html')
    return HttpResponse(template.render(get_full_context(request, {'Title': constance.SITE_SIGN_IN_NAME}), request))


@login_required(login_url='/sign_in')
def sign_out(request):
    logout(request)
    return redirect('/')


def handler404(request, exception):
    response = render(request, 'monitoring/404.html', {})
    response.status_code = 404
    return response


def profile(request, user_id):
    user_profile = get_object_or_404(Profile, user_id=user_id)
    return render(request, "monitoring/profile.html", get_full_context(request, {"Title": user_profile.user.username,
                                                                                 "profile": user_profile}))


def server_profile(request, server_id):
    server = get_object_or_404(Server, id=server_id)
    return render(request, "monitoring/server_profile.html", get_full_context(request, {"Title": server.name,
                                                                                        "server": server}))


def add_server(request):
    form = AddServerForm()

    if request.method == 'POST':

        form = AddServerForm(request.POST)

        if form.is_valid():
            ip = request.POST.get("ip")
            port = request.POST.get("port")

            if len(ip) < 7 or len(port) > 5 or len(port) < 2:
                events.add_event(request, {constance.EVENT_ERROR: [constance.NON_CORRECT_DATA]})
            else:
                try:
                    Server.objects.get(ip=ip, port=port)
                    events.add_event(request,
                                     {constance.EVENT_ERROR: [constance.SUCH_SERVER_EXIST("%s:%s" % (ip, port))]})
                except:
                    try:
                        server = Server.objects.create(ip=ip, port=port, position_in_table=1000)
                        if server.update_info():
                            events.add_event(request, {constance.EVENT_INFO: ["Сервер успешно добавлен"]})
                            return redirect('/')
                        server.delete()
                        raise
                    except:
                        events.add_event(request, {
                            constance.EVENT_ERROR: [constance.NON_CORRECT_DATA_OR_SERVER_DONT_RUN(ip, port)]})

        else:
            events.add_event(request, {constance.EVENT_ERROR: [constance.NON_CORRECT_DATA]})

    return render(request, "monitoring/add_server.html",
                  get_full_context(request, {'Title': constance.SITE_SERVER_ADD_NAME,
                                             'form': form, 'selected_add_server': 'selected'}))


def check_email(email):
    return True


def get_signature_val_for_result(sum, order_id):
    signature_val = str(sum) + ":" + str(order_id) + ":" + ROBOKASSA_PASS2
    signature_val = hashlib.md5(signature_val.encode()).hexdigest()

    return signature_val.upper()


def get_signature_val_for_payment(sum, order_id):
    signature_val = "zilestan_game_monitoring:" + str(sum) + ":" + str(order_id) + ":" + ROBOKASSA_PASS1
    signature_val = hashlib.md5(signature_val.encode()).hexdigest()

    return signature_val.upper()


def buy_place(request):
    places = Place.objects.order_by('-status', 'place_number').all()
    for place in places:
        place.update_disabled_dates()

    clear_orders()

    if request.method == "POST":

        if Server.objects.filter(ip=request.POST.get("ip"), port=request.POST.get("port")).count() == 0:
            logger.error("buy_place: method-POST, servers don't add \n" + str(request.POST))
            events.add_event(request, {constance.EVENT_ERROR: ['Добавьте сервер в мониторинг.']})
        elif request.POST.get('agree') and check_email(request.POST.get("email")) and Server.objects.filter(
                ip=request.POST.get("ip"), port=request.POST.get("port")).count() == 1:
            logger.info("buy_place: method-POST, get_all_fields")
            basket = []
            split_order = []
            total_price = 0
            error = False
            server = Server.objects.get(ip=request.POST.get("ip"), port=request.POST.get("port"))
            logger.info("buy_place: method-POST, server existed")

            for key, value in request.POST.items():
                if key[:4] == "pos_":
                    id = int(key[4:])
                    place = places.get(id=id)
                    date_from = datetime.strptime(request.POST.get('data_from_%d' % id),
                                                  constance.DATE_FORMAT_PYTHON).date()
                    date_to = datetime.strptime(request.POST.get('data_to_%d' % id),
                                                constance.DATE_FORMAT_PYTHON).date()
                    price = place.price

                    if date_to < date_from or date_from < timezone.localtime().date():
                        error = True
                        logger.error("buy_place: method-POST, dates is wrong")
                        break

                    num_days = 0
                    except_dates = []
                    pair_dates = []
                    current = date_from
                    first_date = current
                    prev_date = current
                    cur_num_days = 0

                    while current <= date_to:
                        formatted_date = dateformat.format(current, constance.DATE_FORMAT_PYTHON_TO)
                        if formatted_date not in place.disabled_dates:
                            num_days += 1
                            cur_num_days += 1
                        else:
                            if first_date <= prev_date and cur_num_days != 0:
                                pair_dates.append([first_date, prev_date])
                            first_date = current + timezone.timedelta(days=1)
                            except_dates.append(formatted_date)
                            cur_num_days = 0
                        prev_date = current
                        current = current + timezone.timedelta(days=1)

                    if first_date <= prev_date:
                        pair_dates.append([first_date, prev_date])

                    basket.append([place, date_from, date_to, num_days, price * num_days])
                    split_order.append(pair_dates)
                    total_price += price * num_days

            if error or total_price == 0:
                events.add_event(request, {constance.EVENT_ERROR: [constance.NON_CORRECT_DATA]})
            else:
                order_id = int((str(server.id) + str(timezone.localtime().timestamp())).replace('.', '0')) % 1000000009

                i = 0
                html_message = '<html><head>'
                html_message += '<style> td{    display: table-cell; padding: 5% 2%;} tr:first-child{ background: #1FA88C; ' \
                                'color: white; text-align: center; font-weight: bold;}</style></head>'
                html_message += '<body>Сервер ' + str(server.ip) + ':' + str(server.port) + '<table style="width: 100%; color: #0D0D0D;border-collapse: collapse;"><tr style="font-weight: bold"><td style="border: 1px solid black;">Место</td><td style="border: 1px solid black;">Период</td><td style="border: 1px solid black;">Сумма</td></tr>'
                description = ""
                for place, date_from, date_to, num_days, sum in basket:
                    for split_date_from, split_date_to in split_order[i]:
                        Order.objects.create(place=place, sum=sum, date_from=split_date_from, date_to=split_date_to,
                                             server=server, order_id=order_id, email=request.POST.get("email"))
                        html_message += '<tr><td style="border: 1px solid black;">%s</td><td style="border: 1px solid black;">от %s по %s</td><td style="border: 1px solid black;">%s руб./день</td></tr>' % (
                        place.name, str(split_date_from), str(split_date_to), str(place.price))
                    i += 1

                html_message += '<tr style="font-weight: bold"><td style="border: 1px solid black;" colspan="2">Итог</td><td style="border: 1px solid black;">%s руб.</td></tr></table>' % str(
                    total_price)
                html_message += '</body></html>'

                signature_val = get_signature_val_for_payment(total_price, order_id)

                ex_time = (timezone.localtime() + timezone.timedelta(minutes=3)).isoformat()

                logger.info("buy_place: method-POST, orders created")

                send_mail('Информация о заказе GAMEMONITORINGSITE', 'Спасибо за заказ!', constance.administrator_email,
                          [request.POST.get("email"), constance.administrator_email], fail_silently=False, auth_user=constance.administrator_email,
                          auth_password=constance.administrator_email_password,
                          html_message=html_message)

                return redirect("https://auth.robokassa.ru/Merchant/Index.aspx?MerchantLogin=zilestan_game_monitoring"
                                "&Culture=ru&Encoding=utf-8&Description=" + str(description) +
                                "&OutSum=" + str(total_price) + "&InvId=" + str(
                    order_id) + "&ExpirationDate" + ex_time +
                                "&Email=" + request.POST.get("email") + "&SignatureValue=" + signature_val)

                # return redirect("https://auth.robokassa.ru/Merchant/Index.aspx?MerchantLogin=zilestan_game_monitoring"
                #                 "&Culture=ru&Encoding=utf-8&Description=" + str(description) +
                #                 "&OutSum=" + str(total_price) + "&InvId=" + str(order_id) + "&ExpirationDate" + ex_time +
                #                 "&Email=" + request.POST.get("email") + "&SignatureValue=" + signature_val)

        else:
            logger.error("buy_place: method-POST, don't get all fields\n" + str(request.POST))
            events.add_event(request, {constance.EVENT_ERROR: [constance.NON_CORRECT_DATA]})

    return render(request, "monitoring/buy_place.html",
                  get_full_context(request, {'Title': constance.SITE_BUY_PLACE_NAME,
                                             'places': places,
                                             'selected_buy_place': 'selected'}))


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_expiry_session():
    w = timezone.localtime().weekday()

    expiry_session = timezone.timedelta(weeks=1).total_seconds() - (
            timezone.localtime().time().hour * 60 * 60 + timezone.localtime().time().minute * 60 + timezone.localtime().time().second) - w * 24 * 60 * 60

    return expiry_session


def add_voice(request):
    if request.method == 'GET':
        return redirect("/")

    server = get_object_or_404(Server, id=request.POST['server'])

    if not request.session.has_key('ip'):
        request.session['ip'] = get_client_ip(request)
        request.session['add_voice'] = False
        request.session.set_expiry(get_expiry_session())
    else:
        if request.session['add_voice']:
            return HttpResponse(json.dumps({'results': server.num_points}), content_type='application/json')

    server.num_points += 1
    server.save()

    data = {
        'results': server.num_points
    }

    request.session['add_voice'] = True

    return HttpResponse(json.dumps(data), content_type='application/json')


def add_all_servers(request):
    if request.user.is_superuser:
        file = open(settings.BASE_DIR + "/servers")

        for line in file:
            line = line.rstrip()
            ip = line[:line.find(':')]
            port = int(line[(line.find(':') + 1):])
            Server.objects.create(ip=ip, port=port, position_in_table=-1).update_info()

    return redirect("/")


def payment_result(request):
    logger.info("payment_result: method-GET, " + str(request.GET))
    if request.method == "GET":
        logger.info("payment_result: method-GET, " + str(request.GET))

        if request.GET.get("InvId") is not None:
            logger.info(
                "payment_result: method-GET, " + str(request.GET.get("InvId")) + str(int(request.GET.get("OutSum"))))
            qs = Order.objects.filter(order_id=request.GET.get("InvId"))
            if not (qs.count() == 0 or request.GET.get("SignatureValue").upper() !=
                    get_signature_val_for_result(request.GET.get("OutSum"), request.GET.get("InvId"))):
                Order.objects.filter(order_id=request.GET.get("InvId")).update(active=True)

    return HttpResponse()


def faq(request):
    return render(request, "monitoring/faq.html", get_full_context(request, {'Title': constance.SITE_FAQ_NAME,
                                                                             'selected_faq': 'selected'}))


def offer(request):
    return render(request, "monitoring/offer.html", {})


def rules(request):
    return render(request, "monitoring/rules.html", {})


def add_places(request):
    if request.user.is_superuser:
        add_places_()
    return redirect("/")


def success_payment(request):
    if request.method == "GET":
        events.add_event(request, {constance.EVENT_INFO: ['Заказ принят']})

    return redirect("/")


def failed_payment(request):
    if request.method == "GET":
        events.add_event(request, {constance.EVENT_ERROR: ['Заказ не принят']})

    return redirect("/")
