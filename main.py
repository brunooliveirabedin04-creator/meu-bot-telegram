import requests
import time
from telegram import Bot

TOKEN = "8620944454: AEGTs04cnCznL1iO_emGRdoagv0lg3eV_o"
CHAT_ID = "8291720119"

bot = Bot(token=TOKEN)

alertados = set()

def enviar(msg):
    try:
        bot.send_message(chat_id=CHAT_ID, text=msg)
    except:
        pass
def pegar_jogos():
    url = "https://api.sofascore.com/api/v1/sport/football/events/live"
    
    # Isso faz o script parecer um navegador real e evita o bloqueio
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    
    try:
        r = requests.get(url, headers=headers)
        dados = r.json()
        
        # Verifica se 'events' realmente existe na resposta antes de tentar usar
        if "events" in dados:
            return dados["events"]
        else:
            print("Aviso: Nâo foram encontrados jogos no momento.")
            return []
            
    except Exception as e:
        print(f"Erro na requisição: {e}")
        return []


def pegar_estatisticas(event_id):
    url = f"https://api.sofascore.com/api/v1/event/{event_id}/statistics"
    r = requests.get(url)
    return r.json()

def pegar_minuto(event):
    try:
        return event["time"]["current"]
    except:
        return 0

def analisar():
    jogos = pegar_jogos()

    for j in jogos:
        try:
            event_id = j["id"]

            minuto = pegar_minuto(j)
            if minuto < 45 or minuto > 70:
                continue

            home = j["homeTeam"]["name"]
            away = j["awayTeam"]["name"]

            home_score = j["homeScore"]["current"]
            away_score = j["awayScore"]["current"]

            stats = pegar_estatisticas(event_id)

            corners_home = 0
            corners_away = 0

            for group in stats.get("statistics", []):
                for item in group.get("statisticsItems", []):
                    if item.get("name") == "Corner kicks":
                        corners_home = int(item.get("home", 0))
                        corners_away = int(item.get("away", 0))

            total = corners_home + corners_away

            if total < 4:
                continue

            if corners_home > corners_away:
                fav = home
                fav_corners = corners_home
                opp_corners = corners_away
                fav_score = home_score
                opp_score = away_score
            else:
                fav = away
                fav_corners = corners_away
                opp_corners = corners_home
                fav_score = away_score
                opp_score = home_score

            if fav_score >= opp_score:
                continue

            if fav_corners - opp_corners < 2:
                continue

            if total < 5:
                race = 5
            elif total < 7:
                race = 7
            elif total < 9:
                race = 9
            else:
                continue

            faltam = race - total

            if faltam < 2 or faltam > 3:
                continue

            chave = f"{event_id}-{race}"
            if chave in alertados:
                continue

            alertados.add(chave)

            msg = f"""
🚨 ALERTA RACE ESCANTEIOS

{home} vs {away}
Min: {minuto}'

Placar: {home_score}-{away_score}

Escanteios: {corners_home}x{corners_away}
Total: {total}

Race: {race}
Faltam: {faltam}

Time: {fav}

➡️ ENTRADA: Race {race} cantos
"""

            enviar(msg)

        except:
            continue

while True:
    analisar()
    time.sleep(60)
