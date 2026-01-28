from notion.secrets_eletrogrow import WIX_TOKEN, WIX_ACCOUNT_ID
import requests

# CONFIGURAÇÕES -------------------------
API_KEY = WIX_TOKEN       # account-level API key para Domain DNS API
ACCOUNT_ID = WIX_ACCOUNT_ID    # ID da conta Wix (x-wix-account-id)
DOMAIN = "eletrogrow.com.br"         # domínio gerenciado pela Wix
HOST = "_acme-test.intranet"                   # host TXT de teste
TTL = 300

BASE_URL = "https://www.wixapis.com/domains/v1/dns-zones"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": API_KEY,           # para update-dns-zone é account-level key, não Bearer [web:27]
    "x-wix-account-id": ACCOUNT_ID,     # exigido para chamadas account-level [web:27][web:35]
}


def update_dns_zone(additions=None, deletions=None):
    url = f"{BASE_URL}/{DOMAIN}"  # ver nome exato na doc [web:27]
    payload = {
        "additions": additions or [],
        "deletions": deletions or [],
    }
    resp = requests.patch(url, json=payload, headers=HEADERS, timeout=30)
    print("Status:", resp.status_code)
    print("Resposta:", resp.text)
    resp.raise_for_status()


def create_txt():
    additions=[{
            "type": "TXT",
            "hostName": f'{HOST}.{DOMAIN}',
            "ttl": TTL,
            "values": ["teste-wix-dns-api"]
    }]
    print(f"Criando TXT {HOST}.{DOMAIN}...")
    update_dns_zone(additions=additions)


def delete_txt():
    deletions = [{
            "type": "TXT",
            "hostName": f'{HOST}.{DOMAIN}',
            "ttl": TTL,
            "values": ["teste-wix-dns-api"]
    }]
    print(f"Removendo TXT {HOST}.{DOMAIN}...")
    update_dns_zone(deletions=deletions)


if __name__ == "__main__":
    # 1) Criar TXT
    create_txt()
    input("Verifique no painel DNS da Wix se o TXT apareceu. Pressione ENTER para deletar...")

    # 2) Remover TXT
    delete_txt()
    print("Teste finalizado.")