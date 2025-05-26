import requests
from notion import secrets_eletrogrow
import datetime
from dateutil.relativedelta import relativedelta
import pandas_market_calendars as mcal
import time
import json
from pprint import pprint


headers = {
    "Authorization": "Bearer " + secrets_eletrogrow.NOTION_TOKEN,
    "Notion-Version": "2022-06-28",
    "content-type": "application/json"
}

MONTHS = ['Janeiro',
          'Fevereiro',
          'Março',
          'Abril',
          'Maio',
          'Junho',
          'Julho',
          'Agosto',
          'Setembro',
          'Outubro',
          'Novembro',
          'Dezembro']


def get_users():
    url = 'https://api.notion.com/v1/users/me'
    res = requests.get(url, headers=headers)
    return res.json()['id']


def get_pages(database: str, _filter=None, sort=None, num_pages=None):
    """
    If num_pages is None, get all pages, otherwise just the defined number.
    """
    url = f"https://api.notion.com/v1/databases/{database}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages
    payload = {"page_size": page_size}
    if _filter:
        payload['filter'] = _filter
    if sort:
        payload['sorts'] = sort
    response = requests.post(url, json=payload, headers=headers)
    #pprint(response.json())
    data = response.json()
    if "results" in data.keys():
        results = data["results"]
        while data["has_more"] and get_all:
            payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
            url = f"https://api.notion.com/v1/databases/{database}/query"
            response = requests.post(url, json=payload, headers=headers)
            data = response.json()
            results.extend(data["results"])
        if len(results) > 0:
            for page in results:
                edited_time = datetime.datetime.strptime(page['last_edited_time'],
                                                         "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=datetime.UTC)
                if ((datetime.datetime.now(datetime.UTC) - edited_time).total_seconds() < 20 and
                        page["last_edited_by"]['id'] != get_users()):
                    time.sleep(20)
                    return get_pages(database, _filter)
            return results
    return None


def create_page(database: str, data: dict):
    create_url = "https://api.notion.com/v1/pages"

    payload = {"parent": {"database_id": database}, "properties": data}

    res = requests.post(create_url, headers=headers, json=payload)
    #print(res.content)
    return res


def update_page(page_id: str, data: dict):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {"properties": data}
    res = requests.patch(url, json=payload, headers=headers)
    return res

def isdateutil(date, delta="Positive"):
    try:
        date = date.date()
    except:
        pass
    calendario = mcal.get_calendar("BMF")
    dias_uteis = calendario.schedule(start_date=datetime.datetime.strftime(date - relativedelta(days=7),
                                                                           '%Y-%m-%d'),
                                     end_date=datetime.datetime.strftime(date + relativedelta(days=7),
                                                                         '%Y-%m-%d'))
    while datetime.datetime.fromtimestamp(time.mktime(date.timetuple())) not in dias_uteis.index:
        if delta.capitalize() == "Positive":
            date = date + relativedelta(days=1)
        else:
            date = date - relativedelta(days=1)
    return date


def solve_entry():
    _filter = {"property": "Parcelas criadas",
                    "formula": {
                       "checkbox": {
                           "equals": False
                       }
                   }
               }
    res = get_pages(secrets_eletrogrow.PROJECTS_DATABASE, _filter=_filter)
    if res:
        for page in res:
            valor = page['properties']['Valor']['number']
            parcelas = page['properties']['Parcelas']['number']
            if not parcelas:
                parcelas = 1
            nome = page['properties']["Nome"]["title"][0]["text"]["content"]
            data = datetime.datetime.strptime(page['properties']['Data vencimento']['date']['start'],
                                              '%Y-%m-%d').date()
            data = isdateutil(data)
            project_id = page['id']
            for parcela in range(parcelas):
                payload = {}
                title = f'{nome} - {parcela + 1}/{parcelas}' if parcelas > 1 else nome
                value = valor / parcelas
                date = isdateutil(data + relativedelta(months=parcela))
                payload.update({"Receita": {"title": [{"text": {"content": title}}]}})
                payload.update({'Valor': {'number': value}})
                payload.update({'Data': {'date': {'start': datetime.datetime.strftime(date, '%Y-%m-%d')}}})
                payload.update({'Forma de pagamento': {'multi_select': [{'name': 'PIX'}]}})
                payload.update({'Projeto': {'relation': [{'id': project_id}]}})
                res = create_page(secrets_eletrogrow.ENTRY_DATABASE, payload)
            if res.status_code == 200:
                payload = {"Parcelas criadas": {"checkbox": True}}
                update_page(project_id, payload)


def balance():
    ultimo_dia = datetime.datetime.strftime((datetime.date.today() - relativedelta(days=1)), '%Y-%m-%d')
    #primeiro_dia = datetime.datetime.strftime((datetime.date.today() - relativedelta(months=1)), '%Y-%m-%d')
    hoje = datetime.date.today()
    #hoje = datetime.date(2025,4,1)
    _filter = {"and": [
                       # {"property": "Data",
                       #  "formula": {
                       #      "date": {
                       #          "on_or_after": primeiro_dia
                       #              }
                       #              }
                       # },
                       {"property": "Data",
                        "formula": {
                            "date": {
                                "on_or_before": ultimo_dia
                                    }
                                    }
                        },
                        {"property": "Pago",
                             "formula": {
                                "checkbox": {
                                    "equals": True
                                            }
                                        }
                        }
                    ]
            }
    only_new_filter = {"property": "Balanço",
                 "formula": {
                     "checkbox": {
                         "equals": False
                            }
                     }
                    }
    title = f'{MONTHS[(hoje - relativedelta(days=1)).timetuple()[1] - 1]}/{str((hoje - relativedelta(days=1)).timetuple()[0])[-2:]}'
    res_balance = get_pages(secrets_eletrogrow.BALANCE_DATABASE,
                                  _filter={"property": "Mês", "rich_text": {"equals": title}})
    if not res_balance:
        _filter['and'].append(only_new_filter)
    total_entrada = 0
    total_saida = 0
    res_entry = get_pages(secrets_eletrogrow.ENTRY_DATABASE, _filter=_filter)
    if res_entry:
        for page in res_entry:
            if page['properties']['Pago']['checkbox']:
                total_entrada += page['properties']['Valor']['number']
                check_balance = {"Balanço": {"checkbox": True}}
                update_page(page['id'], check_balance)
    res_exit = get_pages(secrets_eletrogrow.EXIT_DATABASE, _filter=_filter)
    if res_exit:
        for page in res_exit:
            if page['properties']['Pago']['checkbox']:
                total_saida += page['properties']['Valor']['number']
                check_balance = {"Balanço": {"checkbox": True}}
                update_page(page['id'], check_balance)
    payload = {}
    payload.update({"Mês": {"title": [{"text": {"content": title}}]}})
    payload.update({'Entradas': {'number': total_entrada}})
    payload.update({'Saídas': {'number': total_saida}})
    create_page(secrets_eletrogrow.BALANCE_DATABASE, payload)


def recurrence():
    _filter = {"property": "Ativa",
                   "formula": {
                       "checkbox": {
                           "equals": True
                       }
                   }
               }
    res_recurrence = get_pages(secrets_eletrogrow.RECURRENCE_DATABASE, _filter=_filter)
    if res_recurrence:
        for page in res_recurrence:
            if (page['properties']['Data']['number'] == (datetime.date.today()+relativedelta(days=7)).timetuple()[2] and
                    page['properties']['Ativa']['checkbox']):
                title = page['properties']["Despesa"]["title"][0]["text"]["content"]
                title = title + f' - {MONTHS[datetime.date.today().timetuple()[1] - 1]}/{str(datetime.date.today().timetuple()[0])[-2:]}'
                valor = page['properties']['Valor']['number']
                data_vencimento = datetime.datetime.strftime(isdateutil(datetime.date.today()+relativedelta(days=7)), '%Y-%m-%d')
                forma_pagamento = page['properties']['Forma de pagamento']['select']['name']
                tipos = [{"name":tipo['name']} for tipo in page['properties']['Tipo']['multi_select']] \
                    if page['properties']['Tipo']['multi_select'] else [{"name":"Despesa Recorrente"}]
                data_final = page['properties']['Fim']['date']
                payload = {}
                payload.update({"Despesa": {"title": [{"text": {"content": title}}]}})
                payload.update({"Tipo": {"multi_select": tipos}})
                payload.update({'Data': {'date': {'start': data_vencimento}}})
                payload.update({"Forma de pagamento": {"select": {"name": forma_pagamento}}})
                payload.update({'Valor': {'number': valor}})
                create_page(secrets_eletrogrow.EXIT_DATABASE, payload)
                if data_final:
                    data_final = datetime.datetime.strptime(data_final['start'], '%Y-%m-%d').date()
                    if data_final.timetuple()[0:2] == (datetime.date.today() + relativedelta(days=7)).timetuple()[0:2]:
                        update_page(page['id'], {"Ativa": {"checkbox": False}})
def solve_exit():
    _filter = {"property": "Parcelas criadas",
               "formula": {
                   "checkbox": {
                       "equals": False
                   }
               }
               }
    res = get_pages(secrets_eletrogrow.CREDIT_EXIT_DATABASE, _filter=_filter)
    if res:
        for page in res:
            #print(json.dumps(page, indent=4))
            valor = page['properties']['Valor']['number']
            parcelas = page['properties']['Parcelas']['number']
            if not parcelas:
                parcelas = 1
            nome = page['properties']["Despesa"]["title"][0]["text"]["content"]
            data = datetime.datetime.strptime(page['properties']['Data']['date']['start'],
                                              '%Y-%m-%d').date()
            #data = isdateutil(data)
            tipos = [{"name": tipo['name']} for tipo in page['properties']['Tipo']['multi_select']] \
                if page['properties']['Tipo']['multi_select'] else []
            relation_id = page['properties']['Projeto']['relation'][0]['id']\
                if page['properties']['Projeto']['relation'] else None
            project_id = page['id']
            payload = {}
            for parcela in range(parcelas):
                title = f'{nome} - {parcela + 1}/{parcelas}' if parcelas > 1 else nome
                value = valor / parcelas
                date = data + relativedelta(months=parcela)
                payload.update({"Despesa": {"title": [{"text": {"content": title}}]}})
                payload.update({'Valor': {'number': value}})
                payload.update({'Data': {'date': {'start': datetime.datetime.strftime(date, '%Y-%m-%d')}}})
                payload.update({"Tipo": {"multi_select": tipos}})
                if relation_id:
                    payload.update({'Projeto': {'relation': [{'id': relation_id}]}})
                res = create_page(secrets_eletrogrow.CREDIT_PARCEL_DATABASE, payload)
            if res.status_code == 200:
                payload_parcelas = {"Parcelas criadas": {"checkbox": True}}
                update_page(project_id, payload_parcelas)
            if {'name':'Reembolso'} in tipos:
                payload['Receita'] = payload['Despesa']
                payload['Receita']['title'][0]['text']['content'] = nome
                payload.pop('Despesa')
                payload['Valor']['number'] = valor
                payload['Data']['date']['start'] = datetime.datetime.strftime(data, '%Y-%m-%d')
                payload.pop('Tipo')
                payload['Forma de pagamento'] = {'multi_select':[{'name': 'PIX'}, {'name':'Reembolso'}]}
                pprint(payload)
                res = create_page(secrets_eletrogrow.ENTRY_DATABASE, payload)
                pprint(res.content)

def invoice_closing():
    hoje = datetime.date.today()
    #hoje = datetime.date(2025,3,27)
    data = datetime.datetime.strftime(isdateutil(hoje, delta="Negative"), '%Y-%m-%d')
    _filter = {"and": [
        {"property": "Data",
         "formula": {
             "date": {
                 "on_or_before": data
             }
         }
         },
        {"property": "Fechamento",
         "formula": {
             "checkbox": {
                 "equals": False
             }
         }
         }
    ]
    }
    res = get_pages(secrets_eletrogrow.CREDIT_PARCEL_DATABASE, _filter=_filter)
    valor = 0
    if res:
        for page in res:
            valor += page['properties']['Valor']['number']
            payload = {"Fechamento": {"checkbox": True}}
            update_page(page['id'], payload)
            print(valor)
    print(valor)
    despesa = f'Cartão de Crédito {MONTHS[hoje.timetuple()[1] - 1]}/{str(hoje.timetuple()[0])[-2:]}'
    favorecido = secrets_eletrogrow.NUBANK_ID
    tipo = 'Despesa Recorrente'
    data = datetime.datetime.strftime(datetime.date.today() + relativedelta(months=1, day=3), '%Y-%m-%d')
    forma_pagamento = "Boleto"
    payload = {}
    payload.update({"Despesa": {"title": [{"text": {"content": despesa}}]}})
    payload.update({'Valor': {'number': valor}})
    payload.update({'Data': {'date': {'start': data}}})
    payload.update({"Tipo": {"multi_select": [{'name': tipo}]}})
    payload.update({"Forma de pagamento":{"select": {'name':forma_pagamento}}})
    payload.update({'Favorecido': {'relation': [{'id': favorecido}]}})
    res = create_page(secrets_eletrogrow.EXIT_DATABASE, payload)


def dash_gastos(**data):
    gastos = {}
    _filter = {'and':[{'property':'Favorecido',
                   'relation':{
                       'does_not_contain': secrets_eletrogrow.NUBANK_ID
                   }}]}
    start_date = [data[i] for i in ['desde, primeiro_dia', 'start_date'] if i in data.keys()][0]
    if start_date:
        _filter['and'].append({'property': 'Data',
                               'date': {'on_or_after': start_date}})
    end_date = [data[i] for i in ['ate', 'ultimo_dia', 'end_date'] if i in data.keys()][0]
    if end_date:
        _filter['and'].append({'property': 'Data',
                               'date': {'on_or_before': end_date}})

    res = get_pages(secrets_eletrogrow.EXIT_DATABASE, _filter=_filter)
    if res:
        for i in res:
            for tipo in i['properties']['Tipo']['multi_select']:
                if tipo['name'].capitalize() == 'Reembolso':
                    continue
                if tipo['name'].capitalize() in gastos.keys():
                    gastos[tipo['name'].capitalize()] += i['properties']['Valor']['number']
                else:
                    gastos[tipo['name'].capitalize()] = i['properties']['Valor']['number']
    _filter['and'].pop(0)
    res = get_pages(secrets_eletrogrow.CREDIT_PARCEL_DATABASE, _filter=_filter)
    if res:
        for i in res:
            if len(i['properties']['Tipo']['multi_select'])>1:
                if 'Reembolso' in gastos.keys():
                    gastos['Reembolso'] += i['properties']['Valor']['number']
                else:
                    gastos['Reembolso'] = i['properties']['Valor']['number']
                continue
            for tipo in i['properties']['Tipo']['multi_select']:
                if tipo['name'].capitalize() in gastos.keys():
                    gastos[tipo['name'].capitalize()] += i['properties']['Valor']['number']
                else:
                    gastos[tipo['name'].capitalize()] = i['properties']['Valor']['number']
    return gastos

def dash_balance(**data):
    balance={}
    _filter={'and':[]}
    start_date = [data[i] for i in ['desde, primeiro_dia', 'start_date'] if i in data.keys()][0]
    if start_date:
        _filter['and'].append({'timestamp':'created_time', 'created_time': {'on_or_after': start_date}})
    end_date = [data[i] for i in ['ate', 'ultimo_dia', 'end_date'] if i in data.keys()][0]
    if end_date:
        _filter['and'].append({'timestamp':'created_time', 'created_time': {'on_or_before': end_date}})
    res = get_pages(secrets_eletrogrow.BALANCE_DATABASE, _filter=_filter)
    for i in res:
        balance[i['properties']['Mês']['title'][0]['plain_text']] = {'Receita': i['properties']['Entradas']['number'],
                                                                     'Gastos': i['properties']['Saídas']['number'],
                                                                     'Balanço': i['properties']['Saldo']['formula']['number']}
    for i in balance.keys():
        for j in balance[i]:
            if balance[i][j] is None:
                balance[i][j] = 0
    return dict(reversed(list(balance.items())))

def dash_get_project_name():
    nomes_projetos=[]
    projetos = get_pages(secrets_eletrogrow.PROJECTS_DATABASE,_filter={'property': 'Data vencimento',
                               'date': {'on_or_before': datetime.date.today().strftime('%Y-%m-%d')}},
                         num_pages=10)
    clientes = get_pages(secrets_eletrogrow.CLIENTS_DATABASE)
    if projetos:
        for projeto in projetos:
            nome_cliente = None
            for cliente in clientes:
                if projeto['properties']['Clientes']['relation'][0]['id'] in cliente.values():
                     nome_cliente = cliente['properties']['Nome']['title'][0]['plain_text']
                     break
            nomes_projetos.append({'projeto' : projeto['properties']['Nome']['title'][0]['plain_text'],
                                   'cliente': nome_cliente,
                                   'data_vencimento': projeto['properties']['Data vencimento']['date']['start']})
            from main import dbc
            lista = []
            for i in nomes_projetos:
                lista.append(dbc.DropdownMenuItem(f'{i["cliente"]} ---- {i["data_vencimento"]}', header=True))
                lista.append(dbc.DropdownMenuItem(i['projeto']))


    return lista
def get_object(obj):

    url = f'https://api.notion.com/v1/pages/{obj}'

    response = requests.get(url, headers=headers)
    return response.json()


def get_clients():
    response = []
    for i in get_pages(secrets_eletrogrow.CLIENTS_DATABASE, ):
        client = {}
        data = i['properties']
        client['neighborhood'] = data['Bairro']['rich_text'][0]['plain_text'] if data['Bairro']['rich_text'] else None
        client['cep'] = data['CEP']['rich_text'][0]['plain_text'] if data['CEP']['rich_text'] else None
        if data['CPF/CNPJ']['rich_text']:
            if len(data['CPF/CNPJ']['rich_text'][0]['plain_text']) == 14:
                client['cpf'] = data['CPF/CNPJ']['rich_text'][0]['plain_text']
            else:
                client['cnpj'] = data['CPF/CNPJ']['rich_text'][0]['plain_text']
        location = data['Cidade']['rich_text'][0]['plain_text'].split('/') if data['Cidade']['rich_text'] else None
        if location:
            client['city'] = location[0] if len(location) > 0 else None
            client['state'] = location[1] if len(location) > 1 else None
        client['email'] = data['E-mail']['email']
        client['address'] = data['Endereço']['rich_text'][0]['plain_text'] if data['Endereço']['rich_text'] else None
        client['name'] = data['Nome']['title'][0]['plain_text']
        client['phone'] = data['Telefone']['phone_number']
        response.append(client)
    return response

def get_projects():
    response = []
    for i in get_pages(secrets_eletrogrow.PROJECTS_DATABASE,):
        project = {}
        data = i['properties']
        project['client'] = get_object(data['Clientes']['relation'][0]['id'])['properties']['Nome']['title'][0]['plain_text']
        project['due_date'] = data['Data vencimento']['date']['start']
        project['end_project'] = data['Fim projeto/obra']['date']['start'] if data['Fim projeto/obra']['date'] else None
        project['start_work'] = data['Inicio Obra']['date']['start'] if data['Inicio Obra']['date'] else None
        project['start_project'] = data['Inicio Projeto']['date']['start'] if data['Inicio Projeto']['date'] else None
        project['name'] = data['Nome']['title'][0]['plain_text']
        project['parcel'] = data['Parcelas']['number'] if data['Parcelas']['number'] else 1
        project['value'] = data['Valor']['number']
        response.append(project)
    return response

if __name__ == "__main__":
    
    #ModelCreditOutflow
    '''
    for i in get_pages(secrets_eletrogrow.CREDIT_PARCEL_DATABASE, num_pages=3):
        data = i['properties']
        response['date'] = data['Data']['date']['start']
        response['expense'] = data['Despesa']['title'][0]['plain_text']
        response['closing'] = data['Fechamento']['checkbox']
        response['project'] = data['Projeto']['relation'][0]
        response['type'] = [name['name'] for name in data['Tipo']['multi_select']]
        response['value'] = data['Valor']['number']
        print(f'Objeto {n+1}')
        n+=1
        pprint(response)'''



    #TODO:
    #keywords desde-até conversão de string formato d/m/a para '%Y-%m-%d'

    #787c22fd-c856-4863-b7c0-272a2300448c
