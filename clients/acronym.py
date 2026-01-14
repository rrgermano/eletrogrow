PREPOSICOES = {
    "DA", "DE", "DO", "DOS", "DAS", "A", "O", "OS", "AS", "EM", "NO", "NA", "NOS", "NAS"
}


def _get_consoantes(nome: str) -> list[str]:
    return [c for c in nome.upper() if c not in "AEIOU"]


def _consoante_do_meio(palavra: str) -> str | None:
    consoantes = [c for c in palavra.upper() if c not in "AEIOU"]
    if not consoantes:
        return None
    # pega a consoante mais central
    return consoantes[len(consoantes) // 2]


def _codigo_inicial(nome_completo: str) -> str:
    # Remove acentos se precisar (opcional, mas comum)
    nome_limpo = nome_completo.replace("Ã", "A").replace("Ã£", "a")  # etc., ou use unicodedata
    partes = [p.strip().upper() for p in nome_limpo.split() if p.strip()]

    # Remove preposições
    partes_filtradas = [p for p in partes if p not in PREPOSICOES]

    if not partes_filtradas:
        return ""

    # 1) 3 ou mais nomes (sem prep.): 3 iniciais das 3 primeiras
    if len(partes_filtradas) >= 3:
        return partes_filtradas[0][0] + partes_filtradas[1][0] + partes_filtradas[2][0]

    # 2) 1 nome só: primeiras 3 letras (ou o que tiver)
    if len(partes_filtradas) == 1:
        return partes_filtradas[0][:3]

    # 3) 2 nomes: SEMPRE 3 iniciais (JSL para João Silva)
    # se 2ª parte curta, completa com consoante do meio da 2ª ou da 1ª
    p1, p2 = partes_filtradas
    base = p1[0] + p2[0]
    if len(p2) >= 3:
        return base + p2[2]  # 3ª letra da 2ª parte
    else:
        # completa com consoante do meio da 2ª
        c_meio = _consoante_do_meio(p2)
        if c_meio:
            return base + c_meio
        # fallback: consoante do meio da 1ª
        c_meio = _consoante_do_meio(p1)
        if c_meio:
            return base + c_meio
        # último recurso: próxima letra da 1ª
        if len(p1) > 2:
            return p1[0] + p1[1] + p1[2]
        return base + "X"  # ou fallback padrão


def get_project_prefix(nome_completo: str, existentes: set[str]) -> str:
    base = _codigo_inicial(nome_completo)
    if base not in existentes:
        existentes.add(base)
        return base

    partes = [p.strip().upper() for p in nome_completo.split() if p.strip()]
    partes_filtradas = [p for p in partes if p not in PREPOSICOES]

    if len(partes_filtradas) < 2:
        # fallback simples para 1 nome
        return _gerar_fallback(base, existentes)

    p1, p2 = partes_filtradas  # José, Silva

    atual_final = base[-1]  # 'L'

    # PRIORIDADE MÁXIMA: próximas consoantes da 2ª parte APÓS a posição atual
    consoantes_p2 = _get_consoantes(p2)  # ['S','L','V']
    try:
        idx_atual = consoantes_p2.index(atual_final)  # índice de 'L' = 1
        for c in consoantes_p2[idx_atual + 1:]:  # ['V'] ← pega V primeiro!
            cand = base[:-1] + c  # "JSV"
            if cand not in existentes:
                existentes.add(cand)
                return cand
    except ValueError:
        pass  # se não achar a consoante atual na p2

    # PRIORIDADE 2: todas consoantes da 2ª parte (exceto atual)
    for c in consoantes_p2:
        if c != atual_final:
            cand = base[:-1] + c
            if cand not in existentes:
                existentes.add(cand)
                return cand

    # PRIORIDADE 3: consoantes da 1ª parte
    consoantes_p1 = _get_consoantes(p1)
    for c in consoantes_p1:
        if c != atual_final:
            cand = base[:-1] + c
            if cand not in existentes:
                existentes.add(cand)
                return cand

    return _gerar_fallback(base, existentes)


def _gerar_fallback(base: str, existentes: set[str]) -> str:
    """Fallback numérico"""
    suf = 1
    while True:
        cand = f"{base[0:2]}{suf}"
        if cand not in existentes:
            existentes.add(cand)
            return cand
        suf += 1


