from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import defaultdict
import re

app = Flask(__name__)
CORS(app)

@app.route("/formatar", methods=["POST"])
def formatar_tabela():
    data = request.get_json()
    professores = data.get("professores", [])
    restricoes = data.get("restricoes", [])
    turmas_filtradas = data.get("turmasSelecionadas", [])

    if turmas_filtradas:
        professores = [p for p in professores if p.get("turma") in turmas_filtradas]

    limite_aulas_semanais = {p['id']: p.get('limiteAulas', 4) for p in professores}

    dias = ["segunda", "terça", "quarta", "quinta", "sexta"]
    horas = ["07:30", "08:20", "09:10", "10:20", "11:10", "12:00"]

    grade = {}
    indisponiveis = defaultdict(list)
    preferencias = defaultdict(list)
    carga_professor = defaultdict(int)
    horarios_professor = defaultdict(set)
    aulas_por_dia = defaultdict(lambda: defaultdict(int))

    def extrair_chaves(desc):
        desc = desc.lower()
        chaves = []
        for dia in dias:
            for hora in horas:
                chave = f"{dia.capitalize()}_{hora}"
                if dia in desc and hora in desc:
                    chaves.append(chave)
                elif dia in desc and not re.search(r"\d{2}[:h]\d{2}", desc):
                    chaves.append(chave)
                elif hora in desc and not any(d in desc for d in dias):
                    chaves.append(chave)
        if "almoço" in desc or "horário de almoço" in desc:
            for h in ["11:10", "12:00"]:
                for d in dias:
                    chaves.append(f"{d.capitalize()}_{h}")
        return chaves

    for r in restricoes:
        prof_id = r["professorId"]
        desc = r["descricao"].lower()
        chaves = extrair_chaves(desc)

        if "não pode" in desc or "não está disponível" in desc:
            indisponiveis[prof_id].extend(chaves)
        elif "pode" in desc or "quer" in desc:
            preferencias[prof_id].extend(chaves)

    aulas_consecutivas = defaultdict(list)

    pattern = r"terá\s+(\d+)\s+aulas\s+na?\s+(\w+),?.*só pode(?:rá)? dar aula depois das\s+(\d{2}[:h]\d{2})"

    def horarios_apos(hora_min, lista_horas):
        def to_minutes(h):
            h_, m_ = map(int, h.split(":"))
            return h_ * 60 + m_
        min_min = to_minutes(hora_min)
        return [h for h in lista_horas if to_minutes(h) >= min_min]

    for r in restricoes:
        prof_id = r["professorId"]
        desc = r["descricao"].lower()
        m = re.search(pattern, desc)
        if m:
            qtd = int(m.group(1))
            dia = m.group(2)
            hora_min = m.group(3).replace("h", ":")
            tem_seguidas = "(aulas seguidas)" in desc

            if tem_seguidas:
                aulas_consecutivas[prof_id].append((dia, hora_min, qtd))
            else:
                horarios_possiveis = horarios_apos(hora_min, horas)
                for h in horarios_possiveis:
                    chave = f"{dia.capitalize()}_{h}"
                    preferencias[prof_id].append(chave)

    def pode_alocar(prof, chave):
        prof_id = prof["id"]
        if chave in indisponiveis[prof_id]:
            return False
        if chave in horarios_professor[prof_id]:
            return False
        dia = chave.split("_")[0].lower()
        if aulas_por_dia[prof_id][dia] >= 3:
            return False
        if carga_professor[prof_id] >= limite_aulas_semanais.get(prof_id, 15):
            return False
        return True

    def alocar_professor(chave, escolhido):
        prof_id = escolhido["id"]
        grade[chave] = {
            "professor": f"{escolhido['nome']} {escolhido['sobrenome']}",
            "materia": escolhido["materia"],
            "turma": escolhido["turma"]
        }
        carga_professor[prof_id] += 1
        horarios_professor[prof_id].add(chave)
        dia = chave.split("_")[0].lower()
        aulas_por_dia[prof_id][dia] += 1

    def alocar_aulas_consecutivas(prof, dia, hora_min, qtd):
        horarios_disponiveis = horarios_apos(hora_min, horas)
        for i in range(len(horarios_disponiveis) - qtd + 1):
            sequencia = horarios_disponiveis[i:i + qtd]
            chaves = [f"{dia.capitalize()}_{h}" for h in sequencia]
            if all(pode_alocar(prof, c) for c in chaves):
                for c in chaves:
                    alocar_professor(c, prof)
                return True
        return False

    for prof in professores:
        prof_id = prof["id"]
        if prof_id in aulas_consecutivas:
            for (dia, hora_min, qtd) in aulas_consecutivas[prof_id]:
                alocar_aulas_consecutivas(prof, dia, hora_min, qtd)

    for dia in dias:
        for hora in horas:
            chave = f"{dia.capitalize()}_{hora}"
            if chave in grade:
                continue
            candidatos = [
                p for p in professores
                if chave in preferencias[p["id"]] and pode_alocar(p, chave)
            ]
            if candidatos:
                candidatos.sort(key=lambda x: x.get("pontuacao", 0), reverse=True)
                escolhido = candidatos[0]
                alocar_professor(chave, escolhido)

    for dia in dias:
        for hora in horas:
            chave = f"{dia.capitalize()}_{hora}"
            if chave in grade:
                continue
            candidatos = [
                p for p in professores
                if pode_alocar(p, chave)
            ]
            if candidatos:
                candidatos.sort(key=lambda x: carga_professor[x["id"]])
                escolhido = candidatos[0]
                alocar_professor(chave, escolhido)

    return jsonify({"status": "ok", "grade": grade})

if __name__ == "__main__":
    app.run(debug=True)