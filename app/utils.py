import datetime
import time
import pandas_market_calendars as mcal
from dateutil.relativedelta import relativedelta

def is_date_util(date, delta="Positive"):
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


def calcular_periodo_cartao(tipo, mes_vigente):
    # Se não for especificado, usa o mês atual

    today = mes_vigente

    if (today + relativedelta(days=7)) <= is_date_util(today.replace(day=3) + relativedelta(months=1)):
        mes_vigente = today
    else:
        mes_vigente = today+relativedelta(months=1)
    if tipo.lower() == 'inicio':
        return is_date_util(mes_vigente.replace(day=3)) - relativedelta(days=7)
    elif tipo.lower() == 'fim':
        return is_date_util((mes_vigente+relativedelta(months=1)).replace(day=3)) - relativedelta(days=7)
    else:
        raise ValueError("Tipo inválido. Use 'inicio' ou 'fim'")


# Função adicional para obter o período completo
def obter_periodo_completo(mes_vigente = None):
    if not mes_vigente:
        mes_vigente = datetime.date.today()

    return {
        'fechamento': calcular_periodo_cartao('inicio', mes_vigente),
        'vencimento': calcular_periodo_cartao('fim', mes_vigente),
        'mes_referencia': mes_vigente.strftime('%B/%Y')
    }
